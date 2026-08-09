"""
CanopyAI Report Data Collector

This module ONLY READS existing CanopyAI outputs.

It does NOT modify:
- AI model
- segmentation
- impact scoring
- ward ranking
- recommendation engine
- GIS processing

It prepares verified project outputs for the
Explainable AI PDF Report.
"""

from pathlib import Path
import json
import csv
import sys


# ============================================================
# PROJECT PATHS
# ============================================================

# .../CanopyAI/backend/report_engine
REPORT_ENGINE_DIR = Path(__file__).resolve().parent

# .../CanopyAI/backend
BACKEND_DIR = REPORT_ENGINE_DIR.parent

# .../CanopyAI
PROJECT_ROOT = BACKEND_DIR.parent

# .../CanopyAI/outputs
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# .../CanopyAI/outputs/reports
REPORTS_DIR = OUTPUTS_DIR / "reports"


# ============================================================
# FILE READERS
# ============================================================

def read_json(filename):
    """
    Read a JSON file from the existing CanopyAI outputs.
    """

    path = OUTPUTS_DIR / filename

    if not path.exists():
        print(f"[REPORT] Missing JSON: {filename}")
        return None

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception as error:

        print(
            f"[REPORT] Error reading "
            f"{filename}: {error}"
        )

        return None


def read_text(filename):
    """
    Read a text file from the existing CanopyAI outputs.
    """

    path = OUTPUTS_DIR / filename

    if not path.exists():
        print(f"[REPORT] Missing text: {filename}")
        return None

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            return file.read()

    except Exception as error:

        print(
            f"[REPORT] Error reading "
            f"{filename}: {error}"
        )

        return None


