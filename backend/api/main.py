from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api.routes import router
from backend.api.report import router as report_router


# ==========================================================
# APPLICATION
# ==========================================================

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
    parents=True,
    exist_ok=True
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================================
# REPORT DIRECTORY
# ==========================================================

REPORT_DIR = OUTPUT_DIR / "reports"

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================================
# STATIC FILE SERVING
# ==========================================================

app.mount(
    "/outputs",

    StaticFiles(
        directory=str(OUTPUT_DIR)
    ),

    name="outputs"
)


app.mount(
    "/uploads",

    StaticFiles(
        directory=str(UPLOAD_DIR)
    ),

    name="uploads"
)


# ==========================================================
# ROOT
# ==========================================================

@app.get("/")
def root():

    return {
        "project": "CanopyAI",
        "status": "Running",
        "version": "1.0.0"
    }


# ==========================================================
# EXISTING CANOPYAI API ROUTES
# ==========================================================

app.include_router(router)


# ==========================================================
# FINAL AI REPORT ROUTES
# ==========================================================

app.include_router(report_router)