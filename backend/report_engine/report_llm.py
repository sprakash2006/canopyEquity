"""
CanopyAI — Explainable AI Report Narrative Generator

PURPOSE
-------
Generate a long-form, evidence-based narrative for the
final CanopyAI PDF report.

IMPORTANT
---------
This file ONLY generates explanatory text.

It does NOT modify:
- AI model
- segmentation
- prediction
- impact score
- ward ranking
- recommendation logic
- optimization logic
- GIS outputs

The final PDF will be generated separately by:
    report_generator.py
"""

import os
import json
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUTS_DIR = PROJECT_ROOT / "outputs"

REPORTS_DIR = OUTPUTS_DIR / "reports"

REPORTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv(
    PROJECT_ROOT / ".env"
)

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

MODEL_NAME = os.getenv(
    "GEMINI_REPORT_MODEL",
    "gemini-3.6-flash"
)


# ============================================================
# IMPORT REPORT DATA
# ============================================================

from report_data import get_report_data


# ============================================================
# GEMINI CLIENT
# ============================================================

def get_client():

    if not GEMINI_API_KEY:

        raise RuntimeError(
            "\n"
            "==============================================\n"
            "GEMINI API KEY NOT FOUND\n"
            "==============================================\n"
            "Create a .env file in the CanopyAI project root.\n"
            "Add:\n\n"
            "GEMINI_API_KEY=YOUR_API_KEY\n\n"
        )

    return genai.Client(
        api_key=GEMINI_API_KEY
    )


# ============================================================
# SAFE JSON
# ============================================================

def safe_json(data):

    if data is None:
        return "Not available."

    try:

        return json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
            default=str
        )

    except Exception:

        return str(data)


# ============================================================
# NUMERIC CONVERSION
# ============================================================

def to_float(value):

    try:

        if value is None:
            return None

        return float(value)

    except (
        ValueError,
        TypeError
    ):

        return None


# ============================================================
# DASHBOARD ANALYSIS
# ============================================================

def summarize_dashboard(dashboard):

    """
    Summarize the complete dashboard locally.

    We DO NOT send all 250 records to Gemini.
    This prevents unnecessarily large API requests.
    """

    if not isinstance(
        dashboard,
        list
    ):

        return {
            "total_records": 0,
            "scores_available": 0,
            "priority_distribution": {}
        }


    scores = []

    priorities = {}

    canopy_values = []

    temperature_values = []

    tree_values = []


    for ward in dashboard:

        if not isinstance(
            ward,
            dict
        ):

            continue


        # ====================================================
        # SCORE
        # ====================================================

        score_value = (

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
        )


        score = to_float(
            score_value
        )


        if score is not None:

            scores.append(
                score
            )


        # ====================================================
        # PRIORITY
        # ====================================================

        priority = (

            ward.get(
                "Priority"
            )

            or

            ward.get(
                "priority"
            )
        )


        if priority:

            priority = str(
                priority
            ).upper()

            priorities[priority] = (
                priorities.get(
                    priority,
                    0
                )
                + 1
            )


        # ====================================================
        # CANOPY
        # ====================================================

        canopy = (

            ward.get(
                "canopy"
            )

            or

            ward.get(
                "Canopy"
            )

            or

            ward.get(
                "Canopy_Coverage"
            )

            or

            ward.get(
                "canopy_coverage"
            )
        )


        canopy_value = to_float(
            canopy
        )


        if canopy_value is not None:

            canopy_values.append(
                canopy_value
            )


        # ====================================================
        # TEMPERATURE
        # ====================================================

        temperature = (

            ward.get(
                "temperature"
            )

            or

            ward.get(
                "Temperature"
            )

            or

            ward.get(
                "LST"
            )

            or

            ward.get(
                "lst"
            )
        )


        temperature_value = to_float(
            temperature
        )


        if temperature_value is not None:

            temperature_values.append(
                temperature_value
            )


        # ====================================================
        # TREE COUNT
        # ====================================================

        trees = (

            ward.get(
                "trees"
            )

            or

            ward.get(
                "Trees"
            )

            or

            ward.get(
                "tree_count"
            )
        )


        tree_value = to_float(
            trees
        )


        if tree_value is not None:

            tree_values.append(
                tree_value
            )


    # ========================================================
    # RESULT
    # ========================================================

    result = {

        "total_wards":
            len(dashboard),

        "scores_available":
            len(scores),

        "priority_distribution":
            priorities,

        "canopy_values_available":
            len(canopy_values),

        "temperature_values_available":
            len(temperature_values),

        "tree_values_available":
            len(tree_values)
    }


    if scores:

        result.update({

            "minimum_score":
                round(
                    min(scores),
                    4
                ),

            "maximum_score":
                round(
                    max(scores),
                    4
                ),

            "average_score":
                round(
                    sum(scores)
                    / len(scores),
                    4
                )
        })


    if canopy_values:

        result.update({

            "minimum_canopy":
                round(
                    min(canopy_values),
                    4
                ),

            "maximum_canopy":
                round(
                    max(canopy_values),
                    4
                ),

            "average_canopy":
                round(
                    sum(canopy_values)
                    / len(canopy_values),
                    4
                )
        })


    if temperature_values:

        result.update({

            "minimum_temperature":
                round(
                    min(temperature_values),
                    4
                ),

            "maximum_temperature":
                round(
                    max(temperature_values),
                    4
                ),

            "average_temperature":
                round(
                    sum(temperature_values)
                    / len(temperature_values),
                    4
                )
        })


    if tree_values:

        result.update({

            "minimum_tree_count":
                round(
                    min(tree_values),
                    4
                ),

            "maximum_tree_count":
                round(
                    max(tree_values),
                    4
                ),

            "average_tree_count":
                round(
                    sum(tree_values)
                    / len(tree_values),
                    4
                )
        })


    return result


