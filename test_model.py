import numpy as np
import rasterio
import torch
import torch.nn.functional as F

from src.models.segformer import CanopySegFormer

# =====================================================
# SETTINGS
# =====================================================

IMAGE_PATH = r"dataset/train/images/00000.tif"

CHECKPOINT = r"checkpoints/best_model.pth"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# =====================================================
# LOAD MODEL
# =====================================================

print("=" * 60)
print("LOADING MODEL")
print("=" * 60)

model = CanopySegFormer().to(DEVICE)

state = torch.load(CHECKPOINT, map_location=DEVICE)

model.load_state_dict(state)

model.eval()

print("✓ Model Loaded")
print("Device :", DEVICE)

# =====================================================
# LOAD IMAGE
# =====================================================

with rasterio.open(IMAGE_PATH) as src:

    image = src.read().astype(np.float32)

print("\nOriginal Image")
print("Shape :", image.shape)
print("Min   :", image.min())
print("Max   :", image.max())
print("Mean  :", image.mean())

image = image / 10000.0

print("\nNormalized Image")
print("Min   :", image.min())
print("Max   :", image.max())
print("Mean  :", image.mean())

image = torch.from_numpy(image).unsqueeze(0).to(DEVICE)

# =====================================================
# INFERENCE
# =====================================================

with torch.no_grad():

    logits = model(image)

    print("\nLogits Shape :", logits.shape)
    print("Logits Min   :", logits.min().item())
    print("Logits Max   :", logits.max().item())
    print("Logits Mean  :", logits.mean().item())

    logits = F.interpolate(
        logits,
        size=(256, 256),
        mode="bilinear",
        align_corners=False
    )

    prediction = logits.argmax(dim=1).cpu().numpy()[0]

print()
print("=" * 60)
print("PREDICTION")
print("=" * 60)

print("Unique Classes :", np.unique(prediction))
print("Prediction Shape :", prediction.shape)
print("Min :", prediction.min())
print("Max :", prediction.max())