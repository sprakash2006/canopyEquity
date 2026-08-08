"""
==========================================================
CanopyAI
Budget Optimizer (Version 2)
Dynamic Programming (0/1 Knapsack)
==========================================================
"""

from pathlib import Path
import pandas as pd
import numpy as np

# ==========================================================
# PATHS
# ==========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "outputs" / "top_plantation_wards.csv"

OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(exist_ok=True)

# ==========================================================
# USER INPUT
# ==========================================================

BUDGET = 5000000        # ₹50 Lakh

print("=" * 70)
print("CANOPY AI - OPTIMAL PLANTATION PLANNER")
print("=" * 70)

print(f"Budget : ₹{BUDGET:,.0f}")

# ==========================================================
# LOAD DATA
# ==========================================================

df = pd.read_csv(INPUT_FILE)

print(f"Wards Loaded : {len(df)}")

# ==========================================================
# REMOVE INVALID ROWS
# ==========================================================

df = df.dropna(
    subset=[
        "Estimated_Cost",
        "TPIS"
    ]
)

df = df.reset_index(drop=True)

# ==========================================================
# SCALE COST
# ==========================================================
#
# Dynamic Programming cannot work efficiently
# with numbers like ₹3,317,000.
#
# Scale to ₹10,000 units.
#
# ==========================================================

COST_UNIT = 10000

costs = (

    df["Estimated_Cost"]

    / COST_UNIT

).astype(int).tolist()

# ==========================================================
# BENEFIT
# ==========================================================

benefits = (

    df["TPIS"]

    * 1000

).astype(int).tolist()

n = len(df)

capacity = BUDGET // COST_UNIT

print(f"Knapsack Capacity : {capacity}")

# ==========================================================
# DP TABLE
# ==========================================================

dp = np.zeros(

    (

        n + 1,

        capacity + 1

    ),

    dtype=np.int32

)

print("Dynamic Programming Table Created")

# ==========================================================
# BUILD DP TABLE
# ==========================================================

for i in range(1, n + 1):

    cost = costs[i - 1]

    benefit = benefits[i - 1]

    for budget in range(capacity + 1):

        if cost <= budget:

            include = (

                benefit

                +

                dp[
                    i - 1,
                    budget - cost
                ]

            )

            exclude = dp[
                i - 1,
                budget
            ]

            dp[
                i,
                budget
            ] = max(

                include,

                exclude

            )

        else:

            dp[
                i,
                budget
            ] = dp[
                i - 1,
                budget
            ]

print("DP Table Completed")
# ==========================================================
# BACKTRACK
# ==========================================================

print("Finding Optimal Plantation Plan...")

selected_indices = []

remaining_budget = capacity

for i in range(n, 0, -1):

    if dp[i, remaining_budget] != dp[i - 1, remaining_budget]:

        selected_indices.append(i - 1)

        remaining_budget -= costs[i - 1]

selected_indices.reverse()

print(f"Selected Wards : {len(selected_indices)}")

# ==========================================================
# CREATE RESULT DATAFRAME
# ==========================================================

selected_df = df.iloc[selected_indices].copy()

selected_df = selected_df.sort_values(
    by="TPIS",
    ascending=False
)

# ==========================================================
# SUMMARY
# ==========================================================

total_cost = int(

    selected_df[
        "Estimated_Cost"
    ].sum()

)

total_trees = int(

    selected_df[
        "Estimated_Trees"
    ].sum()

)

total_co2 = float(

    selected_df[
        "Estimated_CO2_10Y_kg"
    ].sum()

)

total_temp = float(

    selected_df[
        "Estimated_Temp_Reduction_C"
    ].sum()

)

average_tpis = float(

    selected_df[
        "TPIS"
    ].mean()

)

budget_remaining = BUDGET - total_cost

# ==========================================================
# DISPLAY
# ==========================================================

print()

print("=" * 70)

print("OPTIMAL PLANTATION PLAN")

print("=" * 70)