def read_csv(filename):
    """
    Read a CSV file from the existing CanopyAI outputs.

    Large CSV fields are supported because some of the
    generated recommendation files may contain long
    text or serialized data.
    """

    path = OUTPUTS_DIR / filename

    if not path.exists():
        print(f"[REPORT] Missing CSV: {filename}")
        return []

    try:

        # ----------------------------------------------------
        # FIX:
        # Python's default CSV field limit is only 131072.
        # CanopyAI output may contain larger fields.
        # ----------------------------------------------------

        csv.field_size_limit(
            min(
                sys.maxsize,
                10_000_000
            )
        )

        with open(
            path,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            return list(reader)

    except Exception as error:

        print(
            f"[REPORT] Error reading "
            f"{filename}: {error}"
        )

        return []


# ============================================================
# IMAGE OUTPUTS
# ============================================================

def get_report_images():
    """
    Collect existing CanopyAI visual outputs.

    These images will later be embedded into the
    final Explainable AI PDF report.
    """

    image_files = {

        # Main comparison
        "comparison":
            "comparison.png",

        # Segmentation
        "segmentation":
            "full_segmentation_visualization.png",

        # Impact
        "impact_score":
            "impact_score_web.png",

        # Prediction outputs
        "prediction":
            "prediction_full.png",

        "prediction_colored":
            "prediction_colored.png",

        "prediction_full_colored":
            "prediction_full_colored.png",
    }

    images = {}

    for key, filename in image_files.items():

        path = OUTPUTS_DIR / filename

        images[key] = {

            "filename":
                filename,

            "path":
                str(path),

            "exists":
                path.exists()
        }

    return images


# ============================================================
# SUPPORTING FILES
# ============================================================

def get_supporting_files():
    """
    Collect other files that may be useful for the final report.
    """

    filenames = [

        "canopy_prediction_web.tif",

        "impact_score.tif",

        "ward_rankings_web.geojson",

        "dashboard_data.json",

        "summary_report.json",

        "recommendation_summary.json",

        "top10_recommendations.json",

        "top10_wards.json",

        "final_recommendations.csv",

        "optimized_plan.csv",

        "top_plantation_wards.csv",

        "evaluation_report.txt",

        "recommendation_summary.txt",

        "optimization_summary.txt",

    ]

    result = {}

    for filename in filenames:

        path = OUTPUTS_DIR / filename

        result[filename] = {

            "path":
                str(path),

            "exists":
                path.exists(),

            "size_bytes":
                path.stat().st_size
                if path.exists()
                else 0
        }

    return result


# ============================================================
# EXISTING CANOPYAI OUTPUTS
# ============================================================

def collect_existing_outputs():

    print(
        "\n[REPORT] Reading existing "
        "CanopyAI outputs..."
    )

    data = {

        # ====================================================
        # SUMMARY
        # ====================================================

        "summary_report":
            read_json(
                "summary_report.json"
            ),

        "dashboard":
            read_json(
                "dashboard_data.json"
            ),


        # ====================================================
        # RECOMMENDATIONS
        # ====================================================

        "recommendation_summary":
            read_json(
                "recommendation_summary.json"
            ),

        "top10_recommendations":
            read_json(
                "top10_recommendations.json"
            ),

        "top10_wards":
            read_json(
                "top10_wards.json"
            ),


        # ====================================================
        # CSV RESULTS
        # ====================================================

        "final_recommendations":
            read_csv(
                "final_recommendations.csv"
            ),

        "optimized_plan":
            read_csv(
                "optimized_plan.csv"
            ),

        "top_plantation_wards":
            read_csv(
                "top_plantation_wards.csv"
            ),


        # ====================================================
        # EXISTING TEXT REPORTS
        # ====================================================

        "evaluation_report":
            read_text(
                "evaluation_report.txt"
            ),

        "recommendation_text":
            read_text(
                "recommendation_summary.txt"
            ),

        "optimization_summary":
            read_text(
                "optimization_summary.txt"
            ),


        # ====================================================
        # VISUAL OUTPUTS
        # ====================================================

        "images":
            get_report_images(),


        # ====================================================
        # SUPPORTING FILES
        # ====================================================

        "supporting_files":
            get_supporting_files()
    }

    return data


# ============================================================
# SAFE SUMMARY HELPERS
# ============================================================

def count_records(value):
    """
    Return a safe record count.
    """

    if isinstance(value, list):

        return len(value)

    if isinstance(value, dict):

        return len(value)

    return 0


def get_available_images(images):
    """
    Return only images that actually exist.
    """

    available = {}

    for name, info in images.items():

        if info.get("exists"):

            available[name] = info

    return available


# ============================================================
# MAIN REPORT DATA OBJECT
# ============================================================

def get_report_data():

    existing = collect_existing_outputs()

    images = existing.get(
        "images",
        {}
    )

    report_data = {

        # ====================================================
        # PROJECT INFORMATION
        # ====================================================

        "project": {

            "name":
                "CanopyAI",

            "title":
                "Urban Tree Equity & "
                "Planting Prioritization",

            "description":
                "AI-powered urban tree canopy "
                "equity assessment and planting "
                "prioritization using multispectral "
                "satellite imagery.",

            "report_type":
                "Explainable AI Decision Support Report"
        },


        # ====================================================
        # PATHS
        # ====================================================

        "paths": {

            "project_root":
                str(PROJECT_ROOT),

            "outputs":
                str(OUTPUTS_DIR),

            "reports":
                str(REPORTS_DIR)
        },


        # ====================================================
        # EXISTING DATA
        # ====================================================

        "data":
            existing,


        # ====================================================
        # REPORT METADATA
        # ====================================================

        "metadata": {

            "dashboard_records":
                count_records(
                    existing.get(
                        "dashboard"
                    )
                ),

            "top_wards":
                count_records(
                    existing.get(
                        "top10_wards"
                    )
                ),

            "top_recommendations":
                count_records(
                    existing.get(
                        "top10_recommendations"
                    )
                ),

            "optimized_plan_records":
                count_records(
                    existing.get(
                        "optimized_plan"
                    )
                ),

            "plantation_ward_records":
                count_records(
                    existing.get(
                        "top_plantation_wards"
                    )
                ),

            "available_images":
                list(
                    get_available_images(
                        images
                    ).keys()
                )
        }
    }

    return report_data


# ============================================================
# TEST FUNCTION
# ============================================================

def print_report_status(report_data):

    data = report_data["data"]

    print(
        "\n=============================================="
    )

    print(
        "        CANOPYAI REPORT DATA STATUS"
    )

    print(
        "=============================================="
    )


    # --------------------------------------------------------
    # JSON
    # --------------------------------------------------------

    print("\nJSON OUTPUTS")

    json_outputs = [

        "summary_report",
        "dashboard",
        "recommendation_summary",
        "top10_recommendations",
        "top10_wards"
    ]

    for name in json_outputs:

        value = data.get(name)

        if value is not None:

            if isinstance(value, list):

                print(
                    f"  ✓ {name}: "
                    f"{len(value)} records"
                )

            elif isinstance(value, dict):

                print(
                    f"  ✓ {name}: "
                    f"JSON object loaded"
                )

            else:

                print(
                    f"  ✓ {name}: loaded"
                )

        else:

            print(
                f"  ✗ {name}: missing"
            )


    # --------------------------------------------------------
    # CSV
    # --------------------------------------------------------

    print("\nCSV OUTPUTS")

    csv_outputs = [

        "final_recommendations",
        "optimized_plan",
        "top_plantation_wards"
    ]

    for name in csv_outputs:

        value = data.get(name)

        if isinstance(value, list):

            print(
                f"  ✓ {name}: "
                f"{len(value)} records"
            )

        else:

            print(
                f"  ✗ {name}: unavailable"
            )


    # --------------------------------------------------------
    # TEXT
    # --------------------------------------------------------

    print("\nTEXT OUTPUTS")

    text_outputs = [

        "evaluation_report",
        "recommendation_text",
        "optimization_summary"
    ]

    for name in text_outputs:

        value = data.get(name)

        if value:

            print(
                f"  ✓ {name}: "
                f"{len(value)} characters"
            )

        else:

            print(
                f"  ✗ {name}: missing"
            )


    # --------------------------------------------------------
    # IMAGES
    # --------------------------------------------------------

    print("\nIMAGE OUTPUTS")

    images = data.get(
        "images",
        {}
    )

    for name, info in images.items():

        if info["exists"]:

            print(
                f"  ✓ {name}: "
                f"{info['filename']}"
            )

        else:

            print(
                f"  ✗ {name}: "
                f"{info['filename']} missing"
            )


    # --------------------------------------------------------
    # SUPPORTING FILES
    # --------------------------------------------------------

    print("\nSUPPORTING FILES")

    supporting = data.get(
        "supporting_files",
        {}
    )

    for filename, info in supporting.items():

        if info["exists"]:

            print(
                f"  ✓ {filename}"
            )

        else:

            print(
                f"  - {filename}"
            )


    # --------------------------------------------------------
    # METADATA
    # --------------------------------------------------------

    print("\nREPORT METADATA")

    metadata = report_data.get(
        "metadata",
        {}
    )

    for key, value in metadata.items():

        print(
            f"  {key}: {value}"
        )


    print(
        "\n=============================================="
    )

    print(
        "        REPORT DATA TEST COMPLETE"
    )

    print(
        "==============================================\n"
    )


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":

    report_data = get_report_data()

    print_report_status(
        report_data
    )