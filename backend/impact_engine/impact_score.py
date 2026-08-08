"""
==========================================================
CanopyAI
Impact Score Engine
==========================================================

Final AI Impact Score

Formula:

Impact Score = Benefit * Plantability

Benefit:
    Environmental improvement potential

Plantability:
    Actual plantation feasibility

If planting is impossible:
    Plantability = 0
    Impact Score = 0

Output:
    Impact Score (0-100)
==========================================================
"""


import numpy as np



class ImpactScoreEngine:



    def __init__(self):

        pass




    # ======================================================
    # COMPUTE IMPACT SCORE
    # ======================================================


    def compute(self, rasters):


        benefit = rasters["benefit"]


        plantability = rasters["plantability"]





        # ==================================================
        # FINAL FORMULA
        # ==================================================

        impact = (

            benefit *

            plantability

        )





        # Keep range 0-1

        impact = np.clip(

            impact,

            0,

            1

        )





        # Convert to 0-100

        impact = impact * 100





        # Safety:
        # No plantation possible = no impact

        impact[

            plantability == 0

        ] = 0





        rasters["impact_score"] = impact.astype(

            np.float32

        )



        return rasters







    # ======================================================
    # CLASSIFICATION
    # ======================================================


    @staticmethod
    def classify(score):


        classes = np.zeros_like(

            score,

            dtype=np.uint8

        )



        classes[score >= 80] = 4


        classes[

            (score >= 60) &

            (score < 80)

        ] = 3



        classes[

            (score >= 40) &

            (score < 60)

        ] = 2



        classes[

            (score >= 20) &

            (score < 40)

        ] = 1



        return classes






    # ======================================================
    # GENERATE FINAL OUTPUT
    # ======================================================


    def generate(self, rasters):


        rasters = self.compute(

            rasters

        )



        rasters["impact_class"] = self.classify(

            rasters["impact_score"]

        )



        return rasters






    # ======================================================
    # STATISTICS
    # ======================================================


    @staticmethod
    def statistics(rasters):


        img = rasters["impact_score"]



        print()


        print("="*70)


        print("IMPACT SCORE ENGINE")


        print("="*70)



        print(

            f"Impact Score "

            f"Min={np.nanmin(img):.2f} "

            f"Max={np.nanmax(img):.2f} "

            f"Mean={np.nanmean(img):.2f}"

        )



        unique, counts = np.unique(

            rasters["impact_class"],

            return_counts=True

        )



        print()


        print("Impact Classes")



        for u,c in zip(unique, counts):


            print(

                f"Class {u} : {c:,}"

            )



        print("="*70)