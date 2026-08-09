from pathlib import Path
import subprocess
import sys

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse


router = APIRouter(
    prefix="/report",
    tags=["Report"]
)


# ============================================================
# PROJECT PATHS
# ============================================================

# report.py is:
#
# CanopyAI/
#   backend/
#       api/
#           report.py
#
# parents[0] = api
# parents[1] = backend
# parents[2] = CanopyAI

PROJECT_ROOT = Path(__file__).resolve().parents[2]

REPORT_ENGINE = (
    PROJECT_ROOT
    / "backend"
    / "report_engine"
    / "report_generator.py"
)

REPORT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "reports"
)

REPORT_FILE = (
    REPORT_DIR
    / "CanopyAI_Final_Report.pdf"
)


# ============================================================
# GENERATE REPORT
# ============================================================

@router.post("/generate")
def generate_report():

    try:

        REPORT_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        if not REPORT_ENGINE.exists():

            raise HTTPException(
                status_code=404,
                detail=(
                    "Report generator not found: "
                    f"{REPORT_ENGINE}"
                )
            )

        print(
            "[REPORT API] Starting report generation..."
        )

        result = subprocess.run(
            [
                sys.executable,
                str(REPORT_ENGINE)
            ],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True
        )

        print(
            "[REPORT API] Generator output:"
        )

        print(
            result.stdout
        )

        if result.returncode != 0:

            print(
                "[REPORT API] Generator error:"
            )

            print(
                result.stderr
            )

            raise HTTPException(
                status_code=500,
                detail={
                    "message":
                        "Report generation failed",
                    "error":
                        result.stderr[-4000:]
                }
            )

        if not REPORT_FILE.exists():

            raise HTTPException(
                status_code=500,
                detail=(
                    "Report generator completed "
                    "but PDF was not created."
                )
            )

        file_size = (
            REPORT_FILE.stat().st_size
        )

        return {

            "success": True,

            "message":
                "CanopyAI final report generated successfully.",

            "filename":
                REPORT_FILE.name,

            "size_bytes":
                file_size,

            "download_url":
                "/report/download"

        }

    except HTTPException:

        raise

    except Exception as error:

        print(
            "[REPORT API] Unexpected error:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ============================================================
# DOWNLOAD REPORT
# ============================================================

@router.get("/download")
def download_report():

    if not REPORT_FILE.exists():

        raise HTTPException(
            status_code=404,
            detail=(
                "Final report does not exist. "
                "Generate the report first."
            )
        )

    return FileResponse(

        path=str(
            REPORT_FILE
        ),

        media_type="application/pdf",

        filename=(
            "CanopyAI_Final_Report.pdf"
        )
    )


# ============================================================
# REPORT STATUS
# ============================================================

@router.get("/status")
def report_status():

    exists = REPORT_FILE.exists()

    if not exists:

        return {

            "ready": False,

            "filename":
                "CanopyAI_Final_Report.pdf",

            "size_bytes": 0

        }

    return {

        "ready": True,

        "filename":
            REPORT_FILE.name,

        "size_bytes":
            REPORT_FILE.stat().st_size

    }