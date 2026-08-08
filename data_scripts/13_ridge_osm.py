"""C4 - Delhi Ridge / protected forest layer from OSM.

Tags (doc C4): boundary=protected_area, landuse=forest, leisure=nature_reserve
              (+ natural=wood as a supplement)
Within the MCD boundary. Used to (a) mask protected forest so the optimizer never
recommends planting in a reserve, and (b) report ridge-adjusted canopy.

Outputs:
  - data/vector/ridge/mcd_protected_forest.geojson   (dissolved polygon layer)
  - data/processed/ward_ridge_frac.csv               (ridge_frac per ward)
"""
from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import osmnx as ox
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
WARDS = ROOT / "data" / "aoi" / "mcd_wards_2022.geojson"
OUT_VEC = ROOT / "data" / "vector" / "ridge" / "mcd_protected_forest.geojson"
OUT_CSV = ROOT / "data" / "processed" / "ward_ridge_frac.csv"
CRS = "EPSG:32643"

TAGS = {
    "boundary": ["protected_area", "national_park"],
    "landuse": ["forest"],
    "leisure": ["nature_reserve"],
    "natural": ["wood"],
}


def main() -> int:
    wards = gpd.read_file(WARDS)
    # query OSM with a valid convex hull (osmnx rejects the holey MCD polygon),
    # then clip results back to the true ward union below.
    hull = wards.to_crs(CRS).dissolve().convex_hull.to_crs("EPSG:4326")
    boundary = hull.geometry.iloc[0]

    print("querying OSM for protected/forest features within MCD ...")
    feats = ox.features_from_polygon(boundary, TAGS)
    feats = feats[feats.geometry.type.isin(["Polygon", "MultiPolygon"])].copy()
    print(f"  raw protected/forest features: {len(feats)}")

    prot = feats.to_crs(CRS)
    prot["geometry"] = prot.geometry.buffer(0)  # fix invalid
    prot = prot.clip(wards.to_crs(CRS).dissolve())
    dissolved = prot.dissolve()
    total_km2 = dissolved.geometry.area.iloc[0] / 1e6
    print(f"  protected/forest area within MCD: {total_km2:.1f} km^2")

    # save the dissolved layer (store in 4326)
    OUT_VEC.parent.mkdir(parents=True, exist_ok=True)
    dissolved.to_crs("EPSG:4326")[["geometry"]].to_file(OUT_VEC, driver="GeoJSON")
    print(f"  wrote {OUT_VEC.relative_to(ROOT)}")

    # per-ward ridge fraction
    wm = wards.to_crs(CRS)[["ward_no", "ward_name", "geometry"]].copy()
    wm["ward_area"] = wm.geometry.area
    inter = gpd.overlay(wm, dissolved[["geometry"]], how="intersection")
    inter["ia"] = inter.geometry.area
    rf = inter.groupby("ward_no")["ia"].sum()
    wm["ridge_area"] = wm["ward_no"].map(rf).fillna(0.0)
    wm["ridge_frac"] = (wm["ridge_area"] / wm["ward_area"]).round(4)
    out = wm[["ward_no", "ward_name", "ridge_frac"]].sort_values("ward_no")
    out.to_csv(OUT_CSV, index=False)
    print(f"  wrote {OUT_CSV.relative_to(ROOT)}")
    print(f"\n  wards with any Ridge/forest: {(out.ridge_frac > 0).sum()}/250")
    print("  Top 8 Ridge wards:")
    print(out.nlargest(8, "ridge_frac").to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
