"""A3 - Sentinel-2 NDVI composite for the MCD AOI (Apr 1 - Jun 15).

Implements the doc's Delhi-specific spec:
  - collection COPERNICUS/S2_SR_HARMONIZED, CLOUDY_PIXEL_PERCENTAGE < 40
  - 4-source mask stack (s6.1 / A4):
        s2cloudless probability >= 30   (joined on system:index)
        SCL cloud / shadow / cirrus classes
        AOT (aerosol optical thickness) > 0.5   <- Delhi's binding problem
  - median composite, NDVI = (B8 - B4)/(B8 + B4), 10 m, EPSG:32643
Outputs:
  - NDVI GeoTIFF -> Google Drive (folder CanopyEquity)
  - per-ward mean_ndvi -> data/processed/ward_mean_ndvi.csv  (schema s7)

Usage:
  python 04_ndvi_s2.py --project <GEE_PROJECT_ID> [--year 2026] [--export-raster]
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
OUT_CSV = ROOT / "data" / "processed" / "ward_mean_ndvi.csv"

ANALYSIS_CRS = "EPSG:32643"
CLOUD_PROB_THRESH = 30      # s2cloudless: mask >= this
AOT_THRESH = 0.5            # aerosol optical thickness: drop above (raw = *1000)
SCL_MASK_CLASSES = [3, 8, 9, 10, 11]  # shadow, cloud med/high, cirrus, snow


def _window_filter(years: list[int]) -> "ee.Filter":
    """Union of each year's 1 Apr - 15 Jun window (excludes the monsoon between)."""
    return ee.Filter.Or(*[ee.Filter.date(f"{y}-04-01", f"{y}-06-16") for y in years])


def build_masked_s2(aoi: "ee.Geometry", years: list[int]) -> "ee.ImageCollection":
    win = _window_filter(years)
    s2 = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
          .filterBounds(aoi).filter(win)
          .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 40)))
    clouds = (ee.ImageCollection("COPERNICUS/S2_CLOUD_PROBABILITY")
              .filterBounds(aoi).filter(win))
    joined = ee.Join.saveFirst("cloud_prob").apply(
        primary=s2, secondary=clouds,
        condition=ee.Filter.equals(leftField="system:index", rightField="system:index"))

    def mask_img(img: "ee.Image") -> "ee.Image":
        img = ee.Image(img)
        prob = ee.Image(img.get("cloud_prob")).select("probability")
        scl = img.select("SCL")
        aot = img.select("AOT").multiply(0.001)  # raw DN -> AOT units
        keep = (prob.lt(CLOUD_PROB_THRESH)
                .And(aot.lt(AOT_THRESH)))
        for c in SCL_MASK_CLASSES:
            keep = keep.And(scl.neq(c))
        return img.updateMask(keep)

    return ee.ImageCollection(joined).map(mask_img)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True, help="GEE Cloud project ID")
    ap.add_argument("--years", type=int, nargs="+", default=[2022, 2023])
    ap.add_argument("--export-raster", action="store_true",
                    help="also start a Drive export of the NDVI GeoTIFF")
    args = ap.parse_args()

    ee.Initialize(project=args.project)
    print(f"EE initialized on project '{args.project}'")
    tag = "_".join(str(y) for y in args.years)

    gdf = gpd.read_file(WARDS)
    # Simplify ward geometry (15 m in metric CRS) before sending to EE: the raw
    # KML has thousands of vertices/ward and inline upload hits the 10 MB request
    # cap. 15 m is negligible vs 10 m zonal means.
    simpl_geom = gdf.to_crs(ANALYSIS_CRS).geometry.simplify(15).to_crs("EPSG:4326")
    gsimpl = gpd.GeoDataFrame(
        {"ward_no": gdf["ward_no"].values}, geometry=simpl_geom.values, crs="EPSG:4326")
    wards_fc = geemap.geopandas_to_ee(gsimpl)

    minx, miny, maxx, maxy = gdf.total_bounds
    aoi_rect = ee.Geometry.Rectangle([minx, miny, maxx, maxy])  # tiny payload for filtering
    mcd_boundary = wards_fc.geometry().dissolve(maxError=10)     # server-side, for clip

    coll = build_masked_s2(aoi_rect, args.years)
    n = coll.size().getInfo()
    print(f"window Apr1-Jun15 of {args.years}  |  scenes after filter: {n}")

    def add_ndvi(img):
        return img.addBands(img.normalizedDifference(["B8", "B4"]).rename("NDVI"))
    ndvi = coll.map(add_ndvi).select("NDVI").median().clip(mcd_boundary).rename("NDVI")

    # ---- per-ward mean NDVI (schema s7: mean_ndvi) ----
    stats = ndvi.reduceRegions(
        collection=wards_fc, reducer=ee.Reducer.mean(), scale=10, crs=ANALYSIS_CRS)
    stats = stats.map(lambda f: f.setGeometry(None))  # drop geometry from response
    feats = stats.getInfo()["features"]
    rows = [{"ward_no": f["properties"]["ward_no"],
             "mean_ndvi": f["properties"].get("mean")} for f in feats]
    df = pd.DataFrame(rows).sort_values("ward_no")
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False)
    ok = df["mean_ndvi"].notna().sum()
    print(f"per-ward mean_ndvi: {ok}/{len(df)} wards populated  "
          f"(range {df['mean_ndvi'].min():.3f}..{df['mean_ndvi'].max():.3f})")
    print(f"wrote {OUT_CSV.relative_to(ROOT)}")

    # ---- optional pixel-level raster export to Drive ----
    if args.export_raster:
        task = ee.batch.Export.image.toDrive(
            image=ndvi.toFloat(), description=f"mcd_ndvi_{tag}",
            folder="CanopyEquity", fileNamePrefix=f"mcd_ndvi_{tag}",
            region=aoi_rect, scale=10, crs=ANALYSIS_CRS, maxPixels=1e10,
            fileDimensions=[16384, 16384])  # tile if it exceeds one file
        task.start()
        print(f"started Drive export task id={task.id} -> CanopyEquity/mcd_ndvi_{tag}.tif")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
