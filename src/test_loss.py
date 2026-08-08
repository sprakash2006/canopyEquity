import torch

from training.losses import SegmentationLoss

print("=" * 50)
print("TESTING SEGMENTATION LOSS")
print("=" * 50)

criterion = SegmentationLoss()

# Fake model output
logits = torch.randn(2, 4, 256, 256)

# Fake ground truth mask
targets = torch.randint(0, 4, (2, 256, 256))

loss = criterion(logits, targets)

print(f"Loss Value : {loss.item():.4f}")

print("\n✅ Loss Function Working Successfully!")