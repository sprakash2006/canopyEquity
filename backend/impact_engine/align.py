"""
==========================================================
CanopyAI
Impact Engine
Raster Alignment Engine
==========================================================
"""

import numpy as np
import rasterio

from rasterio.warp import (
    reproject,
    Resampling
)


class RasterAligner:

    def __init__(self, datasets):
        """
        datasets -> Dictionary returned by RasterLoader
        """

        self.datasets = datasets

        # NDVI will be our reference grid
        self.reference = datasets["ndvi"]

        self.aligned = {}

    # ======================================================
    # REPROJECT A SINGLE RASTER
    # ======================================================

    def reproject_raster(
        self,
        raster,
        band=1,
        resampling=Resampling.bilinear
    ):

        destination = np.full(
            (
                self.reference.height,
                self.reference.width
            ),
            np.nan,
            dtype=np.float32
        )

        reproject(
            source=rasterio.band(raster, band),

            destination=destination,

            src_transform=raster.transform,
            src_crs=raster.crs,

            dst_transform=self.reference.transform,
            dst_crs=self.reference.crs,

            src_nodata=raster.nodata,
            dst_nodata=np.nan,

            resampling=resampling
        )

        # Remove invalid GIS NoData values
        destination[destination < -1000] = np.nan

        return destination

    # ======================================================
    # ALIGN ALL RASTERS
    # ======================================================

    def align(self):

        print("\n" + "=" * 70)
        print("ALIGNING ALL RASTERS")
        print("=" * 70)

        # -------------------------
        # NDVI (Already Reference)
        # -------------------------

        ndvi = self.datasets["ndvi"].read(1).astype(np.float32)

        ndvi[ndvi < -1000] = np.nan

        self.aligned["ndvi"] = ndvi

        # -------------------------
        # LAND COVER
        # -------------------------

        self.aligned["landcover"] = self.reproject_raster(
            self.datasets["landcover"],
            band=1,
            resampling=Resampling.nearest
        )

        # -------------------------
        # LST
        # -------------------------

        self.aligned["lst"] = self.reproject_raster(
            self.datasets["lst"],
            band=1,
            resampling=Resampling.bilinear
        )

        # -------------------------
        # RAINFALL
        # -------------------------

        self.aligned["rainfall"] = self.reproject_raster(
            self.datasets["rainfall"],
            band=1,
            resampling=Resampling.bilinear
        )

        # -------------------------
        # VULNERABILITY
        # Band 1 = vulnerability_index
        # -------------------------

        self.aligned["vulnerability"] = self.reproject_raster(
            self.datasets["vulnerability"],
            band=1,
            resampling=Resampling.bilinear
        )

        print()

        for name, raster in self.aligned.items():

            print(
                f"{name:15s}"
                f" Shape={raster.shape}"
                f"  Dtype={raster.dtype}"
            )

        print("\n" + "=" * 70)
        print("ALL RASTERS ALIGNED")
        print("=" * 70)

        return self.aligned

    # ======================================================
    # VALIDATE
    # ======================================================

    def validate(self):

        print("\nChecking Alignment...\n")

        reference_shape = (
            self.reference.height,
            self.reference.width
        )

        for name, raster in self.aligned.items():

            if raster.shape != reference_shape:

                raise ValueError(
                    f"{name} has incorrect shape {raster.shape}"
                )

        print("✓ Every raster has identical dimensions")

        print(f"Reference Shape : {reference_shape}")

        print(f"Reference CRS   : {self.reference.crs}")

        print("\nAlignment Validation Successful")