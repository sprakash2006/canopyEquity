"""
==========================================================
CanopyAI
Impact Engine Runner
==========================================================
"""

from pathlib import Path

from backend.impact_engine.loader import RasterLoader
from backend.impact_engine.align import RasterAligner
from backend.impact_engine.normalize import Normalizer
from backend.impact_engine.canopy import CanopyAnalyzer
from backend.impact_engine.plantability import PlantabilityEngine
from backend.impact_engine.benefit import BenefitEngine
from backend.impact_engine.impact_score import ImpactScoreEngine
from backend.impact_engine.exporter import GeoTIFFExporter


def run():

    # ==========================================================
    # HEADER
    # ==========================================================

    print("=" * 70)
    print("CANOPY AI - IMPACT ENGINE")
    print("=" * 70)

    # ==========================================================
    # DATA DIRECTORY
    # ==========================================================

    DATA_DIR = Path("data")

    # ==========================================================
    # LOAD RASTERS
    # ==========================================================

    loader = RasterLoader(DATA_DIR)

    datasets = loader.load_all()

    loader.summary()

    # ==========================================================
    # ALIGNMENT
    # ==========================================================

    aligner = RasterAligner(datasets)

    aligned = aligner.align()

    aligner.validate()

    print("\n" + "=" * 70)
    print("ALIGNMENT COMPLETED SUCCESSFULLY")
    print("=" * 70)

    # ==========================================================
    # NORMALIZATION
    # ==========================================================

    normalizer = Normalizer()

    normalized = normalizer.normalize(aligned)

    normalizer.statistics(normalized)

    print("\n" + "=" * 70)
    print("NORMALIZATION COMPLETED SUCCESSFULLY")
    print("=" * 70)

    # ==========================================================
    # CANOPY ANALYSIS
    # ==========================================================

    canopy = CanopyAnalyzer()

    normalized = canopy.compute(normalized)

    canopy.statistics(normalized)

    print("\n" + "=" * 70)
    print("CANOPY ANALYSIS COMPLETED SUCCESSFULLY")
    print("=" * 70)

    # ==========================================================
    # PLANTABILITY
    # ==========================================================

    plantability = PlantabilityEngine()

    normalized = plantability.compute(normalized)

    plantability.statistics(normalized)

    print("\n" + "=" * 70)
    print("PLANTABILITY COMPLETED SUCCESSFULLY")
    print("=" * 70)

    # ==========================================================
    # BENEFIT ENGINE
    # ==========================================================

    benefit = BenefitEngine()

    normalized = benefit.compute(normalized)

    benefit.statistics(normalized)

    print("\n" + "=" * 70)
    print("BENEFIT ENGINE COMPLETED SUCCESSFULLY")
    print("=" * 70)

    # ==========================================================
    # IMPACT SCORE
    # ==========================================================

    impact = ImpactScoreEngine()

    normalized = impact.generate(normalized)

    impact.statistics(normalized)

    print("\n" + "=" * 70)
    print("IMPACT SCORE GENERATED SUCCESSFULLY")
    print("=" * 70)

    # ==========================================================
    # EXPORT RESULTS
    # ==========================================================

    exporter = GeoTIFFExporter(datasets["ndvi"])

    exporter.export_all(normalized)

    print("\n" + "=" * 70)
    print("EXPORT COMPLETED SUCCESSFULLY")
    print("=" * 70)

    # ==========================================================
    # FINAL STATUS
    # ==========================================================

    print("\nPIPELINE STATUS")

    print("✔ Raster Loading")
    print("✔ Raster Alignment")
    print("✔ Data Normalization")
    print("✔ Canopy Analysis")
    print("✔ Plantability")
    print("✔ Benefit Layer")
    print("✔ Impact Score")
    print("✔ Export GeoTIFF")

    print("\n" + "=" * 70)
    print("CANOPY AI IMPACT ENGINE COMPLETED SUCCESSFULLY")
    print("=" * 70)

    return {
        "status": "success",
        "outputs": {
            "impact_score": "outputs/impact_score.tif",
            "benefit": "outputs/benefit.tif",
            "plantability": "outputs/plantability.tif",
            "canopy_deficit": "outputs/canopy_deficit.tif",
            "impact_class": "outputs/impact_class.tif"
        }
    }


if __name__ == "__main__":
    run()