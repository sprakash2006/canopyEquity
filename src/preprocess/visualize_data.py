from pathlib import Path
import rasterio
import matplotlib.pyplot as plt

DATA_DIR = Path("data")

files = [
    "mcd_worldcover_4cls.tif",
    "mcd_ndvi_2022_2023.tif",
    "mcd_lst_2022_2023.tif"
]

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

for ax, file in zip(axes, files):

    with rasterio.open(DATA_DIR / file) as src:
        img = src.read(1)

    im = ax.imshow(img, cmap="viridis")
    ax.set_title(file)
    ax.axis("off")

    plt.colorbar(im, ax=ax, fraction=0.046)

plt.tight_layout()
plt.show()