"""Consolidate all per-ward layers into one master table (foundation for engine).

Joins every data/processed/ward_*.csv + the A7 census onto the A1 geometry,
keyed on ward_no. Writes:
  data/processed/mcd_wards_master.geojson   (geometry + all fields)
  data/processed/mcd_wards_master.csv       (attributes only, for quick view)
"""
from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
A1 = ROOT / "data" / "aoi" / "mcd_wards_2022.geojson"
P = ROOT / "data" / "processed"
CEN = ROOT / "data" / "tabular" / "census" / "a7_ward_census_2011.csv"
OUT_GJ = P / "mcd_wards_master.geojson"
OUT_CSV = P / "mcd_wards_master.csv"

# (file, columns to take) - ward_name dropped from joins to avoid dupes
LAYERS = [
    ("ward_mean_ndvi.csv", ["ward_no", "mean_ndvi"]),
    ("ward_mean_lst.csv", ["ward_no", "mean_lst_c"]),
    ("ward_worldcover_frac.csv", ["ward_no", "wc_canopy_frac", "wc_built_frac",
                                  "cropland_frac", "wc_bareother_frac"]),
    ("ward_dusib_jj.csv", ["ward_no", "jj_n_clusters_apportioned", "jj_households",
                           "jj_area_sqm", "jj_area_frac"]),
    ("ward_mean_rainfall.csv", ["ward_no", "mean_annual_rainfall_mm"]),
    ("ward_mean_groundwater.csv", ["ward_no", "mean_gw_depth_m"]),
    ("ward_ridge_frac.csv", ["ward_no", "ridge_frac"]),
    ("ward_water_tier.csv", ["ward_no", "dist_to_water_m", "dist_to_body_m",
                             "water_tier", "water_cost_mult"]),
    ("ward_pm25.csv", ["ward_no", "mean_pm25", "pm25_interp_var"]),  # optional
]


def main() -> int:
    g = gpd.read_file(A1)
    base_cols = ["ward_no", "ward_name", "ac_name", "area_ha", "geometry"]
    g = g[[c for c in base_cols if c in g.columns]]
    n0 = len(g)

    # census (pop + sc + placeholders)
    cen = pd.read_csv(CEN).drop(columns=["ward_name"], errors="ignore")
    g = g.merge(cen, on="ward_no", how="left")

    joined, skipped = [], []
    for fname, cols in LAYERS:
        fp = P / fname
        if not fp.exists():
            skipped.append(fname)
            continue
        df = pd.read_csv(fp)[cols]
        g = g.merge(df, on="ward_no", how="left")
        joined.append(fname)

    assert len(g) == n0 == 250, f"row count changed: {len(g)}"

    # order: geometry last for geojson friendliness handled by gpd
    gdf = gpd.GeoDataFrame(g, geometry="geometry", crs="EPSG:4326")
    gdf.to_file(OUT_GJ, driver="GeoJSON")
    gdf.drop(columns="geometry").to_csv(OUT_CSV, index=False)

    print(f"master table: {len(gdf)} wards x {len(gdf.columns) - 1} attributes")
    print(f"  joined layers: {len(joined)}")
    if skipped:
        print(f"  skipped (not present): {skipped}")
    print(f"  columns: {[c for c in gdf.columns if c != 'geometry']}")
    print(f"\n  wrote {OUT_GJ.relative_to(ROOT)}")
    print(f"  wrote {OUT_CSV.relative_to(ROOT)}")

    # completeness report
    print("\n  field completeness (non-null / 250):")
    for c in gdf.columns:
        if c in ("geometry",):
            continue
        nn = gdf[c].notna().sum()
        flag = "" if nn == 250 else "  <-- gaps"
        print(f"    {c:28s} {nn:3d}{flag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
