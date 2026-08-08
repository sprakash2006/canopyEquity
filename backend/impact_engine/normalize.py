"""
==========================================================
CanopyAI
Normalization Engine
==========================================================
"""

import numpy as np


class Normalizer:

    def __init__(self):
        pass

    # =====================================================
    # Percentile Normalization
    # =====================================================

    @staticmethod
    def percentile_normalize(image):

        image = image.astype(np.float32)

        valid = image[np.isfinite(image)]

        if len(valid) == 0:
            return np.zeros_like(image)

        p2 = np.percentile(valid, 2)
        p98 = np.percentile(valid, 98)

        image = np.clip(image, p2, p98)

        normalized = (image - p2) / (p98 - p2 + 1e-8)

        normalized = np.clip(normalized, 0, 1)

        return normalized

    # =====================================================
    # Inverse Normalize
    # =====================================================

    @staticmethod
    def inverse_percentile(image):

        return 1.0 - image

    # =====================================================
    # Normalize All Layers
    # =====================================================

    def normalize(self, rasters):

        normalized = {}

        # NDVI
        normalized["ndvi"] = self.percentile_normalize(
            rasters["ndvi"]
        )

        # LST
        normalized["lst"] = self.percentile_normalize(
            rasters["lst"]
        )

        # Rainfall
        normalized["rainfall"] = self.percentile_normalize(
            rasters["rainfall"]
        )

        # Vulnerability
        normalized["vulnerability"] = self.percentile_normalize(
            rasters["vulnerability"]
        )

        # Landcover stays categorical
        normalized["landcover"] = rasters["landcover"]

        return normalized

    # =====================================================
    # Statistics
    # =====================================================

    @staticmethod
    def statistics(rasters):

        print("\n" + "=" * 70)
        print("NORMALIZED DATA")
        print("=" * 70)

        for name, img in rasters.items():

            if name == "landcover":

                continue

            print(
                f"{name:15s}"
                f" Min={np.nanmin(img):.3f}"
                f" Max={np.nanmax(img):.3f}"
                f" Mean={np.nanmean(img):.3f}"
            )

        print("=" * 70)