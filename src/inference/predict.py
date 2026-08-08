import os
from pathlib import Path

import numpy as np
import rasterio
import torch
import torch.nn.functional as F
from PIL import Image

from src.configs.config import *
from src.models.segformer import CanopySegFormer


# =====================================================
# DEVICE
# =====================================================

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("=" * 60)
print("CANOPY AI - PREDICTION")
print("=" * 60)
print(f"Device : {DEVICE}")

# =====================================================
# LOAD MODEL
# =====================================================

print("\nLoading Model...")

model = CanopySegFormer().to(DEVICE)

checkpoint = torch.load(
    BEST_MODEL,
    map_location=DEVICE
)

model.load_state_dict(checkpoint)

model.eval()

print("✅ Model Loaded Successfully")

# =====================================================
# INPUT IMAGE
# =====================================================
# =====================================================
# INPUT IMAGE
# =====================================================

image_files = sorted(Path("dataset/val/images").glob("*.tif"))

assert len(image_files) > 0, "No validation images found!"

IMAGE_PATH = str(image_files[0])

print(f"\nUsing Image : {IMAGE_PATH}")
# =====================================================
# READ IMAGE
# =====================================================

with rasterio.open(IMAGE_PATH) as src:

    image = src.read().astype(np.float32)

image = image / 10000.0

image_tensor = torch.from_numpy(image)

image_tensor = image_tensor.unsqueeze(0)

image_tensor = image_tensor.to(DEVICE)

print("Image Shape :", image_tensor.shape)

# =====================================================
# PREDICTION
# =====================================================

print("\nRunning Prediction...")

with torch.no_grad():

    outputs = model(image_tensor)

    # HuggingFace SegFormer Output
    if hasattr(outputs, "logits"):
        logits = outputs.logits
    else:
        logits = outputs

    # Resize to Original Tile Size
    logits = F.interpolate(
        logits,
        size=(256, 256),
        mode="bilinear",
        align_corners=False
    )

    prediction = torch.argmax(
        logits,
        dim=1
    )

prediction = prediction.squeeze().cpu().numpy()

print("\nPrediction Shape :", prediction.shape)

print("Classes Found :", np.unique(prediction))

# =====================================================
# SAVE PREDICTION
# =====================================================

output_dir = Path("outputs")

output_dir.mkdir(
    parents=True,
    exist_ok=True
)

save_path = output_dir / "prediction.png"

prediction_image = Image.fromarray(
    prediction.astype(np.uint8)
)

prediction_image.save(save_path)

print(f"\n✅ Prediction Saved : {save_path}")

print("=" * 60)
print("Prediction Completed Successfully!")
print("=" * 60)