"""
==========================================================
CanopyAI
Plantability Engine
==========================================================

Purpose:
Calculates pixel-level suitability for tree plantation.

Logic:
- Built-up areas cannot be planted -> 0
- Existing trees do not need plantation -> 0
- Open land is best -> 1
- Bare land has potential -> 0.8

Output:
rasters["plantability"] (0-1)
==========================================================
"""

import numpy as np



class PlantabilityEngine:


    """
    Computes plantation feasibility
    from land cover and water availability.
    """



    def __init__(self):

        pass




    # ======================================================
    # LAND COVER SUITABILITY
    # ======================================================


    @staticmethod
    def landcover_score(landcover):


        score = np.zeros_like(

            landcover,

            dtype=np.float32

        )



        # --------------------------------------------------
        # 0 = Built-up
        # No available planting space
        # --------------------------------------------------

        score[landcover == 0] = 0.0




        # --------------------------------------------------
        # 1 = Existing Tree
        # Already green
        # No new plantation required
        # --------------------------------------------------

        score[landcover == 1] = 0.0




        # --------------------------------------------------
        # 2 = Grass / Open Area
        # Best plantation location
        # --------------------------------------------------

        score[landcover == 2] = 1.0




        # --------------------------------------------------
        # 3 = Bare Land
        # High plantation potential
        # --------------------------------------------------

        score[landcover == 3] = 0.8




        return score







    # ======================================================
    # WATER AVAILABILITY SCORE
    # ======================================================


    @staticmethod
    def water_score(rainfall):


        rainfall = rainfall.astype(

            np.float32

        )



        min_val = np.nanmin(

            rainfall

        )


        max_val = np.nanmax(

            rainfall

        )



        normalized = (

            rainfall - min_val

        ) / (

            max_val - min_val + 1e-8

        )



        return np.clip(

            normalized,

            0,

            1

        )








    # ======================================================
    # FINAL PLANTABILITY
    # ======================================================


    def compute(self, rasters):


        landcover = rasters["landcover"]



        # Land suitability

        land_score = self.landcover_score(

            landcover

        )



        # Water availability

        water = self.water_score(

            rasters["rainfall"]

        )





        # ==================================================
        # FINAL FORMULA
        # ==================================================

        plantability = (

            0.85 * land_score +

            0.15 * water

        )




        # ==================================================
        # NDVI SANITY CORRECTION
        # ==================================================
        # A pixel with high NDVI already has vegetation
        # regardless of the land-cover class.  This catches
        # dense-canopy areas the classifier mislabels as
        # "grass" (Cantonment Ridge, Lutyens' Delhi) and
        # stops them from scoring as prime plantation sites.

        ndvi = rasters.get("ndvi")

        if ndvi is not None:

            # NDVI ≥ 0.4 -> already vegetated -> plant = 0
            # NDVI ≤ 0.1 -> bare -> no penalty
            # linear in between.

            existing_veg = np.clip(

                (ndvi - 0.1) / 0.3,

                0.0,

                1.0

            )


            # Unknown NDVI -> treat as partially vegetated,
            # so we don't hand out prime scores in data-gap
            # zones (Cantonment, restricted areas, etc.)

            existing_veg = np.where(

                np.isnan(existing_veg),

                0.5,

                existing_veg

            )


            plantability = plantability * (1.0 - existing_veg)






        # ==================================================
        # HARD CONSTRAINT
        # ==================================================

        # Built-up = impossible to plant

        plantability[

            landcover == 0

        ] = 0.0




        # Existing vegetation

        plantability[

            landcover == 1

        ] = 0.0






        # Keep range 0-1

        plantability = np.clip(

            plantability,

            0,

            1

        )





        rasters["plantability"] = plantability



        return rasters







    # ======================================================
    # STATISTICS
    # ======================================================


    @staticmethod
    def statistics(rasters):


        img = rasters["plantability"]



        print()

        print("=" * 70)

        print("PLANTABILITY ENGINE")

        print("=" * 70)



        print(

            f"Plantability "

            f"Min={np.nanmin(img):.3f} "

            f"Max={np.nanmax(img):.3f} "

            f"Mean={np.nanmean(img):.3f}"

        )


        print("=" * 70)