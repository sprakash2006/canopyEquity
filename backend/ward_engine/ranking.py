"""
==========================================================
CanopyAI
Ward Ranking Engine
==========================================================
"""

import numpy as np


class WardRanking:

    def __init__(self, wards):

        self.wards = wards

    # =====================================================
    # NORMALIZATION
    # =====================================================

    @staticmethod
    def normalize(series):

        # Replace invalid values
        series = (

            series

            .replace([np.inf, -np.inf], np.nan)

            .fillna(0)

        )

        mn = series.min()

        mx = series.max()

        if mx == mn:

            return np.zeros(len(series))

        return (

            series - mn

        ) / (

            mx - mn

        )

    # =====================================================
    # PRIORITY CLASS
    # =====================================================

    @staticmethod
    def priority(score):

        if score >= 80:
            return "VERY HIGH"

        elif score >= 65:
            return "HIGH"

        elif score >= 45:
            return "MEDIUM"

        return "LOW"

    # =====================================================
    # COMPUTE RANKING
    # =====================================================

    def compute(self):

        print()

        print("=" * 70)

        print("COMPUTING WARD RANKINGS")

        print("=" * 70)

        # =================================================
        # HANDLE MISSING VALUES
        # =================================================

        numeric_cols = [

            "Impact_Mean",

            "Impact_Max",

            "Impact_Median",

            "Pixel_Count"

        ]

        for col in numeric_cols:

            self.wards[col] = (

                self.wards[col]

                .replace([np.inf, -np.inf], np.nan)

                .fillna(0)

            )

        # =================================================
        # NORMALIZED FEATURES
        # =================================================

        mean = self.normalize(

            self.wards["Impact_Mean"]

        )

        maximum = self.normalize(

            self.wards["Impact_Max"]

        )

        median = self.normalize(

            self.wards["Impact_Median"]

        )

        pixels = self.normalize(

            self.wards["Pixel_Count"]

        )

        # =================================================
        # COMPOSITE SCORE
        # =================================================

        self.wards["Composite_Score"] = (

              0.60 * mean
            + 0.20 * maximum
            + 0.10 * median
            + 0.10 * pixels

        ) * 100

        # Safety check

        self.wards["Composite_Score"] = (

            self.wards["Composite_Score"]

            .replace([np.inf, -np.inf], np.nan)

            .fillna(0)

        )

        # =================================================
        # SORT
        # =================================================

        self.wards = self.wards.sort_values(

            "Composite_Score",

            ascending=False

        ).reset_index(drop=True)

        # =================================================
        # RANK
        # =================================================

        self.wards["Rank"] = np.arange(

            1,

            len(self.wards) + 1

        )

        self.wards["Percentile"] = (

            self.wards["Composite_Score"]

            .rank(

                pct=True

            ) * 100

        ).round(2)

        self.wards["Priority"] = (

            self.wards["Composite_Score"]

            .apply(

                self.priority

            )

        )

        print("✓ Ward Ranking Completed")

        return self.wards

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(self):

        print()

        print("=" * 70)

        print("TOP 10 WARDS")

        print("=" * 70)

        cols = [

            "Rank",

            "ward_name",

            "Composite_Score",

            "Priority"

        ]

        print(

            self.wards[cols]

            .head(10)

            .to_string(index=False)

        )

        print()

        print("=" * 70)

        print("WARD RANKING SUMMARY")

        print("=" * 70)

        print(f"Total Wards       : {len(self.wards)}")

        print(f"Highest Score     : {self.wards['Composite_Score'].max():.2f}")

        print(f"Lowest Score      : {self.wards['Composite_Score'].min():.2f}")

        print(f"Average Score     : {self.wards['Composite_Score'].mean():.2f}")

        print("=" * 70)