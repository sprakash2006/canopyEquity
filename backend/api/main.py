"""
==========================================================
CanopyAI
FastAPI Backend
==========================================================
"""


from pathlib import Path


from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles



from backend.api.routes import router




app = FastAPI(

    title="CanopyAI API",

    description="AI Powered Urban Tree Canopy Analysis",

    version="1.0.0"

)





# ==========================================================
# CORS
# ==========================================================


app.add_middleware(


    CORSMiddleware,


    allow_origins=[

        "http://localhost:5173"

    ],


    allow_credentials=True,


    allow_methods=[

        "*"

    ],


    allow_headers=[

        "*"

    ]

)






# ==========================================================
# DIRECTORIES
# ==========================================================


OUTPUT_DIR = Path("outputs")

UPLOAD_DIR = Path("uploads")



OUTPUT_DIR.mkdir(
    exist_ok=True
)


UPLOAD_DIR.mkdir(
    exist_ok=True
)







# ==========================================================
# STATIC FILE SERVING
# ==========================================================


app.mount(


    "/outputs",


    StaticFiles(

        directory="outputs"

    ),


    name="outputs"


)




app.mount(


    "/uploads",


    StaticFiles(

        directory="uploads"

    ),


    name="uploads"


)








# ==========================================================
# ROOT
# ==========================================================


@app.get("/")

def root():


    return {


        "project":

        "CanopyAI",


        "status":

        "Running",


        "version":

        "1.0.0"


    }







# ==========================================================
# API ROUTES
# ==========================================================


app.include_router(router)