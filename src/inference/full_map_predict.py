import os
from pathlib import Path

import numpy as np
import rasterio
import torch
import torch.nn.functional as F
from tqdm import tqdm
from PIL import Image

from src.configs.config import *
from src.models.segformer import CanopySegFormer


# =====================================================
# DEVICE
# =====================================================

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("=" * 70)
print("CANOPY AI - FULL SATELLITE PREDICTION")
print("=" * 70)

print(f"Device : {DEVICE}")

# =====================================================
# MODEL
# =====================================================

print("\nLoading SegFormer...")

model = CanopySegFormer().to(DEVICE)

checkpoint = torch.load(
    BEST_MODEL,
    map_location=DEVICE
)

model.load_state_dict(checkpoint)

model.eval()

print("✅ Best Model Loaded")

# =====================================================
# INPUT IMAGE
# =====================================================

IMAGE_PATH = "data/13-band_satellite.tif"

assert os.path.exists(
    IMAGE_PATH
), f"{IMAGE_PATH} not found."

print(f"\nInput Image : {IMAGE_PATH}")

# =====================================================
# PARAMETERS
# =====================================================

TILE_SIZE = 256

STRIDE = 256

NUM_CLASSES = 4

OUTPUT_DIR = Path("outputs")

OUTPUT_DIR.mkdir(
    exist_ok=True
)

print(f"Tile Size : {TILE_SIZE}")
print(f"Stride    : {STRIDE}")

print("=" * 70)
# =====================================================
# READ FULL SATELLITE IMAGE
# =====================================================

print("\nReading Satellite Image...")

with rasterio.open(IMAGE_PATH) as src:

    image = src.read().astype(np.float32)

    profile = src.profile.copy()

    transform = src.transform

    crs = src.crs

    height = src.height

    width = src.width

print(f"Image Shape : {image.shape}")

print(f"Height      : {height}")

print(f"Width       : {width}")

print(f"Bands       : {image.shape[0]}")

# =====================================================
# NORMALIZE
# =====================================================

image = image / 10000.0

# =====================================================
# PADDING
# =====================================================

pad_h = (TILE_SIZE - height % TILE_SIZE) % TILE_SIZE

pad_w = (TILE_SIZE - width % TILE_SIZE) % TILE_SIZE

image = np.pad(
    image,
    (
        (0, 0),
        (0, pad_h),
        (0, pad_w)
    ),
    mode="constant"
)

new_height = image.shape[1]

new_width = image.shape[2]

print("\nAfter Padding")

print(f"Height : {new_height}")

print(f"Width  : {new_width}")

# =====================================================
# EMPTY PREDICTION MAP
# =====================================================

prediction_map = np.zeros(
    (
        new_height,
        new_width
    ),
    dtype=np.uint8
)

print("\nPrediction Map Created")

print("=" * 70)

# =====================================================
# TILE PREDICTION
# =====================================================
# =====================================================
# TILE PREDICTION (BATCHED)
# =====================================================

print("\nRunning Full Image Prediction...")

tiles = []
positions = []

for y in range(0, new_height, STRIDE):

    for x in range(0, new_width, STRIDE):

        tile = image[
            :,
            y:y + TILE_SIZE,
            x:x + TILE_SIZE
        ]

        if tile.shape[1] != TILE_SIZE or tile.shape[2] != TILE_SIZE:
            continue

        tiles.append(tile)
        positions.append((y, x))

print(f"Total Tiles : {len(tiles)}")

with torch.no_grad():

    for i in tqdm(
        range(0, len(tiles), BATCH_SIZE),
        desc="Predicting"
    ):

        batch_tiles = tiles[i:i + BATCH_SIZE]

        batch = torch.stack(
            [
                torch.from_numpy(t).float()
                for t in batch_tiles
            ]
        ).to(DEVICE)

        outputs = model(batch)

        if hasattr(outputs, "logits"):
            logits = outputs.logits
        else:
            logits = outputs

        logits = F.interpolate(
            logits,
            size=(TILE_SIZE, TILE_SIZE),
            mode="bilinear",
            align_corners=False
        )

        preds = torch.argmax(
            logits,
            dim=1
        ).cpu().numpy()

        for j, pred in enumerate(preds):

            y, x = positions[i + j]

            prediction_map[
                y:y + TILE_SIZE,
                x:x + TILE_SIZE
            ] = pred

