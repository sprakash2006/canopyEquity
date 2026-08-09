import numpy as np
import torch
import torch.nn.functional as F


class Predictor:

    def __init__(
        self,
        model,
        device,
        tiles,
        batch_size=8,
        num_classes=4
    ):

        self.model = model
        self.device = device
        self.tiles = tiles
        self.batch_size = batch_size
        self.num_classes = num_classes

        self.predictions = []

    # =====================================================
    # RUN INFERENCE
    # =====================================================

    def predict(self):

        print()
        print("=" * 70)
        print("RUNNING SEGFORMER PREDICTION")
        print("=" * 70)

        self.predictions = []

        total = len(self.tiles)

        debug_done = False

        self.model.eval()

        with torch.no_grad():

            for start in range(
                0,
                total,
                self.batch_size
            ):

                end = min(
                    start + self.batch_size,
                    total
                )

                batch_tiles = self.tiles[
                    start:end
                ]

                # =================================================
                # CREATE BATCH
                # =================================================

                images = np.stack(
                    [
                        tile["image"]
                        for tile in batch_tiles
                    ],
                    axis=0
                )

                images = torch.from_numpy(
                    images
                ).float().to(self.device)

                # =================================================
                # DEBUG INPUT
                # =================================================

                if not debug_done:

                    print()
                    print(
                        "INPUT BATCH"
                    )

                    print(
                        "Shape :",
                        tuple(images.shape)
                    )

                    print(
                        "Min   :",
                        images.min().item()
                    )

                    print(
                        "Max   :",
                        images.max().item()
                    )

                    print(
                        "Mean  :",
                        images.mean().item()
                    )

                    print(
                        "Std   :",
                        images.std().item()
                    )

                # =================================================
                # SEGFORMER
                # =================================================

                output = self.model(
                    images
                )

                # =================================================
                # HANDLE DIFFERENT MODEL OUTPUT FORMATS
                # =================================================

                if hasattr(
                    output,
                    "logits"
                ):

                    logits = output.logits

                elif isinstance(
                    output,
                    dict
                ) and "logits" in output:

                    logits = output["logits"]

                elif isinstance(
                    output,
                    tuple
                ):

                    logits = output[0]

                else:

                    logits = output

                # =================================================
                # DEBUG LOGITS
                # =================================================

                if not debug_done:

                    print()
                    print(
                        "SEGFORMER OUTPUT"
                    )

                    print(
                        "Logits Shape :",
                        tuple(logits.shape)
                    )

                    print(
                        "Logits Min   :",
                        logits.min().item()
                    )

                    print(
                        "Logits Max   :",
                        logits.max().item()
                    )

                    print(
                        "Logits Mean  :",
                        logits.mean().item()
                    )

                # =================================================
                # RESIZE TO TILE SIZE
                # =================================================

                logits = F.interpolate(
                    logits,
                    size=(
                        256,
                        256
                    ),
                    mode="bilinear",
                    align_corners=False
                )

                # =================================================
                # SOFTMAX
                #
                # Converts logits into class probabilities.
                #
                # Shape:
                #
                # [B, 4, 256, 256]
                #
                # =================================================

                probabilities = torch.softmax(
                    logits,
                    dim=1
                )

                # =================================================
                # CHECK NUMBER OF CLASSES
                # =================================================

                if probabilities.shape[1] != self.num_classes:

                    raise ValueError(
                        f"Expected "
                        f"{self.num_classes} classes, "
                        f"but model returned "
                        f"{probabilities.shape[1]}"
                    )

                # =================================================
                # DEBUG PROBABILITIES
                # =================================================

                if not debug_done:

                    print()
                    print(
                        "CLASS PROBABILITIES"
                    )

                    print(
                        "Shape :",
                        tuple(
                            probabilities.shape
                        )
                    )

                    for cls in range(
                        self.num_classes
                    ):

                        class_mean = (
                            probabilities[
                                :, cls
                            ].mean().item()
                        )

                        print(
                            f"Class {cls} "
                            f"Mean Probability : "
                            f"{class_mean:.6f}"
                        )

                # =================================================
                # FINAL CLASS FOR DEBUG ONLY
                # =================================================

                masks = torch.argmax(
                    probabilities,
                    dim=1
                )

                if not debug_done:

                    print()
                    print(
                        "FIRST BATCH CLASS DISTRIBUTION"
                    )

                    unique, counts = np.unique(
                        masks.cpu().numpy(),
                        return_counts=True
                    )

                    for cls, count in zip(
                        unique,
                        counts
                    ):

                        percentage = (
                            count /
                            masks.numel()
                        ) * 100

                        print(
                            f"Class {cls}: "
                            f"{count:,} pixels "
                            f"({percentage:.2f}%)"
                        )

                # =================================================
                # SAVE PROBABILITIES
                # =================================================

                probabilities_np = (
                    probabilities
                    .cpu()
                    .numpy()
                    .astype(np.float32)
                )

                # =================================================
                # SAVE EACH TILE
                # =================================================

                for tile, probs in zip(
                    batch_tiles,
                    probabilities_np
                ):

                    self.predictions.append({

                        "probs": probs,

                        "x": tile["x"],

                        "y": tile["y"],

                        "valid_height": tile.get(
                            "valid_height",
                            256
                        ),

                        "valid_width": tile.get(
                            "valid_width",
                            256
                        ),

                        "tile_size": tile.get(
                            "tile_size",
                            256
                        )

                    })

                debug_done = True

                print(
                    f"\rProcessed "
                    f"{end}/{total}",
                    end=""
                )

        print()

        print(
            "✓ Prediction Completed"
        )

        print(
            f"✓ Predictions Saved : "
            f"{len(self.predictions)}"
        )

        return self.predictions

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(self):

        print()
        print("=" * 70)
        print("PREDICTION SUMMARY")
        print("=" * 70)

        print(
            f"Total Predictions : "
            f"{len(self.predictions)}"
        )

        if len(self.predictions) == 0:

            print(
                "No predictions available."
            )

            return

        sample = self.predictions[0]

        print(
            "Probability Shape :",
            sample["probs"].shape
        )

        print(
            "Expected Shape    :",
            (
                self.num_classes,
                256,
                256
            )
        )

        print(
            "First Tile X      :",
            sample["x"]
        )

        print(
            "First Tile Y      :",
            sample["y"]
        )

        print("=" * 70)
