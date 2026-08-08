pipeline_status = {

    "upload": {
        "name": "Satellite Upload",
        "status": "pending"
    },

    "ai_engine": {
        "name": "AI Segmentation Engine",
        "status": "pending"
    },

    "impact_engine": {
        "name": "Impact Analysis Engine",
        "status": "pending"
    },

    "ward_engine": {
        "name": "Ward Ranking Engine",
        "status": "pending"
    },

    "recommendation_engine": {
        "name": "Recommendation Engine",
        "status": "pending"
    },

    "export": {
        "name": "Export Results",
        "status": "pending"
    }

}


def update_pipeline(step, status):

    pipeline_status[step]["status"] = status


def get_pipeline():

    return pipeline_status