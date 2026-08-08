"""CRS guardrails for CanopyEquity — MCD build.

Analysis CRS : EPSG:32643 (WGS 84 / UTM 43N)  -> all area/length/buffer math
Storage  CRS : EPSG:4326  (WGS 84 lon/lat)    -> all on-disk vector files

Zone 43N spans 72E-78E; MCD spans 76.84-77.35E, comfortably inside (doc s6.2).
"""
from __future__ import annotations

import geopandas as gpd

ANALYSIS_CRS = "EPSG:32643"  # metric, for area/length/buffer
STORAGE_CRS = "EPSG:4326"    # lon/lat, for storage

# MCD bounding box in lon/lat (doc s6.2 + observed KML extent), with slack.
_MCD_LON = (76.7, 77.45)
_MCD_LAT = (28.3, 28.95)


def to_analysis(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Reproject to the metric analysis CRS. Never buffer/measure in 4326."""
    return gdf.to_crs(ANALYSIS_CRS)


def to_storage(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Reproject to the lon/lat storage CRS for writing to disk."""
    return gdf.to_crs(STORAGE_CRS)


def assert_within_mcd(gdf: gpd.GeoDataFrame) -> None:
    """Fail fast if a layer lands outside the Delhi/MCD envelope.

    Catches the classic 'buffered in degrees' and 'wrong CRS' bugs before
    they silently poison a join.
    """
    g = gdf.to_crs(STORAGE_CRS)
    minx, miny, maxx, maxy = g.total_bounds
    if not (_MCD_LON[0] <= minx and maxx <= _MCD_LON[1]
            and _MCD_LAT[0] <= miny and maxy <= _MCD_LAT[1]):
        raise ValueError(
            f"Layer bounds {(minx, miny, maxx, maxy)} fall outside the MCD "
            f"envelope lon{_MCD_LON} lat{_MCD_LAT}. Check the CRS."
        )