# """
# ==========================================================
# CanopyAI
# AI Engine
# SegFormer Predictor
# ==========================================================
# """

# import numpy as np
# import torch
# import torch.nn.functional as F


# class Predictor:

#     def __init__(
#         self,
#         model,
#         device,
#         tiles,
#         batch_size=8
#     ):

#         self.model = model
#         self.device = device
#         self.tiles = tiles
#         self.batch_size = batch_size
#         self.predictions = []

#     # =====================================================
#     # RUN INFERENCE
#     # =====================================================

#     def predict(self):

#         print()
#         print("=" * 70)
#         print("RUNNING SEGFORMER PREDICTION")
#         print("=" * 70)

#         self.predictions = []

#         total = len(self.tiles)

#         debug_done = False

#         with torch.no_grad():

#             for start in range(0, total, self.batch_size):

#                 end = min(start + self.batch_size, total)

#                 batch_tiles = self.tiles[start:end]

#                 images = np.stack(
#                     [tile["image"] for tile in batch_tiles],
#                     axis=0
#                 )

#                 images = torch.from_numpy(images).float().to(self.device)

#                 # ==========================================
#                 # PRINT EVERY BATCH STATS
#                 # ==========================================

#                 print(
#                     f"Batch {start//self.batch_size:03d} | "
#                     f"Min={images.min().item():.4f} "
#                     f"Max={images.max().item():.4f} "
#                     f"Mean={images.mean().item():.6f} "
#                     f"NonZero={(images!=0).sum().item()}"
#                 )

#                 # ==========================================
#                 # DEBUG FIRST NON-EMPTY BATCH ONLY
#                 # ==========================================

#                 if (not debug_done) and images.max().item() > 0:

#                     print()
#                     print("=" * 70)
#                     print("FIRST NON-EMPTY INPUT BATCH")
#                     print("=" * 70)

#                     print("Batch Index :", start // self.batch_size)
#                     print("Shape       :", images.shape)
#                     print("Min         :", images.min().item())
#                     print("Max         :", images.max().item())
#                     print("Mean        :", images.mean().item())
#                     print("Std         :", images.std().item())

#                     for b in range(images.shape[1]):
#                         print(
#                             f"Band {b+1:02d} Mean : "
#                             f"{images[:, b].mean().item():.6f}"
#                         )

#                 # ==========================================
#                 # MODEL
#                 # ==========================================

#                 logits = self.model(images)

#                 if (not debug_done) and images.max().item() > 0:

#                     print()
#                     print("=" * 70)
#                     print("MODEL LOGITS")
#                     print("=" * 70)

#                     print("Shape :", logits.shape)
#                     print("Min   :", logits.min().item())
#                     print("Max   :", logits.max().item())
#                     print("Mean  :", logits.mean().item())

#                     probs = torch.softmax(logits, dim=1)

#                     print()
#                     print("Mean Probability Per Class")

#                     for cls in range(probs.shape[1]):
#                         print(
#                             f"Class {cls}: "
#                             f"{probs[:, cls].mean().item():.6f}"
#                         )

#                 logits = F.interpolate(
#                     logits,
#                     size=(256, 256),
#                     mode="bilinear",
#                     align_corners=False
#                 )

#                 masks = torch.argmax(logits, dim=1)

#                 if (not debug_done) and images.max().item() > 0:

#                     print()
#                     print("=" * 70)
#                     print("FIRST NON-EMPTY BATCH PREDICTION")
#                     print("=" * 70)

#                     unique, counts = np.unique(
#                         masks.cpu().numpy(),
#                         return_counts=True
#                     )

#                     for u, c in zip(unique, counts):
#                         print(f"Class {u}: {c}")

#                     debug_done = True

#                 masks = masks.cpu().numpy().astype(np.uint8)

#                 for tile, mask in zip(batch_tiles, masks):

#                     self.predictions.append({

#                         "mask": mask,

#                         "x": tile["x"],

#                         "y": tile["y"]

#                     })

#                 print(
#                     f"\rProcessed {end}/{total}",
#                     end=""
#                 )

#         print()
#         print("✓ Prediction Completed")

#         return self.predictions

#     # =====================================================
#     # SUMMARY
#     # =====================================================

#     def summary(self):

#         print()
#         print("=" * 70)
#         print("PREDICTION SUMMARY")
#         print("=" * 70)

#         print(f"Total Predictions : {len(self.predictions)}")

#         if len(self.predictions) == 0:
#             return

#         # Check ALL predictions instead of only the first tile
#         all_classes = set()

#         for pred in self.predictions:
#             all_classes.update(np.unique(pred["mask"]).tolist())

#         print(f"Classes Found : {sorted(all_classes)}")
#         print(f"Total Tiles   : {len(self.predictions)}")

#         print("=" * 70)