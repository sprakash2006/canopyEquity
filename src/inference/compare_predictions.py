from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import rasterio
from PIL import Image


# =====================================================
# FILES
# =====================================================

IMAGE_PATH = Path("dataset/val/images/00003.tif")
MASK_PATH = Path("dataset/val/masks/00003.tif")
PRED_PATH = Path("outputs/prediction.png")


# =====================================================
# READ RGB IMAGE
# =====================================================

with rasterio.open(IMAGE_PATH) as src:

    image = src.read([4, 3, 2]).astype(np.float32)

image = np.transpose(image, (1, 2, 0))

image = image / image.max()


# =====================================================
# READ GROUND TRUTH
# =====================================================

with rasterio.open(MASK_PATH) as src:

    mask = src.read(1)


# =====================================================
# READ PREDICTION
# =====================================================

prediction = np.array(Image.open(PRED_PATH))


# =====================================================
# COLOR MAP
# =====================================================

colors = np.array([
    [0, 0, 0],          # Background
    [34, 139, 34],      # Trees
    [30, 144, 255],     # Water
    [220, 20, 60]       # Built-up
], dtype=np.uint8)

mask_color = colors[mask]
prediction_color = colors[prediction]


# =====================================================
# OVERLAY
# =====================================================

overlay = (
    image * 0.5 +
    prediction_color.astype(np.float32) / 255 * 0.5
)

overlay = np.clip(overlay, 0, 1)


# =====================================================
# PLOT
# =====================================================

fig, ax = plt.subplots(
    1,
    4,
    figsize=(18, 6)
)

ax[0].imshow(image)
ax[0].set_title("Original RGB")
ax[0].axis("off")

ax[1].imshow(mask_color)
ax[1].set_title("Ground Truth")
ax[1].axis("off")

ax[2].imshow(prediction_color)
ax[2].set_title("Prediction")
ax[2].axis("off")

ax[3].imshow(overlay)
ax[3].set_title("Overlay")
ax[3].axis("off")

plt.tight_layout()

Path("outputs").mkdir(exist_ok=True)

plt.savefig(
    "outputs/comparison.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print("=" * 60)
print("Comparison Image Saved")
print("outputs/comparison.png")
print("=" * 60)