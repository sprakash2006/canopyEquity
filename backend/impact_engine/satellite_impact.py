"""
==========================================================
CanopyAI
Satellite Impact Engine  (location-agnostic, self-contained)
==========================================================

Analyses WHATEVER satellite image the user just uploaded, and
derives everything it needs FROM THAT IMAGE so results always
match the uploaded location -- no stale files, no Delhi/Pune
leftovers, no caching.

Reference grid  = the uploaded 13-band satellite itself.
Derived layers  :
    NDVI      = (NIR - Red) / (NIR + Red)             (B8, B4)
    NDWI/water = (Green - NIR) / (Green + NIR)         (B3, B8)
    heat      = built-up density * (1 - NDVI)          (LST proxy)
    landcover = NDVI thresholds                        (tree/built/open/bare)

A previously-uploaded support raster (uploads/ndvi.tif,
lst.tif, rainfall.tif, worldcover.tif) is used ONLY if it
geographically overlaps the current image -- otherwise it is
ignored, so a leftover from another city can never leak in.

Output (impact_score.tif + browser overlay) is written on the
uploaded image's grid, so the map re-centres on it automatically.
==========================================================
"""

from pathlib import Path

import numpy as np
import rasterio
from rasterio.warp import transform_bounds
from scipy.ndimage import uniform_filter

from backend.impact_engine.normalize import Normalizer
from backend.impact_engine.canopy import CanopyAnalyzer
from backend.impact_engine.plantability import PlantabilityEngine
from backend.impact_engine.benefit import BenefitEngine
from backend.impact_engine.impact_score import ImpactScoreEngine
from backend.impact_engine.vulnerability_proxy import VulnerabilityProxy
from backend.impact_engine.web_export import WebTileExporter


# Sentinel-2 band indices (1-based) in a 13-band stack.
S2_RED = 4     # B4
S2_GREEN = 3   # B3
S2_NIR = 8     # B8

TREE_CLASS = 1
BUILTUP_CLASS = 2
OPEN_CLASS = 0
BARE_CLASS = 3


