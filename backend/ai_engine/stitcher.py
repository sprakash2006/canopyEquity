import numpy as np


class Stitcher:

    def __init__(
        self,
        predictions,
        image_height,
        image_width,
        num_classes=4
    ):

        self.predictions = predictions

        self.height = image_height
        self.width = image_width

        self.num_classes = num_classes

        self.final_mask = None
        self.confidence_map = None

    # =====================================================
    # STITCH PROBABILITIES
    # =====================================================

    def stitch(self):

        print()
        print("=" * 70)
        print("STITCHING PIXEL-LEVEL PREDICTIONS")
        print("=" * 70)

        probability_sum = np.zeros(
            (
                self.num_classes,
                self.height,
                self.width
            ),
            dtype=np.float32
        )

        weight_sum = np.zeros(
            (
                self.height,
                self.width
            ),
            dtype=np.float32
        )

        # =================================================
        # PROCESS EVERY TILE
        # =================================================

        for index, tile in enumerate(
            self.predictions
        ):

            x = int(tile["x"])
            y = int(tile["y"])

            probs = np.asarray(
                tile["probs"],
                dtype=np.float32
            )

            # -------------------------------------------------
            # Shape:
            #
            # (classes, height, width)
            # -------------------------------------------------

            if probs.ndim != 3:

                raise ValueError(
                    f"Invalid probability shape: "
                    f"{probs.shape}"
                )

            if probs.shape[0] != self.num_classes:

                raise ValueError(
                    f"Expected "
                    f"{self.num_classes} classes, "
                    f"got {probs.shape[0]}"
                )

            tile_height = int(
                tile.get(
                    "valid_height",
                    probs.shape[1]
                )
            )

            tile_width = int(
                tile.get(
                    "valid_width",
                    probs.shape[2]
                )
            )

            # -------------------------------------------------
            # Never go outside image
            # -------------------------------------------------

            tile_height = min(
                tile_height,
                probs.shape[1],
                self.height - y
            )

            tile_width = min(
                tile_width,
                probs.shape[2],
                self.width - x
            )

            if tile_height <= 0:
                continue

            if tile_width <= 0:
                continue

            # -------------------------------------------------
            # Crop probability tile
            # -------------------------------------------------

            probs = probs[
                :,
                :tile_height,
                :tile_width
            ]

            # -------------------------------------------------
            # Add probabilities
            # -------------------------------------------------

            probability_sum[
                :,
                y:y + tile_height,
                x:x + tile_width
            ] += probs

            # -------------------------------------------------
            # Add weight
            # -------------------------------------------------

            weight_sum[
                y:y + tile_height,
                x:x + tile_width
            ] += 1.0

        # =====================================================
        # FIND VALID PIXELS
        # =====================================================

        valid = weight_sum > 0

        # =====================================================
        # AVERAGE OVERLAPPING PREDICTIONS
        # =====================================================

        average_probabilities = np.zeros_like(
            probability_sum
        )

        for cls in range(
            self.num_classes
        ):

            average_probabilities[
                cls
            ][valid] = (

                probability_sum[
                    cls
                ][valid]

                /

                weight_sum[valid]
            )

        # =====================================================
        # FINAL PIXEL CLASS
        # =====================================================

        self.final_mask = np.argmax(
            average_probabilities,
            axis=0
        ).astype(np.uint8)

        # =====================================================
        # CONFIDENCE
        # =====================================================

        self.confidence_map = np.max(
            average_probabilities,
            axis=0
        ).astype(np.float32)

        # -----------------------------------------------------
        # Pixels with no prediction
        # -----------------------------------------------------

        self.final_mask[
            ~valid
        ] = 0

        self.confidence_map[
            ~valid
        ] = 0.0

        # =====================================================
        # REPORT
        # =====================================================

        print(
            "✓ Probability stitching completed"
        )

        print(
            "Final Shape :",
            self.final_mask.shape
        )

        print(
            "Valid Pixels :",
            np.count_nonzero(valid)
        )

        print(
            "Total Pixels :",
            self.height * self.width
        )

        coverage = (
            np.count_nonzero(valid)
            /
            (self.height * self.width)
        ) * 100

        print(
            f"Coverage : {coverage:.2f}%"
        )

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

            print(
                "No stitched mask available."
            )

            return

        unique, counts = np.unique(
            self.final_mask,
            return_counts=True
        )

        print(
            "Output Shape :",
            self.final_mask.shape
        )

        print()

        for cls, count in zip(
            unique,
            counts
        ):

            percentage = (
                count /
                self.final_mask.size
            ) * 100

            print(
                f"Class {cls}: "
                f"{count:,} pixels "
                f"({percentage:.2f}%)"
            )

        if self.confidence_map is not None:

            valid_confidence = (
                self.confidence_map[
                    self.confidence_map > 0
                ]
            )

            if len(
                valid_confidence
            ) > 0:

                print()

                print(
                    "Average Confidence :",
                    f"{valid_confidence.mean():.4f}"
                )

                print(
                    "Minimum Confidence :",
                    f"{valid_confidence.min():.4f}"
                )

                print(
                    "Maximum Confidence :",
                    f"{valid_confidence.max():.4f}"
                )

        print("=" * 70)
# """
# ==========================================================
# CanopyAI
# AI Engine
# Prediction Stitcher
# ==========================================================
# """

# import numpy as np


# class Stitcher:

#     def __init__(
#         self,
#         predictions,
#         image_height,
#         image_width,
#         tile_size=256
#     ):

#         self.predictions = predictions
#         self.height = image_height
#         self.width = image_width
#         self.tile_size = tile_size

#         self.final_mask = None

#     # =====================================================
#     # STITCH TILES
#     # =====================================================

#     def stitch(self):

#         print()
#         print("=" * 70)
#         print("STITCHING PREDICTION TILES")
#         print("=" * 70)

#         self.final_mask = np.zeros(
#             (self.height, self.width),
#             dtype=np.uint8
#         )

#         for tile in self.predictions:

#             x = tile["x"]
#             y = tile["y"]

#             mask = tile["mask"]

#             # ------------------------------------------
#             # Crop edge tiles
#             # ------------------------------------------

#             h = min(self.tile_size, self.height - y)
#             w = min(self.tile_size, self.width - x)

#             self.final_mask[
#                 y:y+h,
#                 x:x+w
#             ] = mask[:h, :w]

#         print("✓ Stitching Completed")

#         return self.final_mask

#     # =====================================================
#     # SUMMARY
#     # =====================================================

#     def summary(self):

#         print()
#         print("=" * 70)
#         print("STITCHING SUMMARY")
#         print("=" * 70)

#         if self.final_mask is None:

#             print("No stitched mask available.")
#             return

#         print("Output Shape :", self.final_mask.shape)

#         unique, counts = np.unique(
#             self.final_mask,
#             return_counts=True
#         )

#         print()

#         print("Pixel Counts")

#         for cls, cnt in zip(unique, counts):

#             print(f"Class {cls} : {cnt}")

#         print()

#         print("Classes :", unique.tolist())

#         print("=" * 70)