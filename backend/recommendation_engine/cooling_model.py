"""
==========================================================
CanopyAI
Recommendation Engine
Cooling Model
==========================================================
"""

import numpy as np


class CoolingModel:

    def __init__(self, wards):

        self.wards = wards

    # =====================================================
    # COMPUTE
    # =====================================================

    def compute(self):

        print()
        print("=" * 70)
        print("COOLING MODEL")
        print("=" * 70)

        # ---------------------------------------------
        # Estimated Cooling
        # ---------------------------------------------
        # Assumption:
        # 20,000 trees ≈ 2°C local cooling
        # Scale linearly and cap at 2°C
        # ---------------------------------------------

        cooling = (

            self.wards["Recommended_Trees"]

            / 20000

        ) * 2.0

        self.wards["Estimated_Cooling_C"] = (

            cooling

            .clip(upper=2.0)

            .round(2)

        )

        print("✓ Cooling Estimation Completed")

        return self.wards

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(self):

        print()

        print("=" * 70)
        print("COOLING SUMMARY")
        print("=" * 70)

        print(

            "Average Cooling :",

            round(

                self.wards["Estimated_Cooling_C"].mean(),

                2

            ),

            "°C"

        )

        print(

            "Maximum Cooling :",

            round(

                self.wards["Estimated_Cooling_C"].max(),

                2

            ),

            "°C"

        )

        print(

            "Minimum Cooling :",

            round(

                self.wards["Estimated_Cooling_C"].min(),

                2

            ),

            "°C"

        )

        print("=" * 70)