# ============================================================
# EVALUATION DATA
# ============================================================

def prepare_evaluation_data(evaluation):

    if evaluation is None:

        return {
            "available": False,
            "content": "Not available."
        }


    text = str(
        evaluation
    )


    # Keep evaluation text because it may contain
    # important accuracy / precision / recall / F1 / IoU
    # information.

    # Limit extremely large evaluation files.
    if len(text) > 25000:

        text = text[:25000]

        text += (
            "\n[Evaluation report truncated for LLM context.]"
        )


    return {

        "available": True,

        "content": text
    }


# ============================================================
# COMPACT REPORT DATA
# ============================================================

def build_compact_report_data(
    report_data
):

    data = report_data.get(
        "data",
        {}
    )


    dashboard = data.get(
        "dashboard"
    )


    compact = {

        # ====================================================
        # PROJECT
        # ====================================================

        "project":
            report_data.get(
                "project",
                {}
            ),


        # ====================================================
        # SUMMARY
        # ====================================================

        "summary_report":
            data.get(
                "summary_report"
            ),


        # ====================================================
        # FULL DASHBOARD SUMMARY
        # ====================================================

        "dashboard_statistics":
            summarize_dashboard(
                dashboard
            ),


        # ====================================================
        # TOP WARDS
        # ====================================================

        "top_10_wards":
            data.get(
                "top10_wards"
            ),


        # ====================================================
        # TOP RECOMMENDATIONS
        # ====================================================

        "top_10_recommendations":
            data.get(
                "top10_recommendations"
            ),


        # ====================================================
        # RECOMMENDATION SUMMARY
        # ====================================================

        "recommendation_summary":
            data.get(
                "recommendation_summary"
            ),


        # ====================================================
        # OPTIMIZATION
        # ====================================================

        "optimized_plan":
            data.get(
                "optimized_plan"
            ),


        # ====================================================
        # EVALUATION
        # ====================================================

        "evaluation":
            prepare_evaluation_data(
                data.get(
                    "evaluation_report"
                )
            ),


        # ====================================================
        # RECOMMENDATION TEXT
        # ====================================================

        "recommendation_analysis":
            data.get(
                "recommendation_text"
            ),


        # ====================================================
        # OPTIMIZATION TEXT
        # ====================================================

        "optimization_analysis":
            data.get(
                "optimization_summary"
            )
    }


    return compact


# ============================================================
# SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """

You are the senior technical analyst responsible for
writing the final Explainable AI report for CanopyAI.

CanopyAI is an AI-powered urban tree canopy equity and
planting prioritization system.

The report is intended for:

- municipal planners
- urban forestry departments
- sustainability officers
- city administrators
- technical reviewers
- project evaluators

This is a serious technical decision-support report.

It is NOT a marketing document.

It is NOT a PowerPoint.

It is NOT a short executive summary.

============================================================
PRIMARY REQUIREMENT
============================================================

Generate approximately 2200–2800 WORDS.

The output MUST be a long-form technical narrative.

