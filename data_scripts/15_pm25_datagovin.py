"""C2 - ward PM2.5 from CPCB stations (data.gov.in real-time AQI) via IDW.

Source: data.gov.in resource 3b01bcb8-... (CPCB real-time AQI, station lat/lon +
        avg_value per pollutant). Filter pollutant_id == PM2.5.
Method: IDW (power 2, k nearest) station -> ward centroid; interpolation
        uncertainty as weighted variance of contributing stations.
Outputs:
  - data/tabular/airquality/cpcb_delhi_pm25_stations.csv
  - data/processed/ward_pm25.csv   (mean_pm25, pm25_interp_var)

CAVEAT: data.gov.in is a LIVE snapshot (not the Apr-Jun seasonal mean the doc
wants). Station locations + method are correct and re-valuable; absolute values
are a current reading. Upgrade to historical seasonal means with an OpenAQ key.
"""
from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import requests
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
WARDS = ROOT / "data" / "aoi" / "mcd_wards_2022.geojson"
OUT_ST = ROOT / "data" / "tabular" / "airquality" / "cpcb_delhi_pm25_stations.csv"
OUT_CSV = ROOT / "data" / "processed" / "ward_pm25.csv"
CRS = "EPSG:32643"
KEY = "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b"  # data.gov.in public sample key
RES_ID = "3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"
K = 8


def _get_page(url, params):
    for attempt in range(6):
        try:
            r = requests.get(url, params=params, timeout=60)
            r.raise_for_status()
            return r.json().get("records", [])
        except requests.exceptions.RequestException as e:
            print(f"    page offset={params['offset']} attempt {attempt + 1} failed "
                  f"({type(e).__name__}); retrying...")
    return None


def fetch_stations():
    url = f"https://api.data.gov.in/resource/{RES_ID}"
    recs = []
    for offset in range(0, 400, 100):  # ~308 Delhi records, page size 100
        params = {"api-key": KEY, "format": "json", "limit": 100,
                  "offset": offset, "filters[state]": "Delhi"}
        page = _get_page(url, params)
        if page is None:
            raise RuntimeError(f"data.gov.in unreachable at offset {offset}")
        print(f"  fetched offset {offset}: {len(page)} records")
        recs.extend(page)
        if len(page) < 100:
            break
    rows = []
    for x in recs:
        if str(x.get("pollutant_id", "")).replace(".", "").upper() != "PM25":
            continue
        try:
            v = float(x.get("avg_value"))
        except (TypeError, ValueError):
            continue
        if v <= 0:
            continue
        rows.append({"station": x["station"], "lat": float(x["latitude"]),
                     "lon": float(x["longitude"]), "pm25": v})
    df = pd.DataFrame(rows).groupby(["station"], as_index=False).agg(
        lat=("lat", "first"), lon=("lon", "first"), pm25=("pm25", "mean"))
    return df


def main() -> int:
    st = fetch_stations()
    OUT_ST.parent.mkdir(parents=True, exist_ok=True)
    st.to_csv(OUT_ST, index=False)
    print(f"PM2.5 stations: {len(st)}  range {st.pm25.min():.0f}..{st.pm25.max():.0f} ug/m3 "
          f"(mean {st.pm25.mean():.0f})")
    print(f"wrote {OUT_ST.relative_to(ROOT)}")

    pts = gpd.GeoDataFrame(st, geometry=gpd.points_from_xy(st.lon, st.lat),
                           crs="EPSG:4326").to_crs(CRS)
    xy = np.c_[pts.geometry.x, pts.geometry.y]
    z = pts["pm25"].to_numpy()
    tree = cKDTree(xy)

    wards = gpd.read_file(WARDS).to_crs(CRS)
    cen = np.c_[wards.geometry.centroid.x, wards.geometry.centroid.y]
    k = min(K, len(st))
    dist, idx = tree.query(cen, k=k)
    dist = np.maximum(dist, 1e-6)
    w = 1.0 / dist ** 2
    zk = z[idx]
    mean = (w * zk).sum(axis=1) / w.sum(axis=1)
    var = (w * (zk - mean[:, None]) ** 2).sum(axis=1) / w.sum(axis=1)  # weighted var

    out = pd.DataFrame({
        "ward_no": wards["ward_no"].values,
        "ward_name": wards["ward_name"].values,
        "mean_pm25": mean.round(1),
        "pm25_interp_var": var.round(1),
    }).sort_values("ward_no")
    out.to_csv(OUT_CSV, index=False)
    print(f"per-ward mean_pm25: {len(out)}/250  "
          f"range {out.mean_pm25.min():.0f}..{out.mean_pm25.max():.0f} ug/m3")
    print(f"wrote {OUT_CSV.relative_to(ROOT)}")
    print("\nMost polluted wards:")
    print(out.nlargest(5, "mean_pm25")[["ward_no", "ward_name", "mean_pm25"]].to_string(index=False))
    print("Least polluted wards:")
    print(out.nsmallest(5, "mean_pm25")[["ward_no", "ward_name", "mean_pm25"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
