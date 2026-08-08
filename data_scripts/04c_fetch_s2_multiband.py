"""A3b - Complete Sentinel-2 L2A multiband GeoTIFF for the MCD AOI.

No-auth path (does NOT use Google Earth Engine): pulls open Sentinel-2 L2A
Cloud-Optimized GeoTIFFs from AWS Earth Search, mosaics the four MGRS tiles
that cover MCD Delhi (43RFM/FN/GM/GN), crops to the ward boundary, and writes a
single multiband GeoTIFF at 10 m in EPSG:32643.

Date 2024-05-08 chosen because all four tiles are ~0% cloud (single-date mosaic,
no seams). Values are raw L2A surface-reflectance DN (uint16); to get reflectance
0..1 use (DN + BOA_ADD_OFFSET) / 10000 with BOA_ADD_OFFSET = -1000 (baseline
>= 04.00). DN 0 = nodata.

Usage:  python 04c_fetch_s2_multiband.py [--date 2024-05-08]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.features import rasterize
from rasterio.merge import merge
from rasterio.warp import transform_bounds, transform_geom
from pystac_client import Client
from shapely.geometry import shape, mapping
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
WARDS = ROOT / "data" / "aoi" / "mcd_wards_2022.geojson"
OUT = ROOT / "data" / "raster" / "mcd_sentinel2_l2a_multiband.tif"

CRS = "EPSG:32643"
RES = 10.0
STAC = "https://earth-search.aws.element84.com/v1"

# (asset key on Earth Search, output band label, native res, resampling)
BANDS = [
    ("coastal",  "B01_coastal_443",  60, Resampling.bilinear),
    ("blue",     "B02_blue_490",     10, Resampling.nearest),
    ("green",    "B03_green_560",    10, Resampling.nearest),
    ("red",      "B04_red_665",      10, Resampling.nearest),
    ("rededge1", "B05_rededge_705",  20, Resampling.bilinear),
    ("rededge2", "B06_rededge_740",  20, Resampling.bilinear),
    ("rededge3", "B07_rededge_783",  20, Resampling.bilinear),
    ("nir",      "B08_nir_842",      10, Resampling.nearest),
    ("nir08",    "B8A_narrownir_865",20, Resampling.bilinear),
    ("nir09",    "B09_watervapor_945",60, Resampling.bilinear),
    ("swir16",   "B11_swir_1610",    20, Resampling.bilinear),
    ("swir22",   "B12_swir_2190",    20, Resampling.bilinear),
    ("scl",      "SCL_scene_class",  20, Resampling.nearest),  # bonus: cloud/land mask
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default="2024-05-08")
    args = ap.parse_args()

    # ---- AOI boundary (dissolved wards) in lon/lat and in target CRS ----
    gj = json.load(open(WARDS, encoding="utf-8"))
    boundary_ll = unary_union([shape(f["geometry"]) for f in gj["features"]])
    minx, miny, maxx, maxy = boundary_ll.bounds
    l, b, r, t = transform_bounds("EPSG:4326", CRS, minx, miny, maxx, maxy)
    # snap bounds to the 10 m grid
    l, b = np.floor(l / RES) * RES, np.floor(b / RES) * RES
    r, t = np.ceil(r / RES) * RES, np.ceil(t / RES) * RES
    width = int(round((r - l) / RES))
    height = int(round((t - b) / RES))
    transform = rasterio.transform.from_bounds(l, b, r, t, width, height)
    print(f"AOI grid: {width} x {height} px @ {RES} m  ({CRS})")

    # ---- find the four tiles for the chosen date ----
    cat = Client.open(STAC)
    items = list(cat.search(
        collections=["sentinel-2-l2a"], bbox=[minx, miny, maxx, maxy],
        datetime=f"{args.date}/{args.date}").items())
    print(f"{args.date}: {len(items)} tiles -> "
          + ", ".join(f"{i.properties.get('grid:code')}"
                      f"({i.properties.get('eo:cloud_cover'):.2f}%)" for i in items))
    if not items:
        raise SystemExit("no scenes for that date")

    # ---- boundary mask on the output grid (nodata outside MCD) ----
    geom32 = transform_geom("EPSG:4326", CRS, mapping(boundary_ll))
    inside = rasterize([(geom32, 1)], out_shape=(height, width),
                       transform=transform, fill=0, dtype="uint8").astype(bool)
    print(f"pixels inside MCD boundary: {inside.sum():,} / {inside.size:,}")

    # ---- per-band mosaic (4 tiles) cropped to the AOI grid ----
    env = dict(GDAL_HTTP_MULTIRANGE="YES", GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
               VSI_CACHE="TRUE", GDAL_HTTP_MAX_RETRY="3", GDAL_HTTP_RETRY_DELAY="1")
    stack = np.zeros((len(BANDS), height, width), dtype="uint16")
    with rasterio.Env(**env):
        for i, (asset, label, res, rs) in enumerate(BANDS, start=1):
            srcs = [rasterio.open(it.assets[asset].href) for it in items]
            arr, _ = merge(srcs, bounds=(l, b, r, t), res=RES, resampling=rs,
                           nodata=0, dtype="uint16")
            for s in srcs:
                s.close()
            band = arr[0]
            band[~inside] = 0  # clip to MCD boundary
            stack[i - 1] = band
            filled = int((band > 0).sum())
            print(f"  [{i:2d}/{len(BANDS)}] {label:20s} native {res:>2d}m -> "
                  f"{filled:,} valid px")

    # ---- write compressed multiband GeoTIFF ----
    OUT.parent.mkdir(parents=True, exist_ok=True)
    profile = dict(driver="GTiff", height=height, width=width, count=len(BANDS),
                   dtype="uint16", crs=CRS, transform=transform, nodata=0,
                   compress="deflate", predictor=2, tiled=True,
                   blockxsize=512, blockysize=512, BIGTIFF="IF_SAFER")
    with rasterio.open(OUT, "w", **profile) as dst:
        dst.write(stack)
        for i, (_, label, _, _) in enumerate(BANDS, start=1):
            dst.set_band_description(i, label)
        dst.update_tags(source="Sentinel-2 L2A (AWS Earth Search / element84)",
                        date=args.date, tiles="43RFM,43RFN,43RGM,43RGN",
                        reflectance="(DN - 1000) / 10000", nodata="0",
                        aoi="MCD Delhi wards 2022 (dissolved)")
    size_mb = OUT.stat().st_size / 1e6
    print(f"\nwrote {OUT.relative_to(ROOT)}  ({size_mb:.1f} MB, {len(BANDS)} bands)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
