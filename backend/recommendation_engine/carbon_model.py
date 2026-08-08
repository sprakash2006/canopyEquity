"""
==========================================================
CanopyAI
Recommendation Engine
Carbon Model
==========================================================
"""

import numpy as np


class CarbonModel:

    def __init__(self, wards):

        self.wards = wards

    # =====================================================
    # COMPUTE
    # =====================================================

    def compute(self):

        print()
        print("=" * 70)
        print("CARBON MODEL")
        print("=" * 70)

        # Average mature tree absorbs ~25 kg CO₂/year

        self.wards["Annual_CO2_kg"] = (

            self.wards["Recommended_Trees"] * 25

        ).round(2)

        self.wards["Annual_CO2_Tons"] = (

            self.wards["Annual_CO2_kg"] / 1000

        ).round(2)

        self.wards["CO2_10Y_Tons"] = (

            self.wards["Annual_CO2_Tons"] * 10

        ).round(2)

        print("✓ Carbon Estimation Completed")

        return self.wards

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(self):

        print()

        print("=" * 70)
        print("CARBON SUMMARY")
        print("=" * 70)

        print(

            "Annual CO₂ (Tons) :",

            round(

                self.wards["Annual_CO2_Tons"].sum(),

                2

            )

        )

        print(

            "10 Year CO₂ (Tons):",

            round(

                self.wards["CO2_10Y_Tons"].sum(),

                2

            )

        )

        print("=" * 70)