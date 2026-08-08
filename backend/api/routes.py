"""
==========================================================
CanopyAI
API Routes
==========================================================
"""


from fastapi import APIRouter, UploadFile, File

from fastapi.encoders import jsonable_encoder

from backend.api.services import AIService

from backend.api.pipeline_state import get_pipeline


import numpy as np
import pandas as pd
import math






# ==========================================================
# UNIVERSAL JSON CLEANER
# ==========================================================


def clean_json(obj):


    if obj is None:

        return None



    # Dictionary

    if isinstance(obj, dict):

        return {

            str(k): clean_json(v)

            for k,v in obj.items()

        }




    # List

    if isinstance(obj, list):

        return [

            clean_json(x)

            for x in obj

        ]




    # Tuple

    if isinstance(obj, tuple):

        return [

            clean_json(x)

            for x in obj

        ]





    # Pandas dataframe

    if isinstance(obj, pd.DataFrame):

        return clean_json(

            obj.to_dict(
                orient="records"
            )

        )






    # Pandas series

    if isinstance(obj, pd.Series):

        return clean_json(

            obj.tolist()

        )







    # Numpy array

    if isinstance(obj,np.ndarray):

        return clean_json(

            obj.tolist()

        )







    # Numpy integer

    if isinstance(obj,np.integer):

        return int(obj)







    # Numpy float

    if isinstance(obj,np.floating):


        value=float(obj)


        if math.isnan(value) or math.isinf(value):

            return None


        return value







    # Normal python float

    if isinstance(obj,float):


        if math.isnan(obj) or math.isinf(obj):

            return None


        return obj






    return obj










# ==========================================================
# ROUTER
# ==========================================================


router = APIRouter()


service = AIService()








# ==========================================================
# ROOT
# ==========================================================


@router.get("/")
def root():

    return {

        "project":"CanopyAI",

        "status":"Running",

        "version":"1.0.0"

    }










# ==========================================================
# HEALTH
# ==========================================================


@router.get("/health")
def health():

    return jsonable_encoder(

        clean_json(
            service.health()
        )

    )










# ==========================================================
# UPLOAD
# ==========================================================


@router.post("/upload")
async def upload(
    
    file:UploadFile = File(...)

):

    result = await service.upload(file)

    return jsonable_encoder(

        clean_json(result)

    )










# ==========================================================
# PREDICT
# ==========================================================


@router.post("/predict")
def predict():


    print("RUNNING PREDICTION API")



    result = service.predict()



    cleaned = clean_json(result)



    return jsonable_encoder(

        cleaned

    )










# ==========================================================
# DASHBOARD
# ==========================================================


@router.get("/dashboard")
def dashboard():

    return jsonable_encoder(

        clean_json(

            service.dashboard()

        )

    )










# ==========================================================
# STATISTICS
# ==========================================================


@router.get("/statistics")
def statistics():

    return jsonable_encoder(

        clean_json(

            service.statistics()

        )

    )










# ==========================================================
# RECOMMENDATIONS
# ==========================================================


@router.get("/recommendations")
def recommendations():

    return jsonable_encoder(

        clean_json(

            service.recommendations()

        )

    )










# ==========================================================
# WARD RANKINGS
# ==========================================================


@router.get("/ward-rankings")
def ward_rankings():

    return jsonable_encoder(

        clean_json(

            service.ward_rankings()

        )

    )










# ==========================================================
# STATUS
# ==========================================================


@router.get("/status")
def status():

    return jsonable_encoder(

        clean_json(

            service.status()

        )

    )










# ==========================================================
# PIPELINE STATUS
# ==========================================================


@router.get("/pipeline-status")
def pipeline_status():

    return jsonable_encoder({

        "status":"success",

        "pipeline":clean_json(

            get_pipeline()

        )

    })