class SatelliteImpactEngine:

    def __init__(self, uploads_dir="uploads", output_dir="outputs"):

        self.uploads = Path(uploads_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.reference = None   # the uploaded satellite dataset
        self.notes = []

    # =====================================================
    # LOCATE THE UPLOADED SATELLITE
    # =====================================================

    def _find_satellite(self):
        """Newest .tif in uploads/ that is NOT a known support layer name."""

        skip = {"ndvi", "lst", "rainfall", "worldcover"}

        tifs = sorted(
            list(self.uploads.glob("*.tif")) +
            list(self.uploads.glob("*.tiff")),
            key=lambda p: p.stat().st_mtime,
        )

        candidates = [
            p for p in tifs if p.stem.lower() not in skip
        ]

        return candidates[-1] if candidates else None

    # =====================================================
    # GEOMETRY HELPERS
    # =====================================================

    def _read_ref_band(self, band):
        """Read one band of the reference (satellite) as float, 0->NaN."""

        arr = self.reference.read(band).astype(np.float32)

        # DN 0 is Sentinel-2 nodata.
        arr[arr == 0] = np.nan
        return arr

    # =====================================================
    # LAYER BUILDERS  (derive from satellite first)
    # =====================================================

    def _build_ndvi(self):

        if self.reference.count >= S2_NIR:
            self.notes.append("ndvi: derived from satellite (B8,B4)")
            red = self._read_ref_band(S2_RED)
            nir = self._read_ref_band(S2_NIR)
            return (nir - red) / (nir + red + 1e-6)

        self.notes.append("ndvi: neutral 0.3 (satellite has <8 bands)")
        return np.full(
            (self.reference.height, self.reference.width), 0.3, np.float32
        )

    def _build_landcover(self, ndvi):

        self.notes.append("landcover: derived from NDVI thresholds")
        lc = np.full_like(ndvi, OPEN_CLASS, dtype=np.float32)
        lc[ndvi >= 0.45] = TREE_CLASS
        lc[ndvi < 0.15] = BUILTUP_CLASS
        lc[(ndvi >= 0.15) & (ndvi < 0.25)] = BARE_CLASS
        return lc

    def _build_lst(self, ndvi, landcover):

        self.notes.append("lst: heat proxy (built-up density x (1-NDVI))")
        built = (landcover == BUILTUP_CLASS).astype(np.float32)
        density = uniform_filter(built, size=25)
        veg_deficit = 1.0 - np.clip(np.nan_to_num(ndvi, nan=0.0), 0, 1)
        return density * veg_deficit

    def _build_rainfall(self, ndvi):

        if self.reference.count >= S2_NIR:
            self.notes.append("rainfall: NDWI water proxy (B3,B8)")
            green = self._read_ref_band(S2_GREEN)
            nir = self._read_ref_band(S2_NIR)
            return (green - nir) / (green + nir + 1e-6)

        self.notes.append("rainfall: neutral 0.5 (satellite has <8 bands)")
        return np.full(
            (self.reference.height, self.reference.width), 0.5, np.float32
        )

    # =====================================================
    # MAIN
    # =====================================================

    def _wipe_outputs(self):
        """Delete every file in outputs/ so nothing from a previous
        run can leak into the current analysis."""
        for f in self.output_dir.iterdir():
            if f.is_file():
                f.unlink()
                print(f"  removed stale: {f.name}")

    def run(self):

        print("=" * 70)
        print("CANOPY AI - SATELLITE IMPACT ENGINE (self-contained)")
        print("=" * 70)

        self._wipe_outputs()

        satellite = self._find_satellite()

        if satellite is None:
            raise FileNotFoundError(
                "No satellite image found in uploads/. "
                "Upload a multi-band GeoTIFF first."
            )

        self.reference = rasterio.open(satellite)

        ll = transform_bounds(
            self.reference.crs, "EPSG:4326", *self.reference.bounds
        )
        print(f"Satellite   : {satellite}")
        print(f"Grid        : {self.reference.width} x {self.reference.height}")
        print(f"CRS         : {self.reference.crs}")
        print(f"Bounds(WGS84): {ll}")

        # ---- derive every layer from the uploaded image ----
        ndvi = self._build_ndvi()
        landcover = self._build_landcover(ndvi)
        lst = self._build_lst(ndvi, landcover)
        rainfall = self._build_rainfall(ndvi)

        rasters = {
            "ndvi": ndvi.astype(np.float32),
            "lst": lst.astype(np.float32),
            "rainfall": rainfall.astype(np.float32),
            "landcover": landcover.astype(np.float32),
        }

        print("\nLAYER SOURCES")
        for n in self.notes:
            print(f"  - {n}")

        # ---- vulnerability proxy + standard formula chain ----
        proxy = VulnerabilityProxy()
        proxy.BUILT_UP_CLASS = BUILTUP_CLASS
        rasters = proxy.compute(rasters)

        rasters = Normalizer().normalize(rasters)
        rasters = CanopyAnalyzer().compute(rasters)
        rasters = PlantabilityEngine().compute(rasters)
        rasters = BenefitEngine().compute(rasters)
        rasters = ImpactScoreEngine().generate(rasters)

        impact = rasters["impact_score"]

        finite = impact[np.isfinite(impact)]
        plant = finite[finite > 0]
        print(
            f"\nImpact  finite={finite.size:,}  plantable={plant.size:,}  "
            f"mean={(plant.mean() if plant.size else 0):.2f}  "
            f"max={(finite.max() if finite.size else 0):.2f}"
        )

        # ---- export GeoTIFF on the uploaded grid ----
        profile = self.reference.profile.copy()
        profile.update(
            dtype="float32", count=1, compress="lzw", nodata=float("nan")
        )
        tif_path = self.output_dir / "impact_score.tif"
        with rasterio.open(tif_path, "w", **profile) as dst:
            dst.write(impact.astype(np.float32), 1)
        print(f"Saved : {tif_path}")

        # ---- browser overlay for THIS location ----
        web = WebTileExporter(self.reference)
        bounds = web.export(
            impact_score=impact, landcover=rasters.get("landcover")
        )

        print("=" * 70)
        print("SATELLITE IMPACT ENGINE COMPLETED")
        print("=" * 70)

        return {
            "status": "success",
            "source_image": str(satellite.name),
            "grid": [self.reference.width, self.reference.height],
            "bounds": bounds,
            "layer_sources": self.notes,
            "outputs": {
                "impact_score": "outputs/impact_score.tif",
                "web_png": "outputs/impact_score_web.png",
            },
        }


def run():
    return SatelliteImpactEngine().run()


if __name__ == "__main__":
    run()
