"""
==========================================================
CanopyAI
Social Scoring Engine
==========================================================
"""

import numpy as np
import pandas as pd


class SocialScorer:

    def __init__(self):

        self.weights = {

            "population": 0.35,

            "slum": 0.30,

            "literacy": 0.20,

            "piped_water": 0.15

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

        population = self.normalize(

            df["total_population"]

        )

        slum = self.normalize(

            df["slum_households"]

        )

        literacy = 1 - self.normalize(

            df["literate_population"]

        )

        piped = 1 - self.normalize(

            df["households_piped_water_premises"]

        )

        score = (

            self.weights["population"] * population +

            self.weights["slum"] * slum +

            self.weights["literacy"] * literacy +

            self.weights["piped_water"] * piped

        )

        df["Social_Score"] = (

            score * 100

        ).round(2)

        return df