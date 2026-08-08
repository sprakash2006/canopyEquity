"""Module 3 - rasterize ward census data to a pixel-level GeoTIFF.

Input
    - Ward boundary map as KML          (data/aoi/delhi_wards_map_raw.kml)
    - Ward census attribute table (CSV) (data/processed/mcd_wards_master.csv)
    - A reference grid raster            (data/raster/preview/mcd_ndvi_2022_2023_60m.tif)
      -> defines CRS + transform + shape, so the census raster is pixel-aligned
         with the NDVI / LST / WorldCover stack from modules 1-2.

Output
    - Multi-band GeoTIFF                 (data/raster/mcd_census_pixel_60m.tif)
      one band per census variable, every pixel carries the value of the ward
      it falls inside.  Pixels outside any ward = nodata.
    - Band manifest JSON                 (data/raster/mcd_census_pixel_60m_bands.json)

"Generalised to the pixel level"
    A census COUNT (population, households, ...) is an *extensive* quantity: the
    ward total is not a per-pixel value, and painting 57,335 people into every
    60 m cell of a ward would be meaningless (a big ward and a small ward would
    look identical).  So count fields are converted to a **density per km2** -
    a true intensive, per-pixel quantity that is comparable across wards and is
    exactly the "population density" the Urban Vulnerability Index needs.
    Fields that are already intensive (fractions / rates) are painted directly.

Environment
    Pure rasterio + numpy + shapely + stdlib.  No geopandas / pandas / pyproj
    required.  KML is parsed with xml.etree; lon/lat -> UTM reprojection is done
    with rasterio.warp (rasterio bundles its own PROJ).

Note on data gaps
    total_households, literate_population, households_piped_water_premises and
    slum_households are still EMPTY in the census table (House-Listing / PCA
    acquisition backlog - see scripts/09_build_a7_census.py).  Literacy and piped
    water access can therefore NOT be rastered yet; the slum signal is carried
    instead by the populated DUSIB jhuggi-jhopri (JJ cluster) columns.  Missing
    fields are reported, never silently faked.
"""
from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import rasterio
from rasterio.features import rasterize
from rasterio.warp import transform as warp_transform
from shapely.geometry import MultiPolygon, Polygon

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_KML = ROOT / "data" / "aoi" / "delhi_wards_map_raw.kml"
DEFAULT_CENSUS = ROOT / "data" / "processed" / "mcd_wards_master.csv"
DEFAULT_REF = ROOT / "data" / "raster" / "preview" / "mcd_ndvi_2022_2023_60m.tif"
DEFAULT_OUT = ROOT / "data" / "raster" / "mcd_census_pixel_60m.tif"

KML_NS = {"k": "http://www.opengis.net/kml/2.2"}
STORAGE_CRS = "EPSG:4326"           # KML lon/lat
NODATA = -9999.0

# --- census columns needed from the CSV (populated for all 250 wards) --------
WARD_KEY = "ward_number"
SRC_COLS = [
    "ward_name",
    "total_population",
    "scheduled_caste_population",
    "jhuggi_jhopri_households",
    "jhuggi_jhopri_area_fraction",
    "area_hectares",
]

# --- output band schema ------------------------------------------------------
# kind: "density" -> value / area_km2   |  "direct" -> paint as-is  |  "raw" -> ward total
# each entry: (band_name, source_column, kind, units, description)
BANDS = [
    ("population_density_per_km2",      "total_population",            "density", "people/km2",
     "Total population divided by ward area (primary density signal for the UVI)."),
    ("total_population",                "total_population",            "raw",     "people",
     "Raw ward total population (same value across the whole ward, for traceability)."),
    ("sc_population_density_per_km2",   "scheduled_caste_population",  "density", "people/km2",
     "Scheduled-Caste population density."),
    ("sc_population_fraction",          None,                          "special", "fraction 0-1",
     "Scheduled-Caste share of total population (marginalisation proxy)."),
    ("slum_jj_household_density_per_km2","jhuggi_jhopri_households",   "density", "households/km2",
     "DUSIB jhuggi-jhopri (slum cluster) household density - proxy for slum households."),
    ("slum_jj_households",              "jhuggi_jhopri_households",    "raw",     "households",
     "Raw JJ (slum) households apportioned to the ward."),
    ("slum_jj_area_fraction",          "jhuggi_jhopri_area_fraction", "direct",  "fraction 0-1",
     "Share of ward area occupied by JJ (slum) clusters."),
    ("ward_area_km2",                  None,                          "special", "km2",
     "Ward area from the reprojected boundary geometry."),
]

