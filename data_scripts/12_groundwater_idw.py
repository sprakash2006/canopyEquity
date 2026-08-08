"""Extra - groundwater depth-to-water-table per ward, from CGWB wells (IDW).

Input : data/tabular/groundwater/cgwb_delhi_gwl_raw.csv
        (170 CGWB monitoring wells, currentlevel = m below ground level, 2013-2021)
Method: recent-years (>=2017) mean depth per well -> IDW interpolation (power 2,
        12 nearest) in EPSG:32643 -> 500 m surface -> per-ward zonal mean.
Outputs:
  - data/processed/ward_mean_groundwater.csv  (mean_gw_depth_m; deeper = worse)
  - data/raster/mcd_groundwater_depth_idw_500m.tif

Higher depth = water table further down = harder/costlier to keep trees alive.
"""
from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import from_origin
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "tabular" / "groundwater" / "cgwb_delhi_gwl_raw.csv"
WARDS = ROOT / "data" / "aoi" / "mcd_wards_2022.geojson"
OUT_CSV = ROOT / "data" / "processed" / "ward_mean_groundwater.csv"
OUT_TIF = ROOT / "data" / "raster" / "mcd_groundwater_depth_idw_500m.tif"
CRS = "EPSG:32643"
RES = 500.0
IDW_POWER = 2
IDW_K = 12


def idw(xy_known, z, xy_query, k=IDW_K, power=IDW_POWER):
    tree = cKDTree(xy_known)
    k = min(k, len(xy_known))
    dist, idx = tree.query(xy_query, k=k)
    dist = np.maximum(dist, 1e-6)
    w = 1.0 / dist ** power
    return (w * z[idx]).sum(axis=1) / w.sum(axis=1)


def main() -> int:
    raw = pd.read_csv(RAW)
    raw["date"] = pd.to_datetime(raw["date"], errors="coerce")
    raw = raw.dropna(subset=["latitude", "longitude", "currentlevel", "date"])
    # recent-years mean depth per station (fallback: all years if none recent)
    recent = raw[raw["date"] >= "2017-01-01"]
    agg = recent.groupby("station_name").agg(
        lat=("latitude", "mean"), lon=("longitude", "mean"),
        depth=("currentlevel", "mean")).reset_index()
    if len(agg) < 30:  # fallback if too few recent
        agg = raw.groupby("station_name").agg(
            lat=("latitude", "mean"), lon=("longitude", "mean"),
            depth=("currentlevel", "mean")).reset_index()
    # sane physical range for depth-to-water (drop obvious errors)
    agg = agg[(agg["depth"] >= 0) & (agg["depth"] <= 100)]
    print(f"wells used: {len(agg)}  depth range {agg.depth.min():.1f}..{agg.depth.max():.1f} m "
          f"(mean {agg.depth.mean():.1f})")

    pts = gpd.GeoDataFrame(agg, geometry=gpd.points_from_xy(agg.lon, agg.lat),
                           crs="EPSG:4326").to_crs(CRS)
    xy_known = np.c_[pts.geometry.x, pts.geometry.y]
    z = pts["depth"].to_numpy()

    wards = gpd.read_file(WARDS).to_crs(CRS)
    minx, miny, maxx, maxy = wards.total_bounds
    nx = int(np.ceil((maxx - minx) / RES))
    ny = int(np.ceil((maxy - miny) / RES))
    xs = minx + (np.arange(nx) + 0.5) * RES
    ys = maxy - (np.arange(ny) + 0.5) * RES
    gx, gy = np.meshgrid(xs, ys)
    grid_vals = idw(xy_known, z, np.c_[gx.ravel(), gy.ravel()]).reshape(ny, nx)

    # --- write raster (mask outside MCD) ---
    transform = from_origin(minx, maxy, RES, RES)
    from rasterio.features import geometry_mask
    mask = geometry_mask([wards.dissolve().geometry.iloc[0]], (ny, nx), transform,
                         invert=True)
    arr = np.where(mask, grid_vals, np.nan).astype("float32")
    OUT_TIF.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(OUT_TIF, "w", driver="GTiff", height=ny, width=nx, count=1,
                       dtype="float32", crs=CRS, transform=transform,
                       nodata=np.nan) as dst:
        dst.write(arr, 1)
    print(f"wrote {OUT_TIF.relative_to(ROOT)} ({nx}x{ny} @ {RES:.0f} m)")

    # --- per-ward zonal mean via grid points ---
    gp = gpd.GeoDataFrame(
        {"v": grid_vals.ravel()},
        geometry=gpd.points_from_xy(gx.ravel(), gy.ravel()), crs=CRS)
    j = gpd.sjoin(gp, wards[["ward_no", "ward_name", "geometry"]], predicate="within")
    wm = j.groupby(["ward_no", "ward_name"])["v"].mean().reset_index()
    wm = wm.rename(columns={"v": "mean_gw_depth_m"})
    wm["mean_gw_depth_m"] = wm["mean_gw_depth_m"].round(2)
    # any ward with no grid point (tiny) -> sample IDW at centroid
    missing = set(wards.ward_no) - set(wm.ward_no)
    if missing:
        cen = wards[wards.ward_no.isin(missing)].copy()
        cxy = np.c_[cen.geometry.centroid.x, cen.geometry.centroid.y]
        cen["mean_gw_depth_m"] = idw(xy_known, z, cxy).round(2)
        wm = pd.concat([wm, cen[["ward_no", "ward_name", "mean_gw_depth_m"]]])
    wm = wm.sort_values("ward_no")
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    wm.to_csv(OUT_CSV, index=False)
    print(f"per-ward: {wm['mean_gw_depth_m'].notna().sum()}/250  "
          f"range {wm.mean_gw_depth_m.min():.1f}..{wm.mean_gw_depth_m.max():.1f} m")
    print(f"wrote {OUT_CSV.relative_to(ROOT)}")
    print("\nSHALLOWEST (best) wards:")
    print(wm.nsmallest(5, "mean_gw_depth_m").to_string(index=False))
    print("\nDEEPEST (worst) wards:")
    print(wm.nlargest(5, "mean_gw_depth_m").to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
