"""
==========================================================
CanopyAI Configuration
==========================================================
This file contains all configurable parameters
used across the Recommendation Engine.
"""

# ==========================================================
# TREE PLANTING IMPACT SCORE WEIGHTS
# ==========================================================

TPIS_WEIGHTS = {

    "low_canopy": 0.30,

    "high_temperature": 0.25,

    "vegetation_deficit": 0.20,

    "urban_vulnerability": 0.15,

    "water_score": 0.10

}

# ==========================================================
# URBAN VULNERABILITY SCORE WEIGHTS
# ==========================================================

UVS_WEIGHTS = {

    "population": 0.40,

    "slum_density": 0.40,

    "temperature": 0.20

}

# ==========================================================
# TREE PLANTATION PARAMETERS
# ==========================================================

# Average plantation cost per tree (₹)
COST_PER_TREE = 200

# Average CO₂ absorbed by one tree in 10 years (kg)
CO2_PER_TREE_10Y = 25

# Approximate temperature reduction per 1000 trees (°C)
TEMP_REDUCTION_PER_1000_TREES = 0.10

# Maximum trees recommended for highest TPIS ward
MAX_TREES = 20000