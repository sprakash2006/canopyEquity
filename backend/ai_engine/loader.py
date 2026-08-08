"""
==========================================================
CanopyAI
AI Engine
SegFormer Model Loader
==========================================================
"""

from pathlib import Path

import torch

from src.models.segformer import CanopySegFormer


class ModelLoader:

    def __init__(self):

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        self.checkpoint = Path(
            "checkpoints/best_model.pth"
        )

        self.model = None

    # =====================================================
    # LOAD MODEL
    # =====================================================

    def load(self):

        print()
        print("=" * 70)
        print("LOADING SEGFORMER MODEL")
        print("=" * 70)

        if not self.checkpoint.exists():
            raise FileNotFoundError(
                f"Checkpoint not found : {self.checkpoint}"
            )

        # --------------------------------------------------
        # Build architecture
        # --------------------------------------------------

        self.model = CanopySegFormer(
            num_classes=4
        )

        # --------------------------------------------------
        # Load checkpoint
        # --------------------------------------------------

        checkpoint = torch.load(
            self.checkpoint,
            map_location="cpu"
        )

        missing_keys, unexpected_keys = self.model.load_state_dict(
            checkpoint,
            strict=False
        )

        # --------------------------------------------------
        # Move to device
        # --------------------------------------------------

        self.model.to(self.device)

        self.model.eval()

        print("✓ Model Loaded Successfully")

        print()
        print(f"Device       : {self.device}")
        print(f"Checkpoint   : {self.checkpoint}")
        print("Architecture : SegFormer-B0")
        print("Input Bands  : 13")
        print("Classes      : 4")

        print()
        print("=" * 70)
        print("CHECKPOINT REPORT")
        print("=" * 70)

        print(
            f"Missing Keys    : {len(missing_keys)}"
        )

        print(
            f"Unexpected Keys : {len(unexpected_keys)}"
        )

        # --------------------------------------------
        # Print missing keys (max 10)
        # --------------------------------------------

        if len(missing_keys) > 0:

            print("\nMissing Parameters:")

            for key in missing_keys[:10]:
                print(" -", key)

            if len(missing_keys) > 10:
                print(" ...")

        # --------------------------------------------
        # Print unexpected keys (max 10)
        # --------------------------------------------

        if len(unexpected_keys) > 0:

            print("\nUnexpected Parameters:")

            for key in unexpected_keys[:10]:
                print(" -", key)

            if len(unexpected_keys) > 10:
                print(" ...")

        print("=" * 70)

        return self.model

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(self):

        print()
        print("=" * 70)
        print("MODEL SUMMARY")
        print("=" * 70)

        print(f"Model  : {self.model.__class__.__name__}")
        print(f"Device : {self.device}")
        print(f"Mode   : {'Evaluation' if not self.model.training else 'Training'}")

        total_params = sum(
            p.numel() for p in self.model.parameters()
        )

        trainable_params = sum(
            p.numel()
            for p in self.model.parameters()
            if p.requires_grad
        )

        print(f"Total Parameters     : {total_params:,}")
        print(f"Trainable Parameters : {trainable_params:,}")

        print("=" * 70)