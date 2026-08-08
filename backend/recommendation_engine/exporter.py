"""
==========================================================
CanopyAI
Recommendation Engine
Exporter
==========================================================
"""

from pathlib import Path
import json


class RecommendationExporter:


    def __init__(self, wards):

        self.wards = wards

        self.output_dir = Path("outputs")

        self.output_dir.mkdir(exist_ok=True)



    # =====================================================
    # EXPORT
    # =====================================================

    def export(self):


        print()

        print("=" * 70)
        print("EXPORTING RECOMMENDATIONS")
        print("=" * 70)



        # =================================================
        # CSV EXPORT
        # =================================================

        csv_path = self.output_dir / "final_recommendations.csv"


        self.wards.to_csv(

            csv_path,

            index=False

        )


        print(f"Saved : {csv_path}")




        # =================================================
        # FRONTEND JSON FORMAT
        # =================================================


        frontend_data=[]


        for _,row in self.wards.head(10).iterrows():


            frontend_data.append({


                "name":

                row.get(
                    "Ward_Name",
                    row.get("name","Unknown")
                ),



                "priority":

                row.get(
                    "Priority",
                    "VERY HIGH"
                ),



                "score":

                float(
                    row.get(
                        "Impact_Score",
                        row.get("score",0)
                    )
                ),



                "trees":

                int(
                    row.get(
                        "Recommended_Trees",
                        0
                    )
                ),



                "budget":

                float(
                    row.get(
                        "Estimated_Budget",
                        0
                    )
                ),



                "cooling":

                str(
                    row.get(
                        "Estimated_Cooling_C",
                        "0"
                    )
                ) + "°C"

            })



        top10_path = (

            self.output_dir /
            "top10_recommendations.json"

        )


        with open(

            top10_path,

            "w",

            encoding="utf-8"

        ) as f:


            json.dump(

                frontend_data,

                f,

                indent=4

            )


        print(
            f"Saved : {top10_path}"
        )




        # =================================================
        # DASHBOARD JSON
        # =================================================


        dashboard_path = (

            self.output_dir /
            "dashboard_recommendations.json"

        )


        self.wards.to_json(

            dashboard_path,

            orient="records",

            indent=2

        )


        print(
            f"Saved : {dashboard_path}"
        )




        # =================================================
        # SUMMARY
        # =================================================


        summary={


            "total_wards":

            int(len(self.wards)),



            "total_trees":

            int(
                self.wards[
                    "Recommended_Trees"
                ].sum()
            ),



            "total_budget":

            float(
                self.wards[
                    "Estimated_Budget"
                ].sum()
            ),



            "annual_co2_tons":

            float(
                self.wards[
                    "Annual_CO2_Tons"
                ].sum()
            ),



            "ten_year_co2_tons":

            float(
                self.wards[
                    "CO2_10Y_Tons"
                ].sum()
            ),



            "average_cooling":

            float(
                self.wards[
                    "Estimated_Cooling_C"
                ].mean()
            )

        }



        summary_path=(

            self.output_dir /
            "recommendation_summary.json"

        )


        with open(

            summary_path,

            "w"

        ) as f:


            json.dump(

                summary,

                f,

                indent=4

            )



        print(
            f"Saved : {summary_path}"
        )



        print()

        print("=" * 70)
        print("ALL FILES EXPORTED")
        print("=" * 70)