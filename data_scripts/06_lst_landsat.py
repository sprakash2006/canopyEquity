"""A5 - Landsat 8/9 Land Surface Temperature (LST) for the MCD AOI.

Spec (doc A5 / s6.1):
  - LANDSAT/LC08/C02/T1_L2 + LANDSAT/LC09/C02/T1_L2  (merged)
  - band ST_B10 (surface temperature product), Apr 1 - Jun 15 of 2022+2023
  - QA_PIXEL bitmask: drop fill/dilated-cloud/cirrus/cloud/shadow/snow
  - scale to degC: DN*0.00341802 + 149.0 (K) - 273.15
  - median composite, 30 m, EPSG:32643 (native ~100 m, delivered 30 m)
Outputs:
  - per-ward mean_lst_c -> data/processed/ward_mean_lst.csv (with ward_name)
  - LST GeoTIFF -> Drive CanopyEquity/mcd_lst_<years>.tif  (with --export-raster)

Note: LST (surface) != air temperature; validate against IMD/CPCB only as a
pattern/magnitude sanity check (doc B4), never as equivalence.

Usage: python 06_lst_landsat.py --project <ID> [--years 2022 2023] [--export-raster]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import ee
import geemap
import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
WARDS = ROOT / "data" / "aoi" / "mcd_wards_2022.geojson"
OUT_CSV = ROOT / "data" / "processed" / "ward_mean_lst.csv"

ANALYSIS_CRS = "EPSG:32643"
# QA_PIXEL bits to reject (Collection 2 Level 2)
_BAD_BITS = [0, 1, 2, 3, 4, 5]  # fill, dilated cloud, cirrus, cloud, shadow, snow


def _window_filter(years):
    return ee.Filter.Or(*[ee.Filter.date(f"{y}-04-01", f"{y}-06-16") for y in years])


def _to_lst_c(img):
    qa = img.select("QA_PIXEL")
    keep = ee.Image.constant(1)
    for b in _BAD_BITS:
        keep = keep.And(qa.bitwiseAnd(1 << b).eq(0))
    lst_c = (img.select("ST_B10").multiply(0.00341802).add(149.0)
             .subtract(273.15).rename("LST_C"))
    return lst_c.updateMask(keep)


def build_lst(aoi, years):
    win = _window_filter(years)
    def prep(cid):
        return (ee.ImageCollection(cid).filterBounds(aoi).filter(win)
                .filter(ee.Filter.lt("CLOUD_COVER", 50)).map(_to_lst_c))
    return prep("LANDSAT/LC08/C02/T1_L2").merge(prep("LANDSAT/LC09/C02/T1_L2"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--years", type=int, nargs="+", default=[2022, 2023])
    ap.add_argument("--export-raster", action="store_true")
    args = ap.parse_args()

    ee.Initialize(project=args.project)
    print(f"EE initialized on project '{args.project}'")
    tag = "_".join(str(y) for y in args.years)

    gdf = gpd.read_file(WARDS)
    simpl = gdf.to_crs(ANALYSIS_CRS).geometry.simplify(15).to_crs("EPSG:4326")
    gsimpl = gpd.GeoDataFrame(
        {"ward_no": gdf["ward_no"].values, "ward_name": gdf["ward_name"].values},
        geometry=simpl.values, crs="EPSG:4326")
    wards_fc = geemap.geopandas_to_ee(gsimpl)
    minx, miny, maxx, maxy = gdf.total_bounds
    rect = ee.Geometry.Rectangle([minx, miny, maxx, maxy])
    boundary = wards_fc.geometry().dissolve(maxError=10)

    coll = build_lst(rect, args.years)
    print(f"window Apr1-Jun15 of {args.years} | Landsat scenes after filter: {coll.size().getInfo()}")
    lst = coll.median().clip(boundary).rename("LST_C")

    stats = lst.reduceRegions(collection=wards_fc, reducer=ee.Reducer.mean(),
                              scale=30, crs=ANALYSIS_CRS)
    stats = stats.map(lambda f: f.setGeometry(None))
    feats = stats.getInfo()["features"]
    rows = [{"ward_no": f["properties"]["ward_no"],
             "ward_name": f["properties"]["ward_name"],
             "mean_lst_c": f["properties"].get("mean")} for f in feats]
    df = pd.DataFrame(rows).sort_values("ward_no")
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False)
    ok = df["mean_lst_c"].notna().sum()
    print(f"per-ward mean_lst_c: {ok}/{len(df)} populated "
          f"(range {df['mean_lst_c'].min():.1f}..{df['mean_lst_c'].max():.1f} degC)")
    print(f"wrote {OUT_CSV.relative_to(ROOT)}")

    if args.export_raster:
        task = ee.batch.Export.image.toDrive(
            image=lst.toFloat(), description=f"mcd_lst_{tag}",
            folder="CanopyEquity", fileNamePrefix=f"mcd_lst_{tag}",
            region=rect, scale=30, crs=ANALYSIS_CRS, maxPixels=1e10)
        task.start()
        print(f"started Drive export task id={task.id} -> CanopyEquity/mcd_lst_{tag}.tif")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