# Fields the objective wants but that are NOT in the source table yet.
MISSING_FIELDS = {
    "literate_population": "literacy rate  (House-Listing / PCA backlog)",
    "households_piped_water_premises": "piped water access  (House-Listing / PCA backlog)",
    "total_households": "household density  (House-Listing / PCA backlog)",
    "slum_households": "census slum households  (using DUSIB JJ proxy instead)",
}


# ---------------------------------------------------------------------------
# KML parsing + reprojection
# ---------------------------------------------------------------------------
def _parse_coords(text: str) -> list[tuple[float, float]]:
    """'lon,lat[,alt] lon,lat ...' -> [(lon, lat), ...]."""
    pts = []
    for tok in text.split():
        parts = tok.split(",")
        if len(parts) >= 2:
            pts.append((float(parts[0]), float(parts[1])))
    return pts


def _reproject_ring(ring, dst_crs):
    """Reproject a list of (lon, lat) to dst_crs -> list of (x, y)."""
    lons = [p[0] for p in ring]
    lats = [p[1] for p in ring]
    xs, ys = warp_transform(STORAGE_CRS, dst_crs, lons, lats)
    return list(zip(xs, ys))


def load_ward_geoms(kml_path: Path, dst_crs) -> dict[int, MultiPolygon]:
    """Parse the ward KML -> {ward_no: shapely geometry in dst_crs}.

    Handles MultiGeometry (several polygons per ward) and innerBoundaryIs (holes).
    """
    root = ET.parse(kml_path).getroot()
    wards: dict[int, list[Polygon]] = {}

    for pm in root.findall(".//k:Placemark", KML_NS):
        attrs = {sd.get("name"): (sd.text or "")
                 for sd in pm.findall(".//k:SimpleData", KML_NS)}
        raw = attrs.get("Ward_No", "").strip()
        if not raw:
            continue
        ward_no = int(float(raw))

        polys: list[Polygon] = []
        for poly_el in pm.findall(".//k:Polygon", KML_NS):
            outer_el = poly_el.find(
                ".//k:outerBoundaryIs/k:LinearRing/k:coordinates", KML_NS)
            if outer_el is None or not outer_el.text:
                continue
            shell = _reproject_ring(_parse_coords(outer_el.text), dst_crs)
            holes = []
            for inner_el in poly_el.findall(
                    ".//k:innerBoundaryIs/k:LinearRing/k:coordinates", KML_NS):
                if inner_el.text:
                    holes.append(_reproject_ring(_parse_coords(inner_el.text), dst_crs))
            poly = Polygon(shell, holes)
            if not poly.is_valid:
                poly = poly.buffer(0)          # fix self-touching rings
            if poly.is_empty:
                continue
            if isinstance(poly, MultiPolygon):  # buffer(0) may split into parts
                polys.extend(g for g in poly.geoms if not g.is_empty)
            else:
                polys.append(poly)

        if polys:
            wards.setdefault(ward_no, []).extend(polys)

    return {wn: (parts[0] if len(parts) == 1 else MultiPolygon(parts))
            for wn, parts in wards.items()}


