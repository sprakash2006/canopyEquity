import random
import numpy as np
import torch

from torch.utils.data import DataLoader
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR

from src.configs.config import *

from src.datasets.canopy_dataset import CanopyDataset
from src.models.segformer import CanopySegFormer

from src.training.losses import SegmentationLoss
from src.training.trainer import Trainer
# =====================================================
# RANDOM SEED
# =====================================================

def set_seed(seed):

    random.seed(seed)

    np.random.seed(seed)

    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


    # =====================================================
# MAIN
# =====================================================

def main():

    print("=" * 60)
    print("CANOPY AI TRAINING")
    print("=" * 60)

    set_seed(SEED)

    print(f"Device : {DEVICE}")

    # -------------------------------------------------
    # DATASET
    # -------------------------------------------------

    train_dataset = CanopyDataset(
        image_dir=IMAGE_DIR,
        mask_dir=MASK_DIR
    )

    val_dataset = CanopyDataset(
        image_dir="dataset/val/images",
        mask_dir="dataset/val/masks"
    )

    print(f"Training Images   : {len(train_dataset)}")
    print(f"Validation Images : {len(val_dataset)}") 

        # -------------------------------------------------
    # DATALOADER
    # -------------------------------------------------

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0,
        pin_memory=True
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0,
        pin_memory=True
    )   
        # -------------------------------------------------
    # MODEL
    # -------------------------------------------------

    model = CanopySegFormer().to(DEVICE)

    criterion = SegmentationLoss()

    optimizer = AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY
    )

    scheduler = CosineAnnealingLR(
        optimizer,
        T_max=EPOCHS
    )

    trainer = Trainer(
        model=model,
        criterion=criterion,
        optimizer=optimizer,
        device=DEVICE,
        num_classes=NUM_CLASSES
    )

    print("Everything Initialized Successfully!")

        # =====================================================
    # TRAINING LOOP
    # =====================================================

    best_loss = float("inf")

    history = {
        "train_loss": [],
        "val_loss": [],
        "train_dice": [],
        "val_dice": [],
        "train_iou": [],
        "val_iou": [],
        "train_acc": [],
        "val_acc": []
    }

    print("\nStarting Training...\n")

    for epoch in range(EPOCHS):

        print("=" * 70)
        print(f"Epoch {epoch + 1}/{EPOCHS}")
        print("=" * 70)

        # -------------------------
        # Train
        # -------------------------

        train_metrics = trainer.train_epoch(train_loader)

        # -------------------------
        # Validation
        # -------------------------

        val_metrics = trainer.validate_epoch(val_loader)

        # -------------------------
        # Scheduler
        # -------------------------

        scheduler.step()

        # -------------------------
        # Save History
        # -------------------------

        history["train_loss"].append(train_metrics["loss"])
        history["val_loss"].append(val_metrics["loss"])

        history["train_acc"].append(train_metrics["pixel_accuracy"])
        history["val_acc"].append(val_metrics["pixel_accuracy"])

        history["train_dice"].append(train_metrics["dice_score"])
        history["val_dice"].append(val_metrics["dice_score"])

        history["train_iou"].append(train_metrics["iou_score"])
        history["val_iou"].append(val_metrics["iou_score"])

        # -------------------------
        # Print Metrics
        # -------------------------

        print("\nTRAIN")

        print(f"Loss            : {train_metrics['loss']:.4f}")
        print(f"Pixel Accuracy  : {train_metrics['pixel_accuracy']:.4f}")
        print(f"Dice Score      : {train_metrics['dice_score']:.4f}")
        print(f"IoU Score       : {train_metrics['iou_score']:.4f}")

        print("\nVALIDATION")

        print(f"Loss            : {val_metrics['loss']:.4f}")
        print(f"Pixel Accuracy  : {val_metrics['pixel_accuracy']:.4f}")
        print(f"Dice Score      : {val_metrics['dice_score']:.4f}")
        print(f"IoU Score       : {val_metrics['iou_score']:.4f}")

        print(f"\nLearning Rate   : {optimizer.param_groups[0]['lr']:.8f}")

        # -------------------------
        # Save Best Model
        # -------------------------

        if val_metrics["loss"] < best_loss:

            best_loss = val_metrics["loss"]

            torch.save(
                model.state_dict(),
                BEST_MODEL
            )

            print("\n✅ Best Model Saved!")

        print()

            # =====================================================
    # TRAINING FINISHED
    # =====================================================

    print("\n" + "=" * 70)
    print("TRAINING COMPLETED")
    print("=" * 70)

    print(f"Best Validation Loss : {best_loss:.4f}")
    print(f"Best Model Saved At  : {BEST_MODEL}")

    print("\nFinal Training Metrics")
    print("-" * 70)

    print(f"Train Loss      : {history['train_loss'][-1]:.4f}")
    print(f"Validation Loss : {history['val_loss'][-1]:.4f}")

    print(f"Train Accuracy  : {history['train_acc'][-1]:.4f}")
    print(f"Validation Acc  : {history['val_acc'][-1]:.4f}")

    print(f"Train Dice      : {history['train_dice'][-1]:.4f}")
    print(f"Validation Dice : {history['val_dice'][-1]:.4f}")

    print(f"Train IoU       : {history['train_iou'][-1]:.4f}")
    print(f"Validation IoU  : {history['val_iou'][-1]:.4f}")

    print("=" * 70)


# =====================================================
# ENTRY POINT
# =====================================================

