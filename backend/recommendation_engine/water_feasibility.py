"""
==========================================================
CanopyAI
Recommendation Engine
Water Feasibility Engine
==========================================================
"""

import numpy as np


class WaterFeasibility:

    def __init__(self, wards):

        self.wards = wards

    # =====================================================
    # NORMALIZATION
    # =====================================================

    @staticmethod
    def normalize(series, inverse=False):

        series = (

            series
            .replace([np.inf, -np.inf], np.nan)
            .fillna(series.median())

        )

        mn = series.min()
        mx = series.max()

        if mx == mn:

            return np.zeros(len(series))

        norm = (series - mn) / (mx - mn)

        if inverse:

            norm = 1 - norm

        return norm

    # =====================================================
    # WATER CLASS
    # =====================================================

    @staticmethod
    def classify(score):

        if score >= 0.70:
            return "HIGH"

        elif score >= 0.40:
            return "MEDIUM"

        return "LOW"

    # =====================================================
    # COMPUTE WATER FEASIBILITY
    # =====================================================

    def compute(self):

        print()
        print("=" * 70)
        print("WATER FEASIBILITY ENGINE")
        print("=" * 70)

        # -------------------------------------------------
        # Groundwater (smaller depth = better)
        # -------------------------------------------------

        groundwater = self.normalize(

            self.wards["mean_gw_depth_m"],

            inverse=True

        )

        # -------------------------------------------------
        # Rainfall (higher = better)
        # -------------------------------------------------

        rainfall = self.normalize(

            self.wards["mean_annual_rainfall_mm"]

        )

        # -------------------------------------------------
        # Water Tier
        # -------------------------------------------------

        tier_score = self.wards["water_tier"].map({

            "W1": 1.00,
            "W2": 0.75,
            "W3": 0.50,
            "W4": 0.25

        }).fillna(0.50)

        # -------------------------------------------------
        # Final Score
        # -------------------------------------------------

        self.wards["Water_Feasibility"] = (

              0.45 * groundwater
            + 0.35 * rainfall
            + 0.20 * tier_score

        ).round(3)

        # -------------------------------------------------
        # Water Class
        # -------------------------------------------------

        self.wards["Water_Class"] = (

            self.wards["Water_Feasibility"]

            .apply(self.classify)

        )

        print("✓ Water Feasibility Computed")

        return self.wards

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(self):

        print()

        print("=" * 70)
        print("WATER FEASIBILITY SUMMARY")
        print("=" * 70)

        print(

            self.wards["Water_Class"]

            .value_counts()

            .to_string()

        )

        print()

        print(

            "Average Score :",

            round(

                self.wards["Water_Feasibility"].mean(),

                3

            )

        )

        print()

        print(

            self.wards[[

                "ward_name",

                "Water_Feasibility",

                "Water_Class"

            ]]

            .head(10)

            .to_string(index=False)

        )

        print()

        print("=" * 70)