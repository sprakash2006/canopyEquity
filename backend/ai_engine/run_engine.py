"""
==========================================================
CanopyAI
AI Engine
==========================================================
"""

from backend.ai_engine.loader import ModelLoader
from backend.ai_engine.tiler import RasterTiler
from backend.ai_engine.predictor import Predictor
from backend.ai_engine.stitcher import Stitcher
from backend.ai_engine.exporter import GeoTIFFExporter


def run():

    # ==========================================================
    # HEADER
    # ==========================================================

    print("=" * 70)
    print("CANOPY AI - AI ENGINE")
    print("=" * 70)

    # ==========================================================
    # LOAD SEGFORMER MODEL
    # ==========================================================

    loader = ModelLoader()

    model = loader.load()

    loader.summary()

    print()
    print("=" * 70)
    print("MODEL LOADED SUCCESSFULLY")
    print("=" * 70)

    # ==========================================================
    # LOAD SATELLITE IMAGE
    # ==========================================================

    tiler = RasterTiler()

    dataset = tiler.load()

    tiles = tiler.create_tiles()

    tiler.summary()

    print()
    print("=" * 70)
    print("TILE GENERATION COMPLETED SUCCESSFULLY")
    print("=" * 70)

    # ==========================================================
    # RUN SEGFORMER PREDICTION
    # ==========================================================

    predictor = Predictor(
        model=model,
        device=loader.device,
        tiles=tiles,
        batch_size=8
    )

    predictions = predictor.predict()

    predictor.summary()

    print()
    print("=" * 70)
    print("PREDICTION COMPLETED SUCCESSFULLY")
    print("=" * 70)

    # ==========================================================
    # STITCH ALL PREDICTIONS
    # ==========================================================

    stitcher = Stitcher(
        predictions=predictions,
        image_height=dataset.height,
        image_width=dataset.width,
        tile_size=256
    )

    final_mask = stitcher.stitch()

    stitcher.summary()

    print()
    print("=" * 70)
    print("STITCHING COMPLETED SUCCESSFULLY")
    print("=" * 70)

    # ==========================================================
    # EXPORT FINAL GEOTIFF
    # ==========================================================

    exporter = GeoTIFFExporter(
        mask=final_mask,
        reference_dataset=dataset,
        output_path="outputs/canopy_prediction.tif"
    )

    exporter.export()

    exporter.summary()

    print()
    print("=" * 70)
    print("EXPORT COMPLETED SUCCESSFULLY")
    print("=" * 70)

    # ==========================================================
    # PIPELINE STATUS
    # ==========================================================

    print()
    print("=" * 70)
    print("AI ENGINE STATUS")
    print("=" * 70)

    print("✔ Load SegFormer Model")
    print("✔ Tile Generator")
    print("✔ Prediction")
    print("✔ Stitch Tiles")
    print("✔ Export GeoTIFF")
    print("⬜ Post Processing")
    print("⬜ Canopy Generator")

    print()
    print("=" * 70)
    print("CANOPY AI ENGINE COMPLETED")
    print("=" * 70)

    print("Output File : outputs/canopy_prediction.tif")

    print("=" * 70)

    return {
        "status": "success",
        "output_file": "outputs/canopy_prediction.tif",
        "tiles": len(tiles),
        "image_size": {
            "width": dataset.width,
            "height": dataset.height
        }
    }


if __name__ == "__main__":
    run()