The final PDF will be approximately 3 pages.

The PDF will contain:

- mostly text
- a few actual maps
- selected metrics
- selected recommendation information

The maps are supporting evidence.

THE TEXT IS THE MAIN CONTENT.

Do not compress the report.

Do not stop after the executive summary.

Do not produce only 500–1000 words.

============================================================
EVIDENCE RULE
============================================================

Use ONLY information provided in the supplied CanopyAI
data.

Never invent numerical values.

Never modify numerical values.

Never fabricate:

- accuracy
- precision
- recall
- F1
- IoU
- model confidence
- number of wards
- tree count
- budget
- cooling estimate
- carbon estimate
- impact score
- canopy percentage
- temperature
- geographic location
- environmental outcome

If a requested metric does not exist:

"Not available in the current analysis output."

============================================================
IMPORTANT DISTINCTION
============================================================

Clearly distinguish between:

1. Measured/computed results

2. AI/model-derived results

3. Interpretation

4. Planning recommendations

For example:

A model-derived estimate must not be presented as
a directly measured real-world outcome.

A recommendation must not be presented as a guarantee.

============================================================
ANALYTICAL CHAIN
============================================================

Explain the complete CanopyAI pipeline:

Satellite imagery
        ↓
Pixel-level AI prediction
        ↓
Land-cover / canopy interpretation
        ↓
Spatial impact analysis
        ↓
Ward-level aggregation
        ↓
Ward ranking
        ↓
Planting recommendation
        ↓
Resource optimization

The report MUST explain:

- what happens at each stage
- what information is produced
- why the stage is useful
- how it contributes to the next stage
- how it ultimately supports decision-making

============================================================
PIXEL-LEVEL VS WARD-LEVEL EXPLANATION
============================================================

This is especially important.

Explain why pixel-level analysis is useful even though
the final recommendation is made at ward level.

Explain that:

pixel-level analysis provides spatial detail,

while ward-level aggregation converts that detail
into an administrative unit that can be prioritized,
budgeted, validated and acted upon.

Do not claim that ward boundaries are inherently
more accurate than pixel-level information.

Explain the difference between analytical resolution
and administrative decision-making.

============================================================
METRIC EXPLANATION
============================================================

When actual metrics are available, do not simply list them.

Explain what they mean.

For example:

Accuracy describes the proportion of evaluated samples
classified correctly.

Precision indicates how often predicted positive classes
correspond to the relevant reference class.

Recall indicates how much of the reference class was
successfully detected.

F1 summarizes precision and recall.

IoU evaluates overlap between predicted and reference
regions.

Only discuss metrics that actually appear in the
provided evaluation output.

============================================================
WRITING DEPTH
============================================================

For every major finding answer:

WHAT?
WHY?
HOW?
SO WHAT?

For example:

WHAT was observed?

WHAT does the number/map represent?

WHY is it important?

HOW does it connect to the next analytical stage?

SO WHAT can the decision-maker do with it?

Do not merely describe a chart or map.

Interpret it.

============================================================
REPORT STRUCTURE
============================================================


TITLE

CANOPYAI:
EXPLAINABLE AI DECISION SUPPORT REPORT

Urban Tree Equity & Planting Prioritization Assessment


============================================================
1. EXECUTIVE SUMMARY
============================================================

Write 4 substantial paragraphs.

Discuss:

- purpose
- urban tree-equity problem
- spatial planning challenge
- CanopyAI approach
- scale of analysis
- major verified findings
- planning significance

Use actual values where available.


============================================================
2. INTRODUCTION AND PROBLEM CONTEXT
============================================================

Write 3 substantial paragraphs.

Explain:

- why urban tree distribution matters
- why city-wide averages are insufficient
- why spatially explicit information is needed
- why satellite imagery is useful
- why pixel-level intelligence can improve planning
- why administrative prioritization is required


============================================================
3. DATA AND ANALYTICAL FRAMEWORK
============================================================

Write 4 substantial paragraphs.

Explain:

- satellite observations
- multispectral information if supported
- pixel-level processing
- AI prediction
- segmentation
- canopy interpretation
- spatial indicators
- administrative aggregation

Do not invent technical details.


============================================================
4. AI MODEL AND PERFORMANCE
============================================================

Write 4 substantial paragraphs.

Use actual evaluation information.

Discuss available:

- accuracy
- precision
- recall
- F1
- IoU
- class-wise performance
- test sample/pixel counts
- model evaluation information

