from datasets.canopy_dataset import CanopyDataset

dataset = CanopyDataset(
    image_dir="dataset/train/images",
    mask_dir="dataset/train/masks"
)

print("=" * 50)
print("CANOPY DATASET TEST")
print("=" * 50)

print("Total Samples:", len(dataset))

image, mask = dataset[150]

print("\nImage Shape:", image.shape)
print("Mask Shape :", mask.shape)

print("Image dtype:", image.dtype)
print("Mask dtype :", mask.dtype)

print("Image Min:", image.min().item())
print("Image Max:", image.max().item())

print("Unique Classes:", mask.unique())