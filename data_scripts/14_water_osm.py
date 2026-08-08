"""B1 - OSM water infrastructure + preliminary water-tier constraint (doc s6.6).

Tags: natural=water, landuse=reservoir, waterway=*, man_made in
      {water_works, water_tower, reservoir_covered}.
Within MCD (queried on convex hull, clipped to ward union).

Water tiers (doc s6.6) - PRELIMINARY (B2 DJB STPs will refine W2):
  W1 Direct     : ward within 200 m of any water feature   -> mult 1.0
  W2 Serviceable: ward centroid within 3 km of a water body -> mult 1.35
  W3 Blocked    : neither                                    -> blocked list

Outputs:
  - data/vector/osm/mcd_water_features.geojson
  - data/processed/ward_water_tier.csv
      dist_to_water_m, dist_to_body_m, water_tier, water_cost_mult
"""
from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import osmnx as ox
import pandas as pd
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
WARDS = ROOT / "data" / "aoi" / "mcd_wards_2022.geojson"
OUT_VEC = ROOT / "data" / "vector" / "osm" / "mcd_water_features.geojson"
OUT_CSV = ROOT / "data" / "processed" / "ward_water_tier.csv"
CRS = "EPSG:32643"

TAGS = {
    "natural": ["water"],
    "landuse": ["reservoir"],
    "waterway": True,
    "man_made": ["water_works", "water_tower", "reservoir_covered"],
}
W1_DIST = 200.0
W2_DIST = 3000.0


def main() -> int:
    wards = gpd.read_file(WARDS)
    ward_union = wards.to_crs(CRS).dissolve()
    hull = ward_union.convex_hull.to_crs("EPSG:4326").geometry.iloc[0]

    print("querying OSM water features within MCD ...")
    feats = ox.features_from_polygon(hull, TAGS).to_crs(CRS)
    feats["geometry"] = feats.geometry.buffer(0).where(
        feats.geometry.type.isin(["Polygon", "MultiPolygon"]), feats.geometry)
    feats = feats.clip(ward_union)
    print(f"  water features within MCD: {len(feats)}")

    OUT_VEC.parent.mkdir(parents=True, exist_ok=True)
    feats.reset_index()[["geometry"]].to_crs("EPSG:4326").to_file(OUT_VEC, driver="GeoJSON")
    print(f"  wrote {OUT_VEC.relative_to(ROOT)}")

    # unified geometries for distance
    water_all = unary_union(feats.geometry.values)
    bodies = feats[feats.geometry.type.isin(["Polygon", "MultiPolygon"])]
    water_bodies = unary_union(bodies.geometry.values) if len(bodies) else water_all

    wm = wards.to_crs(CRS)[["ward_no", "ward_name", "geometry"]].copy()
    wm["dist_to_water_m"] = wm.geometry.distance(water_all).round(1)
    wm["dist_to_body_m"] = wm.geometry.centroid.distance(water_bodies).round(1)

    def tier(r):
        if r["dist_to_water_m"] <= W1_DIST:
            return "W1", 1.0
        if r["dist_to_body_m"] <= W2_DIST:
            return "W2", 1.35
        return "W3", None

    tw = wm.apply(tier, axis=1, result_type="expand")
    wm["water_tier"], wm["water_cost_mult"] = tw[0], tw[1]
    out = wm[["ward_no", "ward_name", "dist_to_water_m", "dist_to_body_m",
              "water_tier", "water_cost_mult"]].sort_values("ward_no")
    out.to_csv(OUT_CSV, index=False)
    print(f"  wrote {OUT_CSV.relative_to(ROOT)}")
    print("\n  water-tier distribution:")
    print(out["water_tier"].value_counts().sort_index().to_string())
    if (out["water_tier"] == "W3").any():
        print("\n  W3 (infrastructure-blocked) wards:")
        print(out[out.water_tier == "W3"][["ward_no", "ward_name", "dist_to_body_m"]]
              .to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
