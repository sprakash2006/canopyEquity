"""
==========================================================
CanopyAI
Recommendation Engine
Tree Allocation Engine
==========================================================
"""

import numpy as np


class TreeAllocator:

    def __init__(self, wards):

        self.wards = wards

    # =====================================================
    # NORMALIZATION
    # =====================================================

    @staticmethod
    def normalize(series):

        mn = series.min()
        mx = series.max()

        if mx == mn:
            return np.ones(len(series))

        return (series - mn) / (mx - mn)

    # =====================================================
    # TREE ALLOCATION
    # =====================================================

    def allocate(self):

        print()
        print("=" * 70)
        print("TREE ALLOCATION ENGINE")
        print("=" * 70)

        impact = self.normalize(

            self.wards["Composite_Score"]

        )

        population = self.normalize(

            self.wards["Pixel_Count"]

        )

        trees = (

            2000
            +
            impact * 12000
            +
            population * 6000

        )

        self.wards["Recommended_Trees"] = (

            trees.round().astype(int)

        )

        print("✓ Tree Allocation Completed")

        return self.wards

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(self):

        print()

        print("=" * 70)

        print("TREE ALLOCATION SUMMARY")

        print("=" * 70)

        print(

            "Total Trees :",

            f"{self.wards['Recommended_Trees'].sum():,}"

        )

        print(

            "Average Trees/Ward :",

            int(

                self.wards["Recommended_Trees"].mean()

            )

        )

        print(

            "Maximum Trees :",

            int(

                self.wards["Recommended_Trees"].max()

            )

        )

        print(

            "Minimum Trees :",

            int(

                self.wards["Recommended_Trees"].min()

            )

        )

        print("=" * 70)