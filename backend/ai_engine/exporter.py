"""
==========================================================
CanopyAI
AI Engine
GeoTIFF Exporter
==========================================================
"""

from pathlib import Path

import rasterio
from rasterio.warp import (
    calculate_default_transform,
    reproject,
    Resampling
)


class GeoTIFFExporter:

    def __init__(
        self,
        mask,
        reference_dataset,
        output_path="outputs/canopy_prediction.tif"
    ):

        self.mask = mask
        self.reference = reference_dataset
        self.output_path = Path(output_path)

    # =====================================================
    # EXPORT ORIGINAL GEOTIFF
    # =====================================================

    def export(self):

        print()
        print("=" * 70)
        print("EXPORTING GEOTIFF")
        print("=" * 70)

        self.output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        profile = self.reference.profile.copy()

        profile.update(

            dtype=rasterio.uint8,

            count=1,

            compress="lzw"

        )

        with rasterio.open(

            self.output_path,

            "w",

            **profile

        ) as dst:

            dst.write(

                self.mask,

                1

            )

        print("✓ Original GeoTIFF Exported")

        print(self.output_path.resolve())

        # --------------------------------------------
        # Create Web Version Automatically
        # --------------------------------------------

        self.export_web_version()

        return self.output_path

    # =====================================================
    # EXPORT WEB VERSION (EPSG:4326)
    # =====================================================

    def export_web_version(self):

        print()
        print("=" * 70)
        print("CREATING WEB GEOTIFF")
        print("=" * 70)

        destination = self.output_path.parent / "canopy_prediction_web.tif"

        dst_crs = "EPSG:4326"

        with rasterio.open(self.output_path) as src:

            transform, width, height = calculate_default_transform(

                src.crs,

                dst_crs,

                src.width,

                src.height,

                *src.bounds

            )

            kwargs = src.meta.copy()

            kwargs.update({

                "crs": dst_crs,

                "transform": transform,

                "width": width,

                "height": height,

                "compress": "lzw"

            })

            with rasterio.open(

                destination,

                "w",

                **kwargs

            ) as dst:

                reproject(

                    source=rasterio.band(src, 1),

                    destination=rasterio.band(dst, 1),

                    src_transform=src.transform,

                    src_crs=src.crs,

                    dst_transform=transform,

                    dst_crs=dst_crs,

                    resampling=Resampling.nearest

                )

        print("✓ Web GeoTIFF Created")

        print(destination.resolve())

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(self):

        print()

        print("=" * 70)

        print("EXPORT SUMMARY")

        print("=" * 70)

        print("Original :", self.output_path)

        print("Web      :", self.output_path.parent / "canopy_prediction_web.tif")

        print("CRS      :", self.reference.crs)

        print("Size     :", self.reference.width, "x", self.reference.height)

        print("=" * 70)