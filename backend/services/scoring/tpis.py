"""
==========================================================
CanopyAI
TPIS Intelligence Engine
(Tree Plantation Impact Score)
==========================================================
"""

import numpy as np
import pandas as pd


class TPISScorer:

    def __init__(self):

        # Final AI weights
        self.weights = {

            "environment": 0.40,

            "social": 0.35,

            "feasibility": 0.25

        }

        self.base_tree_cost = 200

        self.max_trees = 20000

        self.co2_per_tree = 25

    # ======================================================
    # NORMALIZATION
    # ======================================================

    @staticmethod
    def normalize(series):

        series = series.copy()

        series = series.fillna(series.median())

        mn = series.min()

        mx = series.max()

        if mn == mx:

            return pd.Series(
                np.zeros(len(series)),
                index=series.index
            )

        return (series - mn) / (mx - mn)

    # ======================================================
    # URBAN VULNERABILITY
    # ======================================================

    def calculate_uvs(self, df):

        population = self.normalize(

            df["total_population"]

        )

        slums = self.normalize(

            df["slum_households"]

        )

        heat = self.normalize(

            df["mean_land_surface_temperature_celsius"]

        )

        literacy = 1 - self.normalize(

            df["literate_population"]

        )

        uvs = (

            0.40 * population +

            0.30 * slums +

            0.20 * heat +

            0.10 * literacy

        )

        df["Urban_Vulnerability_Score"] = (

            uvs * 100

        ).round(2)

        return df

    # ======================================================
    # PRIORITY
    # ======================================================

    @staticmethod
    def priority(score):

        if score >= 85:
            return "VERY HIGH"

        if score >= 70:
            return "HIGH"

        if score >= 55:
            return "MEDIUM"

        return "LOW"

    # ======================================================
    # REASON
    # ======================================================

    @staticmethod
    def recommendation_reason(row):

        reasons = []

        if row.Environment_Score >= 75:
            reasons.append("Environmental Restoration")

        if row.Social_Score >= 75:
            reasons.append("High Social Need")

        if row.Feasibility_Score >= 70:
            reasons.append("Highly Feasible")

        if row.Urban_Vulnerability_Score >= 70:
            reasons.append("Urban Heat & Population Pressure")

        if len(reasons) == 0:
            reasons.append("General Greening Opportunity")

        return ", ".join(reasons)

    # ======================================================
    # MAIN ENGINE
    # ======================================================

    def calculate(self, df):

        df = self.calculate_uvs(df)

        # -----------------------
        # TPIS
        # -----------------------

        df["TPIS"] = (

            self.weights["environment"] * df["Environment_Score"]

            +

            self.weights["social"] * df["Social_Score"]

            +

            self.weights["feasibility"] * df["Feasibility_Score"]

        ).round(2)

        # -----------------------
        # Priority
        # -----------------------

        df["Priority"] = df["TPIS"].apply(

            self.priority

        )

        # -----------------------
        # Estimated Trees
        # -----------------------

        trees = (

            df["TPIS"]

            / 100

            * self.max_trees

        )

        trees = trees.fillna(0)

        df["Estimated_Trees"] = trees.astype(int)

        # -----------------------
        # Terrain factor
        # -----------------------

        terrain = (

            1

            +

            self.normalize(

                df["ridge_fraction"]

            ) * 0.20

        )

        water = (

            df["water_cost_multiplier"]

            .fillna(1)

        )

        # -----------------------
        # Cost
        # -----------------------

        cost = (

            df["Estimated_Trees"]

            *

            self.base_tree_cost

            *

            terrain

            *

            water

        )

        cost = cost.fillna(0)

        df["Estimated_Cost"] = cost.astype(int)

        # -----------------------
        # CO₂
        # -----------------------

        df["Estimated_CO2_10Y_kg"] = (

            df["Estimated_Trees"]

            *

            self.co2_per_tree

        )

        # -----------------------
        # Temperature
        # -----------------------

        df["Estimated_Temp_Reduction_C"] = (

            df["Estimated_Trees"]

            / 1000

        ) * 0.10

        # -----------------------
        # Reason
        # -----------------------

        df["Recommendation_Reason"] = df.apply(

            self.recommendation_reason,

            axis=1

        )

        return df