for rank, row in enumerate(

    selected_df.itertuples(),

    start=1

):

    print()

    print(f"{rank}. {row.ward_name}")

    print(f"Ward Number      : {row.ward_number}")

    print(f"Priority         : {row.Priority}")

    print(f"TPIS             : {row.TPIS:.3f}")

    print(f"Trees            : {int(row.Estimated_Trees):,}")

    print(f"Cost             : ₹{row.Estimated_Cost:,.0f}")

    print(f"Reason           : {row.Recommendation_Reason}")

print()

print("=" * 70)

print("SUMMARY")

print("=" * 70)

print(f"Selected Wards        : {len(selected_df)}")

print(f"Total Trees           : {total_trees:,}")

print(f"Budget Used           : ₹{total_cost:,.0f}")

print(f"Budget Remaining      : ₹{budget_remaining:,.0f}")

print(f"Average TPIS          : {average_tpis:.3f}")

print(f"Expected CO₂ (10Y)    : {total_co2/1000:.2f} Tons")

print(f"Temperature Reduction : {total_temp:.2f} °C")
# ==========================================================
# CREATE PLANTATION REPORT
# ==========================================================

print("\nGenerating Plantation Report...")

report = selected_df.copy()

report["Estimated_CO2_10Y_Tons"] = (
    report["Estimated_CO2_10Y_kg"] / 1000
).round(2)

report["Estimated_Cost_Lakh"] = (
    report["Estimated_Cost"] / 100000
).round(2)

report["Trees_per_Hectare"] = (
    report["Estimated_Trees"] /
    report["area_hectares"].replace(0, np.nan)
).fillna(0).round(0)

# ==========================================================
# PLANTATION PRIORITY SCORE
# ==========================================================

report["Plantation_Score"] = (

    report["TPIS"] * 100

).round(2)

# ==========================================================
# SAVE OPTIMIZED PLAN
# ==========================================================

optimized_csv = OUTPUT_DIR / "optimized_plan.csv"

report.to_csv(
    optimized_csv,
    index=False
)

# ==========================================================
# SAVE SUMMARY
# ==========================================================

summary_file = OUTPUT_DIR / "optimization_summary.txt"

with open(summary_file, "w") as f:

    f.write("=" * 70 + "\n")
    f.write("CANOPY AI - OPTIMAL PLANTATION PLAN\n")
    f.write("=" * 70 + "\n\n")

    f.write(f"Budget                 : ₹{BUDGET:,.0f}\n")
    f.write(f"Budget Used            : ₹{total_cost:,.0f}\n")
    f.write(f"Budget Remaining       : ₹{budget_remaining:,.0f}\n")
    f.write(f"Selected Wards         : {len(report)}\n")
    f.write(f"Trees To Plant         : {total_trees:,}\n")
    f.write(f"Average TPIS           : {average_tpis:.3f}\n")
    f.write(f"Expected CO₂ (10 Years): {total_co2/1000:.2f} Tons\n")
    f.write(f"Temperature Reduction  : {total_temp:.2f} °C\n\n")

    f.write("=" * 70 + "\n")
    f.write("SELECTED WARDS\n")
    f.write("=" * 70 + "\n\n")

    for i, row in enumerate(report.itertuples(), start=1):

        f.write(f"{i}. {row.ward_name}\n")
        f.write(f"   Ward Number : {row.ward_number}\n")
        f.write(f"   Priority    : {row.Priority}\n")
        f.write(f"   TPIS        : {row.TPIS:.3f}\n")
        f.write(f"   Trees       : {int(row.Estimated_Trees):,}\n")
        f.write(f"   Cost        : ₹{row.Estimated_Cost:,.0f}\n")
        f.write(f"   Reason      : {row.Recommendation_Reason}\n")
        f.write("\n")

print("Optimization Report Generated")

# ==========================================================
# FINAL OUTPUT
# ==========================================================

print("\n" + "=" * 70)
print("CANOPY AI OPTIMIZATION COMPLETED")
print("=" * 70)

print(f"Optimized CSV      : {optimized_csv}")
print(f"Summary Report     : {summary_file}")

print("=" * 70)