"""
==========================================================
CanopyAI
Sentinel-2 Fetcher (via Microsoft Planetary Computer)
==========================================================

Given a GeoJSON polygon, download a 13-band Sentinel-2
raster covering that area and save it as
uploads/latest.tif so the existing AI pipeline can run
on it exactly as if the user had uploaded a TIF.

Strategy: latest LEAST-CLOUDY scene in the last 90 days
that intersects the polygon.

Notes on the "13" bands:
    Sentinel-2 L2A publishes 12 usable bands
    (no B10 — cirrus band, absent from L2A).
    We stack B01..B09, B8A, insert a zeros band in the
    B10 slot, then B11, B12  →  13 bands total,
    matching what the AI model was trained on.

Dependencies (install once):
    pip install pystac-client planetary-computer rioxarray

The heavy imports are done LAZILY inside fetch() so the
rest of the backend still boots if these aren't installed.
==========================================================
"""

from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import rasterio


# Band ordering the model was trained on
FULL_BAND_ORDER = [
    "B01", "B02", "B03", "B04", "B05",
    "B06", "B07", "B08", "B8A", "B09",
    "B10", "B11", "B12"
]

# L2A doesn't have B10 (cirrus) — we'll pad with zeros
L2A_MISSING = {"B10"}


def _extract_geometry(geojson):

    """Accept FeatureCollection / Feature / bare geometry."""

    if not isinstance(geojson, dict):
        raise ValueError("GeoJSON must be a dict")

    t = geojson.get("type")

    if t == "FeatureCollection":
        feats = geojson.get("features") or []
        if not feats:
            raise ValueError("FeatureCollection has no features")
        return feats[0].get("geometry")

    if t == "Feature":
        return geojson.get("geometry")

    if t in ("Polygon", "MultiPolygon"):
        return geojson

    raise ValueError(
        f"Unsupported GeoJSON type: {t!r} "
        "(expected FeatureCollection, Feature, Polygon, or MultiPolygon)"
    )


# =====================================================
# MAIN FETCH
# =====================================================


