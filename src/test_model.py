import torch

from models.segformer import CanopySegFormer

print("Loading Model...")

model = CanopySegFormer()

print("Model Loaded Successfully!")

# Fake input
x = torch.randn(2, 13, 256, 256)

print("Running Forward Pass...")

y = model(x)

print("=" * 50)
print("MODEL TEST SUCCESSFUL")
print("=" * 50)

print("Input Shape :", x.shape)
print("Output Shape:", y.shape)