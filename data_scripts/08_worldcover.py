"""A6 - ESA WorldCover v200 (2021) remapped to the 4 project classes.

Remap (doc A6): 10 Tree->canopy(1) · 50 Built->built(2) · 40 Cropland->cropland(3)
                · everything else -> bare/other(0)
Outputs:
  - per-ward class fractions -> data/processed/ward_worldcover_frac.csv
      wc_canopy_frac, wc_built_frac, cropland_frac (schema s7), wc_bareother_frac
  - 4-class raster -> Drive CanopyEquity/mcd_worldcover_4cls.tif  (--export-raster)

NB: wc_canopy_frac is a WEAK baseline label from WorldCover, NOT the final
canopy_fraction (that comes from the U-Net). cropland_frac flags fringe wards.

Usage: python 08_worldcover.py --project <ID> [--export-raster]
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
OUT_CSV = ROOT / "data" / "processed" / "ward_worldcover_frac.csv"
ANALYSIS_CRS = "EPSG:32643"

WC_FROM = [10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100]
WC_TO = [1, 0, 0, 3, 2, 0, 0, 0, 0, 0, 0]   # canopy=1 built=2 cropland=3 other=0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--export-raster", action="store_true")
    args = ap.parse_args()

    ee.Initialize(project=args.project)
    print(f"EE initialized on project '{args.project}'")

    gdf = gpd.read_file(WARDS)
    simpl = gdf.to_crs(ANALYSIS_CRS).geometry.simplify(15).to_crs("EPSG:4326")
    gsimpl = gpd.GeoDataFrame(
        {"ward_no": gdf["ward_no"].values, "ward_name": gdf["ward_name"].values},
        geometry=simpl.values, crs="EPSG:4326")
    wards_fc = geemap.geopandas_to_ee(gsimpl)
    boundary = wards_fc.geometry().dissolve(maxError=10)
    minx, miny, maxx, maxy = gdf.total_bounds
    rect = ee.Geometry.Rectangle([minx, miny, maxx, maxy])

    wc = ee.ImageCollection("ESA/WorldCover/v200").mosaic().select("Map")
    cls = wc.remap(WC_FROM, WC_TO).rename("cls").clip(boundary)

    frac = ee.Image.cat([
        cls.eq(1).rename("wc_canopy_frac"),
        cls.eq(2).rename("wc_built_frac"),
        cls.eq(3).rename("cropland_frac"),
        cls.eq(0).rename("wc_bareother_frac"),
    ])
    stats = frac.reduceRegions(collection=wards_fc, reducer=ee.Reducer.mean(),
                               scale=10, crs=ANALYSIS_CRS)
    stats = stats.map(lambda f: f.setGeometry(None))
    feats = stats.getInfo()["features"]
    rows = [{"ward_no": p["ward_no"], "ward_name": p["ward_name"],
             "wc_canopy_frac": p.get("wc_canopy_frac"),
             "wc_built_frac": p.get("wc_built_frac"),
             "cropland_frac": p.get("cropland_frac"),
             "wc_bareother_frac": p.get("wc_bareother_frac")}
            for p in (f["properties"] for f in feats)]
    df = pd.DataFrame(rows).sort_values("ward_no")
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False)

    print(f"per-ward fractions: {df['wc_canopy_frac'].notna().sum()}/{len(df)} populated")
    print(f"wrote {OUT_CSV.relative_to(ROOT)}")
    print("\nMCD-wide class share (mean of ward fractions):")
    for c in ["wc_canopy_frac", "wc_built_frac", "cropland_frac", "wc_bareother_frac"]:
        print(f"  {c:20s} {df[c].mean()*100:5.1f}%")
    print("\nTop 6 cropland wards (should be the agricultural fringe):")
    print(df.sort_values("cropland_frac", ascending=False)
          .head(6)[["ward_no", "ward_name", "cropland_frac"]].to_string(index=False))

    if args.export_raster:
        task = ee.batch.Export.image.toDrive(
            image=cls.toByte(), description="mcd_worldcover_4cls",
            folder="CanopyEquity", fileNamePrefix="mcd_worldcover_4cls",
            region=rect, scale=10, crs=ANALYSIS_CRS, maxPixels=1e10,
            fileDimensions=[16384, 16384])
        task.start()
        print(f"\nstarted Drive export task id={task.id} -> CanopyEquity/mcd_worldcover_4cls.tif")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