Explain what the metrics indicate.

Explain what they do NOT prove.

Do not exaggerate performance.


============================================================
5. EXPLAINABLE AI PIPELINE
============================================================

Write 4 substantial paragraphs.

Explain:

Satellite imagery
→ prediction
→ segmentation/canopy interpretation
→ impact analysis
→ ward ranking
→ recommendation

Explain how the system progressively transforms
complex spatial observations into interpretable
planning evidence.


============================================================
6. SPATIAL AND IMPACT ANALYSIS
============================================================

Write 4 substantial paragraphs.

Use actual available:

- minimum impact score
- maximum impact score
- average impact score
- priority distribution
- canopy statistics
- temperature statistics

ONLY if present.

Explain what the Impact Score means within the
CanopyAI framework.

Explain spatial variation.

Do not invent reasons for observed spatial patterns.


============================================================
7. WARD-LEVEL ANALYSIS
============================================================

Write 4 substantial paragraphs.

Use the actual top ward information.

Discuss:

- highest-priority wards
- ranking
- scores
- supplied indicators
- relative prioritization

Explain why ward aggregation is useful.

Explain how the output can be used by municipal planners.

Explain the relationship between:

pixel-level evidence

and

ward-level administrative action.


============================================================
8. PLANTING RECOMMENDATION ANALYSIS
============================================================

Write 4 substantial paragraphs.

Use the actual recommendation data.

Discuss available:

- priority
- ward
- score
- proposed trees
- budget
- cooling estimate
- carbon estimate
- intervention type
- other supplied recommendation fields

Explain how recommendations connect to previous
analytical stages.

Do not invent missing information.


============================================================
9. RESOURCE OPTIMIZATION AND IMPLEMENTATION
============================================================

Write 3 substantial paragraphs.

Use the optimized plantation plan.

Explain:

- resource allocation
- budget allocation
- planting quantities
- prioritization
- sequencing
- implementation planning

Explain how optimization helps a decision-maker.

Clearly distinguish model optimization from final
on-ground implementation.


============================================================
10. DECISION-SUPPORT INTERPRETATION
============================================================

Write 3 substantial paragraphs.

Explain how a municipality could use the results.

Discuss:

priority identification
→ field validation
→ site verification
→ feasibility assessment
→ resource allocation
→ implementation
→ monitoring

Write this mainly in paragraphs.

Do not turn the whole section into a checklist.


============================================================
11. LIMITATIONS AND VALIDATION
============================================================

Write 3 substantial paragraphs.

Explain:

- difference between satellite evidence and field conditions
- difference between model prediction and observation
- importance of field validation
- importance of checking actual planting feasibility
- need for future monitoring

Only use limitations supported by the project context.


============================================================
12. CONCLUSION
============================================================

Write 3 substantial paragraphs.

Summarize:

- satellite analysis
- AI prediction
- segmentation
- spatial analysis
- impact scoring
- ward prioritization
- recommendation
- optimization
- planning value

Explain the complete transformation:

complex spatial data

into

interpretable evidence

into

actionable planning priorities.

End with a strong evidence-based conclusion.


============================================================
FIGURE REFERENCES
============================================================

The final PDF will contain actual CanopyAI maps.

Naturally refer to them in the narrative.

Examples:

"Figure 1 presents the spatial comparison generated
by the CanopyAI analysis."

"Figure 2 illustrates the pixel-level prediction
used in the subsequent spatial analysis."

"Figure 3 presents the resulting impact-priority
surface."

"The visual evidence should be interpreted together
with the corresponding numerical and ward-level results."

Do NOT invent image contents.

Do NOT make the report image-heavy.


============================================================
STYLE
============================================================

Use:

- professional technical language
- long-form paragraphs
- logical transitions
- evidence interpretation
- precise terminology
- decision-oriented explanation

Avoid:

- marketing language
- generic AI claims
- excessive bullets
- repetitive sentences
- one-line fragments
- informal language
- emojis
- presentation-style writing

The report should resemble a concise technical research
paper / municipal analytical report.


============================================================
FINAL LENGTH REQUIREMENT
============================================================

Minimum target:

2200 words

Preferred:

2300–2600 words

Maximum:

2800 words

DO NOT stop early.

DO NOT provide a short summary.

Produce the COMPLETE report from Executive Summary
through Conclusion.
"""


# ============================================================
# BUILD USER PROMPT
# ============================================================

def build_report_prompt(
    compact_data
):

    return f"""

