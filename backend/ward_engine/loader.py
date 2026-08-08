"""
==========================================================
CanopyAI
Ward Engine
Loader
==========================================================
"""

from pathlib import Path

import geopandas as gpd
import rasterio


class WardLoader:

    def __init__(self):

        self.data_dir = Path("data")

        self.output_dir = Path("outputs")

        self.wards = None

        self.impact = None

    # =====================================================
    # LOAD WARD BOUNDARIES
    # =====================================================

    def load_wards(self):

        files = list(self.data_dir.glob("*.geojson"))

        if len(files) == 0:

            raise FileNotFoundError(
                "Ward GeoJSON not found."
            )

        path = files[0]

        self.wards = gpd.read_file(path)

        print()
        print("=" * 70)
        print("WARD BOUNDARIES LOADED")
        print("=" * 70)
        print(f"File   : {path.name}")
        print(f"Wards  : {len(self.wards)}")
        print(f"CRS    : {self.wards.crs}")

        return self.wards

    # =====================================================
    # LOAD IMPACT SCORE
    # =====================================================

    def load_impact(self):

        path = self.output_dir / "impact_score.tif"

        if not path.exists():

            raise FileNotFoundError(
                "impact_score.tif not found."
            )

        self.impact = rasterio.open(path)

        print()
        print("=" * 70)
        print("IMPACT SCORE LOADED")
        print("=" * 70)
        print(f"Width  : {self.impact.width}")
        print(f"Height : {self.impact.height}")
        print(f"CRS    : {self.impact.crs}")

        return self.impact

    # =====================================================
    # REPROJECT WARDS
    # =====================================================

    def reproject_wards(self):

        if self.wards.crs != self.impact.crs:

            print()
            print("=" * 70)
            print("REPROJECTING WARD BOUNDARIES")
            print("=" * 70)

            print(f"From : {self.wards.crs}")
            print(f"To   : {self.impact.crs}")

            self.wards = self.wards.to_crs(
                self.impact.crs
            )

            print("✓ Reprojection Successful")

        else:

            print()
            print("Ward CRS already matches raster CRS.")

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(self):

        print()
        print("=" * 70)
        print("WARD ENGINE DATA READY")
        print("=" * 70)

        print(f"Total Wards : {len(self.wards)}")
        print(f"Raster Size : {self.impact.width} x {self.impact.height}")
        print(f"Raster CRS  : {self.impact.crs}")
        print(f"Ward CRS    : {self.wards.crs}")

    # =====================================================
    # LOAD EVERYTHING
    # =====================================================

    def load_all(self):

        self.load_wards()

        self.load_impact()

        self.reproject_wards()

        self.summary()

        return {

            "wards": self.wards,

            "impact": self.impact

        }