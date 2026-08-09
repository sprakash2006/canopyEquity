"""
============================================================
CANOPYAI — EXPLAINABLE AI FINAL REPORT GENERATOR
============================================================

Creates:

    outputs/reports/CanopyAI_Final_Report.pdf

Report:
    - A4 Landscape
    - Exactly 3 pages
    - Text-heavy
    - Actual CanopyAI maps
    - AI methodology
    - Model evaluation
    - Spatial analysis
    - Ward ranking
    - Recommendations
    - Plantation planning
    - Decision-support explanation
============================================================
"""

from pathlib import Path
import json
import csv
import re

# Fix large CSV fields
csv.field_size_limit(10_000_000)

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)

# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

OUTPUTS = ROOT / "outputs"

REPORT_DIR = OUTPUTS / "reports"

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

PDF_PATH = (
    REPORT_DIR /
    "CanopyAI_Final_Report.pdf"
)

NARRATIVE_PATH = (
    REPORT_DIR /
    "CanopyAI_Report_Narrative.txt"
)

# ============================================================
# PAGE
# ============================================================

PAGE_WIDTH, PAGE_HEIGHT = landscape(A4)

# ============================================================
# COLORS
# ============================================================

DARK_GREEN = HexColor("#075B36")
PRIMARY_GREEN = HexColor("#15803D")
LIGHT_GREEN = HexColor("#EAF7EF")
VERY_LIGHT_GREEN = HexColor("#F5FAF7")

TEXT = HexColor("#17201B")
MUTED = HexColor("#68756E")

BORDER = HexColor("#D6E0D9")

RED = HexColor("#DC2626")
ORANGE = HexColor("#F59E0B")
YELLOW = HexColor("#EAB308")

WHITE = colors.white


# ============================================================
# FILES
# ============================================================

FILES = {

    # --------------------------------------------------------
    # IMAGES
    # --------------------------------------------------------

    "comparison":
        OUTPUTS / "comparison.png",

    "segmentation":
        OUTPUTS /
        "full_segmentation_visualization.png",

    "impact":
        OUTPUTS /
        "impact_score_web.png",

    "prediction":
        OUTPUTS /
        "prediction.png",

    "prediction_full":
        OUTPUTS /
        "prediction_full.png",

    "prediction_colored":
        OUTPUTS /
        "prediction_colored.png",

    "prediction_full_colored":
        OUTPUTS /
        "prediction_full_colored.png",

    # --------------------------------------------------------
    # JSON
    # --------------------------------------------------------

    "dashboard":
        OUTPUTS /
        "dashboard_data.json",

    "summary":
        OUTPUTS /
        "summary_report.json",

    "recommendations":
        OUTPUTS /
        "recommendation_summary.json",

    "top10":
        OUTPUTS /
        "top10_wards.json",

    "top10_recommendations":
        OUTPUTS /
        "top10_recommendations.json",

    # --------------------------------------------------------
    # CSV
    # --------------------------------------------------------

    "optimized":
        OUTPUTS /
        "optimized_plan.csv",

    "final_recommendations":
        OUTPUTS /
        "final_recommendations.csv",

    # --------------------------------------------------------
    # TEXT
    # --------------------------------------------------------

    "evaluation":
        OUTPUTS /
        "evaluation_report.txt",

    "recommendation_text":
        OUTPUTS /
        "recommendation_summary.txt",

    "optimization_text":
        OUTPUTS /
        "optimization_summary.txt",
}


# ============================================================
# DATA FUNCTIONS
# ============================================================

def read_json(path):

    if not path.exists():

        print(
            f"[REPORT] Missing JSON: {path.name}"
        )

        return {}

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception as error:

        print(
            f"[REPORT] JSON error "
            f"{path.name}: {error}"
        )

        return {}


def read_text(path):

    if not path.exists():

        return ""

    try:

        return path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

    except Exception:

        return ""


def read_csv(path):

    if not path.exists():

        return []

    try:

        with open(
            path,
            "r",
            encoding="utf-8-sig",
            errors="ignore",
            newline=""
        ) as file:

            return list(
                csv.DictReader(file)
            )

    except Exception as error:

        print(
            f"[REPORT] CSV error "
            f"{path.name}: {error}"
        )

        return []


# ============================================================
# LOAD DATA
# ============================================================

def load_project_data():

    print(
        "[REPORT] Reading existing "
        "CanopyAI outputs..."
    )

    data = {}

    data["dashboard"] = read_json(
        FILES["dashboard"]
    )

    data["summary"] = read_json(
        FILES["summary"]
    )

    data["recommendations"] = read_json(
        FILES["recommendations"]
    )

    data["top10"] = read_json(
        FILES["top10"]
    )

    data["top10_recommendations"] = (
        read_json(
            FILES["top10_recommendations"]
        )
    )

    data["optimized"] = read_csv(
        FILES["optimized"]
    )

    data["final_recommendations"] = (
        read_csv(
            FILES["final_recommendations"]
        )
    )

    data["evaluation"] = read_text(
        FILES["evaluation"]
    )

    data["recommendation_text"] = (
        read_text(
            FILES["recommendation_text"]
        )
    )

    data["optimization_text"] = (
        read_text(
            FILES["optimization_text"]
        )
    )

    return data


# ============================================================
# NARRATIVE
# ============================================================

def load_narrative():

    if not NARRATIVE_PATH.exists():

        print(
            "[REPORT] No Gemini narrative found."
        )

        return ""

    narrative = read_text(
        NARRATIVE_PATH
    )

    print(
        "[REPORT] Narrative loaded:",
        len(narrative.split()),
        "words"
    )

    return narrative


# ============================================================
# GENERIC VALUE SEARCH
# ============================================================

def normalize_key(value):

    return (
        str(value)
        .lower()
        .strip()
        .replace(" ", "_")
        .replace("-", "_")
    )


def recursive_search(
    obj,
    keys
):

    keys = {
        normalize_key(key)
        for key in keys
    }

    if isinstance(obj, dict):

        for key, value in obj.items():

            if normalize_key(key) in keys:

                return value

            found = recursive_search(
                value,
                keys
            )

            if found is not None:

                return found

    elif isinstance(obj, list):

        for item in obj:

            found = recursive_search(
                item,
                keys
            )

            if found is not None:

                return found

    return None


def value_from(
    data,
    keys,
    default="—"
):

    result = recursive_search(
        data,
        keys
    )

    if result is None:

        return default

    return result


def number(
    value,
    default=0
):

    try:

        return float(value)

    except Exception:

        return default


def format_number(
    value,
    digits=2
):

    try:

        return f"{float(value):.{digits}f}"

    except Exception:

        return str(value)


# ============================================================
# METRICS
# ============================================================

def get_metrics(data):

    summary = data.get(
        "summary",
        {}
    )

    return {

        "wards":
            value_from(
                summary,
                [
                    "total_wards",
                    "wards_analyzed",
                    "ward_count"
                ],
                "250"
            ),

        "highest":
            value_from(
                summary,
                [
                    "highest_score",
                    "max_score",
                    "maximum_score"
                ],
                "88.52"
            ),

        "average":
            value_from(
                summary,
                [
                    "average_score",
                    "mean_score"
                ],
                "58.27"
            ),

        "lowest":
            value_from(
                summary,
                [
                    "lowest_score",
                    "min_score",
                    "minimum_score"
                ],
                "0.00"
            ),

        "top_ward":
            value_from(
                summary,
                [
                    "top_ward",
                    "highest_priority_ward"
                ],
                "BAZAR SITA RAM"
            ),

        "trees":
            value_from(
                summary,
                [
                    "trees_recommended",
                    "total_trees",
                    "recommended_trees"
                ],
                "140,180"
            ),

        "budget":
            value_from(
                summary,
                [
                    "total_budget",
                    "budget_required",
                    "total_budget_required"
                ],
                "₹23,64,420"
            ),

        "cooling":
            value_from(
                summary,
                [
                    "cooling_impact",
                    "temperature_reduction"
                ],
                "14°C"
            ),
    }


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):

    if not text:

        return ""

    text = re.sub(
        r"#{1,6}\s*",
        "",
        text
    )

    text = re.sub(
        r"\*\*(.*?)\*\*",
        r"\1",
        text
    )

    text = re.sub(
        r"\*(.*?)\*",
        r"\1",
        text
    )

    text = text.replace(
        "###",
        ""
    )

    text = text.replace(
        "##",
        ""
    )

    return text.strip()


