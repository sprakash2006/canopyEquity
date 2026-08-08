"""
==========================================================
CanopyAI
Recommendation Engine V4
==========================================================
"""

from pathlib import Path
import pandas as pd

from backend.services.scoring.environment import EnvironmentScorer
from backend.services.scoring.social import SocialScorer
from backend.services.scoring.feasibility import FeasibilityScorer
from backend.services.scoring.tpis import TPISScorer

# ==========================================================
# PATHS
# ==========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATASET = BASE_DIR / "processed" / "mcd_wards_master.csv"

OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(exist_ok=True)

print("=" * 70)
print("CANOPY AI - RECOMMENDATION ENGINE")
print("=" * 70)

# ==========================================================
# LOAD DATA
# ==========================================================

df = pd.read_csv(DATASET)

print(f"Wards Loaded : {len(df)}")

# ==========================================================
# INITIALIZE ENGINES
# ==========================================================

environment_engine = EnvironmentScorer()

social_engine = SocialScorer()

feasibility_engine = FeasibilityScorer()

tpis_engine = TPISScorer()

print("AI Engines Loaded")

# ==========================================================
# ENVIRONMENT
# ==========================================================

df = environment_engine.calculate(df)

print("Environment Score Completed")

# ==========================================================
# SOCIAL
# ==========================================================

df = social_engine.calculate(df)

print("Social Score Completed")

# ==========================================================
# FEASIBILITY
# ==========================================================

df = feasibility_engine.calculate(df)

print("Feasibility Score Completed")

# ==========================================================
# TPIS
# ==========================================================

df = tpis_engine.calculate(df)

print("TPIS Engine Completed")

# ==========================================================
# SORT
# ==========================================================

recommendations = df.sort_values(

    by="TPIS",

    ascending=False

).reset_index(drop=True)
# ==========================================================
# DISPLAY TOP RECOMMENDATIONS
# ==========================================================

TOP_K = 10

top = recommendations.head(TOP_K)

print()

print("=" * 70)
print("TOP TREE PLANTATION RECOMMENDATIONS")
print("=" * 70)

for rank, row in enumerate(top.itertuples(), start=1):

    print()

    print(f"{rank}. {row.ward_name}")

    print(f"Ward Number            : {row.ward_number}")

    print(f"Environment Score      : {row.Environment_Score:.2f}")

    print(f"Social Score           : {row.Social_Score:.2f}")

    print(f"Feasibility Score      : {row.Feasibility_Score:.2f}")

    print(f"Urban Vulnerability    : {row.Urban_Vulnerability_Score:.2f}")

    print(f"TPIS                   : {row.TPIS:.2f}")

    print(f"Priority               : {row.Priority}")

    print(f"Estimated Trees        : {row.Estimated_Trees:,}")

    print(f"Estimated Cost         : ₹{row.Estimated_Cost:,.0f}")

    print(f"Estimated CO₂ (10Y)    : {row.Estimated_CO2_10Y_kg/1000:.2f} Tons")

    print(f"Temperature Reduction  : {row.Estimated_Temp_Reduction_C:.2f} °C")

    print(f"Reason                 : {row.Recommendation_Reason}")

print()

print("=" * 70)

# ==========================================================
# SAVE CSV
# ==========================================================

csv_path = OUTPUT_DIR / "top_plantation_wards.csv"

recommendations.to_csv(
    csv_path,
    index=False
)

print("Recommendation CSV Saved")

print(csv_path)

# ==========================================================
# SAVE SUMMARY
# ==========================================================

summary_path = OUTPUT_DIR / "recommendation_summary.txt"

with open(summary_path, "w", encoding="utf-8") as file:

    file.write("=" * 70 + "\n")

    file.write("CANOPY AI - TREE PLANTATION RECOMMENDATION REPORT\n")

    file.write("=" * 70 + "\n\n")

    file.write(f"Total Wards Analysed : {len(recommendations)}\n")

    file.write(f"Top Recommendations  : {TOP_K}\n\n")

    for rank, row in enumerate(top.itertuples(), start=1):

        file.write(f"{rank}. {row.ward_name}\n")

        file.write(f"   Ward Number           : {row.ward_number}\n")

        file.write(f"   Environment Score     : {row.Environment_Score:.2f}\n")

        file.write(f"   Social Score          : {row.Social_Score:.2f}\n")

        file.write(f"   Feasibility Score     : {row.Feasibility_Score:.2f}\n")

        file.write(f"   Urban Vulnerability   : {row.Urban_Vulnerability_Score:.2f}\n")

        file.write(f"   TPIS                  : {row.TPIS:.2f}\n")

        file.write(f"   Priority              : {row.Priority}\n")

        file.write(f"   Estimated Trees       : {row.Estimated_Trees:,}\n")

        file.write(f"   Estimated Cost        : ₹{row.Estimated_Cost:,.0f}\n")

        file.write(f"   Estimated CO₂ (10Y)   : {row.Estimated_CO2_10Y_kg/1000:.2f} Tons\n")

        file.write(f"   Temperature Reduction : {row.Estimated_Temp_Reduction_C:.2f} °C\n")

        file.write(f"   Reason                : {row.Recommendation_Reason}\n")

        file.write("\n")

print("Recommendation Summary Saved")

print(summary_path)

print()

print("=" * 70)

print("RECOMMENDATION ENGINE COMPLETED SUCCESSFULLY")

print("=" * 70)