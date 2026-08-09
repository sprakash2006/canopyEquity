"""
==========================================================
CanopyAI
Impact Score Engine  (v2 — spatial + stretched)
==========================================================

Formula (v2):

    benefit_spatial = gaussian_smooth(benefit, sigma≈500 m)
    raw_impact      = sqrt(benefit_spatial * plantability)
    impact_score    = percentile_stretch(raw_impact, 2..98) * 100
    impact_score[plantability == 0] = 0

Why:
  * gaussian smoothing lets plantable pixels inherit the
    cooling need of nearby built-up / hot pixels — a bare
    lot beside a slum should score high because that's
    where planting actually helps humans.
  * geometric mean (sqrt of product) preserves the "both
    factors required" logic without crushing mid values
    to a fraction of what they should be.
  * percentile stretch spreads the population across the
    full 0-100 range instead of everything sitting in the
    low tens.

Output:
    Impact Score (0-100), 0 wherever planting is impossible.
==========================================================
"""


import numpy as np
from scipy.ndimage import gaussian_filter



class ImpactScoreEngine:


    # Sigma for the neighborhood smoothing, in *pixels*.
    # Source rasters are 10 m/px, so 50 px ≈ 500 m — the
    # scale at which a cluster of trees actually influences
    # microclimate.
    NEIGHBOURHOOD_SIGMA_PX = 50

    # Percentile cut-offs for the final stretch.  Trimming
    # 2% off each tail resists outliers without discarding
    # meaningful extremes.
    STRETCH_LOW_PCT  = 2
    STRETCH_HIGH_PCT = 98



    def __init__(self):
        pass



    # ======================================================
    # COMPUTE IMPACT SCORE  (v2)
    # ======================================================


    def compute(self, rasters):


        benefit       = rasters["benefit"].astype(np.float32)
        plantability  = rasters["plantability"].astype(np.float32)

        # Pixels where any critical input was NaN are honest
        # unknowns — mark them so we can render them as
        # transparent "no data" on the map instead of pretending
        # we have a confident answer.

        unknown = np.isnan(benefit) | np.isnan(plantability)

        # Also treat data-gap NDVI as unknown if we have it,
        # since NDVI drives both benefit and plantability.

        ndvi = rasters.get("ndvi")

        if ndvi is not None:
            unknown = unknown | np.isnan(ndvi)


        # --------------------------------------------------
        # 1. Neighborhood benefit
        # --------------------------------------------------
        # Spread each pixel's "need" into a ~500 m halo so
        # plantable pixels on the *edge* of hot / dense
        # zones inherit that need.

        benefit_spatial = gaussian_filter(
            np.nan_to_num(benefit, nan=0.0),
            sigma=self.NEIGHBOURHOOD_SIGMA_PX
        )


        # --------------------------------------------------
        # 2. Geometric mean (sqrt of product)
        # --------------------------------------------------
        # Keeps the "both required" logic — if plantability
        # is 0, impact is 0 — but doesn't compress mid-values
        # into a small fraction.

        raw = np.sqrt(
            np.clip(benefit_spatial, 0, 1) *
            np.clip(plantability,    0, 1)
        )


        # --------------------------------------------------
        # 3. Percentile stretch on plantable pixels only
        # --------------------------------------------------
        # Compute the 2..98 percentile band over pixels
        # that can actually be planted — otherwise the huge
        # zero-mass from built-up areas would dominate the
        # distribution and flatten everything.

        planted_mask = plantability > 0

        if planted_mask.any():

            lo = float(np.percentile(raw[planted_mask], self.STRETCH_LOW_PCT))
            hi = float(np.percentile(raw[planted_mask], self.STRETCH_HIGH_PCT))

            if hi > lo:
                stretched = (raw - lo) / (hi - lo)
            else:
                stretched = raw

        else:
            stretched = raw


        impact = np.clip(stretched, 0, 1) * 100.0


        # --------------------------------------------------
        # 4. Hard constraint: never plant where you can't
        # --------------------------------------------------

        impact[plantability == 0] = 0.0


        # --------------------------------------------------
        # 5. Propagate data gaps as NaN, not fake scores
        # --------------------------------------------------

        impact[unknown] = np.nan


        rasters["impact_score"] = impact.astype(np.float32)

        return rasters



    # ======================================================
    # CLASSIFICATION (5 tiers)
    # ======================================================


    @staticmethod
    def classify(score):

        classes = np.zeros_like(score, dtype=np.uint8)

        classes[score >= 80]                    = 4
        classes[(score >= 60) & (score < 80)]   = 3
        classes[(score >= 40) & (score < 60)]   = 2
        classes[(score >= 20) & (score < 40)]   = 1

        return classes



    # ======================================================
    # PUBLIC ENTRY
    # ======================================================


    def generate(self, rasters):

        rasters = self.compute(rasters)

        rasters["impact_class"] = self.classify(
            rasters["impact_score"]
        )

        return rasters



    # ======================================================
    # STATISTICS
    # ======================================================


    @staticmethod
    def statistics(rasters):

        img = rasters["impact_score"]

        print()
        print("=" * 70)
        print("IMPACT SCORE ENGINE  (v2)")
        print("=" * 70)

        print(
            f"Impact Score "
            f"Min={np.nanmin(img):.2f} "
            f"Max={np.nanmax(img):.2f} "
            f"Mean={np.nanmean(img):.2f} "
            f"Median={float(np.nanmedian(img)):.2f}"
        )

        unique, counts = np.unique(
            rasters["impact_class"], return_counts=True
        )

        print()
        print("Impact Classes")

        for u, c in zip(unique, counts):
            print(f"  Class {u} : {c:,}")

        print("=" * 70)