def fetch(geojson, save_path="uploads/latest.tif", max_cloud=30,
          cleanup=True, run_aux=True):

    """Fetch a 13-band Sentinel-2 raster covering the GeoJSON.

    cleanup: if True, delete every *.tif in save_path's parent first
             (matches the /upload behaviour so old uploads don't linger).
             Set False if you want to keep siblings (e.g. latest.tif).
    run_aux: if True, also build NDVI / WorldCover / LST / rainfall.
    """

    # Lazy imports — if the user doesn't have these installed
    # the rest of the backend still works.
    try:
        import pystac_client
        import planetary_computer
        import rioxarray  # noqa: F401 (registers .rio accessor)
        from shapely.geometry import shape
    except ImportError as e:
        raise ImportError(
            "Sentinel fetcher requires extra packages. "
            "Install with:\n"
            "    pip install pystac-client planetary-computer rioxarray shapely\n"
            f"(missing: {e.name})"
        )

    geometry = _extract_geometry(geojson)
    geom_shape = shape(geometry)
    bbox = list(geom_shape.bounds)   # [minx, miny, maxx, maxy]

    print(f"[fetcher] bbox = {bbox}")

    # -------------------------------------------------
    # 1. Search Planetary Computer STAC
    # -------------------------------------------------

    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace
    )

    now = datetime.utcnow()
    start = (now - timedelta(days=90)).strftime("%Y-%m-%d")
    end = now.strftime("%Y-%m-%d")

    print(f"[fetcher] searching {start} → {end}, cloud < {max_cloud}%")

    search = catalog.search(
        collections=["sentinel-2-l2a"],
        bbox=bbox,
        datetime=f"{start}/{end}",
        query={"eo:cloud_cover": {"lt": max_cloud}}
    )

    items = list(search.items())

    if not items:
        raise RuntimeError(
            f"No Sentinel-2 L2A scenes found in the last 90 days "
            f"with cloud cover < {max_cloud}% intersecting the polygon. "
            f"Try widening the polygon or a different area."
        )

    items.sort(
        key=lambda i: i.properties.get("eo:cloud_cover", 100)
    )
    best = items[0]

    cloud = best.properties.get("eo:cloud_cover", "?")
    scene_date = best.properties.get("datetime", "?")

    print(f"[fetcher] chosen scene {best.id}")
    print(f"[fetcher] date   = {scene_date}")
    print(f"[fetcher] cloud  = {cloud}%")

    # -------------------------------------------------
    # 2. Download + resample each band to 10m grid
    # -------------------------------------------------

    ref_da = None
    stacked = []

    for band in FULL_BAND_ORDER:

        if band in L2A_MISSING:
            # Placeholder — real band data appended after ref is known
            stacked.append(None)
            continue

        asset = best.assets.get(band)
        if asset is None:
            print(f"[fetcher] WARN band {band} not in assets — padding zeros")
            stacked.append(None)
            continue

        print(f"[fetcher] loading {band} from {asset.href[:80]}...")

        # Use rioxarray (registered via `import rioxarray` above)
        import rioxarray as rxr
        da = rxr.open_rasterio(asset.href, masked=True)

        # Clip to polygon.
        # IMPORTANT: our geometry is in EPSG:4326 (lon/lat) but the
        # Sentinel raster is in UTM (meters) — pass crs= so rioxarray
        # reprojects the geometry before intersecting.
        try:
            da = da.rio.clip(
                [geom_shape.__geo_interface__],
                crs="EPSG:4326",
                from_disk=True,
                all_touched=True
            )
        except Exception as e:
            print(f"[fetcher] clip failed for {band}: {e} — skipping band")
            stacked.append(None)
            continue

        # First real band becomes the reference grid (10m)
        if ref_da is None:
            ref_da = da
        else:
            da = da.rio.reproject_match(ref_da)

        stacked.append(da.squeeze().values)

    if ref_da is None:
        raise RuntimeError(
            "Could not load any Sentinel-2 bands — "
            "polygon may be outside the scene footprint."
        )

    # Fill None placeholders (B10, missing bands) with zeros
    zeros = np.zeros_like(stacked[0], dtype=np.float32)
    stacked = [
        (b if b is not None else zeros.copy())
        for b in stacked
    ]

    assert len(stacked) == 13, f"Expected 13 bands, got {len(stacked)}"

    stack = np.stack(stacked, axis=0).astype(np.float32)

    # -------------------------------------------------
    # 3. Save as multi-band GeoTIFF
    # -------------------------------------------------

    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    # remove old TIFs in uploads to match existing upload behaviour
    if cleanup:
        for old in save_path.parent.glob("*.tif"):
            try:
                old.unlink()
            except Exception:
                pass
        for old in save_path.parent.glob("*.tiff"):
            try:
                old.unlink()
            except Exception:
                pass

    profile = {
        "driver": "GTiff",
        "height": stack.shape[1],
        "width": stack.shape[2],
        "count": 13,
        "dtype": "float32",
        "crs": ref_da.rio.crs,
        "transform": ref_da.rio.transform(),
        "compress": "lzw",
        "tiled": True
    }

    with rasterio.open(save_path, "w", **profile) as dst:
        for i in range(13):
            dst.write(stack[i], i + 1)

    print(f"[fetcher] saved {save_path} — shape {stack.shape}")

    # -------------------------------------------------
    # 4. Build auxiliary rasters (NDVI, WorldCover, LST, rainfall)
    #    Impact engine will now find them in uploads/ and
    #    prefer them over the Delhi files in data/.
    # -------------------------------------------------

    aux_results = None

    if run_aux:
        from backend.imagery_fetcher.aux_fetcher import build_all_aux

        aux_results = build_all_aux(
            geometry,
            sentinel_path=str(save_path),
            uploads_dir=str(save_path.parent)
        )

    return {
        "status": "success",
        "saved_path": str(save_path),
        "scene_id": best.id,
        "scene_date": scene_date,
        "cloud_cover_pct": cloud,
        "shape": list(stack.shape),
        "bbox": bbox,
        "aux": aux_results
    }
