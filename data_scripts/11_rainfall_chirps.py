"""Extra - annual rainfall per ward from CHIRPS (GEE).

Source : UCSB-CHG/CHIRPS/DAILY (~5.5 km, mm/day)
Metric : annual TOTAL precipitation (mm), averaged over 2022 + 2023
         (full year, not the Apr-Jun dry window - that window has ~no rain)
Outputs:
  - per-ward mean_annual_rainfall_mm -> data/processed/ward_mean_rainfall.csv
  - pixel raster -> Drive CanopyEquity/mcd_rainfall_2022_2023.tif  (--export-raster)

NB: CHIRPS is ~5.5 km, far coarser than a ward, so ward-to-ward variation is
small by construction. Reported for completeness / water-availability context.

Usage: python 11_rainfall_chirps.py --project <ID> [--years 2022 2023] [--export-raster]
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
OUT_CSV = ROOT / "data" / "processed" / "ward_mean_rainfall.csv"
ANALYSIS_CRS = "EPSG:32643"


def annual_total(year: int, aoi):
    return (ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
            .filterBounds(aoi)
            .filterDate(f"{year}-01-01", f"{year + 1}-01-01")
            .select("precipitation").sum())


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

    yearly = [annual_total(y, rect) for y in args.years]
    rain = ee.ImageCollection(yearly).mean().clip(boundary).rename("rain_mm")

    # sample at 1 km so wards smaller than a CHIRPS pixel still get a value
    stats = rain.reduceRegions(collection=wards_fc, reducer=ee.Reducer.mean(),
                               scale=1000, crs=ANALYSIS_CRS)
    stats = stats.map(lambda f: f.setGeometry(None))
    feats = stats.getInfo()["features"]
    rows = [{"ward_no": p["ward_no"], "ward_name": p["ward_name"],
             "mean_annual_rainfall_mm": p.get("mean")}
            for p in (f["properties"] for f in feats)]
    df = pd.DataFrame(rows).sort_values("ward_no")
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False)
    ok = df["mean_annual_rainfall_mm"].notna().sum()
    print(f"per-ward rainfall: {ok}/{len(df)} populated "
          f"(range {df['mean_annual_rainfall_mm'].min():.0f}.."
          f"{df['mean_annual_rainfall_mm'].max():.0f} mm; "
          f"city mean {df['mean_annual_rainfall_mm'].mean():.0f} mm)")
    print(f"wrote {OUT_CSV.relative_to(ROOT)}")

    if args.export_raster:
        task = ee.batch.Export.image.toDrive(
            image=rain.toFloat(), description=f"mcd_rainfall_{tag}",
            folder="CanopyEquity", fileNamePrefix=f"mcd_rainfall_{tag}",
            region=rect, scale=5566, crs=ANALYSIS_CRS, maxPixels=1e10)
        task.start()
        print(f"started Drive export task id={task.id} -> CanopyEquity/mcd_rainfall_{tag}.tif")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
