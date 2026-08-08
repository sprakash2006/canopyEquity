from pathlib import Path
import rasterio
from rasterio.windows import Window
from rasterio.windows import transform
import numpy as np
import pandas as pd
from tqdm import tqdm

# =====================================================
# CONFIGURATION
# =====================================================

IMAGE_PATH = Path("data/13-band_satellite.tif")
MASK_PATH = Path("data/mcd_worldcover_4cls.tif")

OUTPUT_DIR = Path("dataset")

TRAIN_IMAGE_DIR = OUTPUT_DIR / "train" / "images"
TRAIN_MASK_DIR = OUTPUT_DIR / "train" / "masks"

TILE_SIZE = 256
STRIDE = 128              # 50% overlap
BACKGROUND_THRESHOLD = 0.95

# =====================================================
# CREATE OUTPUT FOLDERS
# =====================================================

TRAIN_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
TRAIN_MASK_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("CANOPY AI TILE GENERATOR V2")
print("=" * 60)

# =====================================================
# OPEN DATASETS
# =====================================================

image = rasterio.open(IMAGE_PATH)
mask = rasterio.open(MASK_PATH)

# =====================================================
# VALIDATION
# =====================================================

assert image.width == mask.width, "Width mismatch"
assert image.height == mask.height, "Height mismatch"
assert image.crs == mask.crs, "CRS mismatch"

print("✓ Image and Mask Alignment Verified")

print(f"Image Size : {image.width} x {image.height}")
print(f"Bands      : {image.count}")
print(f"Tile Size  : {TILE_SIZE}")
print(f"Stride     : {STRIDE}")

# =====================================================
# TOTAL WINDOWS
# =====================================================

rows = list(range(0, image.height - TILE_SIZE + 1, STRIDE))
cols = list(range(0, image.width - TILE_SIZE + 1, STRIDE))

total_windows = len(rows) * len(cols)

print(f"Total Sliding Windows : {total_windows}")

# =====================================================
# STATISTICS
# =====================================================

saved_tiles = 0
skipped_tiles = 0

metadata = []

# =====================================================
# HELPER FUNCTION
# =====================================================

def background_ratio(mask_tile):

    total_pixels = mask_tile.size

    background_pixels = np.sum(mask_tile == 0)

    return background_pixels / total_pixels

# =====================================================
# TILE GENERATION
# =====================================================

print("\nGenerating Tiles...\n")

for row in tqdm(rows, desc="Rows"):

    for col in cols:

        window = Window(col, row, TILE_SIZE, TILE_SIZE)

        # ---------------------------------------
        # Read Image (13 Bands)
        # ---------------------------------------

        image_tile = image.read(window=window)

        # ---------------------------------------
        # Read Mask
        # ---------------------------------------

        mask_tile = mask.read(1, window=window)

        # ---------------------------------------
        # Skip Mostly Background Tiles
        # ---------------------------------------

        bg_ratio = background_ratio(mask_tile)

        if bg_ratio >= BACKGROUND_THRESHOLD:
            skipped_tiles += 1
            continue

        # ---------------------------------------
        # Classes Present
        # ---------------------------------------

        classes = np.unique(mask_tile)

        # ---------------------------------------
        # Image Profile
        # ---------------------------------------

        image_profile = image.profile.copy()

        image_profile.update(
            width=TILE_SIZE,
            height=TILE_SIZE,
            transform=transform(window, image.transform)
        )

        # ---------------------------------------
        # Mask Profile
        # ---------------------------------------

        mask_profile = mask.profile.copy()

        mask_profile.update(
            width=TILE_SIZE,
            height=TILE_SIZE,
            transform=transform(window, mask.transform)
        )

        # ---------------------------------------
        # File Names
        # ---------------------------------------

        image_name = TRAIN_IMAGE_DIR / f"{saved_tiles:05d}.tif"
        mask_name = TRAIN_MASK_DIR / f"{saved_tiles:05d}.tif"

        # ---------------------------------------
        # Save Image
        # ---------------------------------------

        with rasterio.open(image_name, "w", **image_profile) as dst:
            dst.write(image_tile)

        # ---------------------------------------
        # Save Mask
        # ---------------------------------------

        with rasterio.open(mask_name, "w", **mask_profile) as dst:
            dst.write(mask_tile, 1)

        # ---------------------------------------
        # Store Metadata
        # ---------------------------------------

        metadata.append({
            "tile_id": saved_tiles,
            "row": row,
            "col": col,
            "background_ratio": round(bg_ratio, 4),
            "classes": ",".join(map(str, classes.tolist()))
        })

        saved_tiles += 1

        # =====================================================
# SAVE METADATA
# =====================================================

metadata_df = pd.DataFrame(metadata)

metadata_csv = OUTPUT_DIR / "tile_metadata.csv"

metadata_df.to_csv(metadata_csv, index=False)

# =====================================================
# CLOSE DATASETS
# =====================================================

image.close()
mask.close()

# =====================================================
# FINAL REPORT
# =====================================================

print("\n")
print("=" * 70)
print("               TILE GENERATION COMPLETED")
print("=" * 70)

print(f"Total Sliding Windows : {total_windows}")
print(f"Tiles Saved           : {saved_tiles}")
print(f"Tiles Skipped         : {skipped_tiles}")

print()

print(f"Image Folder  : {TRAIN_IMAGE_DIR}")
print(f"Mask Folder   : {TRAIN_MASK_DIR}")
print(f"Metadata CSV  : {metadata_csv}")

print()

save_percentage = (saved_tiles / total_windows) * 100
skip_percentage = (skipped_tiles / total_windows) * 100

print(f"Saved Percentage   : {save_percentage:.2f}%")
print(f"Skipped Percentage : {skip_percentage:.2f}%")

print("=" * 70)

# =====================================================
# CLASS SUMMARY
# =====================================================

all_classes = set()

for row in metadata:
    cls = row["classes"].split(",")
    for c in cls:
        all_classes.add(int(c))

print("\nClasses Present In Dataset")

for c in sorted(all_classes):
    print(f"✓ Class {c}")

print("\nMetadata Preview\n")

print(metadata_df.head())

print("\nDataset Ready For Training!")

print("=" * 70)