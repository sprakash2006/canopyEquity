"""
==========================================================
CanopyAI
Benefit Engine
==========================================================

Environmental Benefit Score

Higher score =
More environmental benefit after plantation

Factors:
- Heat stress
- Canopy deficit
- Population vulnerability
- Vegetation deficit

Output:
rasters["benefit"] (0-1)
==========================================================
"""


import numpy as np



class BenefitEngine:



    def __init__(self):


        self.weights = {


            # Heat stress contribution

            "heat": 0.35,


            # Existing canopy deficiency

            "canopy": 0.30,


            # Human vulnerability

            "vulnerability": 0.20,


            # Vegetation deficit

            "vegetation": 0.15


        }





    # =====================================================
    # COMPUTE BENEFIT SCORE
    # =====================================================


    def compute(self, rasters):



        heat = np.nan_to_num(

            rasters["lst"],

            nan=0

        )



        canopy = np.nan_to_num(

            rasters["canopy_deficit"],

            nan=0

        )



        vulnerability = np.nan_to_num(

            rasters["vulnerability"],

            nan=0

        )



        ndvi = np.nan_to_num(

            rasters["ndvi"],

            nan=0

        )



        # Low vegetation means
        # higher plantation benefit

        vegetation = 1 - ndvi





        # =================================================
        # FINAL BENEFIT FORMULA
        # =================================================


        benefit = (


            self.weights["heat"]

            *

            heat



            +

            

            self.weights["canopy"]

            *

            canopy



            +



            self.weights["vulnerability"]

            *

            vulnerability



            +



            self.weights["vegetation"]

            *

            vegetation


        )






        # Keep between 0-1

        benefit = np.clip(


            benefit,


            0,


            1


        )






        rasters["benefit"] = benefit.astype(


            np.float32


        )



        return rasters







    # =====================================================
    # STATISTICS
    # =====================================================


    @staticmethod
    def statistics(rasters):


        img = rasters["benefit"]



        print()


        print("=" * 70)


        print("BENEFIT ENGINE")


        print("=" * 70)



        print(


            f"Benefit "

            f"Min={np.nanmin(img):.3f} "

            f"Max={np.nanmax(img):.3f} "

            f"Mean={np.nanmean(img):.3f}"


        )



        print("=" * 70)