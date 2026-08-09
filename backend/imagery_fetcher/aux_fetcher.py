"""
==========================================================
CanopyAI
Auxiliary raster fetcher
==========================================================

Produces the extra rasters the impact engine needs when
we're not running on the pre-baked Delhi data:

    uploads/ndvi.tif        derived from Sentinel B04, B08
    uploads/worldcover.tif  ESA WorldCover 10m (remapped to 4 classes)
    uploads/lst.tif         MODIS 8-day LST (~1 km, resampled)
    uploads/rainfall.tif    uniform placeholder (0.5)

All rasters are written to the SAME grid as
uploads/latest.tif (Sentinel-2 stack), so the impact
engine aligner can consume them without reprojection
surprises.

Skipped rasters just default to the placeholder — the
pipeline degrades gracefully rather than crashing.
==========================================================
"""

from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import rasterio
from rasterio.enums import Resampling


# ESA WorldCover 10-class → CanopyAI 4-class remap
# Target classes: 0 = bare/other, 1 = canopy, 2 = built-up, 3 = cropland
WORLDCOVER_REMAP = {
    10: 1,   # Tree cover        -> canopy
    20: 0,   # Shrubland         -> bare/other
    30: 0,   # Grassland         -> bare/other
    40: 3,   # Cropland          -> cropland
    50: 2,   # Built-up          -> built-up
    60: 0,   # Bare/sparse veg   -> bare/other
    70: 0,   # Snow/ice          -> bare/other
    80: 0,   # Permanent water   -> bare/other
    90: 0,   # Herbaceous wetl.  -> bare/other
    95: 1,   # Mangroves         -> canopy
    100: 0,  # Moss/lichen       -> bare/other
}


# =====================================================
# NDVI FROM SENTINEL
# =====================================================


def derive_ndvi(sentinel_path, save_path):

    """NDVI = (B08 - B04) / (B08 + B04)
       Band stack order: 1:B01 2:B02 3:B03 4:B04 5:B05 6:B06 7:B07 8:B08 ..."""

    print(f"[aux] deriving NDVI from {sentinel_path}")

    with rasterio.open(sentinel_path) as src:

        red = src.read(4).astype(np.float32)   # B04
        nir = src.read(8).astype(np.float32)   # B08

        with np.errstate(divide="ignore", invalid="ignore"):
            ndvi = (nir - red) / (nir + red + 1e-6)

        ndvi = np.clip(ndvi, -1.0, 1.0)

        profile = src.profile.copy()
        profile.update(count=1, dtype="float32", compress="lzw")

    with rasterio.open(save_path, "w", **profile) as dst:
        dst.write(ndvi, 1)

    print(f"[aux] wrote {save_path}  range=[{ndvi.min():.2f}, {ndvi.max():.2f}]")


# =====================================================
# WORLDCOVER  (ESA 10m global, remapped to 4 classes)
# =====================================================


def fetch_worldcover(geom, ref_path, save_path):

    import pystac_client, planetary_computer
    import rioxarray as rxr
    from shapely.geometry import shape

    print("[aux] fetching ESA WorldCover ...")

    geom_shape = shape(geom)
    bbox = list(geom_shape.bounds)

    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace
    )

    search = catalog.search(
        collections=["esa-worldcover"],
        bbox=bbox
    )

    items = list(search.items())

    if not items:
        raise RuntimeError("No ESA WorldCover data covers this polygon")

    # Take the most recent (WorldCover has 2020 + 2021 versions)
    items.sort(
        key=lambda i: i.properties.get("start_datetime", ""),
        reverse=True
    )
    item = items[0]

    asset = item.assets.get("map")
    if asset is None:
        raise RuntimeError("WorldCover item missing 'map' asset")

    with rasterio.open(ref_path) as ref:
        ref_crs = ref.crs
        ref_transform = ref.transform
        ref_shape = (ref.height, ref.width)
        ref_profile = ref.profile.copy()

    da = rxr.open_rasterio(asset.href, masked=True)

    # Clip in native CRS (WorldCover is EPSG:4326)
    da = da.rio.clip(
        [geom_shape.__geo_interface__],
        crs="EPSG:4326",
        from_disk=True,
        all_touched=True
    )

    # Reproject to Sentinel grid (nearest — preserve categorical values)
    da = da.rio.reproject(
        dst_crs=ref_crs,
        transform=ref_transform,
        shape=ref_shape,
        resampling=Resampling.nearest
    )

    src_classes = da.squeeze().values.astype(np.uint16)

    # Remap to 4 classes
    out = np.zeros_like(src_classes, dtype=np.uint8)
    for src_val, dst_val in WORLDCOVER_REMAP.items():
        out[src_classes == src_val] = dst_val

    ref_profile.update(count=1, dtype="uint8", compress="lzw", nodata=None)

    with rasterio.open(save_path, "w", **ref_profile) as dst:
        dst.write(out, 1)

    print(f"[aux] wrote {save_path}  classes={np.unique(out).tolist()}")


# =====================================================
# LST  (MODIS 8-day day-time LST, ~1 km resampled)
# =====================================================


