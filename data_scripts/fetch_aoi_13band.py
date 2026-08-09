"""
Fetch a 13-band Sentinel-2 L2A GeoTIFF for an arbitrary AOI polygon.

No Google Earth Engine auth needed: pulls open Sentinel-2 L2A
Cloud-Optimized GeoTIFFs from AWS Earth Search (element84), picks the
least-cloudy scene in a date window, mosaics whatever tiles cover the AOI,
crops to the polygon bbox at 10 m, and writes a single 13-band GeoTIFF
in EPSG:32643 -- the exact format the CanopyAI pipeline expects
(same as uploads/pune.tif).

Band order (matches backend/impact_engine/satellite_impact.py):
  1 coastal(B01) 2 blue(B02) 3 green(B03) 4 red(B04) 5 rededge1(B05)
  6 rededge2(B06) 7 rededge3(B07) 8 nir(B08) 9 narrownir(B8A)
  10 watervapor(B09) 11 swir16(B11) 12 swir22(B12) 13 SCL(scene class)

Reflectance = (DN - 1000) / 10000  (baseline >= 04.00). DN 0 = nodata.

Usage (run with the project venv so deps resolve):
  venv/Scripts/python.exe data_scripts/fetch_aoi_13band.py \
      --aoi data/aoi/user_aoi.geojson \
      --out uploads/aoi.tif \
      --start 2025-11-01 --end 2026-02-28 --max-cloud 20
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.merge import merge
from rasterio.warp import transform_bounds
from pystac_client import Client
from shapely.geometry import shape
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]

CRS = "EPSG:32643"
RES = 10.0
STAC = "https://earth-search.aws.element84.com/v1"

# (asset key on Earth Search, output band label, resampling)
BANDS = [
    ("coastal",  "B01_coastal_443",   Resampling.bilinear),
    ("blue",     "B02_blue_490",      Resampling.nearest),
    ("green",    "B03_green_560",     Resampling.nearest),
    ("red",      "B04_red_665",       Resampling.nearest),
    ("rededge1", "B05_rededge_705",   Resampling.bilinear),
    ("rededge2", "B06_rededge_740",   Resampling.bilinear),
    ("rededge3", "B07_rededge_783",   Resampling.bilinear),
    ("nir",      "B08_nir_842",       Resampling.nearest),
    ("nir08",    "B8A_narrownir_865", Resampling.bilinear),
    ("nir09",    "B09_watervapor_945",Resampling.bilinear),
    ("swir16",   "B11_swir_1610",     Resampling.bilinear),
    ("swir22",   "B12_swir_2190",     Resampling.bilinear),
    ("scl",      "SCL_scene_class",   Resampling.nearest),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--aoi", default="data/aoi/user_aoi.geojson")
    ap.add_argument("--out", default="uploads/aoi.tif")
    ap.add_argument("--start", default="2025-11-01")
    ap.add_argument("--end", default="2026-02-28")
    ap.add_argument("--max-cloud", type=float, default=30.0)
    args = ap.parse_args()

    aoi_path = (ROOT / args.aoi) if not Path(args.aoi).is_absolute() else Path(args.aoi)
    out_path = (ROOT / args.out) if not Path(args.out).is_absolute() else Path(args.out)

    # ---- AOI polygon (lon/lat) + target-CRS grid ----
    gj = json.load(open(aoi_path, encoding="utf-8"))
    aoi_ll = unary_union([shape(f["geometry"]) for f in gj["features"]])
    minx, miny, maxx, maxy = aoi_ll.bounds
    print(f"AOI bbox (lon/lat): {minx:.5f},{miny:.5f} .. {maxx:.5f},{maxy:.5f}")

    l, b, r, t = transform_bounds("EPSG:4326", CRS, minx, miny, maxx, maxy)
    l, b = np.floor(l / RES) * RES, np.floor(b / RES) * RES
    r, t = np.ceil(r / RES) * RES, np.ceil(t / RES) * RES
    width = int(round((r - l) / RES))
    height = int(round((t - b) / RES))
    transform = rasterio.transform.from_bounds(l, b, r, t, width, height)
    print(f"Output grid: {width} x {height} px @ {RES} m  ({CRS})")

    # ---- search Sentinel-2 L2A, pick least-cloudy scene ----
    cat = Client.open(STAC)
    search = cat.search(
        collections=["sentinel-2-l2a"],
        bbox=[minx, miny, maxx, maxy],
        datetime=f"{args.start}/{args.end}",
        query={"eo:cloud_cover": {"lt": args.max_cloud}},
    )
    items = list(search.items())
    if not items:
        raise SystemExit(
            "No scenes below the cloud threshold in that window. "
            "Try widening --start/--end or raising --max-cloud."
        )

    items.sort(key=lambda i: i.properties.get("eo:cloud_cover", 100))
    best = items[0]
    best_date = best.properties["datetime"][:10]
    print(f"Found {len(items)} candidate scenes. Best: {best_date} "
          f"({best.properties.get('eo:cloud_cover'):.1f}% cloud, "
          f"tile {best.properties.get('grid:code')})")

    # use every scene from that same date (covers AOIs spanning 2 tiles)
    same_date = [i for i in items if i.properties["datetime"][:10] == best_date]

    # ---- per-band mosaic cropped to the AOI grid ----
    env = dict(GDAL_HTTP_MULTIRANGE="YES", GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
               VSI_CACHE="TRUE", GDAL_HTTP_MAX_RETRY="3", GDAL_HTTP_RETRY_DELAY="1")
    stack = np.zeros((len(BANDS), height, width), dtype="uint16")

    with rasterio.Env(**env):
        for i, (asset, label, rs) in enumerate(BANDS, start=1):
            srcs = []
            for it in same_date:
                if asset in it.assets:
                    srcs.append(rasterio.open(it.assets[asset].href))
            if not srcs:
                print(f"  [{i:2d}/{len(BANDS)}] {label:20s} MISSING -> zeros")
                continue
            arr, _ = merge(srcs, bounds=(l, b, r, t), res=RES,
                           resampling=rs, nodata=0, dtype="uint16")
            for s in srcs:
                s.close()
            stack[i - 1] = arr[0]
            filled = int((arr[0] > 0).sum())
            print(f"  [{i:2d}/{len(BANDS)}] {label:20s} -> {filled:,} valid px")

    # ---- write compressed 13-band GeoTIFF ----
    out_path.parent.mkdir(parents=True, exist_ok=True)
    profile = dict(driver="GTiff", height=height, width=width, count=len(BANDS),
                   dtype="uint16", crs=CRS, transform=transform, nodata=0,
                   compress="deflate", predictor=2, tiled=True,
                   blockxsize=512, blockysize=512, BIGTIFF="IF_SAFER")
    with rasterio.open(out_path, "w", **profile) as dst:
        dst.write(stack)
        for i, (_, label, _) in enumerate(BANDS, start=1):
            dst.set_band_description(i, label)
        dst.update_tags(source="Sentinel-2 L2A (AWS Earth Search / element84)",
                        date=best_date, reflectance="(DN - 1000) / 10000",
                        nodata="0", aoi=str(aoi_path.name))

    size_mb = out_path.stat().st_size / 1e6
    print(f"\nwrote {out_path}  ({size_mb:.1f} MB, {len(BANDS)} bands, {best_date})")
    print("Next: POST /upload this file (or drop it in uploads/) then run /predict.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
