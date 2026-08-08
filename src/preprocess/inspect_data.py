import rasterio
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Path to your data folder
DATA_DIR = Path("data")

# TIFF files to inspect
files = [
    "mcd_worldcover_4cls.tif",
    "mcd_ndvi_2022_2023.tif",
    "mcd_lst_2022_2023.tif",
    "mcd_rainfall_2022_2023.tif"
]

for file in files:
    path = DATA_DIR / file

    print("=" * 60)
    print(f"File : {file}")

    with rasterio.open(path) as src:

        print(f"Width      : {src.width}")
        print(f"Height     : {src.height}")
        print(f"Bands      : {src.count}")
        print(f"Data Type  : {src.dtypes}")
        print(f"CRS        : {src.crs}")
        print(f"Resolution : {src.res}")
        print(f"NoData     : {src.nodata}")

        image = src.read(1)

        print(f"Min Value  : {np.nanmin(image)}")
        print(f"Max Value  : {np.nanmax(image)}")

        if "worldcover" in file.lower():
            unique = np.unique(image)
            print(f"Classes    : {unique}")

print("\nInspection Completed Successfully!")