def fetch_lst(geom, ref_path, save_path):

    import pystac_client, planetary_computer
    import rioxarray as rxr
    from shapely.geometry import shape

    print("[aux] fetching MODIS 8-day LST ...")

    geom_shape = shape(geom)
    bbox = list(geom_shape.bounds)

    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace
    )

    # Search a wider window — MODIS composites are 8-day, so 120 days
    # gives us plenty of scenes to average.
    now = datetime.utcnow()
    start = (now - timedelta(days=120)).strftime("%Y-%m-%d")
    end = now.strftime("%Y-%m-%d")

    search = catalog.search(
        collections=["modis-11A2-061"],
        bbox=bbox,
        datetime=f"{start}/{end}"
    )

    items = list(search.items())

    if not items:
        raise RuntimeError(
            "No MODIS LST composites in the last 120 days for this area"
        )

    # Take latest
    items.sort(
        key=lambda i: i.properties.get("datetime", ""),
        reverse=True
    )
    item = items[0]

    # MODIS 11A2 day-time LST asset key
    asset = (
        item.assets.get("LST_Day_1km")
        or item.assets.get("lst-day-1km")
        or item.assets.get("LST_Day")
    )

    if asset is None:
        raise RuntimeError(
            f"MODIS item {item.id} missing day LST asset. "
            f"Available: {list(item.assets.keys())[:8]}"
        )

    with rasterio.open(ref_path) as ref:
        ref_crs = ref.crs
        ref_transform = ref.transform
        ref_shape = (ref.height, ref.width)
        ref_profile = ref.profile.copy()

    da = rxr.open_rasterio(asset.href, masked=True)

    da = da.rio.clip(
        [geom_shape.__geo_interface__],
        crs="EPSG:4326",
        from_disk=True,
        all_touched=True
    )

    # Reproject to Sentinel grid (bilinear — continuous)
    da = da.rio.reproject(
        dst_crs=ref_crs,
        transform=ref_transform,
        shape=ref_shape,
        resampling=Resampling.bilinear
    )

    # MODIS LST comes in Kelvin scaled by 0.02.
    # We don't need real Kelvin — the normalizer stretches to 0..1.
    values = da.squeeze().values.astype(np.float32)

    ref_profile.update(count=1, dtype="float32", compress="lzw", nodata=None)

    with rasterio.open(save_path, "w", **ref_profile) as dst:
        dst.write(values, 1)

    print(f"[aux] wrote {save_path}  "
          f"range=[{np.nanmin(values):.1f}, {np.nanmax(values):.1f}]")


# =====================================================
# PLACEHOLDER WRITER
# =====================================================


def write_placeholder(ref_path, save_path, value=0.5,
                       dtype="float32", label="placeholder"):

    """
    Write a single-band raster of `value` on the SAME grid as
    ref_path. Used when a real fetch fails, so the impact
    engine still finds a file in uploads/ and doesn't fall
    back to the Delhi baseline data.
    """

    with rasterio.open(ref_path) as ref:
        profile = ref.profile.copy()
        shape_ = (ref.height, ref.width)

    profile.update(count=1, dtype=dtype, compress="lzw", nodata=None)

    if dtype == "uint8":
        arr = np.full(shape_, int(value), dtype=np.uint8)
    else:
        arr = np.full(shape_, value, dtype=np.float32)

    with rasterio.open(save_path, "w", **profile) as dst:
        dst.write(arr, 1)

    print(f"[aux] wrote {save_path}  ({label}, value={value})")


def make_rainfall_placeholder(ref_path, save_path):
    write_placeholder(
        ref_path, save_path,
        value=0.5,
        label="rainfall placeholder"
    )


# =====================================================
# ORCHESTRATOR
# =====================================================


def build_all_aux(geom, sentinel_path="uploads/latest.tif",
                  uploads_dir="uploads"):

    """Called after Sentinel is downloaded. Produces every aux
       raster the impact engine expects. Any single failure is
       logged but doesn't kill the whole pipeline."""

    uploads_dir = Path(uploads_dir)
    uploads_dir.mkdir(parents=True, exist_ok=True)

    results = {}

    # ---- NDVI (always works — pure math on Sentinel bands) ----
    try:
        derive_ndvi(sentinel_path, uploads_dir / "ndvi.tif")
        results["ndvi"] = "ok"
    except Exception as e:
        print(f"[aux] NDVI derivation FAILED: {e} — writing zeros")
        write_placeholder(
            sentinel_path, uploads_dir / "ndvi.tif",
            value=0.0, label="ndvi placeholder"
        )
        results["ndvi"] = f"placeholder ({e})"

    # ---- WorldCover ----
    try:
        fetch_worldcover(geom, sentinel_path, uploads_dir / "worldcover.tif")
        results["worldcover"] = "ok"
    except Exception as e:
        print(f"[aux] WorldCover FAILED: {e} — writing class-0 placeholder")
        write_placeholder(
            sentinel_path, uploads_dir / "worldcover.tif",
            value=0, dtype="uint8", label="worldcover placeholder (all class 0)"
        )
        results["worldcover"] = f"placeholder ({e})"

    # ---- LST ----
    try:
        fetch_lst(geom, sentinel_path, uploads_dir / "lst.tif")
        results["lst"] = "ok"
    except Exception as e:
        print(f"[aux] LST FAILED: {e} — writing 0.5 placeholder")
        write_placeholder(
            sentinel_path, uploads_dir / "lst.tif",
            value=0.5, label="lst placeholder (neutral heat)"
        )
        results["lst"] = f"placeholder ({e})"

    # ---- Rainfall placeholder (always) ----
    try:
        make_rainfall_placeholder(
            sentinel_path, uploads_dir / "rainfall.tif"
        )
        results["rainfall"] = "ok (placeholder)"
    except Exception as e:
        print(f"[aux] rainfall placeholder FAILED: {e}")
        results["rainfall"] = f"error: {e}"

    return results
