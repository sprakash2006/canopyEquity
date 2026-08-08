"""
==========================================================
CanopyAI
GeoTIFF Exporter
==========================================================
"""

from pathlib import Path

import rasterio
import numpy as np


class GeoTIFFExporter:

    def __init__(self, reference_dataset):

        self.reference = reference_dataset

        self.output_dir = Path("outputs")

        self.output_dir.mkdir(exist_ok=True)

    # =====================================================
    # EXPORT SINGLE BAND
    # =====================================================

    def export(self, image, filename, dtype):

        path = self.output_dir / filename

        profile = self.reference.profile.copy()

        profile.update(

            dtype=dtype,

            count=1,

            compress="lzw"

        )

        with rasterio.open(

            path,

            "w",

            **profile

        ) as dst:

            dst.write(

                image.astype(dtype),

                1

            )

        print(f"Saved : {path}")

    # =====================================================
    # EXPORT EVERYTHING
    # =====================================================

    def export_all(self, rasters):

        print()

        print("=" * 70)

        print("EXPORTING RESULTS")

        print("=" * 70)

        self.export(

            rasters["impact_score"],

            "impact_score.tif",

            np.float32

        )

        self.export(

            rasters["impact_class"],

            "impact_class.tif",

            np.uint8

        )

        self.export(

            rasters["benefit"],

            "benefit.tif",

            np.float32

        )

        self.export(

            rasters["plantability"],

            "plantability.tif",

            np.float32

        )

        self.export(

            rasters["canopy_deficit"],

            "canopy_deficit.tif",

            np.float32

        )

        print()

        print("=" * 70)

        print("ALL FILES EXPORTED")

        print("=" * 70)