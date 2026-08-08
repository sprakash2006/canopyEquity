"""
==========================================================
CanopyAI
Recommendation Engine
Budget Optimizer
==========================================================
"""

import numpy as np


class BudgetOptimizer:

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
            return np.zeros(len(series))

        return (series - mn) / (mx - mn)

    # =====================================================
    # COMPUTE BUDGET
    # =====================================================

    def compute(self):

        print()
        print("=" * 70)
        print("BUDGET OPTIMIZER")
        print("=" * 70)

        impact = self.normalize(

            self.wards["Composite_Score"]

        )

        # ₹200 per tree
        base_budget = (

            self.wards["Recommended_Trees"] * 200

        )

        # High-priority wards receive up to 20% additional budget
        multiplier = 1 + (impact * 0.20)

        self.wards["Estimated_Budget"] = (

            base_budget * multiplier

        ).round(0).astype(int)

        print("✓ Budget Optimization Completed")

        return self.wards

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(self):

        print()

        print("=" * 70)
        print("BUDGET SUMMARY")
        print("=" * 70)

        print(
            "Total Budget : ₹{:,.0f}".format(
                self.wards["Estimated_Budget"].sum()
            )
        )

        print(
            "Average Budget/Ward : ₹{:,.0f}".format(
                self.wards["Estimated_Budget"].mean()
            )
        )

        print(
            "Highest Budget : ₹{:,.0f}".format(
                self.wards["Estimated_Budget"].max()
            )
        )

        print(
            "Lowest Budget : ₹{:,.0f}".format(
                self.wards["Estimated_Budget"].min()
            )
        )

        print("=" * 70)