"""
==========================================================
CanopyAI
Canopy Analysis Engine
==========================================================
"""

import numpy as np
from scipy.ndimage import uniform_filter


class CanopyAnalyzer:

    """
    Computes:

    1. Local Canopy Fraction
    2. Canopy Deficit
    """

    def __init__(self):

        # WorldCover class id for trees
        self.CANOPY_CLASS = 1

        # 51x51 moving window
        self.window = 51

    # =====================================================
    # LOCAL CANOPY FRACTION
    # =====================================================

    def canopy_fraction(self, landcover):

        canopy = (

            landcover == self.CANOPY_CLASS

        ).astype(np.float32)

        fraction = uniform_filter(

            canopy,

            size=self.window,

            mode="nearest"

        )

        return fraction

    # =====================================================
    # CANOPY DEFICIT
    # =====================================================

    @staticmethod
    def canopy_deficit(fraction):

        deficit = 1.0 - fraction

        deficit = np.clip(

            deficit,

            0,

            1

        )

        return deficit

    # =====================================================
    # MAIN
    # =====================================================

    def compute(self, rasters):

        canopy_fraction = self.canopy_fraction(

            rasters["landcover"]

        )

        canopy_deficit = self.canopy_deficit(

            canopy_fraction

        )

        rasters["canopy_fraction"] = canopy_fraction

        rasters["canopy_deficit"] = canopy_deficit

        return rasters

    # =====================================================
    # STATS
    # =====================================================

    @staticmethod
    def statistics(rasters):

        print()

        print("=" * 70)

        print("CANOPY ANALYSIS")

        print("=" * 70)

        for name in [

            "canopy_fraction",

            "canopy_deficit"

        ]:

            img = rasters[name]

            print(

                f"{name:20s}"

                f" Min={np.nanmin(img):.3f}"

                f" Max={np.nanmax(img):.3f}"

                f" Mean={np.nanmean(img):.3f}"

            )

        print("=" * 70)