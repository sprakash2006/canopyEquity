"""C1 assignment - place 675 DUSIB JJ clusters onto the 250 wards via the
assembly-constituency (AC) bridge, since ward numbers don't align (11% AC
agreement) and location text doesn't geocode (5% yield).

Method (disclosed limitation): each cluster carries a reliable ECI AC number
(ac_no), and every 2022 ward carries its AC (AC_No, from the KML). We apportion
each cluster's households + area across the MCD wards of its AC, weighted by
ward population (a prior for where settlements sit). Conserves totals within
each AC; smooths within-AC location. This is the honest ceiling given no
coordinates and non-aligning ward numbers.

Output: data/processed/ward_dusib_jj.csv
  ward_no, ward_name, jj_n_clusters_apportioned, jj_households, jj_area_sqm, jj_area_frac
"""
from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_KML = ROOT / "data" / "aoi" / "delhi_wards_map_raw.kml"
A1 = ROOT / "data" / "aoi" / "mcd_wards_2022.geojson"
DUSIB = ROOT / "data" / "tabular" / "dusib" / "dusib_jj_clusters_675.csv"
OUT = ROOT / "data" / "processed" / "ward_dusib_jj.csv"
ANALYSIS_CRS = "EPSG:32643"


def main() -> int:
    # --- ward table: ward_no, ac_no, pop, area_sqm, name ---
    kml = gpd.read_file(RAW_KML)
    kml = kml[kml["Ward_No"].astype(int) != 0].copy()
    a1 = gpd.read_file(A1).to_crs(ANALYSIS_CRS)
    ward = pd.DataFrame({
        "ward_no": kml["Ward_No"].astype(int).values,
        "ac_no": kml["AC_No"].astype(int).values,
        "ac_name": kml["AC_Name"].values,
        "pop": pd.to_numeric(kml["TotalPop"], errors="coerce").fillna(0).values,
    })
    ward = ward.merge(
        pd.DataFrame({"ward_no": a1["ward_no"].values,
                      "ward_name": a1["ward_name"].values,
                      "ward_area_sqm": a1.geometry.area.values}),
        on="ward_no")

    # --- AC alignment sanity check ---
    print("=== AC bridge sanity (KML AC_No -> AC_Name) ===")
    ac_names = ward.drop_duplicates("ac_no").set_index("ac_no")["ac_name"]
    for a in [21, 28, 40, 60]:
        print(f"  AC {a}: {ac_names.get(a, '(not in MCD)')}")

    # --- DUSIB clusters ---
    d = pd.read_csv(DUSIB)
    d["ac_no"] = pd.to_numeric(d["ac_no"], errors="coerce")
    d["households"] = pd.to_numeric(d["households"], errors="coerce").fillna(0)
    d["area_sqm"] = pd.to_numeric(d["area_sqm"], errors="coerce").fillna(0)
    print(f"\nclusters: {len(d)} | with ac_no: {d['ac_no'].notna().sum()}")

    mcd_acs = set(ward["ac_no"].unique())
    d = d.dropna(subset=["ac_no"]).copy()
    d["ac_no"] = d["ac_no"].astype(int)
    in_mcd = d[d["ac_no"].isin(mcd_acs)].copy()
    dropped = d[~d["ac_no"].isin(mcd_acs)]
    print(f"clusters in an MCD AC: {len(in_mcd)} | outside MCD ACs "
          f"(NDMC/Cantt etc.): {len(dropped)}")

    # --- per-AC population weights ---
    ac_pop = ward.groupby("ac_no")["pop"].transform("sum")
    ward["w_pop"] = ward["pop"] / ac_pop.replace(0, pd.NA)
    ward["w_pop"] = ward["w_pop"].fillna(1.0 / ward.groupby("ac_no")["ward_no"].transform("count"))

    # --- apportion each cluster to its AC's wards ---
    acc = {wn: {"hh": 0.0, "area": 0.0, "n": 0.0} for wn in ward["ward_no"]}
    grp = ward.groupby("ac_no")
    for _, c in in_mcd.iterrows():
        members = grp.get_group(c["ac_no"])
        for _, m in members.iterrows():
            acc[m["ward_no"]]["hh"] += c["households"] * m["w_pop"]
            acc[m["ward_no"]]["area"] += c["area_sqm"] * m["w_pop"]
            acc[m["ward_no"]]["n"] += m["w_pop"]

    res = ward[["ward_no", "ward_name", "ward_area_sqm"]].copy()
    res["jj_n_clusters_apportioned"] = res["ward_no"].map(lambda w: round(acc[w]["n"], 2))
    res["jj_households"] = res["ward_no"].map(lambda w: round(acc[w]["hh"])).astype(int)
    res["jj_area_sqm"] = res["ward_no"].map(lambda w: round(acc[w]["area"])).astype(int)
    res["jj_area_frac"] = (res["jj_area_sqm"] / res["ward_area_sqm"]).round(5)
    res = res.drop(columns="ward_area_sqm").sort_values("ward_no")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    res.to_csv(OUT, index=False)

    # --- conservation check ---
    print("\n=== conservation ===")
    print(f"  households  in={int(in_mcd['households'].sum()):>8} "
          f"out={res['jj_households'].sum():>8}")
    print(f"  area_sqm    in={int(in_mcd['area_sqm'].sum()):>8} "
          f"out={res['jj_area_sqm'].sum():>8}")
    print(f"  wards with any JJ: {(res['jj_households'] > 0).sum()}/250")
    print(f"\nTop 8 wards by JJ households:")
    print(res.sort_values("jj_households", ascending=False)
          .head(8)[["ward_no", "ward_name", "jj_households", "jj_area_frac"]]
          .to_string(index=False))
    print(f"\nwrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
