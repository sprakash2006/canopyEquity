"""
==========================================================
CanopyAI
Ward Engine
Zonal Statistics
==========================================================
"""

from pathlib import Path

import pandas as pd
from rasterstats import zonal_stats


class ZonalStatistics:

    def __init__(self, wards, raster):

        self.wards = wards
        self.raster = raster
        self.results = None

    # =====================================================
    # COMPUTE ZONAL STATS
    # =====================================================

    def compute(self):

        print()
        print("=" * 70)
        print("COMPUTING ZONAL STATISTICS")
        print("=" * 70)

        stats = zonal_stats(

            self.wards,
            self.raster.name,

            stats=[
                "min",
                "max",
                "mean",
                "median",
                "std",
                "count"
            ],

            nodata=self.raster.nodata,

            geojson_out=False

        )

        df = self.wards.copy()

        df["Impact_Min"] = [s["min"] for s in stats]
        df["Impact_Max"] = [s["max"] for s in stats]
        df["Impact_Mean"] = [s["mean"] for s in stats]
        df["Impact_Median"] = [s["median"] for s in stats]
        df["Impact_STD"] = [s["std"] for s in stats]
        df["Pixel_Count"] = [s["count"] for s in stats]

        self.results = df

        print("✓ Zonal Statistics Computed")

        return self.results

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(self):

        print()
        print("=" * 70)
        print("WARD STATISTICS SUMMARY")
        print("=" * 70)

        print(f"Total Wards : {len(self.results)}")

        print(
            "Average Impact Score :",
            round(
                self.results["Impact_Mean"].mean(),
                2
            )
        )

        print(
            "Highest Impact Score :",
            round(
                self.results["Impact_Max"].max(),
                2
            )
        )

        print(
            "Lowest Impact Score :",
            round(
                self.results["Impact_Min"].min(),
                2
            )
        )

        print("=" * 70)