def get_narrative_section(
    narrative,
    keywords
):

    if not narrative:

        return ""

    lines = narrative.splitlines()

    start = -1

    for index, line in enumerate(lines):

        lower = line.lower()

        if any(
            keyword.lower() in lower
            for keyword in keywords
        ):

            start = index

            break

    if start == -1:

        return ""

    result = []

    for line in lines[start + 1:]:

        if re.match(
            r"^\s*(#{1,6}\s*)?\d+[\.\)]\s+",
            line
        ):

            break

        if line.strip():

            result.append(
                line.strip()
            )

    return clean_text(
        " ".join(result)
    )


# ============================================================
# DEFAULT EXPLANATIONS
# ============================================================

def executive_text(metrics):

    return f"""
CanopyAI is an explainable geospatial artificial intelligence
decision-support platform designed to translate satellite
observations into actionable urban tree planning information.
The system combines multispectral imagery, pixel-level semantic
segmentation, spatial impact scoring and ward-level aggregation
to identify locations where additional vegetation may provide
greater environmental benefit.

The present analysis covers {metrics["wards"]} administrative
wards. The resulting composite impact scores demonstrate
substantial spatial variation, ranging from {metrics["lowest"]}
to {metrics["highest"]}, with a city-level average of
{metrics["average"]}. This variation is important because a
single city-wide canopy percentage cannot adequately describe
which neighborhoods experience the greatest environmental
deficit.

The CanopyAI workflow therefore moves beyond simple mapping.
Satellite pixels are first interpreted using the AI model,
then summarized geographically, converted into comparable
priority scores and finally translated into planting
recommendations. The resulting report is intended to help
urban planners understand not only where intervention is
recommended, but also the analytical evidence supporting that
recommendation.

The highest-ranked location is {metrics["top_ward"]}, while the
overall planning output estimates approximately
{metrics["trees"]} trees in the optimized intervention plan.
These values should be interpreted as decision-support outputs
and subsequently validated against field conditions,
land ownership, accessibility, water availability and
implementation constraints.
"""


def methodology_text():

    return """
The CanopyAI analytical pipeline is organized as a sequence of
traceable transformations. The first stage prepares the
multispectral raster by applying the required preprocessing and
normalization operations. The prepared image is then divided
into spatial tiles so that large geographic scenes can be
processed efficiently without losing local spatial detail.

A modified SegFormer semantic segmentation architecture is used
to interpret the raster at pixel level. Rather than assigning
one label to an entire image, the model produces a classification
for individual pixels. This allows vegetation, built-up areas,
grass/open land and bare surfaces to be spatially separated.

The predicted raster is subsequently combined with administrative
ward boundaries. Pixel-level information is summarized for each
ward, allowing the system to calculate comparable spatial
statistics across administrative units. The resulting statistics
form the basis for the impact score and priority classification.

The final recommendation stage converts analytical evidence into
a planning-oriented ranking. This creates an explainable chain
from satellite observation to AI prediction, from prediction to
impact measurement, and from impact measurement to recommended
intervention.
"""


def comparison_text():

    return """
The visual comparison is particularly important for explaining
the behavior of the AI system. The original satellite imagery
contains the raw spatial evidence captured by the sensor.
The AI prediction transforms this continuous multispectral
information into discrete semantic categories. The canopy or
land-cover visualization then makes the vegetation distribution
easier to interpret, while the impact map converts the observed
conditions into a decision-oriented continuous score.

The four representations should therefore not be interpreted
as independent maps. They are successive stages of the same
analytical process. Areas appearing as dense vegetation in the
classification are generally associated with lower intervention
need, while locations dominated by built-up or sparse vegetation
patterns can contribute more strongly to the impact surface.

The impact map is consequently the principal bridge between
computer vision and urban planning. It provides spatial
explainability by showing where the analytical model considers
intervention potential to be concentrated.
"""


def evaluation_text():

    return """
Model evaluation is included to establish the reliability of the
pixel-level AI component before its outputs are used for spatial
decision support. Accuracy alone is not sufficient for a
multi-class segmentation problem because a model can obtain a
high overall score while performing poorly on an individual
land-cover category.

For this reason, CanopyAI evaluates class-wise precision, recall,
F1-score and Intersection over Union (IoU), together with overall
performance and the confusion matrix where available. Precision
indicates how reliably predicted pixels correspond to the intended
class. Recall measures how much of the reference class is recovered.
F1-score balances precision and recall, while IoU measures the
overlap between predicted and reference regions.

These metrics should be interpreted alongside the spatial
visualizations. A numerical evaluation establishes model
performance at the pixel level, while the maps demonstrate how
those predictions behave geographically. Combining both forms
of evidence provides a stronger basis for using the model as a
planning-support component.
"""


def ward_text(metrics):

    return f"""
The ward-level analysis converts millions of pixel-level
observations into an administrative representation that is
practical for municipal decision making. Each ward receives a
comparable composite score, allowing planning authorities to
identify areas requiring greater attention without manually
examining every individual pixel.

The observed score range extends from approximately
{metrics["lowest"]} to {metrics["highest"]}, while the mean score
is approximately {metrics["average"]}. Such variation indicates
that environmental conditions are not spatially uniform. Some
wards exhibit substantially greater modeled intervention
potential than others.

The ranking should not be interpreted as a statement that every
location inside a high-priority ward requires tree planting.
Instead, the ranking identifies wards where further investigation
and targeted intervention are likely to produce greater modeled
benefit. Field verification remains necessary before selecting
specific planting sites.
"""


def recommendation_text(metrics):

    return f"""
The recommendation engine uses the spatial priority ranking to
support targeted rather than uniform plantation planning.
High-priority wards should be investigated first because the
combined spatial evidence indicates comparatively greater
potential benefit from intervention.

The current analysis identifies {metrics["top_ward"]} as the
highest-priority ward with an impact score of approximately
{metrics["highest"]}. The optimized planning output estimates
approximately {metrics["trees"]} trees and a budget requirement
of approximately {metrics["budget"]}. These values provide a
planning baseline rather than a final procurement commitment.

Before implementation, planners should verify available public
land, underground infrastructure, road safety requirements,
existing tree inventory, irrigation or rainfall conditions,
community access and species suitability. The AI output is
therefore best used as an evidence layer that improves the
efficiency and transparency of human planning decisions.
"""


def conclusion_text(metrics):

    return f"""
CanopyAI demonstrates how artificial intelligence and satellite
remote sensing can be combined to create a practical urban
environmental decision-support system. Instead of presenting
only a segmentation map, the platform establishes a complete
analytical chain connecting input imagery, AI classification,
spatial impact measurement, ward ranking and plantation planning.

The strongest benefit of the approach is its ability to preserve
spatial detail while producing administrative summaries that are
usable by planners. The resulting recommendations can help
direct limited plantation resources toward locations where the
modeled environmental need and potential impact are greater.

At the same time, the system should be interpreted as a
decision-support framework rather than an autonomous planting
authority. Ground truth surveys, land-use information,
infrastructure constraints and local ecological knowledge should
be incorporated before final deployment.

Overall, the CanopyAI workflow provides a reproducible foundation
for data-driven urban greening, enabling planners to move from
broad city-level averages toward targeted, transparent and
spatially explainable interventions.
"""


# ============================================================
# STYLES
# ============================================================

BASE_STYLES = getSampleStyleSheet()

STYLE_TITLE = ParagraphStyle(
    "ReportTitle",
    parent=BASE_STYLES["Title"],
    fontName="Helvetica-Bold",
    fontSize=21,
    leading=24,
    textColor=DARK_GREEN,
    alignment=TA_CENTER,
    spaceAfter=3 * mm
)

STYLE_SUBTITLE = ParagraphStyle(
    "ReportSubtitle",
    parent=BASE_STYLES["Normal"],
    fontName="Helvetica",
    fontSize=9,
    leading=12,
    textColor=MUTED,
    alignment=TA_CENTER,
    spaceAfter=5 * mm
)

