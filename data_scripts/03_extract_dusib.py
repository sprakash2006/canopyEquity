"""C1 - extract the DUSIB 675 JJ-cluster register to a clean CSV.

Source: data/tabular/dusib/List-of-JJ-675-Clusters1.pdf  (19pp, digital text,
        11 cols incl. Ward No. + Land Area in Sqm + House Holds -- the three
        fields C1 needs; the 'primary' 46pp PDF lacks ward + area).

Output: data/tabular/dusib/dusib_jj_clusters_675.csv
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "data/tabular/dusib/List-of-JJ-675-Clusters1.pdf"
OUT = ROOT / "data/tabular/dusib/dusib_jj_clusters_675.csv"

COLS = [
    "s_no", "code", "ac_no", "div", "location", "households",
    "land_owning_agency", "area_sqm", "parliamentary_constituency",
    "ward_no_flat", "revenue_distt",
]
HEADER_TOKENS = {"s.no", "sno", "code", "ac no"}


def _clean(v):
    if v is None:
        return ""
    return re.sub(r"\s+", " ", str(v)).strip()


def _to_int(v):
    s = re.sub(r"[^0-9]", "", _clean(v))
    return int(s) if s else None


def main() -> int:
    rows = []
    with pdfplumber.open(PDF) as pdf:
        for page in pdf.pages:
            for tbl in page.extract_tables():
                for raw in tbl:
                    cells = [_clean(c) for c in raw]
                    if not any(cells):
                        continue
                    # skip header rows (repeat every page)
                    if _clean(cells[0]).lower() in HEADER_TOKENS:
                        continue
                    if len(cells) < 11:
                        cells = cells + [""] * (11 - len(cells))
                    elif len(cells) > 11:
                        cells = cells[:11]
                    rows.append(cells)

    df = pd.DataFrame(rows, columns=COLS)
    # keep only genuine data rows: s_no numeric
    df = df[df["s_no"].str.match(r"^\d+$", na=False)].copy()
    for c in ("households", "area_sqm", "ward_no_flat", "ac_no", "s_no"):
        df[c] = df[c].map(_to_int)

    df = df.drop_duplicates(subset="s_no").sort_values("s_no").reset_index(drop=True)

    print("===== DUSIB EXTRACTION =====")
    print(f"  rows extracted        : {len(df)}  (target 675)")
    print(f"  ward_no present       : {df['ward_no_flat'].notna().sum()} / {len(df)}")
    print(f"  households present     : {df['households'].notna().sum()} / {len(df)}")
    print(f"  area_sqm present       : {df['area_sqm'].notna().sum()} / {len(df)}")
    print(f"  ward_no range          : {df['ward_no_flat'].min()} .. {df['ward_no_flat'].max()}")
    print(f"  total JJ households     : {int(df['households'].sum(skipna=True)):,}")
    print(f"  total JJ area           : {df['area_sqm'].sum(skipna=True)/1e6:.2f} km^2")
    print(f"  distinct revenue distts : {sorted(df['revenue_distt'].dropna().unique().tolist())}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"\nWrote {OUT.relative_to(ROOT)}")
    if len(df) != 675:
        print(f"  NOTE: {len(df)} != 675 -- inspect page breaks / merged rows before use.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
