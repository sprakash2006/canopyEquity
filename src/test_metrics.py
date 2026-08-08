import torch

from training.metrics import SegmentationMetrics

metrics = SegmentationMetrics(num_classes=4)

logits = torch.randn(2, 4, 256, 256)

targets = torch.randint(0, 4, (2, 256, 256))

result = metrics.calculate(logits, targets)

print("=" * 50)
print("METRICS TEST")
print("=" * 50)

for k, v in result.items():
    print(f"{k:20s}: {v:.4f}")

print("\n✅ Metrics Working Successfully!")