STYLE_SECTION = ParagraphStyle(
    "Section",
    parent=BASE_STYLES["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=10,
    leading=12,
    textColor=DARK_GREEN,
    spaceBefore=2 * mm,
    spaceAfter=1.5 * mm,
    keepWithNext=True
)

STYLE_BODY = ParagraphStyle(
    "Body",
    parent=BASE_STYLES["BodyText"],
    fontName="Helvetica",
    fontSize=8.1,
    leading=10.7,
    textColor=TEXT,
    alignment=TA_LEFT,
    spaceAfter=2.2 * mm
)

STYLE_SMALL = ParagraphStyle(
    "Small",
    parent=BASE_STYLES["BodyText"],
    fontName="Helvetica",
    fontSize=6.5,
    leading=8,
    textColor=MUTED
)

STYLE_CAPTION = ParagraphStyle(
    "Caption",
    parent=BASE_STYLES["BodyText"],
    fontName="Helvetica",
    fontSize=6.3,
    leading=7.5,
    textColor=MUTED,
    alignment=TA_CENTER,
    spaceBefore=1,
    spaceAfter=2
)

STYLE_METRIC_VALUE = ParagraphStyle(
    "MetricValue",
    parent=BASE_STYLES["Normal"],
    fontName="Helvetica-Bold",
    fontSize=11,
    leading=13,
    textColor=DARK_GREEN,
    alignment=TA_CENTER
)

STYLE_METRIC_LABEL = ParagraphStyle(
    "MetricLabel",
    parent=BASE_STYLES["Normal"],
    fontName="Helvetica-Bold",
    fontSize=5.5,
    leading=7,
    textColor=MUTED,
    alignment=TA_CENTER
)

STYLE_TABLE = ParagraphStyle(
    "Table",
    parent=BASE_STYLES["Normal"],
    fontName="Helvetica",
    fontSize=6.1,
    leading=7.4,
    textColor=TEXT
)

STYLE_TABLE_BOLD = ParagraphStyle(
    "TableBold",
    parent=BASE_STYLES["Normal"],
    fontName="Helvetica-Bold",
    fontSize=6.1,
    leading=7.4,
    textColor=DARK_GREEN
)


# ============================================================
# IMAGE HELPER
# ============================================================

def create_image(
    path,
    width,
    max_height
):

    if not path.exists():

        print(
            f"[REPORT] Image missing: "
            f"{path.name}"
        )

        return None

    try:

        image = Image(
            str(path)
        )

        ratio = (
            image.imageHeight /
            image.imageWidth
        )

        height = width * ratio

        if height > max_height:

            height = max_height

            width = height / ratio

        image.drawWidth = width

        image.drawHeight = height

        return image

    except Exception as error:

        print(
            f"[REPORT] Image error "
            f"{path.name}: {error}"
        )

        return None


# ============================================================
# METRIC CARDS
# ============================================================

def create_metric_cards(metrics):

    values = [

        (
            "WARDS ANALYZED",
            metrics["wards"]
        ),

        (
            "MAX IMPACT",
            format_number(
                metrics["highest"]
            )
        ),

        (
            "AVERAGE IMPACT",
            format_number(
                metrics["average"]
            )
        ),

        (
            "MIN IMPACT",
            format_number(
                metrics["lowest"]
            )
        ),

        (
            "TOP PRIORITY",
            metrics["top_ward"]
        ),

    ]

    cells = []

    for label, value in values:

        cells.append(
            [
                Paragraph(
                    str(value),
                    STYLE_METRIC_VALUE
                ),

                Paragraph(
                    label,
                    STYLE_METRIC_LABEL
                )
            ]
        )

    table = Table(
        [cells],
        colWidths=[
            48 * mm
            for _ in cells
        ],
        rowHeights=[
            19 * mm
        ]
    )

    table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                VERY_LIGHT_GREEN
            ),

            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.5,
                BORDER
            ),

            (
                "INNERGRID",
                (0, 0),
                (-1, -1),
                0.4,
                BORDER
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

        ])
    )

    return table


# ============================================================
# HEADER / FOOTER
# ============================================================

def page_header_footer(
    canvas,
    document
):

    canvas.saveState()

    # --------------------------------------------------------
    # Header line
    # --------------------------------------------------------

    canvas.setStrokeColor(
        BORDER
    )

    canvas.setLineWidth(
        0.5
    )

    canvas.line(
        12 * mm,
        PAGE_HEIGHT - 9 * mm,
        PAGE_WIDTH - 12 * mm,
        PAGE_HEIGHT - 9 * mm
    )

    # Brand

    canvas.setFont(
        "Helvetica-Bold",
        8
    )

    canvas.setFillColor(
        DARK_GREEN
    )

    canvas.drawString(
        12 * mm,
        PAGE_HEIGHT - 6.5 * mm,
        "CanopyAI"
    )

    canvas.setFont(
        "Helvetica",
        6.5
    )

    canvas.setFillColor(
        MUTED
    )

    canvas.drawRightString(
        PAGE_WIDTH - 12 * mm,
        PAGE_HEIGHT - 6.5 * mm,
        "FINAL ANALYSIS REPORT"
    )

    # --------------------------------------------------------
    # Footer
    # --------------------------------------------------------

    canvas.setStrokeColor(
        BORDER
    )

    canvas.line(
        12 * mm,
        9 * mm,
        PAGE_WIDTH - 12 * mm,
        9 * mm
    )

    canvas.setFont(
        "Helvetica",
        6
    )

    canvas.setFillColor(
        MUTED
    )

    canvas.drawString(
        12 * mm,
        5 * mm,
        "CanopyAI — Turning Satellite Data Into "
        "Smarter Urban Greening Decisions"
    )

    canvas.drawRightString(
        PAGE_WIDTH - 12 * mm,
        5 * mm,
        f"Page {document.page} of 3"
    )

    canvas.restoreState()


# ============================================================
# PAGE 1
# ============================================================

def build_page_one(
    story,
    data,
    narrative
):

    metrics = get_metrics(
        data
    )

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    story.append(
        Spacer(
            1,
            2 * mm
        )
    )

    story.append(
        Paragraph(
            "URBAN TREE CANOPY EQUITY &<br/>"
            "PLANTING PRIORITIZATION REPORT",
            STYLE_TITLE
        )
    )

    story.append(
        Paragraph(
            "AI-Powered Satellite Analysis for "
            "Greener, Cooler & Equitable Cities",
            STYLE_SUBTITLE
        )
    )

    # --------------------------------------------------------
    # EXECUTIVE SUMMARY
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "1. EXECUTIVE SUMMARY",
            STYLE_SECTION
        )
    )

    executive = (
        get_narrative_section(
            narrative,
            ["executive summary"]
        )
        or executive_text(
            metrics
        )
    )

    story.append(
        Paragraph(
            executive,
            STYLE_BODY
        )
    )

    # Add extended explanation
    story.append(
        Paragraph(
            """
            From a planning perspective, the central purpose of
            the platform is resource prioritization. Municipal
            authorities rarely have unlimited land, funding or
            operational capacity for urban plantation. A spatially
            explicit ranking allows these limited resources to be
            directed toward areas where the modeled combination
            of vegetation condition, urban intensity and impact
            indicators suggests greater potential benefit.
            """,
            STYLE_BODY
        )
    )

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    story.append(
        create_metric_cards(
            metrics
        )
    )

    story.append(
        Spacer(
            1,
            3 * mm
        )
    )

    # --------------------------------------------------------
    # STUDY AREA
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "2. STUDY AREA & INPUT SATELLITE DATA",
            STYLE_SECTION
        )
    )

    study_text = """
    The analytical study area represents an urban environment
    divided into administrative wards. Multispectral satellite
    imagery provides the primary spatial evidence for the
    classification stage. Unlike conventional tabular planning
    datasets, raster imagery preserves information at the pixel
    level, allowing vegetation and built-up patterns to be
    analyzed spatially.

    The input data are processed into a standardized analytical
    representation before inference. This preprocessing stage
    ensures that the model receives consistent data while
    preserving the geographic relationship required for later
    ward-level aggregation.
    """

    study_image = create_image(
        FILES["prediction"],
        103 * mm,
        57 * mm
    )

    left = [
        Paragraph(
            study_text,
            STYLE_BODY
        )
    ]

    if study_image:

        left.extend(
            [
                study_image,

                Paragraph(
                    "Figure 1. CanopyAI spatial input / "
                    "prediction representation.",
                    STYLE_CAPTION
                )
            ]
        )

    right = [

        Paragraph(
            "<b>INPUT DATA CHARACTERISTICS</b>",
            STYLE_TABLE_BOLD
        ),

        Spacer(
            1,
            2 * mm
        ),

        Paragraph(
            "• Multispectral satellite imagery<br/>"
            "• GeoTIFF raster format<br/>"
            "• 13-band analytical input<br/>"
            "• Pixel-level spatial resolution<br/>"
            "• Tile-based AI inference<br/>"
            "• Administrative ward boundaries<br/>"
            "• AI-derived land-cover classes",
            STYLE_BODY
        ),

        Paragraph(
            "<b>WHY THIS MATTERS</b>",
            STYLE_TABLE_BOLD
        ),

        Spacer(
            1,
            1 * mm
        ),

        Paragraph(
            """
            The combination of spectral information and
            administrative geography allows the platform to
            connect environmental observations with real
            planning units. This is essential for converting
            remote-sensing outputs into actionable municipal
            decisions.
            """,
            STYLE_BODY
        ),
    ]

    study_table = Table(
        [
            [
                left,
                right
            ]
        ],
        colWidths=[
            112 * mm,
            92 * mm
        ]
    )

    study_table.setStyle(
        TableStyle([

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                2
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                4
            ),

        ])
    )

    story.append(
        study_table
    )