# ---------------------------------------------------------------------------
# Census table (stdlib csv)
# ---------------------------------------------------------------------------
def load_census(csv_path: Path) -> dict[int, dict]:
    import csv
    out: dict[int, dict] = {}
    with open(csv_path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            try:
                wn = int(float(row[WARD_KEY]))
            except (ValueError, KeyError):
                continue
            rec = {}
            for col in SRC_COLS:
                v = row.get(col, "")
                if col == "ward_name":
                    rec[col] = v
                else:
                    try:
                        rec[col] = float(v)
                    except ValueError:
                        rec[col] = np.nan
            out[wn] = rec
    return out


# ---------------------------------------------------------------------------
# Band value computation
# ---------------------------------------------------------------------------
def band_value(band, rec: dict, area_km2: float) -> float:
    name, col, kind, *_ = band
    if kind == "special":
        if name == "ward_area_km2":
            return area_km2
        if name == "sc_population_fraction":
            pop = rec.get("total_population", np.nan)
            sc = rec.get("scheduled_caste_population", np.nan)
            return sc / pop if pop and pop > 0 else np.nan
        return np.nan
    val = rec.get(col, np.nan)
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return np.nan
    if kind == "density":
        return val / area_km2 if area_km2 > 0 else np.nan
    return float(val)                                   # raw / direct


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--kml", type=Path, default=DEFAULT_KML)
    ap.add_argument("--census", type=Path, default=DEFAULT_CENSUS)
    ap.add_argument("--reference", type=Path, default=DEFAULT_REF,
                    help="Raster whose grid (CRS/transform/shape) the output aligns to.")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--all-touched", action="store_true",
                    help="Paint every pixel the polygon touches (default: cell-centre).")
    args = ap.parse_args()

    # 1. reference grid ------------------------------------------------------
    with rasterio.open(args.reference) as ref:
        dst_crs = ref.crs
        transform = ref.transform
        height, width = ref.height, ref.width
    print(f"[grid] {args.reference.name}  crs={dst_crs}  size={width}x{height}  "
          f"res={transform.a:g} m")

    # 2. geometry + attributes ----------------------------------------------
    geoms = load_ward_geoms(args.kml, dst_crs)
    census = load_census(args.census)
    print(f"[kml ] {len(geoms)} ward polygons parsed  (crs={dst_crs})")
    print(f"[csv ] {len(census)} ward census records")

    matched = sorted(set(geoms) & set(census))
    only_kml = sorted(set(geoms) - set(census))
    only_csv = sorted(set(census) - set(geoms))
    print(f"[join] matched={len(matched)}  kml-only={only_kml}  csv-only={only_csv}")

    # 3. per-ward area + band values ----------------------------------------
    n_bands = len(BANDS)
    stacks = np.full((n_bands, height, width), NODATA, dtype="float32")
    per_band_shapes: list[list] = [[] for _ in range(n_bands)]

    for wn in matched:
        geom = geoms[wn]
        rec = census[wn]
        area_km2 = geom.area / 1e6                       # geom is metric (UTM)
        for bi, band in enumerate(BANDS):
            v = band_value(band, rec, area_km2)
            if v is None or (isinstance(v, float) and np.isnan(v)):
                continue
            per_band_shapes[bi].append((geom, float(v)))

    # 4. rasterize each band -------------------------------------------------
    for bi, shapes in enumerate(per_band_shapes):
        if not shapes:
            print(f"[warn] band '{BANDS[bi][0]}' has no data -> all nodata")
            continue
        stacks[bi] = rasterize(
            shapes, out_shape=(height, width), transform=transform,
            fill=NODATA, all_touched=args.all_touched, dtype="float32",
        )

    # 5. write GeoTIFF -------------------------------------------------------
    args.out.parent.mkdir(parents=True, exist_ok=True)
    profile = {
        "driver": "GTiff", "height": height, "width": width, "count": n_bands,
        "dtype": "float32", "crs": dst_crs, "transform": transform,
        "nodata": NODATA, "compress": "deflate", "predictor": 2, "tiled": True,
    }
    with rasterio.open(args.out, "w", **profile) as dst:
        for bi, band in enumerate(BANDS):
            dst.write(stacks[bi], bi + 1)
            dst.set_band_description(bi + 1, band[0])
            dst.update_tags(bi + 1, units=band[3], kind=band[2],
                            source_column=str(band[1]), description=band[4])
        dst.update_tags(
            module="3-census-pixel-raster",
            aligned_to=args.reference.name,
            method="counts->density per km2 ; fractions painted directly",
            missing_fields="; ".join(f"{k}={v}" for k, v in MISSING_FIELDS.items()),
        )

    # 6. manifest ------------------------------------------------------------
    manifest = {
        "output": str(args.out),
        "crs": str(dst_crs),
        "grid": {"width": width, "height": height,
                 "pixel_size_m": abs(transform.a),
                 "aligned_to": str(args.reference)},
        "nodata": NODATA,
        "wards_rendered": len(matched),
        "bands": [
            {"index": i + 1, "name": b[0], "source_column": b[1],
             "kind": b[2], "units": b[3], "description": b[4],
             "min": None if not per_band_shapes[i] else round(
                 float(np.nanmin([v for _, v in per_band_shapes[i]])), 4),
             "max": None if not per_band_shapes[i] else round(
                 float(np.nanmax([v for _, v in per_band_shapes[i]])), 4)}
            for i, b in enumerate(BANDS)
        ],
        "missing_fields": MISSING_FIELDS,
    }
    manifest_path = args.out.with_name(args.out.stem + "_bands.json")
    manifest_path.write_text(json.dumps(manifest, indent=2))

    # 7. report --------------------------------------------------------------
    print(f"\n[done] wrote {args.out}")
    print(f"       {n_bands} bands, {len(matched)} wards, nodata={NODATA}")
    print(f"       manifest -> {manifest_path.name}")
    print("\n  band  name                                  units            range")
    for m in manifest["bands"]:
        rng = "-" if m["min"] is None else f"{m['min']:g} .. {m['max']:g}"
        print(f"  {m['index']:>4}  {m['name']:<38}{m['units']:<16} {rng}")
    print("\n  NOT rendered (data not in source table yet):")
    for k, v in MISSING_FIELDS.items():
        print(f"    - {k:<34} {v}")


if __name__ == "__main__":
    main()
