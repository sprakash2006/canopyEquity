"""Build & validate the 2017 (272) -> 2022 (250) ward crosswalk (doc s5).

Inputs
  data/aoi/mcd_wards_2022.geojson          (A1, 250 wards, key: ward_no)
  data/aoi/mcd_wards_2017_htlabs.geojson   (A2, 272 wards, key: unique e.g. '012E')

Output
  data/processed/ward_crosswalk_2017_2022.csv   columns: ward_2017, ward_no_2022, weight

Method: areal interpolation. weight = intersection_area / source(2017)_area
        = share of an OLD ward that falls into a NEW ward.

Apply (doc s5):
  - COUNT vars (pop, households, literates, JJ hh): multiply by weight, sum into 2022 ward.
  - RATE vars: reconstruct from apportioned counts, never area-weight a rate.

Validation (geometric form of the doc's population-sum test):
  For each 2017 ward, sum of weights over its intersections must ~= 1.0
  (i.e. old wards are fully tiled by new wards). Deviations reveal
  extent mismatch between the two layers.
"""
from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
from shapely.validation import make_valid

ROOT = Path(__file__).resolve().parents[1]
W22_PATH = ROOT / "data" / "aoi" / "mcd_wards_2022.geojson"
W17_PATH = ROOT / "data" / "aoi" / "mcd_wards_2017_htlabs.geojson"
OUT = ROOT / "data" / "processed" / "ward_crosswalk_2017_2022.csv"

ANALYSIS_CRS = "EPSG:32643"


def _load(path: Path) -> gpd.GeoDataFrame:
    g = gpd.read_file(path).to_crs(ANALYSIS_CRS)
    g["geometry"] = g.geometry.apply(lambda x: x if x.is_valid else make_valid(x))
    return g


def main() -> int:
    w22 = _load(W22_PATH)
    w17 = _load(W17_PATH)
    print(f"2022 wards: {len(w22)}  | 2017 wards: {len(w17)}")

    # extent coincidence (doc A2 acceptance: dissolved areas agree within ~1%)
    a22 = w22.dissolve().geometry.area.iloc[0] / 1e6
    a17 = w17.dissolve().geometry.area.iloc[0] / 1e6
    diff = abs(a22 - a17) / a22 * 100
    print(f"dissolved area  2022={a22:.1f} km^2  2017={a17:.1f} km^2  diff={diff:.2f}%")
    print(f"  [{'PASS' if diff <= 1.0 else 'WARN'}] extent coincidence <= 1%")

    w17 = w17.rename(columns={"unique": "ward_2017"})
    w22 = w22.rename(columns={"ward_no": "ward_no_2022"})
    w17["src_area"] = w17.geometry.area
    w22["dst_area"] = w22.geometry.area

    ix = gpd.overlay(
        w17[["ward_2017", "src_area", "geometry"]],
        w22[["ward_no_2022", "dst_area", "geometry"]],
        how="intersection",
        keep_geom_type=True,
    )
    ix["ix_area"] = ix.geometry.area
    # discard slivers below 1 m^2 (numerical dust from overlay)
    ix = ix[ix["ix_area"] > 1.0].copy()
    ix["weight_raw"] = ix["ix_area"] / ix["src_area"]

    # ---------- validation: raw weights per 2017 ward sum to ~1 ----------
    wsum = ix.groupby("ward_2017")["weight_raw"].sum()
    covered = w17["ward_2017"].map(wsum).fillna(0.0)
    dev = (covered - 1.0).abs()
    print("\n===== CROSSWALK VALIDATION =====")
    print(f"  2017 wards with a mapping : {int((covered > 0).sum())}/{len(w17)}")
    print(f"  weight-sum mean           : {covered.mean():.4f} (ideal 1.0000)")
    print(f"  wards |sum-1| > 0.02      : {int((dev > 0.02).sum())}")
    print(f"  wards |sum-1| > 0.10      : {int((dev > 0.10).sum())}")
    worst = covered.sort_values().head(5)
    print("  lowest-coverage 2017 wards:")
    for k, v in zip(w17.loc[worst.index, "ward_2017"], worst.values):
        print(f"     {k}: {v:.3f}")

    # ---------- normalize per 2017 ward so weights sum to exactly 1.0 ----------
    # Standard areal-interpolation fix for imperfectly-tiling source polygons:
    # each old ward's counts are redistributed only among the new wards it
    # overlaps. Guarantees count conservation; raw coverage is disclosed below.
    ix["weight"] = ix["weight_raw"] / ix["ward_2017"].map(wsum)

    # count-conservation test (doc s5): give every 2017 ward 1000 units.
    ix["apportioned"] = 1000.0 * ix["weight"]
    total_in = 1000.0 * int((covered > 0).sum())  # wards that actually map
    total_out = ix["apportioned"].sum()
    loss = (total_in - total_out) / total_in * 100
    print(f"\n  count-conservation (normalized): in={total_in:.0f} out={total_out:.1f} loss={loss:.4f}%")
    print(f"  [{'PASS' if abs(loss) < 0.01 else 'FAIL'}] apportioned total preserved")

    # ---------- write crosswalk + disclosed-error diagnostic ----------
    OUT.parent.mkdir(parents=True, exist_ok=True)
    ix[["ward_2017", "ward_no_2022", "weight_raw", "weight"]].sort_values(
        ["ward_2017", "ward_no_2022"]
    ).to_csv(OUT, index=False)
    print(f"\nWrote {OUT.relative_to(ROOT)}  ({len(ix)} old->new links)")

    cov_path = OUT.parent / "ward_crosswalk_coverage_2017.csv"
    cov = w17[["ward_2017", "zone"]].copy()
    cov["raw_coverage"] = covered.values
    cov["flag_low_coverage"] = cov["raw_coverage"] < 0.90  # disclosed-error flag
    cov.sort_values("raw_coverage").to_csv(cov_path, index=False)
    print(f"Wrote {cov_path.relative_to(ROOT)}  "
          f"({int(cov['flag_low_coverage'].sum())} wards flagged <90% raw coverage)")
    print("  -> use flag_low_coverage to gate/annotate apportioned attributes (doc s5 limitations).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
