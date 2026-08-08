"""
==========================================================
CanopyAI
Impact Engine
GeoTIFF Loader
==========================================================
"""

from pathlib import Path
import rasterio


class RasterLoader:

    def __init__(self, data_dir):

        self.data_dir = Path(data_dir)

        self.datasets = {}

    # =====================================================
    # LOAD SINGLE RASTER
    # =====================================================

    def load(self, filename):

        path = self.data_dir / filename

        if not path.exists():

            raise FileNotFoundError(
                f"{filename} not found at {path}"
            )

        raster = rasterio.open(path)

        print(f"Loaded : {filename}")
        print(f"Shape  : {raster.height} x {raster.width}")
        print(f"Bands  : {raster.count}")
        print(f"CRS    : {raster.crs}")
        print("-" * 60)

        return raster

    # =====================================================
    # LOAD ALL RASTERS
    # =====================================================

    def load_all(self):

        self.datasets["sentinel"] = self.load(
            "13-band_satellite.tif"
        )

        self.datasets["landcover"] = self.load(
            "mcd_worldcover_4cls.tif"
        )

        self.datasets["ndvi"] = self.load(
            "mcd_ndvi_2022_2023.tif"
        )

        self.datasets["lst"] = self.load(
            "mcd_lst_2022_2023.tif"
        )

        self.datasets["rainfall"] = self.load(
            "mcd_rainfall_2022_2023.tif"
        )

        self.datasets["vulnerability"] = self.load(
            "mcd_vulnerability_score.tif"
        )

        return self.datasets

    # =====================================================
    # PRINT SUMMARY
    # =====================================================

    def summary(self):

        print("\n" + "=" * 70)
        print("LOADED DATASETS")
        print("=" * 70)

        for name, raster in self.datasets.items():

            print(f"{name.upper()}")

            print(f"Shape : {raster.height} x {raster.width}")

            print(f"Bands : {raster.count}")

            print(f"CRS   : {raster.crs}")

            print("-" * 70)