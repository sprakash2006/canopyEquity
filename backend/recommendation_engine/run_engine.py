"""
==========================================================
CanopyAI
Recommendation Engine
==========================================================
"""

from backend.recommendation_engine.loader import RecommendationLoader
from backend.recommendation_engine.tree_allocator import TreeAllocator
from backend.recommendation_engine.budget_optimizer import BudgetOptimizer
from backend.recommendation_engine.water_feasibility import WaterFeasibility
from backend.recommendation_engine.carbon_model import CarbonModel
from backend.recommendation_engine.cooling_model import CoolingModel
from backend.recommendation_engine.final_recommendation import FinalRecommendation
from backend.recommendation_engine.exporter import RecommendationExporter



def run():


    print("=" * 70)
    print("CANOPY AI - RECOMMENDATION ENGINE")
    print("=" * 70)



    # ======================================================
    # LOAD DATA
    # ======================================================

    loader = RecommendationLoader()

    datasets = loader.load_all()



    # ======================================================
    # TREE ALLOCATION
    # ======================================================

    allocator = TreeAllocator(
        datasets["wards"]
    )

    wards = allocator.allocate()


    print("\nTREE ALLOCATION COMPLETED")



    # ======================================================
    # BUDGET OPTIMIZATION
    # ======================================================

    budget = BudgetOptimizer(
        wards
    )

    wards = budget.compute()


    print("\nBUDGET OPTIMIZATION COMPLETED")



    # ======================================================
    # WATER
    # ======================================================

    water = WaterFeasibility(
        wards
    )

    wards = water.compute()


    print("\nWATER FEASIBILITY COMPLETED")



    # ======================================================
    # CARBON
    # ======================================================

    carbon = CarbonModel(
        wards
    )

    wards = carbon.compute()


    print("\nCARBON MODEL COMPLETED")



    # ======================================================
    # COOLING
    # ======================================================

    cooling = CoolingModel(
        wards
    )

    wards = cooling.compute()


    print("\nCOOLING MODEL COMPLETED")



    # ======================================================
    # FINAL RECOMMENDATION
    # ======================================================

    final = FinalRecommendation(
        wards
    )

    wards = final.compute()


    print("\nFINAL RECOMMENDATION COMPLETED")



    # ======================================================
    # EXPORT
    # ======================================================

    exporter = RecommendationExporter(
        wards
    )

    exporter.export()



    print("\nEXPORT COMPLETED")



    # ======================================================
    # RETURN API RESPONSE
    # ======================================================

    return {


        "status":"success",


        "message":
        "Recommendation Engine completed successfully",



        "outputs":{


            "top10_recommendations":
            "outputs/top10_recommendations.json",


            "final_recommendations":
            "outputs/final_recommendations.csv",


            "optimized_plan":
            "outputs/optimized_plan.csv",


            "summary":
            "outputs/recommendation_summary.json"

        },


        "sample": wards[:5]


    }



if __name__=="__main__":

    run()