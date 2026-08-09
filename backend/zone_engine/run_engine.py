"""
==========================================================
CanopyAI
Zone Engine
==========================================================

Auto-generates a grid tessellation over the impact raster
(no pre-drawn ward polygons required) and computes per-zone
statistics from impact_score.tif.

Output:
    outputs/auto_zones.geojson  (EPSG:4326, for the map)
    outputs/auto_zones.csv      (tabular, for the dashboard)

Each zone has:
    zone_id
    impact_mean
    impact_max
    impact_std
    impact_count
    priority       (VERY HIGH / HIGH / MEDIUM / LOW / VERY LOW)
    bounds         (bbox in WGS84 for zoom-to)
==========================================================
"""

from pathlib import Path

import numpy as np
import rasterio
from rasterstats import zonal_stats

import geopandas as gpd
from shapely.geometry import box


# Number of cells per side of the grid.
# 20 × 20 = 400 zones — a good balance of detail vs. render cost.
GRID_CELLS_PER_SIDE = 20


# =====================================================
# BUILD GRID
# =====================================================


def build_grid(raster_path):

    print()
    print("=" * 70)
    print("BUILDING AUTO GRID")
    print("=" * 70)

    with rasterio.open(raster_path) as src:
        bounds = src.bounds
        crs = src.crs

    n = GRID_CELLS_PER_SIDE

    dx = (bounds.right - bounds.left) / n
    dy = (bounds.top - bounds.bottom) / n

    polygons = []
    zone_ids = []

    for i in range(n):

        for j in range(n):

            left = bounds.left + i * dx
            right = left + dx
            bottom = bounds.bottom + j * dy
            top = bottom + dy

            polygons.append(box(left, bottom, right, top))

            zone_ids.append(f"Z-{i:02d}-{j:02d}")

    gdf = gpd.GeoDataFrame(
        {
            "zone_id": zone_ids,
            "geometry": polygons
        },
        crs=crs
    )

    print(f"Grid : {n} x {n} = {len(gdf)} zones")
    print(f"CRS  : {crs}")
    print(f"Cell : {dx:.0f} x {dy:.0f} (raster units)")

    return gdf


# =====================================================
# ZONAL STATISTICS
# =====================================================


def compute_stats(gdf, raster_path):

    print()
    print("=" * 70)
    print("COMPUTING PER-ZONE STATISTICS")
    print("=" * 70)

    stats = zonal_stats(
        gdf,
        raster_path,
        stats=["mean", "max", "std", "count"],
        nodata=None,
        geojson_out=False
    )

    gdf["impact_mean"] = [
        (s.get("mean") if s.get("mean") is not None else 0)
        for s in stats
    ]

    gdf["impact_max"] = [
        (s.get("max") if s.get("max") is not None else 0)
        for s in stats
    ]

    gdf["impact_std"] = [
        (s.get("std") if s.get("std") is not None else 0)
        for s in stats
    ]

    gdf["impact_count"] = [
        (s.get("count") if s.get("count") is not None else 0)
        for s in stats
    ]

    # Drop empty zones (edge cells that overlap only nodata)
    before = len(gdf)
    gdf = gdf[gdf["impact_count"] > 0].reset_index(drop=True)
    after = len(gdf)

    print(f"Zones with data : {after} / {before}")

    return gdf


# =====================================================
# PRIORITY CLASSIFICATION
# =====================================================


def classify_priority(gdf):

    def to_priority(score):

        if score >= 70:
            return "VERY HIGH"
        if score >= 55:
            return "HIGH"
        if score >= 40:
            return "MEDIUM"
        if score >= 25:
            return "LOW"
        return "VERY LOW"

    gdf["priority"] = gdf["impact_mean"].apply(to_priority)

    # Rank by mean impact
    gdf = gdf.sort_values(
        "impact_mean",
        ascending=False
    ).reset_index(drop=True)

    gdf["rank"] = np.arange(1, len(gdf) + 1)

    return gdf


# =====================================================
# EXPORT
# =====================================================


def export(gdf, output_dir):

    print()
    print("=" * 70)
    print("EXPORTING AUTO ZONES")
    print("=" * 70)

    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    # Reproject to WGS84 for the frontend
    gdf_web = gdf.to_crs("EPSG:4326")

    # Add bounds (for zoom-to on click)
    gdf_web["bbox"] = gdf_web.geometry.bounds.apply(
        lambda r: [r.minx, r.miny, r.maxx, r.maxy],
        axis=1
    )

    geojson_path = output_dir / "auto_zones.geojson"

    gdf_web.drop(columns=["bbox"]).to_file(
        geojson_path,
        driver="GeoJSON"
    )

    print(f"Saved : {geojson_path}")

    csv_path = output_dir / "auto_zones.csv"

    gdf_web.drop(columns=["geometry", "bbox"]).to_csv(
        csv_path,
        index=False
    )

    print(f"Saved : {csv_path}")

    return {
        "geojson": str(geojson_path),
        "csv": str(csv_path)
    }


# =====================================================
# MAIN
# =====================================================


def run():

    print("=" * 70)
    print("CANOPY AI - ZONE ENGINE  (auto-generated grid)")
    print("=" * 70)

    impact_raster = "outputs/impact_score.tif"

    if not Path(impact_raster).exists():

        return {
            "status": "error",
            "message": f"{impact_raster} not found — run impact engine first"
        }

    # 1. Build grid
    gdf = build_grid(impact_raster)

    # 2. Compute stats per cell
    gdf = compute_stats(gdf, impact_raster)

    # 3. Classify + rank
    gdf = classify_priority(gdf)

    # 4. Export
    files = export(gdf, "outputs")

    print()
    print("=" * 70)
    print("ZONE ENGINE COMPLETED")
    print("=" * 70)

    print(f"Total zones : {len(gdf)}")

    top = gdf.head(5)[["zone_id", "impact_mean", "priority"]]

    print("\nTOP 5 ZONES")
    print(top.to_string(index=False))

    return {
        "status": "success",
        "total_zones": int(len(gdf)),
        "files": files
    }


if __name__ == "__main__":
    run()
