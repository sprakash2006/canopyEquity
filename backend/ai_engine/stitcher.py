"""
==========================================================
CanopyAI
AI Engine
Prediction Stitcher
==========================================================
"""

import numpy as np


class Stitcher:

    def __init__(
        self,
        predictions,
        image_height,
        image_width,
        tile_size=256
    ):

        self.predictions = predictions
        self.height = image_height
        self.width = image_width
        self.tile_size = tile_size

        self.final_mask = None

    # =====================================================
    # STITCH TILES
    # =====================================================

    def stitch(self):

        print()
        print("=" * 70)
        print("STITCHING PREDICTION TILES")
        print("=" * 70)

        self.final_mask = np.zeros(
            (self.height, self.width),
            dtype=np.uint8
        )

        for tile in self.predictions:

            x = tile["x"]
            y = tile["y"]

            mask = tile["mask"]

            # ------------------------------------------
            # Crop edge tiles
            # ------------------------------------------

            h = min(self.tile_size, self.height - y)
            w = min(self.tile_size, self.width - x)

            self.final_mask[
                y:y+h,
                x:x+w
            ] = mask[:h, :w]

        print("✓ Stitching Completed")

        return self.final_mask

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(self):

        print()
        print("=" * 70)
        print("STITCHING SUMMARY")
        print("=" * 70)

        if self.final_mask is None:

            print("No stitched mask available.")
            return

        print("Output Shape :", self.final_mask.shape)

        unique, counts = np.unique(
            self.final_mask,
            return_counts=True
        )

        print()

        print("Pixel Counts")

        for cls, cnt in zip(unique, counts):

            print(f"Class {cls} : {cnt}")

        print()

        print("Classes :", unique.tolist())

        print("=" * 70)