Generate the complete CanopyAI Explainable AI
Decision-Support Report using ONLY the verified
data below.

============================================================
VERIFIED CANOPYAI DATA
============================================================

{safe_json(compact_data)}

============================================================
END VERIFIED DATA
============================================================

Follow every requirement in the system instructions.

IMPORTANT:

The final report must be approximately
2200–2800 words.

The report must be text-heavy.

Every numerical statement must be traceable to the
provided CanopyAI data.

If information is unavailable, explicitly state that
it is not available.

Do not invent missing information.

Begin with:

CANOPYAI:
EXPLAINABLE AI DECISION SUPPORT REPORT

and continue through the complete Conclusion section.
"""


# ============================================================
# GENERATE REPORT
# ============================================================

def generate_report():

    print(
        "\n=============================================="
    )

    print(
        "     CANOPYAI EXPLAINABLE REPORT ENGINE"
    )

    print(
        "==============================================\n"
    )


    # --------------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------------

    print(
        "[REPORT] Loading CanopyAI outputs..."
    )

    report_data = get_report_data()


    # --------------------------------------------------------
    # COMPACT DATA
    # --------------------------------------------------------

    print(
        "[REPORT] Preparing compact evidence dataset..."
    )

    compact_data = build_compact_report_data(
        report_data
    )


    # --------------------------------------------------------
    # CLIENT
    # --------------------------------------------------------

    print(
        "[REPORT] Creating Gemini client..."
    )

    client = get_client()


    # --------------------------------------------------------
    # PROMPT
    # --------------------------------------------------------

    prompt = build_report_prompt(
        compact_data
    )


    print(
        "[REPORT] Sending long-form report request..."
    )

    print(
        f"[REPORT] Model: {MODEL_NAME}"
    )

    print(
        "[REPORT] Target length: 2200-2800 words"
    )


    # --------------------------------------------------------
    # GEMINI
    # --------------------------------------------------------

    try:

        response = client.models.generate_content(

            model=MODEL_NAME,

            contents=prompt,

            config=types.GenerateContentConfig(

                system_instruction=
                    SYSTEM_INSTRUCTION,

                temperature=0.2,

                max_output_tokens=9000
            )
        )

    except Exception as error:

        print(
            "\n=============================================="
        )

        print(
            "       GEMINI REPORT GENERATION ERROR"
        )

        print(
            "=============================================="
        )

        print(
            str(error)
        )

        print(
            "\n==============================================\n"
        )

        raise


    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    if not response.text:

        raise RuntimeError(
            "Gemini returned an empty report."
        )


    narrative = response.text.strip()


    # --------------------------------------------------------
    # WORD COUNT
    # --------------------------------------------------------

    word_count = len(
        narrative.split()
    )


    print(
        f"\n[REPORT] Generated word count: {word_count}"
    )


    # --------------------------------------------------------
    # SAVE TXT
    # --------------------------------------------------------

    output_file = (
        REPORTS_DIR
        / "CanopyAI_Report_Narrative.txt"
    )


    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            narrative
        )


    # --------------------------------------------------------
    # SAVE JSON METADATA
    # --------------------------------------------------------

    metadata_file = (
        REPORTS_DIR
        / "CanopyAI_Report_Metadata.json"
    )


    metadata = {

        "model":
            MODEL_NAME,

        "word_count":
            word_count,

        "target_minimum":
            2200,

        "target_preferred":
            "2300-2600",

        "target_maximum":
            2800,

        "status":
            "generated",

        "source":
            "CanopyAI existing outputs"
    }


    with open(
        metadata_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4
        )


    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

    print(
        "\n=============================================="
    )

    print(
        "       REPORT GENERATED SUCCESSFULLY"
    )

    print(
        "=============================================="
    )

    print(
        f"\nWord count: {word_count}"
    )

    print(
        f"\nNarrative saved to:"
    )

    print(
        output_file
    )

    print(
        f"\nMetadata saved to:"
    )

    print(
        metadata_file
    )

    print(
        "\n==============================================\n"
    )


    # --------------------------------------------------------
    # WARN IF TOO SHORT
    # --------------------------------------------------------

    if word_count < 1800:

        print(
            "[WARNING] Report is shorter than expected."
        )

        print(
            "[WARNING] We can increase the report length "
            "in the next iteration."
        )


    return narrative


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    generate_report()