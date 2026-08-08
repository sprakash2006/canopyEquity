"""
==========================================================
CanopyAI
Recommendation Engine
Final Recommendation Engine
==========================================================
"""

import numpy as np


class FinalRecommendation:

    def __init__(self, wards):

        self.wards = wards

    # =====================================================
    # NORMALIZATION
    # =====================================================

    @staticmethod
    def normalize(series):

        mn = series.min()
        mx = series.max()

        if mx == mn:
            return np.ones(len(series))

        return (series - mn) / (mx - mn)

    # =====================================================
    # PRIORITY
    # =====================================================

    @staticmethod
    def classify(score):

        if score >= 80:
            return "VERY HIGH"

        elif score >= 60:
            return "HIGH"

        elif score >= 40:
            return "MEDIUM"

        return "LOW"

    # =====================================================
    # COMPUTE
    # =====================================================

    def compute(self):

        print()
        print("=" * 70)
        print("FINAL RECOMMENDATION ENGINE")
        print("=" * 70)

        impact = self.normalize(
            self.wards["Composite_Score"]
        )

        water = self.normalize(
            self.wards["Water_Feasibility"]
        )

        carbon = self.normalize(
            self.wards["Annual_CO2_Tons"]
        )

        cooling = self.normalize(
            self.wards["Estimated_Cooling_C"]
        )

        budget = 1 - self.normalize(
            self.wards["Estimated_Budget"]
        )

        self.wards["Final_Score"] = (

              0.35 * impact
            + 0.20 * water
            + 0.20 * carbon
            + 0.15 * cooling
            + 0.10 * budget

        ) * 100

        self.wards["Final_Score"] = (

            self.wards["Final_Score"]

            .round(2)

        )

        self.wards = self.wards.sort_values(

            "Final_Score",

            ascending=False

        ).reset_index(drop=True)

        self.wards["Final_Rank"] = np.arange(

            1,

            len(self.wards)+1

        )

        self.wards["Recommendation"] = (

            self.wards["Final_Score"]

            .apply(self.classify)

        )

        print("✓ Final Recommendation Generated")

        return self.wards

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(self):

        print()

        print("=" * 70)
        print("TOP 10 RECOMMENDED WARDS")
        print("=" * 70)

        print(

            self.wards[[

                "Final_Rank",

                "ward_name",

                "Final_Score",

                "Recommendation"

            ]]

            .head(10)

            .to_string(index=False)

        )

        print("=" * 70)