"""
==========================================================
CanopyAI
Environmental Scoring Engine
==========================================================
"""

import numpy as np
import pandas as pd


class EnvironmentScorer:

    def __init__(self):

        self.weights = {

            "canopy": 0.30,

            "temperature": 0.25,

            "ndvi": 0.20,

            "bare": 0.10,

            "rainfall": 0.10,

            "cropland": 0.05

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
    # SCORE
    # ======================================================

    def calculate(self, df):

        canopy = 1 - self.normalize(

            df["worldcover_canopy_fraction"]

        )

        temperature = self.normalize(

            df["mean_land_surface_temperature_celsius"]

        )

        ndvi = 1 - self.normalize(

            df["mean_normalized_difference_vegetation_index"]

        )

        bare = self.normalize(

            df["worldcover_bare_or_other_fraction"]

        )

        rainfall = self.normalize(

            df["mean_annual_rainfall_millimeters"]

        )

        cropland = self.normalize(

            df["cropland_fraction"]

        )

        score = (

            self.weights["canopy"] * canopy +

            self.weights["temperature"] * temperature +

            self.weights["ndvi"] * ndvi +

            self.weights["bare"] * bare +

            self.weights["rainfall"] * rainfall +

            self.weights["cropland"] * cropland

        )

        df["Environment_Score"] = (

            score * 100

        ).round(2)

        return df