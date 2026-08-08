from pathlib import Path
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

path = Path("data/mcd_worldcover_4cls.tif")

with rasterio.open(path) as src:
    img = src.read(1)

classes, counts = np.unique(img, return_counts=True)

print("\nClass Distribution\n")

for c, cnt in zip(classes, counts):
    print(f"Class {c}: {cnt:,}")

# Temporary colors (we'll rename them after identifying classes)
colors = [
    "#000000",  # Class 0
    "#00ff00",  # Class 1
    "#ff0000",  # Class 2
    "#0000ff"   # Class 3
]

cmap = ListedColormap(colors)

plt.figure(figsize=(10,10))
plt.imshow(img, cmap=cmap)
plt.title("WorldCover Classes")
plt.colorbar()
plt.show()