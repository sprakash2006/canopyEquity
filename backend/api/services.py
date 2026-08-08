"""
==========================================================
CanopyAI
API Services
==========================================================
"""


import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd


from backend.ai_engine.run_engine import run as run_ai
from backend.impact_engine.run_engine import run as run_impact
from backend.ward_engine.run_engine import run as run_ward
from backend.recommendation_engine.run_engine import run as run_recommendation


from backend.api.pipeline_state import update_pipeline





class AIService:


    def __init__(self):


        self.outputs = Path(
            "outputs"
        )


        self.uploads = Path(
            "uploads"
        )


        self.outputs.mkdir(
            exist_ok=True
        )


        self.uploads.mkdir(
            exist_ok=True
        )



        self.prediction_file = (
            self.outputs /
            "canopy_prediction.tif"
        )


        self.dashboard_file = (
            self.outputs /
            "dashboard_data.json"
        )


        self.statistics_file = (
            self.outputs /
            "summary_report.json"
        )


        self.recommendation_file = (
            self.outputs /
            "top10_recommendations.json"
        )


        self.final_recommendation_file = (
            self.outputs /
            "final_recommendations.csv"
        )


        self.ward_file = (
            self.outputs /
            "ward_rankings.geojson"
        )




    # =========================================
    # READ JSON
    # =========================================


    def _read_json(self,file_path):


        if not file_path.exists():

            return None



        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:


            return json.load(file)




    # =========================================
    # SERIALIZER
    # =========================================


    def make_json_serializable(self,obj):


        if obj is None:

            return None



        if isinstance(obj,dict):

            return {

                k:
                self.make_json_serializable(v)

                for k,v in obj.items()

            }



        if isinstance(obj,list):

            return [

                self.make_json_serializable(x)

                for x in obj

            ]



        if isinstance(obj,np.integer):

            return int(obj)



        if isinstance(obj,np.floating):

            return float(obj)



        return obj

    # =========================================
    # HEALTH
    # =========================================


    def health(self):


        return {


            "status":
            "healthy",


            "service":
            "CanopyAI Backend"


        }





    # =========================================
    # UPLOAD
    # =========================================


    async def upload(self,file):


        try:


            save_path = (
                self.uploads /
                file.filename
            )



            with open(
                save_path,
                "wb"
            ) as buffer:


                shutil.copyfileobj(
                    file.file,
                    buffer
                )



            update_pipeline(
                "upload",
                "completed"
            )



            return {


                "status":
                "success",


                "filename":
                file.filename


            }



        except Exception as e:


            return {


                "status":
                "error",


                "message":
                str(e)


            }






    # =========================================
    # RUN COMPLETE AI PIPELINE
    # =========================================


    def predict(self):


        try:



            update_pipeline(
                "ai_engine",
                "running"
            )


            ai_result = run_ai()



            update_pipeline(
                "ai_engine",
                "completed"
            )



            update_pipeline(
                "impact_engine",
                "running"
            )


            impact_result = run_impact()



            update_pipeline(
                "impact_engine",
                "completed"
            )



            update_pipeline(
                "ward_engine",
                "running"
            )


            ward_result = run_ward()



            update_pipeline(
                "ward_engine",
                "completed"
            )



            update_pipeline(
                "recommendation_engine",
                "running"
            )


            recommendation_result = run_recommendation()



            update_pipeline(
                "recommendation_engine",
                "completed"
            )



            update_pipeline(
                "export",
                "completed"
            )



            return {


                "status":
                "success",


                "message":
                "AI Pipeline Completed",


                "ai":
                self.make_json_serializable(
                    ai_result
                ),


                "impact":
                self.make_json_serializable(
                    impact_result
                ),


                "ward":
                self.make_json_serializable(
                    ward_result
                ),


                "recommendation":
                self.make_json_serializable(
                    recommendation_result
                )


            }




        except Exception as e:


            return {


                "status":
                "error",


                "message":
                str(e)


            }

    # =========================================
    # DASHBOARD
    # =========================================


    def dashboard(self):


        try:


            dashboard_data = self._read_json(
                self.dashboard_file
            )


            summary_data = self._read_json(
                self.statistics_file
            )



            return {


                "status":
                "success",


                "dashboard":

                dashboard_data
                if dashboard_data
                else [],



                "summary":

                summary_data
                if summary_data
                else {}

            }



        except Exception as e:


            return {


                "status":
                "error",


                "message":
                str(e)


            }





    # =========================================
    # STATISTICS
    # =========================================


    def statistics(self):


        data = self._read_json(
            self.statistics_file
        )


        return {


            "status":
            "success",


            "statistics":

            data
            if data
            else {}

        }





    # =========================================
    # RECOMMENDATIONS
    # =========================================


        # =========================================
    # RECOMMENDATIONS
    # =========================================

    def recommendations(self):


        try:


            file = self.final_recommendation_file



            if not file.exists():


                return {


                    "status": "error",


                    "message": "final_recommendations.csv not found",


                    "recommendations": []


                }




            df = pd.read_csv(file)



            print(
                "CSV COLUMNS:"
            )


            print(
                df.columns.tolist()
            )



            # remove NaN values

            df = df.fillna(0)



            recommendations = df.to_dict(

                orient="records"

            )



            return {


                "status": "success",


                "recommendations": recommendations


            }





        except Exception as e:



            print(
                "RECOMMENDATION ERROR:",
                e
            )



            return {


                "status": "error",


                "message": str(e),


                "recommendations": []


            }



    # =========================================
    # WARD RANKINGS
    # =========================================


    def ward_rankings(self):


        try:


            data = self._read_json(
                self.ward_file
            )


            return {


                "status":
                "success",


                "data":

                data
                if data
                else {}

            }




        except Exception as e:


            return {


                "status":
                "error",


                "message":
                str(e)


            }

    # =========================================
    # SYSTEM STATUS
    # =========================================


    def status(self):


        return {


            "status":
            "online",


            "service":
            "CanopyAI",


            "files": {


                "prediction":
                self.prediction_file.exists(),


                "dashboard":
                self.dashboard_file.exists(),


                "statistics":
                self.statistics_file.exists(),


                "recommendations":
                self.final_recommendation_file.exists(),


                "ward_rankings":
                self.ward_file.exists()


            }


        }                              
