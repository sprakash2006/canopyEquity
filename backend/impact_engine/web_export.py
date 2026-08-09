"""
==========================================================
CanopyAI
Web Tile Exporter
==========================================================

Turns the impact-score raster into a browser-ready overlay:

  * reprojects the score to WGS84 (Leaflet's CRS)
  * colours it with the red -> yellow -> green priority ramp
  * tints non-plantable pixels by land cover so the whole
    analysed extent is covered
  * leaves data-gap (NaN) pixels fully transparent
  * writes the WGS84 lat/lon bounds alongside

This runs inside the impact pipeline, so it regenerates
automatically for WHATEVER location was uploaded — the
frontend just reads impact_score_web.png + its bounds and
centres the map on them.  No Delhi hard-coding anywhere.
==========================================================
"""

import json
import time
from pathlib import Path

import numpy as np
import rasterio
from rasterio.warp import (
    calculate_default_transform,
    reproject,
    Resampling,
)
from PIL import Image


# Red -> yellow -> green priority ramp (score 0..100).
# Low score = low priority = green, high = red.
COLOR_STOPS = [
    (0,   (22, 101, 52)),
    (8,   (34, 197, 94)),
    (20,  (163, 230, 53)),
    (35,  (250, 204, 21)),
    (50,  (234, 179, 8)),
    (65,  (249, 115, 22)),
    (80,  (220, 38, 38)),
    (100, (153, 27, 27)),
]

# Muted tints for non-plantable land cover (score == 0),
# so the map reads as a full segmentation, not sparse dots.
#   0 = bare, 1 = tree, 2 = built-up, 3 = cropland
LANDCOVER_TINT = {
    0: (180, 180, 180),   # bare -> light grey
    1: (30, 95, 50),      # existing tree -> forest green
    2: (120, 120, 125),   # built-up -> muted grey
    3: (200, 190, 140),   # cropland -> pale tan
}

PLANTABLE_ALPHA = 220     # bright, dominant
NON_PLANTABLE_ALPHA = 100  # subtle, basemap shows through


class WebTileExporter:

    def __init__(self, reference_dataset, output_dir="outputs"):

        # Any aligned source raster works as the geo reference
        # (same CRS + transform as the score grid).
        self.reference = reference_dataset

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    # =====================================================
    # PUBLIC ENTRY
    # =====================================================

    def export(self, impact_score, landcover=None,
               png_name="impact_score_web.png",
               bounds_name="impact_score_web.bounds.json"):

        src_crs = self.reference.crs
        src_transform = self.reference.transform
        src_h, src_w = impact_score.shape

        # Bounds of the source grid in its native CRS.
        left, top = src_transform * (0, 0)
        right, bottom = src_transform * (src_w, src_h)

        dst_crs = "EPSG:4326"

        dst_transform, dst_w, dst_h = calculate_default_transform(
            src_crs, dst_crs,
            src_w, src_h,
            left, bottom, right, top,
        )

        # -------------------------------------------------
        # Reproject score to WGS84
        # -------------------------------------------------

        score = np.full((dst_h, dst_w), np.nan, dtype=np.float32)

        reproject(
            source=np.ascontiguousarray(impact_score.astype(np.float32)),
            destination=score,
            src_transform=src_transform,
            src_crs=src_crs,
            dst_transform=dst_transform,
            dst_crs=dst_crs,
            src_nodata=np.nan,
            dst_nodata=np.nan,
            resampling=Resampling.nearest,
        )

        # -------------------------------------------------
        # Reproject land cover (optional tint layer)
        # -------------------------------------------------

        land = None

        if landcover is not None:

            land = np.full((dst_h, dst_w), 255, dtype=np.float32)

            reproject(
                source=np.ascontiguousarray(landcover.astype(np.float32)),
                destination=land,
                src_transform=src_transform,
                src_crs=src_crs,
                dst_transform=dst_transform,
                dst_crs=dst_crs,
                resampling=Resampling.nearest,
            )

        # -------------------------------------------------
        # Colourise
        # -------------------------------------------------

        rgba = self._colorize(score, land)

        png_path = self.output_dir / png_name
        Image.fromarray(rgba, mode="RGBA").save(
            png_path, optimize=True, compress_level=6
        )

        # -------------------------------------------------
        # Bounds json (Leaflet imageOverlay corners)
        # -------------------------------------------------

        w_left, w_top = dst_transform * (0, 0)
        w_right, w_bottom = dst_transform * (dst_w, dst_h)

        bounds = {
            "north": float(w_top),
            "south": float(w_bottom),
            "west": float(w_left),
            "east": float(w_right),
            # Changes every run so the frontend can cache-bust
            # the PNG even when the extent is unchanged.
            "version": int(time.time()),
        }

        bounds_path = self.output_dir / bounds_name
        with open(bounds_path, "w", encoding="utf-8") as f:
            json.dump(bounds, f)

        print(f"Saved : {png_path}")
        print(f"Saved : {bounds_path}")
        print(f"Web bounds (WGS84): {bounds}")

        return bounds

    # =====================================================
    # COLOR MAPPING
    # =====================================================

    def _colorize(self, score, land):

        h, w = score.shape

        pos = np.array([s[0] for s in COLOR_STOPS], dtype=np.float32)
        cols = np.array([s[1] for s in COLOR_STOPS], dtype=np.float32)

        r = np.zeros((h, w), dtype=np.uint8)
        g = np.zeros((h, w), dtype=np.uint8)
        b = np.zeros((h, w), dtype=np.uint8)
        alpha = np.zeros((h, w), dtype=np.uint8)

        # --- Plantable pixels: bright priority ramp
        plantable = (~np.isnan(score)) & (score > 0.5)
        v = np.clip(score[plantable], 0, 100)
        r[plantable] = np.interp(v, pos, cols[:, 0]).astype(np.uint8)
        g[plantable] = np.interp(v, pos, cols[:, 1]).astype(np.uint8)
        b[plantable] = np.interp(v, pos, cols[:, 2]).astype(np.uint8)
        alpha[plantable] = PLANTABLE_ALPHA

        # --- Non-plantable pixels (score 0): land-cover tint
        if land is not None:

            non_plantable = (
                (~np.isnan(score)) & (score <= 0.5) & (land != 255)
            )

            lc = land[non_plantable].astype(np.int32)

            default = (150, 150, 150)

            r[non_plantable] = np.select(
                [lc == k for k in LANDCOVER_TINT],
                [LANDCOVER_TINT[k][0] for k in LANDCOVER_TINT],
                default=default[0],
            )
            g[non_plantable] = np.select(
                [lc == k for k in LANDCOVER_TINT],
                [LANDCOVER_TINT[k][1] for k in LANDCOVER_TINT],
                default=default[1],
            )
            b[non_plantable] = np.select(
                [lc == k for k in LANDCOVER_TINT],
                [LANDCOVER_TINT[k][2] for k in LANDCOVER_TINT],
                default=default[2],
            )
            alpha[non_plantable] = NON_PLANTABLE_ALPHA

        # NaN pixels stay fully transparent (alpha already 0).

        return np.stack([r, g, b, alpha], axis=-1)
