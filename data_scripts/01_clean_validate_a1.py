"""A1 - clean & validate the MCD 2022 250-ward layer.

Input : data/aoi/delhi_wards_map_raw.kml   (251 features: 250 wards + 1 null sliver)
Output: data/aoi/mcd_wards_2022.geojson     (EPSG:4326, 250 features, tidy schema)

Acceptance test (doc s2 A1 / s8):
  - exactly 250 features
  - ward_no unique, no nulls
  - dissolved area 1,397 km^2 +/- 3% in EPSG:32643
  - geometries valid after make_valid(), no self-intersections
"""
from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
from shapely.validation import make_valid

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "aoi" / "delhi_wards_map_raw.kml"
OUT = ROOT / "data" / "aoi" / "mcd_wards_2022.geojson"

ANALYSIS_CRS = "EPSG:32643"
TARGET_AREA_KM2 = 1397.0
AREA_TOL = 0.03

# raw KML field -> tidy name
RENAME = {
    "Ward_No": "ward_no",
    "WardName": "ward_name",
    "AC_Name": "ac_name",       # assembly constituency (NOT the MCD zone)
    "TotalPop": "pop2011_kml",  # census pop pre-attached to 2022 wards (provenance TBD)
    "SC_Pop": "sc_pop2011_kml",
}


def main() -> int:
    print(f"Reading {SRC.name} ...")
    gdf = gpd.read_file(SRC)
    print(f"  raw features: {len(gdf)}  | CRS: {gdf.crs}")

    # coerce ward_no to int for filtering
    gdf["Ward_No"] = gdf["Ward_No"].astype(int)

    # --- drop the null sliver (Ward_No == 0, blank name, zero pop) ---
    sliver = gdf[gdf["Ward_No"] == 0]
    print(f"  dropping {len(sliver)} sliver feature(s) with Ward_No==0")
    gdf = gdf[gdf["Ward_No"] != 0].copy()

    # --- tidy schema ---
    keep = [c for c in RENAME if c in gdf.columns]
    gdf = gdf[keep + ["geometry"]].rename(columns=RENAME)
    # NOTE: 'zone' (12 MCD zones) intentionally omitted - the analysis is
    # ward-level only; every downstream metric is computed per ward_no.

    # --- validate geometries ---
    n_invalid = int((~gdf.geometry.is_valid).sum())
    if n_invalid:
        print(f"  make_valid() on {n_invalid} invalid geometr(ies)")
        gdf["geometry"] = gdf.geometry.apply(make_valid)

    # ================= ACCEPTANCE TESTS =================
    checks: list[tuple[str, bool, str]] = []

    n = len(gdf)
    checks.append(("feature count == 250", n == 250, f"{n}"))

    uniq = gdf["ward_no"].is_unique and gdf["ward_no"].notna().all()
    checks.append(("ward_no unique & non-null", bool(uniq), f"{gdf['ward_no'].nunique()} unique"))

    rng_ok = set(gdf["ward_no"]) == set(range(1, 251))
    checks.append(("ward_no covers 1..250", rng_ok, "complete" if rng_ok else "GAPS"))

    all_valid = bool(gdf.geometry.is_valid.all())
    checks.append(("all geometries valid", all_valid, ""))

    gm = gdf.to_crs(ANALYSIS_CRS)
    dissolved = gm.dissolve().geometry.iloc[0]
    area_km2 = dissolved.area / 1e6
    lo, hi = TARGET_AREA_KM2 * (1 - AREA_TOL), TARGET_AREA_KM2 * (1 + AREA_TOL)
    area_ok = lo <= area_km2 <= hi
    checks.append((f"dissolved area {lo:.0f}-{hi:.0f} km^2", area_ok, f"{area_km2:.1f} km^2"))

    # self-intersection of dissolved boundary is implied by validity of the union
    checks.append(("dissolved union valid (no self-intersect)", bool(dissolved.is_valid), ""))

    print("\n===== A1 ACCEPTANCE =====")
    ok = True
    for name, passed, detail in checks:
        flag = "PASS" if passed else "FAIL"
        ok = ok and passed
        print(f"  [{flag}] {name:42s} {detail}")

    # per-ward area for downstream use (store in ha, computed in metric CRS)
    gdf["area_ha"] = gm.geometry.area.values / 1e4

    if not ok:
        print("\n>>> A1 FAILED acceptance. Not writing output.")
        return 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_crs("EPSG:4326").to_file(OUT, driver="GeoJSON")
    print(f"\nWrote {OUT.relative_to(ROOT)}  ({len(gdf)} features, EPSG:4326)")
    print(f"  columns: {list(gdf.columns)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