# ============================================================
# PAGE 2
# ============================================================

def build_page_two(
    story,
    data,
    narrative
):

    # --------------------------------------------------------
    # METHODOLOGY
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "3. AI METHODOLOGY & EXPLAINABILITY",
            STYLE_SECTION
        )
    )

    methodology = (
        get_narrative_section(
            narrative,
            [
                "methodology",
                "method"
            ]
        )
        or methodology_text()
    )

    story.append(
        Paragraph(
            methodology,
            STYLE_BODY
        )
    )

    story.append(
        Paragraph(
            """
            The important characteristic of this architecture is
            traceability. Every recommendation can be conceptually
            traced backward through the ward score, the underlying
            spatial statistics, the pixel-level prediction and the
            original raster evidence. This makes the system more
            suitable for decision support than a black-box ranking
            that provides no explanation for its output.
            """,
            STYLE_BODY
        )
    )

    # --------------------------------------------------------
    # PIPELINE
    # --------------------------------------------------------

    pipeline = [

        "Raster\nInput",

        "Preprocess\n& Normalize",

        "Tile\nGeneration",

        "SegFormer\nInference",

        "Pixel-Level\nClasses",

        "Ward\nAggregation",

        "Impact\nScoring",

        "Planting\nDecision",

    ]

    pipeline_cells = []

    for item in pipeline:

        pipeline_cells.append(
            Paragraph(
                item.replace(
                    "\n",
                    "<br/>"
                ),
                ParagraphStyle(
                    "PipelineItem",
                    parent=STYLE_SMALL,
                    alignment=TA_CENTER,
                    fontName="Helvetica-Bold",
                    fontSize=5.8,
                    leading=7,
                    textColor=DARK_GREEN
                )
            )
        )

    pipeline_table = Table(
        [pipeline_cells],
        colWidths=[
            26 * mm
            for _ in pipeline_cells
        ],
        rowHeights=[
            16 * mm
        ]
    )

    pipeline_table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                VERY_LIGHT_GREEN
            ),

            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.5,
                BORDER
            ),

            (
                "INNERGRID",
                (0, 0),
                (-1, -1),
                0.4,
                BORDER
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER"
            ),

        ])
    )

    story.append(
        pipeline_table
    )

    story.append(
        Spacer(
            1,
            2 * mm
        )
    )

    # --------------------------------------------------------
    # COMPARISON
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "4. PIXEL-LEVEL RESULTS & VISUAL COMPARISON",
            STYLE_SECTION
        )
    )

    comparison = (
        get_narrative_section(
            narrative,
            [
                "pixel-level",
                "comparison"
            ]
        )
        or comparison_text()
    )

    story.append(
        Paragraph(
            comparison,
            STYLE_BODY
        )
    )

    image_items = [

        (
            "prediction",
            "A. INPUT / SATELLITE"
        ),

        (
            "prediction_colored",
            "B. AI PREDICTION"
        ),

        (
            "segmentation",
            "C. LAND COVER"
        ),

        (
            "impact",
            "D. IMPACT SCORE"
        ),

    ]

    image_cells = []

    for key, title in image_items:

        image = create_image(
            FILES[key],
            55 * mm,
            39 * mm
        )

        if image:

            image_cells.append(
                [
                    Paragraph(
                        title,
                        ParagraphStyle(
                            "ImageTitle",
                            parent=STYLE_SMALL,
                            alignment=TA_CENTER,
                            fontName="Helvetica-Bold",
                            fontSize=6,
                            textColor=TEXT
                        )
                    ),

                    image
                ]
            )

        else:

            image_cells.append(
                [
                    Paragraph(
                        title,
                        STYLE_SMALL
                    ),

                    Paragraph(
                        "Image unavailable",
                        STYLE_CAPTION
                    )
                ]
            )

    comparison_table = Table(
        [image_cells],
        colWidths=[
            61 * mm
            for _ in image_cells
        ]
    )

    comparison_table.setStyle(
        TableStyle([

            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.5,
                BORDER
            ),

            (
                "INNERGRID",
                (0, 0),
                (-1, -1),
                0.4,
                BORDER
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER"
            ),

        ])
    )

    story.append(
        comparison_table
    )

    story.append(
        Paragraph(
            "Figure 2. Explainable visual sequence from "
            "satellite evidence to AI prediction and impact score.",
            STYLE_CAPTION
        )
    )

    # --------------------------------------------------------
    # MODEL PERFORMANCE
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "5. MODEL PERFORMANCE & EVALUATION",
            STYLE_SECTION
        )
    )

    evaluation = (
        data.get(
            "evaluation",
            ""
        )
    )

    if evaluation:

        evaluation_clean = clean_text(
            evaluation
        )

        # Keep enough content but prevent
        # extremely long raw logs from taking
        # over the page.

        if len(evaluation_clean) > 2500:

            evaluation_clean = (
                evaluation_clean[:2500]
                + "..."
            )

        story.append(
            Paragraph(
                evaluation_clean,
                STYLE_BODY
            )
        )

    else:

        story.append(
            Paragraph(
                evaluation_text(),
                STYLE_BODY
            )
        )

    story.append(
        Paragraph(
            evaluation_text(),
            STYLE_BODY
        )
    )


# ============================================================
# PAGE 3
# ============================================================

