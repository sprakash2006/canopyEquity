"""A7 - assemble the ward-level census CSV (schema per doc A7 / s7).

Target columns (keyed on the 250-ward 2022 geometry, ward_no):
  total_population, sc_population           -> filled now from the A1 KML
                                               (already apportioned to 2022 wards)
  total_households, literate_population,
  households_piped_water_premises,
  slum_households                           -> EMPTY: need NADA ward PCA (cat 6282)
                                               + House Listing tables, then crosswalk

This writes a real, schema-correct file today; the 4 empty columns are the
explicit acquisition backlog, not a silent omission.
"""
from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
A1 = ROOT / "data" / "aoi" / "mcd_wards_2022.geojson"
OUT = ROOT / "data" / "tabular" / "census" / "a7_ward_census_2011.csv"

SCHEMA = [
    "ward_no", "ward_name",
    "total_population", "sc_population",          # filled from KML
    "total_households", "literate_population",    # need PCA
    "households_piped_water_premises", "slum_households",  # need House Listing
]

a1 = gpd.read_file(A1)[["ward_no", "ward_name", "pop2011_kml", "sc_pop2011_kml"]]
df = pd.DataFrame({
    "ward_no": a1["ward_no"],
    "ward_name": a1["ward_name"],
    "total_population": a1["pop2011_kml"].astype("Int64"),
    "sc_population": a1["sc_pop2011_kml"].astype("Int64"),
    "total_households": pd.NA,
    "literate_population": pd.NA,
    "households_piped_water_premises": pd.NA,
    "slum_households": pd.NA,
})[SCHEMA].sort_values("ward_no")

OUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT, index=False)

filled = [c for c in SCHEMA[2:] if df[c].notna().any()]
empty = [c for c in SCHEMA[2:] if not df[c].notna().any()]
print(f"wrote {OUT.relative_to(ROOT)}  ({len(df)} wards)")
print(f"  total_population sum : {int(df['total_population'].sum()):,}")
print(f"  sc_population sum     : {int(df['sc_population'].sum()):,}")
print(f"  FILLED columns  : {filled}")
print(f"  EMPTY  columns  : {empty}  <- need NADA PCA + House Listing")
