"""
==========================================================
CanopyAI
AI Engine
Raster Tiler
==========================================================
"""

from pathlib import Path

import numpy as np
import rasterio


class RasterTiler:

    def __init__(
        self,
        raster_path=None,
        tile_size=256
    ):

        # =====================================================
        # SELECT INPUT IMAGE
        # =====================================================

        if raster_path is None:

            uploads = Path("uploads")

            tif_files = sorted(uploads.glob("*.tif")) + sorted(
                uploads.glob("*.tiff")
            )

            if len(tif_files) > 0:

                raster_path = tif_files[-1]

                print()
                print("=" * 70)
                print("USING UPLOADED SATELLITE IMAGE")
                print("=" * 70)
                print(raster_path)

            else:

                raster_path = "data/13-band_satellite.tif"

                print()
                print("=" * 70)
                print("NO UPLOADED IMAGE FOUND")
                print("USING DEFAULT SATELLITE IMAGE")
                print("=" * 70)
                print(raster_path)

        self.raster_path = Path(raster_path)

        self.tile_size = tile_size

        self.dataset = None

        self.tiles = []

    # =====================================================
    # LOAD RASTER
    # =====================================================

    def load(self):

        print()
        print("=" * 70)
        print("LOADING SATELLITE IMAGE")
        print("=" * 70)

        if not self.raster_path.exists():

            raise FileNotFoundError(

                f"Raster not found : {self.raster_path}"

            )

        self.dataset = rasterio.open(self.raster_path)

        print(f"Raster Path : {self.raster_path}")
        print(f"Width       : {self.dataset.width}")
        print(f"Height      : {self.dataset.height}")
        print(f"Bands       : {self.dataset.count}")
        print(f"Tile Size   : {self.tile_size}")
        print(f"CRS         : {self.dataset.crs}")

        return self.dataset

    # =====================================================
    # CREATE TILES
    # =====================================================

    def create_tiles(self):

        print()
        print("=" * 70)
        print("GENERATING TILES")
        print("=" * 70)

        img = self.dataset.read().astype(np.float32)

        print("\nRAW IMAGE")
        print("Shape    :", img.shape)
        print("Min      :", img.min())
        print("Max      :", img.max())
        print("Mean     :", img.mean())
        print("NonZero  :", np.count_nonzero(img))

        # Same normalization used during training

        img /= 10000.0

        print("\nNORMALIZED IMAGE")
        print("Shape    :", img.shape)
        print("Min      :", img.min())
        print("Max      :", img.max())
        print("Mean     :", img.mean())
        print("NonZero  :", np.count_nonzero(img))

        bands, height, width = img.shape

        self.tiles = []

        count = 0

        for y in range(0, height, self.tile_size):

            for x in range(0, width, self.tile_size):

                tile = img[
                    :,
                    y:y+self.tile_size,
                    x:x+self.tile_size
                ]

                if (

                    tile.shape[1] != self.tile_size

                    or

                    tile.shape[2] != self.tile_size

                ):

                    padded = np.zeros(

                        (
                            bands,
                            self.tile_size,
                            self.tile_size
                        ),

                        dtype=np.float32

                    )

                    padded[
                        :,
                        :tile.shape[1],
                        :tile.shape[2]
                    ] = tile

                    tile = padded

                if count < 10:

                    print("\n" + "-" * 60)
                    print(f"TILE {count}")
                    print(f"x = {x}")
                    print(f"y = {y}")
                    print("Shape    :", tile.shape)
                    print("Min      :", tile.min())
                    print("Max      :", tile.max())
                    print("Mean     :", tile.mean())
                    print("Std      :", tile.std())
                    print("NonZero  :", np.count_nonzero(tile))

                    for b in range(tile.shape[0]):

                        print(

                            f"Band {b+1:02d} Mean : {tile[b].mean():.6f}"

                        )

                    print("-" * 60)

                self.tiles.append({

                    "image": tile,

                    "x": x,

                    "y": y

                })

                count += 1

        print()
        print(f"✓ Tiles Created : {count}")

        return self.tiles

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(self):

        print()

        print("=" * 70)
        print("TILE SUMMARY")
        print("=" * 70)

        print(f"Total Tiles : {len(self.tiles)}")

        if len(self.tiles) > 0:

            sample = self.tiles[0]["image"]

            print(f"Tile Shape  : {sample.shape}")
            print(f"Data Type   : {sample.dtype}")
            print("Sample Min  :", sample.min())
            print("Sample Max  :", sample.max())
            print("Sample Mean :", sample.mean())

        print("=" * 70)