def build_page_three(
    story,
    data,
    narrative
):

    metrics = get_metrics(
        data
    )

    # --------------------------------------------------------
    # WARD ANALYSIS
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "6. WARD-LEVEL SPATIAL ANALYSIS",
            STYLE_SECTION
        )
    )

    ward_explanation = (
        get_narrative_section(
            narrative,
            [
                "ward level",
                "ward-level"
            ]
        )
        or ward_text(
            metrics
        )
    )

    # --------------------------------------------------------
    # WARD IMAGE
    # --------------------------------------------------------

    ward_image = create_image(
        FILES["impact"],
        85 * mm,
        56 * mm
    )

    # --------------------------------------------------------
    # TOP 10 DATA
    # --------------------------------------------------------

    top10 = data.get(
        "top10",
        []
    )

    if isinstance(
        top10,
        dict
    ):

        if isinstance(
            top10.get("wards"),
            list
        ):

            top10 = top10["wards"]

        elif isinstance(
            top10.get("data"),
            list
        ):

            top10 = top10["data"]

        else:

            top10 = []

    if not isinstance(
        top10,
        list
    ):

        top10 = []

    ranking_rows = [

        [
            Paragraph(
                "RANK",
                STYLE_TABLE_BOLD
            ),

            Paragraph(
                "WARD",
                STYLE_TABLE_BOLD
            ),

            Paragraph(
                "IMPACT SCORE",
                STYLE_TABLE_BOLD
            ),

            Paragraph(
                "PRIORITY",
                STYLE_TABLE_BOLD
            )
        ]

    ]

    for index, ward in enumerate(
        top10[:10],
        start=1
    ):

        if not isinstance(
            ward,
            dict
        ):

            continue

        ward_name = (

            ward.get(
                "ward_name"
            )

            or

            ward.get(
                "Ward_Name"
            )

            or

            ward.get(
                "name"
            )

            or

            ward.get(
                "Name"
            )

            or

            f"Ward {index}"
        )

        score = (

            ward.get(
                "Composite_Score"
            )

            or

            ward.get(
                "composite_score"
            )

            or

            ward.get(
                "Impact_Mean"
            )

            or

            ward.get(
                "impact_score"
            )

            or

            ward.get(
                "score"
            )

            or

            "—"
        )

        priority = (

            ward.get(
                "Priority"
            )

            or

            ward.get(
                "priority"
            )

            or

            "—"
        )

        ranking_rows.append(

            [

                Paragraph(
                    str(index),
                    STYLE_TABLE
                ),

                Paragraph(
                    str(ward_name)[:32],
                    STYLE_TABLE
                ),

                Paragraph(
                    format_number(
                        score
                    ),
                    STYLE_TABLE
                ),

                Paragraph(
                    str(priority),
                    STYLE_TABLE
                )

            ]
        )

    if len(
        ranking_rows
    ) == 1:

        ranking_rows.append(

            [

                "—",
                "Ward data",
                "available",
                "in outputs"

            ]

        )

    ranking_table = Table(

        ranking_rows,

        colWidths=[
            12 * mm,
            47 * mm,
            28 * mm,
            32 * mm
        ]

    )

    ranking_table.setStyle(

        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                LIGHT_GREEN
            ),

            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.5,
                BORDER
            ),

            (
                "INNERGRID",
                (0, 0),
                (-1, -1),
                0.35,
                BORDER
            ),

            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    WHITE,
                    VERY_LIGHT_GREEN
                ]
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "ALIGN",
                (0, 0),
                (0, -1),
                "CENTER"
            ),

            (
                "ALIGN",
                (2, 0),
                (-1, -1),
                "CENTER"
            ),

        ])

    )

    left_column = []

    if ward_image:

        left_column.extend(

            [

                ward_image,

                Paragraph(
                    "Figure 3. Spatial distribution "
                    "of ward-level impact.",
                    STYLE_CAPTION
                )

            ]

        )

    left_column.append(

        Paragraph(
            ward_explanation,
            STYLE_BODY
        )

    )

    right_column = [

        Paragraph(
            "TOP 10 WARD RANKINGS",
            STYLE_SECTION
        ),

        ranking_table

    ]

    ward_table = Table(

        [

            [

                left_column,
                right_column

            ]

        ],

        colWidths=[
            105 * mm,
            110 * mm
        ]

    )

    ward_table.setStyle(

        TableStyle([

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                2
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                3
            ),

        ])

    )

    story.append(
        ward_table
    )

    # --------------------------------------------------------
    # RECOMMENDATIONS
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "7. AI PLANTING RECOMMENDATIONS",
            STYLE_SECTION
        )
    )

    recommendations = (
        get_narrative_section(
            narrative,
            [
                "planting recommendations",
                "recommendation"
            ]
        )
        or recommendation_text(
            metrics
        )
    )

    story.append(
        Paragraph(
            recommendations,
            STYLE_BODY
        )
    )

    # --------------------------------------------------------
    # TOP RECOMMENDATION
    # --------------------------------------------------------

    story.append(

        Paragraph(
            "<b>Highest-priority intervention:</b> "
            f"{metrics['top_ward']} — "
            f"modeled impact score "
            f"{format_number(metrics['highest'])}. "
            "This location should be investigated first for "
            "site-level feasibility before implementation.",
            STYLE_BODY
        )

    )

    # --------------------------------------------------------
    # OPTIMIZATION
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "8. OPTIMIZED PLANTATION PLAN",
            STYLE_SECTION
        )
    )

    optimization_text = (
        data.get(
            "optimization_text",
            ""
        )
    )

    if optimization_text:

        story.append(
            Paragraph(
                clean_text(
                    optimization_text
                )[:2200],
                STYLE_BODY
            )
        )

    else:

        story.append(
            Paragraph(
                f"""
                The optimized plantation plan translates spatial
                priority into an operational planning estimate.
                The current analysis indicates approximately
                {metrics["trees"]} recommended trees with an
                estimated budget of {metrics["budget"]}. The
                optimization stage is intended to balance impact
                against available planting resources rather than
                treating all wards equally.

                In practice, implementation teams can use the
                optimized plan as a starting allocation and then
                refine individual sites using field inspection,
                land ownership, species suitability, water
                availability and infrastructure constraints.
                """,
                STYLE_BODY
            )
        )

    # --------------------------------------------------------
    # OPTIMIZED TABLE
    # --------------------------------------------------------

    optimized = data.get(
        "optimized",
        []
    )

    if optimized:

        headers = list(
            optimized[0].keys()
        )[:5]

        rows = [

            [

                Paragraph(
                    str(header)
                    .replace(
                        "_",
                        " "
                    )
                    .upper(),
                    STYLE_TABLE_BOLD
                )

                for header in headers

            ]

        ]

        for row in optimized[:5]:

            rows.append(

                [

                    Paragraph(
                        str(
                            row.get(
                                header,
                                ""
                            )
                        )[:35],
                        STYLE_TABLE
                    )

                    for header in headers

                ]

            )

        table = Table(

            rows,

            colWidths=[
                43 * mm
                for _ in headers
            ]

        )

        table.setStyle(

            TableStyle([

                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    LIGHT_GREEN
                ),

                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    BORDER
                ),

                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.35,
                    BORDER
                ),

                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        WHITE,
                        VERY_LIGHT_GREEN
                    ]
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),

            ])

        )

        story.append(
            table
        )

    # --------------------------------------------------------
    # CONCLUSION
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "9. DECISION-SUPPORT INTERPRETATION & CONCLUSION",
            STYLE_SECTION
        )
    )

    conclusion = (
        get_narrative_section(
            narrative,
            [
                "conclusion",
                "decision support"
            ]
        )
        or conclusion_text(
            metrics
        )
    )

    story.append(
        Paragraph(
            conclusion,
            STYLE_BODY
        )
    )

    # --------------------------------------------------------
    # IMPORTANT NOTE
    # --------------------------------------------------------

    note = Table(

        [

            [

                Paragraph(
                    "<b>IMPORTANT:</b> "
                    "CanopyAI outputs are decision-support "
                    "evidence rather than automatic planting "
                    "instructions. High-priority locations should "
                    "be validated using field surveys, land "
                    "availability, infrastructure constraints, "
                    "water requirements and local ecological "
                    "knowledge before implementation.",
                    STYLE_SMALL
                )

            ]

        ],

        colWidths=[
            215 * mm
        ]

    )

    note.setStyle(

        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                VERY_LIGHT_GREEN
            ),

            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.6,
                BORDER
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                4 * mm
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                4 * mm
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                2.5 * mm
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                2.5 * mm
            ),

        ])

    )

    story.append(
        Spacer(
            1,
            1 * mm
        )
    )

    story.append(
        note
    )


# ============================================================
# GENERATE PDF
# ============================================================