if __name__ == "__main__":
    main()
# import random
# import numpy as np
# import torch

# from torch.utils.data import DataLoader
# from torch.optim import AdamW
# from torch.optim.lr_scheduler import CosineAnnealingLR

# from src.configs.config import *

# from src.datasets.canopy_dataset import CanopyDataset
# from src.models.segformer import CanopySegFormer

# from training.losses import SegmentationLoss
# from src.training.trainer import Trainer


# # =====================================================
# # RANDOM SEED
# # =====================================================

# def set_seed(seed):

#     random.seed(seed)

#     np.random.seed(seed)

#     torch.manual_seed(seed)

#     torch.cuda.manual_seed_all(seed)


# # =====================================================
# # MAIN
# # =====================================================

# def main():

#     print("=" * 60)
#     print("CANOPY AI TRAINING")
#     print("=" * 60)

#     set_seed(SEED)

#     print(f"Device : {DEVICE}")

#     # -------------------------------------------------
#     # Dataset
#     # -------------------------------------------------

#     train_dataset = CanopyDataset(
#         image_dir=IMAGE_DIR,
#         mask_dir=MASK_DIR
#     )

#     val_dataset = CanopyDataset(
#         image_dir="dataset/val/images",
#         mask_dir="dataset/val/masks"
#     )

#     print(f"Training Images   : {len(train_dataset)}")
#     print(f"Validation Images : {len(val_dataset)}")

#     # -------------------------------------------------
#     # DataLoader
#     # -------------------------------------------------

#     train_loader = DataLoader(
#         train_dataset,
#         batch_size=BATCH_SIZE,
#         shuffle=True,
#         num_workers=0,
#         pin_memory=True
#     )

#     val_loader = DataLoader(
#         val_dataset,
#         batch_size=BATCH_SIZE,
#         shuffle=False,
#         num_workers=0,
#         pin_memory=True
#     )

#     # -------------------------------------------------
#     # Model
#     # -------------------------------------------------

#     print("\nLoading SegFormer...")

#     model = CanopySegFormer().to(DEVICE)

#     print("Model Loaded Successfully!")

#     # -------------------------------------------------
#     # Loss
#     # -------------------------------------------------

#     criterion = SegmentationLoss()

#     # -------------------------------------------------
#     # Optimizer
#     # -------------------------------------------------

#     optimizer = AdamW(
#         model.parameters(),
#         lr=LEARNING_RATE,
#         weight_decay=WEIGHT_DECAY
#     )

#     # -------------------------------------------------
#     # Scheduler
#     # -------------------------------------------------

#     scheduler = CosineAnnealingLR(
#         optimizer,
#         T_max=EPOCHS
#     )

#     # -------------------------------------------------
#     # Trainer
#     # -------------------------------------------------

#     trainer = Trainer(
#         model=model,
#         criterion=criterion,
#         optimizer=optimizer,
#         device=DEVICE,
#         num_classes=NUM_CLASSES
#     )

#     print("\nEverything Initialized Successfully!")
#         # =====================================================
#     # TRAINING LOOP
#     # =====================================================

#     best_loss = float("inf")

#     history = {
#         "loss": [],
#         "pixel_accuracy": [],
#         "dice_score": [],
#         "iou_score": []
#     }

#     print("\nStarting Training...\n")

#     for epoch in range(EPOCHS):

#         print("=" * 70)
#         print(f"Epoch {epoch + 1}/{EPOCHS}")
#         print("=" * 70)

#         train_metrics = trainer.train_epoch(train_loader)

#         scheduler.step()

#         history["loss"].append(train_metrics["loss"])
#         history["pixel_accuracy"].append(train_metrics["pixel_accuracy"])
#         history["dice_score"].append(train_metrics["dice_score"])
#         history["iou_score"].append(train_metrics["iou_score"])

#         print()

#         print(f"Train Loss       : {train_metrics['loss']:.4f}")
#         print(f"Pixel Accuracy   : {train_metrics['pixel_accuracy']:.4f}")
#         print(f"Dice Score       : {train_metrics['dice_score']:.4f}")
#         print(f"IoU Score        : {train_metrics['iou_score']:.4f}")

#         print(
#             f"Learning Rate    : "
#             f"{optimizer.param_groups[0]['lr']:.8f}"
#         )

#         # -------------------------------------------------
#         # Save Best Model
#         # -------------------------------------------------

#         if train_metrics["loss"] < best_loss:

#             best_loss = train_metrics["loss"]

#             torch.save(
#                 model.state_dict(),
#                 BEST_MODEL
#             )

#             print("\n✅ Best Model Saved!")

#         print()

#             # =====================================================
#     # TRAINING COMPLETE
#     # =====================================================

#     print("\n" + "=" * 70)
#     print("TRAINING COMPLETED")
#     print("=" * 70)

#     print(f"Best Training Loss : {best_loss:.4f}")
#     print(f"Best Model Saved At: {BEST_MODEL}")

#     print("\nFinal Metrics")

#     print(f"Loss            : {history['loss'][-1]:.4f}")
#     print(f"Pixel Accuracy  : {history['pixel_accuracy'][-1]:.4f}")
#     print(f"Dice Score      : {history['dice_score'][-1]:.4f}")
#     print(f"IoU Score       : {history['iou_score'][-1]:.4f}")

#     print("=" * 70)


# # =====================================================
# # ENTRY POINT
# # =====================================================

# if __name__ == "__main__":

#     main()