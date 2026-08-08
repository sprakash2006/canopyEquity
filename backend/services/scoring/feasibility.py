"""
==========================================================
CanopyAI
Plantation Feasibility Scoring Engine
==========================================================
"""

import numpy as np
import pandas as pd


class FeasibilityScorer:

    def __init__(self):

        self.weights = {

            "groundwater": 0.30,

            "rainfall": 0.20,

            "water_distance": 0.20,

            "water_cost": 0.15,

            "ridge": 0.10,

            "water_tier": 0.05

        }

    # ======================================================
    # NORMALIZATION
    # ======================================================

    @staticmethod
    def normalize(series):

        series = series.copy()

        series = series.fillna(series.median())

        minimum = series.min()

        maximum = series.max()

        if minimum == maximum:

            return pd.Series(
                np.zeros(len(series)),
                index=series.index
            )

        return (series - minimum) / (maximum - minimum)

    # ======================================================
    # WATER TIER SCORE
    # ======================================================

    @staticmethod
    def encode_water_tier(series):

        values = series.astype(str).str.lower().str.strip()

        mapping = {

            "high": 1.00,
            "medium": 0.70,
            "low": 0.40,

            # numeric values if present
            "1": 1.00,
            "2": 0.70,
            "3": 0.40

        }

        return values.map(mapping).fillna(0.50)

    # ======================================================
    # SCORE
    # ======================================================

    def calculate(self, df):

        groundwater = 1 - self.normalize(

            df["mean_groundwater_depth_meters"]

        )

        rainfall = self.normalize(

            df["mean_annual_rainfall_millimeters"]

        )

        water_distance = 1 - self.normalize(

            df["distance_to_water_body_meters"]

        )

        water_cost = 1 - self.normalize(

            df["water_cost_multiplier"]

        )

        ridge = 1 - self.normalize(

            df["ridge_fraction"]

        )

        tier = self.encode_water_tier(

            df["water_tier"]

        )

        score = (

            self.weights["groundwater"] * groundwater +

            self.weights["rainfall"] * rainfall +

            self.weights["water_distance"] * water_distance +

            self.weights["water_cost"] * water_cost +

            self.weights["ridge"] * ridge +

            self.weights["water_tier"] * tier

        )

        df["Feasibility_Score"] = (

            score * 100

        ).round(2)

        return df