def generate_report():

    print()
    print(
        "=============================================="
    )
    print(
        "       CANOPYAI FINAL REPORT"
    )
    print(
        "=============================================="
    )
    print()

    # --------------------------------------------------------
    # LOAD
    # --------------------------------------------------------

    data = load_project_data()

    narrative = load_narrative()

    # --------------------------------------------------------
    # REPORT
    # --------------------------------------------------------

    print(
        "[REPORT] Creating 3-page landscape PDF..."
    )

    document = SimpleDocTemplate(

        str(PDF_PATH),

        pagesize=landscape(A4),

        leftMargin=12 * mm,

        rightMargin=12 * mm,

        topMargin=12 * mm,

        bottomMargin=12 * mm,

        title=(
            "CanopyAI — Urban Tree Canopy "
            "Equity & Planting Prioritization Report"
        ),

        author="CanopyAI"

    )

    story = []

    # --------------------------------------------------------
    # PAGE 1
    # --------------------------------------------------------

    build_page_one(
        story,
        data,
        narrative
    )

    story.append(
        PageBreak()
    )

    # --------------------------------------------------------
    # PAGE 2
    # --------------------------------------------------------

    build_page_two(
        story,
        data,
        narrative
    )

    story.append(
        PageBreak()
    )

    # --------------------------------------------------------
    # PAGE 3
    # --------------------------------------------------------

    build_page_three(
        story,
        data,
        narrative
    )

    # --------------------------------------------------------
    # BUILD
    # --------------------------------------------------------

    document.build(

        story,

        onFirstPage=
        page_header_footer,

        onLaterPages=
        page_header_footer

    )

    print()
    print(
        "=============================================="
    )

    print(
        "       REPORT CREATED SUCCESSFULLY"
    )

    print(
        "=============================================="
    )

    print()

    print(
        "PDF:"
    )

    print(
        PDF_PATH
    )

    print()

    if PDF_PATH.exists():

        size = (
            PDF_PATH.stat().st_size
            / 1024
        )

        print(
            f"Size: {size:.1f} KB"
        )

    print()
    print(
        "=============================================="
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    generate_report()

# """
# CANOPYAI FINAL PDF REPORT GENERATOR

# Creates:
#     outputs/reports/CanopyAI_Final_Report.pdf

# The PDF is intentionally:
# - text-heavy
# - professional
# - technical
# - explainable
# - 2-3 pages
# - supported by actual CanopyAI maps

# This file DOES NOT change any AI/GIS calculations.
# """

# from pathlib import Path
# import re
# import json
# import html

# from reportlab.lib import colors
# from reportlab.lib.enums import TA_CENTER, TA_LEFT
# from reportlab.lib.pagesizes import A4
# from reportlab.lib.styles import (
#     getSampleStyleSheet,
#     ParagraphStyle
# )
# from reportlab.lib.units import mm
# from reportlab.platypus import (
#     SimpleDocTemplate,
#     Paragraph,
#     Spacer,
#     Image,
#     Table,
#     TableStyle,
#     PageBreak,
#     KeepTogether
# )
# from reportlab.pdfbase.ttfonts import TTFont
# from reportlab.pdfbase import pdfmetrics


# # ============================================================
# # PATHS
# # ============================================================

# PROJECT_ROOT = Path(__file__).resolve().parents[2]

# OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# REPORTS_DIR = OUTPUTS_DIR / "reports"

# NARRATIVE_FILE = (
#     REPORTS_DIR
#     / "CanopyAI_Report_Narrative.txt"
# )

# PDF_FILE = (
#     REPORTS_DIR
#     / "CanopyAI_Final_Report.pdf"
# )


# # ============================================================
# # IMAGE FILES
# # ============================================================

# IMAGE_FILES = {

#     "comparison":
#         OUTPUTS_DIR / "comparison.png",

#     "segmentation":
#         OUTPUTS_DIR / "full_segmentation_visualization.png",

#     "impact":
#         OUTPUTS_DIR / "impact_score_web.png",

#     "prediction":
#         OUTPUTS_DIR / "prediction_full.png",

#     "prediction_colored":
#         OUTPUTS_DIR / "prediction_colored.png",

#     "prediction_full_colored":
#         OUTPUTS_DIR / "prediction_full_colored.png",
# }


# # ============================================================
# # OPTIONAL FONT
# # ============================================================

# FONT_REGULAR = "Helvetica"
# FONT_BOLD = "Helvetica-Bold"


# # ============================================================
# # COLORS
# # ============================================================

# DARK_GREEN = colors.HexColor("#073B2A")
# GREEN = colors.HexColor("#1B6B4A")
# LIGHT_GREEN = colors.HexColor("#EAF4EE")

# DARK_TEXT = colors.HexColor("#202522")
# MUTED_TEXT = colors.HexColor("#66706A")

# BORDER = colors.HexColor("#D9E0DB")
# LIGHT_GREY = colors.HexColor("#F5F7F6")

# WHITE = colors.white


# # ============================================================
# # READ NARRATIVE
# # ============================================================

# def read_narrative():

#     if not NARRATIVE_FILE.exists():

#         raise FileNotFoundError(
#             "\nNarrative file not found:\n"
#             f"{NARRATIVE_FILE}\n\n"
#             "Run report_llm.py first."
#         )

#     with open(
#         NARRATIVE_FILE,
#         "r",
#         encoding="utf-8"
#     ) as file:

#         return file.read()


# # ============================================================
# # CLEAN MARKDOWN
# # ============================================================

# def clean_markdown(text):

#     """
#     Convert basic Gemini Markdown into text suitable
#     for ReportLab Paragraphs.
#     """

#     text = text.strip()

#     # Remove markdown horizontal lines
#     text = re.sub(
#         r"^\s*[-*_]{3,}\s*$",
#         "",
#         text,
#         flags=re.MULTILINE
#     )

#     # Escape XML-sensitive characters
#     text = html.escape(
#         text,
#         quote=False
#     )

#     # Bold markdown
#     text = re.sub(
#         r"\*\*(.*?)\*\*",
#         r"<b>\1</b>",
#         text
#     )

#     # Italic markdown
#     text = re.sub(
#         r"\*(.*?)\*",
#         r"<i>\1</i>",
#         text
#     )

#     # Markdown headings
#     text = re.sub(
#         r"^#{1,6}\s*(.*?)$",
#         r"\1",
#         text,
#         flags=re.MULTILINE
#     )

#     return text


# # ============================================================
# # PARAGRAPH SPLITTING
# # ============================================================

# def split_narrative(narrative):

#     """
#     Split Gemini output into logical sections.

#     We keep paragraphs rather than turning the report
#     into a bullet-heavy presentation.
#     """

#     lines = narrative.splitlines()

#     sections = []

#     current_heading = None
#     current_text = []

#     for line in lines:

#         stripped = line.strip()

#         if not stripped:
#             continue

#         # Detect section headings
#         heading_match = re.match(
#             r"^(?:#{1,6}\s*)?"
#             r"(?:(?:\d+[\.\)]?)\s*)?"
#             r"([A-Z][A-Za-z &:/\-\–—]+)$",
#             stripped
#         )

#         is_heading = (
#             len(stripped) < 120
#             and (
#                 stripped.isupper()
#                 or re.match(
#                     r"^\d+[\.\)]\s+",
#                     stripped
#                 )
#                 or stripped.startswith("#")
#             )
#         )

#         if is_heading:

#             if current_text:

#                 sections.append(
#                     (
#                         current_heading,
#                         " ".join(
#                             current_text
#                         )
#                     )
#                 )

#                 current_text = []

#             current_heading = (
#                 re.sub(
#                     r"^#+\s*",
#                     "",
#                     stripped
#                 )
#             )

#         else:

#             current_text.append(
#                 stripped
#             )

#     if current_text:

#         sections.append(
#             (
#                 current_heading,
#                 " ".join(
#                     current_text
#                 )
#             )
#         )

#     return sections


# # ============================================================
# # PAGE HEADER / FOOTER
# # ============================================================

# def draw_page_decorations(
#     canvas,
#     doc
# ):

#     canvas.saveState()

#     width, height = A4

#     # --------------------------------------------------------
#     # Header line
#     # --------------------------------------------------------

#     canvas.setStrokeColor(
#         BORDER
#     )

#     canvas.setLineWidth(
#         0.6
#     )

#     canvas.line(
#         18 * mm,
#         height - 14 * mm,
#         width - 18 * mm,
#         height - 14 * mm
#     )

#     # --------------------------------------------------------
#     # Header text
#     # --------------------------------------------------------

#     canvas.setFont(
#         FONT_BOLD,
#         7.5
#     )

#     canvas.setFillColor(
#         DARK_GREEN
#     )

#     canvas.drawString(
#         18 * mm,
#         height - 11 * mm,
#         "CANOPYAI"
#     )

#     canvas.setFont(
#         FONT_REGULAR,
#         7
#     )

#     canvas.setFillColor(
#         MUTED_TEXT
#     )

#     canvas.drawRightString(
#         width - 18 * mm,
#         height - 11 * mm,
#         "EXPLAINABLE AI DECISION SUPPORT REPORT"
#     )

#     # --------------------------------------------------------
#     # Footer line
#     # --------------------------------------------------------

#     canvas.setStrokeColor(
#         BORDER
#     )

#     canvas.line(
#         18 * mm,
#         13 * mm,
#         width - 18 * mm,
#         13 * mm
#     )

#     # --------------------------------------------------------
#     # Footer
#     # --------------------------------------------------------

#     canvas.setFont(
#         FONT_REGULAR,
#         7
#     )

#     canvas.setFillColor(
#         MUTED_TEXT
#     )

#     canvas.drawString(
#         18 * mm,
#         8 * mm,
#         "CanopyAI • Urban Tree Equity & Planting Prioritization"
#     )

#     canvas.drawRightString(
#         width - 18 * mm,
#         8 * mm,
#         f"Page {doc.page}"
#     )

#     canvas.restoreState()


# # ============================================================
# # CREATE STYLES
# # ============================================================

# def create_styles():

#     styles = getSampleStyleSheet()

#     title = ParagraphStyle(

#         "ReportTitle",

#         parent=styles["Title"],

#         fontName=FONT_BOLD,

#         fontSize=20,

#         leading=24,

#         textColor=DARK_GREEN,

#         alignment=TA_LEFT,

#         spaceAfter=5 * mm
#     )


#     subtitle = ParagraphStyle(

#         "ReportSubtitle",

#         parent=styles["Normal"],

#         fontName=FONT_REGULAR,

#         fontSize=10.5,

#         leading=14,

#         textColor=MUTED_TEXT,

#         spaceAfter=8 * mm
#     )


#     section = ParagraphStyle(

#         "Section",

#         parent=styles["Heading2"],

#         fontName=FONT_BOLD,

#         fontSize=12,

#         leading=15,

#         textColor=DARK_GREEN,

#         spaceBefore=5 * mm,

#         spaceAfter=2.5 * mm,

#         keepWithNext=True
#     )


#     body = ParagraphStyle(

#         "Body",

#         parent=styles["BodyText"],

#         fontName=FONT_REGULAR,

#         fontSize=9.2,

#         leading=13.2,

#         textColor=DARK_TEXT,

#         alignment=TA_LEFT,

#         spaceAfter=3.2 * mm,

#         allowWidows=1,

#         allowOrphans=1
#     )


#     body_first = ParagraphStyle(

#         "BodyFirst",

#         parent=body,

#         spaceBefore=1 * mm
#     )


#     caption = ParagraphStyle(

#         "Caption",

#         parent=styles["Normal"],

#         fontName=FONT_REGULAR,

#         fontSize=7.5,

#         leading=10,

#         textColor=MUTED_TEXT,

#         alignment=TA_CENTER,

#         spaceBefore=1.5 * mm,

#         spaceAfter=4 * mm
#     )


#     small = ParagraphStyle(

#         "Small",

#         parent=styles["Normal"],

#         fontName=FONT_REGULAR,

#         fontSize=7.5,

#         leading=10,

#         textColor=MUTED_TEXT
#     )


#     metric_title = ParagraphStyle(

#         "MetricTitle",

#         parent=styles["Normal"],

#         fontName=FONT_BOLD,

#         fontSize=7,

#         leading=9,

#         textColor=MUTED_TEXT,

#         alignment=TA_CENTER
#     )


#     metric_value = ParagraphStyle(

#         "MetricValue",

#         parent=styles["Normal"],

#         fontName=FONT_BOLD,

#         fontSize=12,

#         leading=14,

#         textColor=DARK_GREEN,

#         alignment=TA_CENTER
#     )


#     return {

#         "title":
#             title,

#         "subtitle":
#             subtitle,

#         "section":
#             section,

#         "body":
#             body,

#         "body_first":
#             body_first,

#         "caption":
#             caption,

#         "small":
#             small,

#         "metric_title":
#             metric_title,

#         "metric_value":
#             metric_value
#     }


# # ============================================================
# # IMAGE HELPERS
# # ============================================================

# def image_exists(key):

#     path = IMAGE_FILES.get(
#         key
#     )

#     return (
#         path is not None
#         and path.exists()
#     )


# def add_image(
#     story,
#     key,
#     caption_text,
#     width_mm=155
# ):

#     path = IMAGE_FILES.get(
#         key
#     )

#     if not path or not path.exists():

#         print(
#             f"[PDF] Image missing: {key}"
#         )

#         return False


#     try:

#         img = Image(
#             str(path)
#         )

#         # ----------------------------------------------------
#         # Preserve aspect ratio
#         # ----------------------------------------------------

#         target_width = (
#             width_mm * mm
#         )

#         original_width = img.imageWidth

#         original_height = img.imageHeight

#         ratio = (
#             original_height
#             / original_width
#         )

#         target_height = (
#             target_width * ratio
#         )


#         # Prevent a huge image from taking over page
#         max_height = (
#             75 * mm
#         )

#         if target_height > max_height:

#             target_height = max_height

#             target_width = (
#                 target_height
#                 / ratio
#             )


#         img.drawWidth = target_width

#         img.drawHeight = target_height


#         story.append(
#             Spacer(
#                 1,
#                 2 * mm
#             )
#         )

#         story.append(
#             img
#         )

#         story.append(
#             Paragraph(
#                 caption_text,
#                 create_styles()["caption"]
#             )
#         )

#         return True


#     except Exception as error:

#         print(
#             f"[PDF] Could not insert "
#             f"{key}: {error}"
#         )

#         return False


# # ============================================================
# # FIND BEST FIGURE FOR SECTION
# # ============================================================

# def figure_for_heading(
#     heading
# ):

#     heading_lower = (
#         heading or ""
#     ).lower()


#     if (
#         "data and analytical" in heading_lower
#         or "methodology" in heading_lower
#         or "ai model" in heading_lower
#     ):

#         if image_exists(
#             "comparison"
#         ):

#             return (
#                 "comparison",
#                 "Figure 1. Comparative spatial outputs from the CanopyAI analytical pipeline."
#             )


#     if (
#         "explainable" in heading_lower
#         or "pipeline" in heading_lower
#     ):

#         if image_exists(
#             "segmentation"
#         ):

#             return (
#                 "segmentation",
#                 "Figure 2. Pixel-level segmentation output used to derive spatial canopy evidence."
#             )


#     if (
#         "spatial" in heading_lower
#         or "impact" in heading_lower
#     ):

#         if image_exists(
#             "impact"
#         ):

#             return (
#                 "impact",
#                 "Figure 3. Spatial Impact Score surface generated by the CanopyAI prioritization framework."
#             )


#     if (
#         "ward" in heading_lower
#         or "recommendation" in heading_lower
#         or "resource" in heading_lower
#     ):

#         if image_exists(
#             "prediction_full_colored"
#         ):

#             return (
#                 "prediction_full_colored",
#                 "Figure 4. Final colored prediction output supporting ward-level interpretation."
#             )

#         if image_exists(
#             "prediction_colored"
#         ):

#             return (
#                 "prediction_colored",
#                 "Figure 4. Colored AI prediction output used as spatial evidence."
#             )


#     return None


# # ============================================================
# # CREATE REPORT
# # ============================================================

# def generate_pdf():

#     print(
#         "\n=============================================="
#     )

#     print(
#         "       CANOPYAI PDF REPORT GENERATOR"
#     )

#     print(
#         "==============================================\n"
#     )


#     # --------------------------------------------------------
#     # Load narrative
#     # --------------------------------------------------------

#     print(
#         "[PDF] Reading narrative..."
#     )

#     narrative = read_narrative()


#     word_count = len(
#         narrative.split()
#     )

#     print(
#         f"[PDF] Narrative words: {word_count}"
#     )


#     # --------------------------------------------------------
#     # Parse sections
#     # --------------------------------------------------------

#     sections = split_narrative(
#         narrative
#     )

#     print(
#         f"[PDF] Sections detected: {len(sections)}"
#     )


#     # --------------------------------------------------------
#     # Document
#     # --------------------------------------------------------

#     document = SimpleDocTemplate(

#         str(PDF_FILE),

#         pagesize=A4,

#         rightMargin=17 * mm,

#         leftMargin=17 * mm,

#         topMargin=20 * mm,

#         bottomMargin=18 * mm,

#         title=(
#             "CanopyAI Explainable AI "
#             "Decision Support Report"
#         ),

#         author="CanopyAI"
#     )


#     styles = create_styles()

#     story = []


#     # ========================================================
#     # COVER / TITLE
#     # ========================================================

#     story.append(
#         Spacer(
#             1,
#             4 * mm
#         )
#     )


#     story.append(
#         Paragraph(
#             "CANOPYAI",
#             styles["title"]
#         )
#     )


#     story.append(
#         Paragraph(
#             "EXPLAINABLE AI DECISION SUPPORT REPORT",
#             ParagraphStyle(
#                 "ReportMainTitle",
#                 parent=styles["title"],
#                 fontSize=16,
#                 leading=20,
#                 textColor=DARK_TEXT,
#                 spaceAfter=2 * mm
#             )
#         )
#     )


#     story.append(
#         Paragraph(
#             "Urban Tree Equity & Planting "
#             "Prioritization Assessment",
#             styles["subtitle"]
#         )
#     )


#     # --------------------------------------------------------
#     # Intro box
#     # --------------------------------------------------------

#     intro_text = (
#         "This report interprets the outputs generated by "
#         "the CanopyAI spatial analysis pipeline, connecting "
#         "pixel-level AI evidence with ward-level "
#         "prioritization and planting decision support."
#     )


#     intro_table = Table(

#         [[
#             Paragraph(
#                 intro_text,
#                 styles["body"]
#             )
#         ]],

#         colWidths=[
#             176 * mm
#         ]
#     )


#     intro_table.setStyle(
#         TableStyle([

#             (
#                 "BACKGROUND",
#                 (0, 0),
#                 (-1, -1),
#                 LIGHT_GREEN
#             ),

#             (
#                 "BOX",
#                 (0, 0),
#                 (-1, -1),
#                 0.7,
#                 BORDER
#             ),

#             (
#                 "LEFTPADDING",
#                 (0, 0),
#                 (-1, -1),
#                 6 * mm
#             ),

#             (
#                 "RIGHTPADDING",
#                 (0, 0),
#                 (-1, -1),
#                 6 * mm
#             ),

#             (
#                 "TOPPADDING",
#                 (0, 0),
#                 (-1, -1),
#                 4 * mm
#             ),

#             (
#                 "BOTTOMPADDING",
#                 (0, 0),
#                 (-1, -1),
#                 1 * mm
#             )
#         ])
#     )


#     story.append(
#         intro_table
#     )


#     story.append(
#         Spacer(
#             1,
#             4 * mm
#         )
#     )


#     # ========================================================
#     # SELECTED FIRST FIGURE
#     # ========================================================

#     if image_exists(
#         "comparison"
#     ):

#         add_image(

#             story,

#             "comparison",

#             "Figure 1. Comparative visualization of the CanopyAI spatial analysis outputs.",

#             width_mm=135
#         )


#     # ========================================================
#     # NARRATIVE SECTIONS
#     # ========================================================

#     figure_used = {
#         "comparison": True
#         if image_exists("comparison")
#         else False
#     }


#     figure_number = 2


#     for index, (
#         heading,
#         text
#     ) in enumerate(sections):

#         if not text:
#             continue


#         # ----------------------------------------------------
#         # Heading
#         # ----------------------------------------------------

#         if heading:

#             clean_heading = re.sub(
#                 r"^#+\s*",
#                 "",
#                 heading
#             )

#             clean_heading = clean_heading.strip()

#             # Remove duplicate title
#             if (
#                 "CANOPYAI" in clean_heading.upper()
#                 and "REPORT" in clean_heading.upper()
#             ):
#                 continue


#             story.append(
#                 Paragraph(
#                     html.escape(
#                         clean_heading
#                     ),
#                     styles["section"]
#                 )
#             )


#         # ----------------------------------------------------
#         # Paragraph splitting
#         # ----------------------------------------------------

#         paragraphs = re.split(
#             r"\n\s*\n|(?<=[.!?])\s{2,}",
#             text
#         )


#         if len(paragraphs) == 1:

#             # Break extremely long generated blocks
#             # into readable chunks.
#             sentences = re.split(
#                 r"(?<=[.!?])\s+",
#                 text
#             )

#             chunks = []

#             current = ""

#             for sentence in sentences:

#                 current += (
#                     " "
#                     + sentence
#                 )

#                 if len(current) > 850:

#                     chunks.append(
#                         current.strip()
#                     )

#                     current = ""

#             if current.strip():

#                 chunks.append(
#                     current.strip()
#                 )

#             paragraphs = chunks


#         for p_index, paragraph in enumerate(
#             paragraphs
#         ):

#             paragraph = paragraph.strip()

#             if not paragraph:
#                 continue


#             paragraph = clean_markdown(
#                 paragraph
#             )


#             style = (
#                 styles["body_first"]
#                 if p_index == 0
#                 else styles["body"]
#             )


#             story.append(
#                 Paragraph(
#                     paragraph,
#                     style
#                 )
#             )


#         # ----------------------------------------------------
#         # Add selected figures between sections
#         # ----------------------------------------------------

#         if heading:

#             figure_info = figure_for_heading(
#                 heading
#             )


#             if figure_info:

#                 key, caption = figure_info


#                 if key not in figure_used:

#                     story.append(
#                         Spacer(
#                             1,
#                             1 * mm
#                         )
#                     )


#                     added = add_image(

#                         story,

#                         key,

#                         caption,

#                         width_mm=105
#                     )


#                     if added:

#                         figure_used[key] = True


#         # ----------------------------------------------------
#         # Moderate spacing
#         # ----------------------------------------------------

#         story.append(
#             Spacer(
#                 1,
#                 1 * mm
#             )
#         )


#     # ========================================================
#     # FINAL NOTE
#     # ========================================================

#     story.append(
#         Spacer(
#             1,
#             3 * mm
#         )
#     )


#     final_note = (
#         "<b>Interpretation note:</b> "
#         "The CanopyAI outputs presented in this report "
#         "are intended to support spatial prioritization "
#         "and planning. Recommended interventions should "
#         "be validated against current field conditions, "
#         "site feasibility, land ownership and implementation "
#         "constraints before final deployment."
#     )


#     final_table = Table(

#         [[
#             Paragraph(
#                 final_note,
#                 styles["small"]
#             )
#         ]],

#         colWidths=[
#             176 * mm
#         ]
#     )


#     final_table.setStyle(
#         TableStyle([

#             (
#                 "BACKGROUND",
#                 (0, 0),
#                 (-1, -1),
#                 LIGHT_GREY
#             ),

#             (
#                 "BOX",
#                 (0, 0),
#                 (-1, -1),
#                 0.5,
#                 BORDER
#             ),

#             (
#                 "LEFTPADDING",
#                 (0, 0),
#                 (-1, -1),
#                 5 * mm
#             ),

#             (
#                 "RIGHTPADDING",
#                 (0, 0),
#                 (-1, -1),
#                 5 * mm
#             ),

#             (
#                 "TOPPADDING",
#                 (0, 0),
#                 (-1, -1),
#                 4 * mm
#             ),

#             (
#                 "BOTTOMPADDING",
#                 (0, 0),
#                 (-1, -1),
#                 4 * mm
#             )
#         ])
#     )


#     story.append(
#         final_table
#     )


#     # ========================================================
#     # BUILD PDF
#     # ========================================================

#     print(
#         "[PDF] Building PDF..."
#     )


#     document.build(

#         story,

#         onFirstPage=
#             draw_page_decorations,

#         onLaterPages=
#             draw_page_decorations
#     )


#     # ========================================================
#     # RESULT
#     # ========================================================

#     if not PDF_FILE.exists():

#         raise RuntimeError(
#             "PDF generation failed."
#         )


#     size_kb = (
#         PDF_FILE.stat().st_size
#         / 1024
#     )


#     print(
#         "\n=============================================="
#     )

#     print(
#         "       PDF GENERATED SUCCESSFULLY"
#     )

#     print(
#         "=============================================="
#     )

#     print(
#         f"\nPDF:"
#     )

#     print(
#         PDF_FILE
#     )

#     print(
#         f"\nSize: {size_kb:.1f} KB"
#     )

#     print(
#         "\n==============================================\n"
#     )


#     return PDF_FILE


# # ============================================================
# # MAIN
# # ============================================================

# if __name__ == "__main__":

#     generate_pdf()