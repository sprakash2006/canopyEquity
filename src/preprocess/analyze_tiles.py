from pathlib import Path
import rasterio
import numpy as np
from collections import Counter

MASK_FOLDER = Path("dataset/train/masks")

mask_files = sorted(MASK_FOLDER.glob("*.tif"))

print("=" * 60)
print("CANOPY TILE ANALYSIS")
print("=" * 60)

print(f"Total Tiles : {len(mask_files)}")

empty_tiles = 0
single_class_tiles = 0
multi_class_tiles = 0

global_counter = Counter()

for mask_path in mask_files:

    with rasterio.open(mask_path) as src:
        mask = src.read(1)

    classes, counts = np.unique(mask, return_counts=True)

    # Count pixels of every class
    for c, cnt in zip(classes, counts):
        global_counter[int(c)] += int(cnt)

    # Empty tile (only background)
    if len(classes) == 1 and classes[0] == 0:
        empty_tiles += 1

    # Only one class
    elif len(classes) == 1:
        single_class_tiles += 1

    # Multiple classes
    else:
        multi_class_tiles += 1

print("\n" + "=" * 60)
print("Tile Statistics")
print("=" * 60)

print(f"Empty Tiles        : {empty_tiles}")
print(f"Single Class Tiles : {single_class_tiles}")
print(f"Multi Class Tiles  : {multi_class_tiles}")

print("\n" + "=" * 60)
print("Pixel Distribution")
print("=" * 60)

total_pixels = sum(global_counter.values())

for cls in sorted(global_counter.keys()):

    percentage = (global_counter[cls] / total_pixels) * 100

    print(
        f"Class {cls} : "
        f"{global_counter[cls]:,} pixels "
        f"({percentage:.2f}%)"
    )

print("\n" + "=" * 60)

if empty_tiles > len(mask_files) * 0.20:
    print("⚠ More than 20% tiles are empty.")
    print("Recommendation : Regenerate tiles with overlap.")
else:
    print("✓ Dataset quality looks good.")
    print("Recommendation : Continue Training.")

print("=" * 60)