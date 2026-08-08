from pathlib import Path

import rasterio
import numpy as np
import torch
from torch.utils.data import Dataset


class CanopyDataset(Dataset):

    def __init__(self, image_dir, mask_dir, transform=None):

        self.image_dir = Path(image_dir)
        self.mask_dir = Path(mask_dir)

        self.image_files = sorted(self.image_dir.glob("*.tif"))
        self.mask_files = sorted(self.mask_dir.glob("*.tif"))

        assert len(self.image_files) == len(self.mask_files), \
            "Number of images and masks do not match!"

        self.transform = transform

    def __len__(self):

        return len(self.image_files)

    def __getitem__(self, idx):

        # -------------------------
        # Read Image
        # -------------------------

        with rasterio.open(self.image_files[idx]) as src:
            image = src.read().astype(np.float32)

        # -------------------------
        # Normalize Image
        # -------------------------

        image = image / 10000.0

        # -------------------------
        # Read Mask
        # -------------------------

        with rasterio.open(self.mask_files[idx]) as src:
            mask = src.read(1).astype(np.int64)

        # -------------------------
        # Convert to Tensor
        # -------------------------

        image = torch.from_numpy(image)

        mask = torch.from_numpy(mask)

        # -------------------------
        # Optional Transform
        # -------------------------

        if self.transform:

            image, mask = self.transform(image, mask)

        return image, mask