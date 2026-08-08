from pathlib import Path
import rasterio
import numpy as np

IMAGE_PATH = Path("dataset/train/images/00300.tif")

with rasterio.open(IMAGE_PATH) as src:

    print("Bands :", src.count)

    for i in range(src.count):

        band = src.read(i+1)

        print(f"Band {i+1}")

        print("Shape :", band.shape)
        print("Min   :", band.min())
        print("Max   :", band.max())
        print("Mean  :", band.mean())
        print("----------------")