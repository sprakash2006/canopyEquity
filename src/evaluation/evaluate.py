from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report
)
from torch.utils.data import DataLoader
from tqdm import tqdm

from src.configs.config import *
from src.datasets.canopy_dataset import CanopyDataset
from src.models.segformer import CanopySegFormer


# =====================================================
# DEVICE
# =====================================================

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("=" * 70)
print("CANOPY AI MODEL EVALUATION")
print("=" * 70)

print("Device :", DEVICE)

# =====================================================
# DATASET
# =====================================================

dataset = CanopyDataset(
    image_dir="dataset/val/images",
    mask_dir="dataset/val/masks"
)

loader = DataLoader(
    dataset,
    batch_size=2,
    shuffle=False,
    num_workers=0
)

print("Validation Images :", len(dataset))

# =====================================================
# MODEL
# =====================================================

model = CanopySegFormer().to(DEVICE)

checkpoint = torch.load(
    BEST_MODEL,
    map_location=DEVICE
)

model.load_state_dict(checkpoint)

model.eval()

print("Model Loaded Successfully.")

# =====================================================
# STORAGE
# =====================================================

all_preds = []
all_targets = []

# =====================================================
# EVALUATION
# =====================================================

with torch.no_grad():

    for images, masks in tqdm(loader):

        images = images.to(DEVICE)

        outputs = model(images)

        if hasattr(outputs, "logits"):
            logits = outputs.logits
        else:
            logits = outputs

        logits = F.interpolate(
            logits,
            size=masks.shape[-2:],
            mode="bilinear",
            align_corners=False
        )

        preds = torch.argmax(
            logits,
            dim=1
        )

        all_preds.extend(
            preds.cpu().numpy().flatten()
        )

        all_targets.extend(
            masks.numpy().flatten()
        )

# =====================================================
# NUMPY
# =====================================================

all_preds = np.array(all_preds)

all_targets = np.array(all_targets)

# =====================================================
# METRICS
# =====================================================

accuracy = accuracy_score(
    all_targets,
    all_preds
)

precision, recall, f1, _ = precision_recall_fscore_support(
    all_targets,
    all_preds,
    average="macro",
    zero_division=0
)

cm = confusion_matrix(
    all_targets,
    all_preds
)

report = classification_report(
    all_targets,
    all_preds,
    digits=4
)

# =====================================================
# IoU
# =====================================================

ious = []

for cls in range(NUM_CLASSES):

    pred = all_preds == cls

    gt = all_targets == cls

    intersection = np.logical_and(
        pred,
        gt
    ).sum()

    union = np.logical_or(
        pred,
        gt
    ).sum()

    if union == 0:
        ious.append(0)

    else:
        ious.append(
            intersection / union
        )

mean_iou = np.mean(ious)

# =====================================================
# PRINT
# =====================================================

print("\n" + "=" * 70)

print("FINAL RESULTS")

print("=" * 70)

print(f"Accuracy  : {accuracy:.4f}")

print(f"Precision : {precision:.4f}")

print(f"Recall    : {recall:.4f}")

print(f"F1 Score  : {f1:.4f}")

print(f"Mean IoU  : {mean_iou:.4f}")

print("\nPer Class IoU")

for i, score in enumerate(ious):

    print(f"Class {i} : {score:.4f}")

print("\nConfusion Matrix")

print(cm)

print("\nClassification Report")

print(report)

print("=" * 70)

# =====================================================
# SAVE
# =====================================================

Path("outputs").mkdir(exist_ok=True)

with open("outputs/evaluation_report.txt", "w") as f:

    f.write("=" * 70 + "\n")

    f.write("CANOPY AI EVALUATION\n")

    f.write("=" * 70 + "\n\n")

    f.write(f"Accuracy : {accuracy:.4f}\n")

    f.write(f"Precision : {precision:.4f}\n")

    f.write(f"Recall : {recall:.4f}\n")

    f.write(f"F1 Score : {f1:.4f}\n")

    f.write(f"Mean IoU : {mean_iou:.4f}\n\n")

    f.write("Per Class IoU\n")

    for i, score in enumerate(ious):

        f.write(f"Class {i} : {score:.4f}\n")

    f.write("\n")

    f.write("Confusion Matrix\n")

    f.write(str(cm))

    f.write("\n\n")

    f.write(report)

print("\n✅ Report Saved")

print("outputs/evaluation_report.txt")