print("\n✅ Full Image Prediction Completed")

print("=" * 70)
# =====================================================
# REMOVE PADDING
# =====================================================

prediction_map = prediction_map[
    :height,
    :width
]

print("\nPadding Removed")

print(f"Final Shape : {prediction_map.shape}")

# =====================================================
# SAVE PNG
# =====================================================

png_path = OUTPUT_DIR / "prediction_full.png"

Image.fromarray(
    prediction_map.astype(np.uint8)
).save(png_path)

print(f"\n✅ PNG Saved : {png_path}")

# =====================================================
# SAVE GEOTIFF
# =====================================================

profile.update(
    dtype=rasterio.uint8,
    count=1,
    compress="lzw"
)

tif_path = OUTPUT_DIR / "prediction_full.tif"

with rasterio.open(
    tif_path,
    "w",
    **profile
) as dst:

    dst.write(
        prediction_map.astype(np.uint8),
        1
    )

print(f"✅ GeoTIFF Saved : {tif_path}")

# =====================================================
# SUMMARY
# =====================================================

print("\n" + "=" * 70)
print("FULL SATELLITE PREDICTION COMPLETED")
print("=" * 70)

print(f"Image Size : {width} x {height}")
print(f"Classes Found : {np.unique(prediction_map)}")
print(f"PNG Output : {png_path}")
print(f"GeoTIFF Output : {tif_path}")

print("=" * 70)

# =====================================================
# AREA STATISTICS
# =====================================================

print("\nCalculating Area Statistics...")

unique, counts = np.unique(
    prediction_map,
    return_counts=True
)

class_names = {
    0: "Bare / Other",
    1: "Canopy",
    2: "Built-up",
    3: "Cropland"
}

total_pixels = prediction_map.size

print("\n" + "=" * 70)
print("AREA STATISTICS")
print("=" * 70)

stats_path = OUTPUT_DIR / "area_statistics.txt"

with open(stats_path, "w") as f:

    f.write("=" * 70 + "\n")
    f.write("CANOPY AI - AREA STATISTICS\n")
    f.write("=" * 70 + "\n\n")

    for cls, cnt in zip(unique, counts):

        percentage = (cnt / total_pixels) * 100

        name = class_names.get(cls, f"Class {cls}")

        print(f"{name:15s}: {cnt:10d} pixels ({percentage:.2f}%)")

        f.write(
            f"{name:15s}: "
            f"{cnt:10d} pixels "
            f"({percentage:.2f}%)\n"
        )

print("\n✅ Area Statistics Saved")
print(stats_path)

print("=" * 70)

# =====================================================
# COLORED SEGMENTATION MAP
# =====================================================

print("\nGenerating Colored Segmentation Map...")
colors = np.array([

    [160, 160, 160],    # Bare / Other (Gray)

    [34, 139, 34],      # Canopy (Green)

    [220, 20, 60],      # Built-up (Red)

    [255, 215, 0]       # Cropland (Yellow)

], dtype=np.uint8)

colored_prediction = colors[prediction_map]

colored_path = OUTPUT_DIR / "prediction_full_colored.png"

Image.fromarray(
    colored_prediction
).save(colored_path)

print(f"✅ Colored Prediction Saved : {colored_path}")

# =====================================================
# VISUALIZATION
# =====================================================

import matplotlib.pyplot as plt
from matplotlib.patches import Patch

legend = [

    Patch(facecolor=np.array(colors[0]) / 255,
          edgecolor="black",
          label="Bare / Other"),

    Patch(facecolor=np.array(colors[1]) / 255,
          edgecolor="black",
          label="Canopy"),

    Patch(facecolor=np.array(colors[2]) / 255,
          edgecolor="black",
          label="Built-up"),

    Patch(facecolor=np.array(colors[3]) / 255,
          edgecolor="black",
          label="Cropland")

]

plt.figure(figsize=(10, 10))

plt.imshow(colored_prediction)

plt.title("Full Satellite Segmentation")

plt.legend(
    handles=legend,
    loc="lower right"
)

plt.axis("off")

figure_path = OUTPUT_DIR / "full_segmentation_visualization.png"

plt.savefig(
    figure_path,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print(f"✅ Visualization Saved : {figure_path}")

print("=" * 70)