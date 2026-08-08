from pathlib import Path
import random
import shutil

random.seed(42)

DATASET = Path("dataset")

train_img = DATASET / "train" / "images"
train_mask = DATASET / "train" / "masks"

val_img = DATASET / "val" / "images"
val_mask = DATASET / "val" / "masks"

val_img.mkdir(parents=True, exist_ok=True)
val_mask.mkdir(parents=True, exist_ok=True)

image_files = sorted(train_img.glob("*.tif"))

random.shuffle(image_files)

split = int(len(image_files) * 0.8)

train_files = image_files[:split]
val_files = image_files[split:]

print("=" * 60)
print("Splitting Dataset")
print("=" * 60)

for img in val_files:

    mask = train_mask / img.name

    shutil.move(str(img), str(val_img / img.name))
    shutil.move(str(mask), str(val_mask / mask.name))

print(f"Training Images : {len(train_files)}")
print(f"Validation Images : {len(val_files)}")

print("\nDataset Split Completed Successfully!")