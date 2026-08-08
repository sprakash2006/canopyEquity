"""
==========================================================
CanopyAI
API Schemas
==========================================================
"""

from pydantic import BaseModel


# ==========================================================
# HEALTH RESPONSE
# ==========================================================

class HealthResponse(BaseModel):

    status: str
    ai_engine: str
    backend: str


# ==========================================================
# PREDICTION RESPONSE
# ==========================================================

class PredictionResponse(BaseModel):

    status: str
    message: str
    output_file: str


# ==========================================================
# STATISTICS RESPONSE
# ==========================================================

class StatisticsResponse(BaseModel):

    canopy_percentage: float
    total_pixels: int
    class0: int
    class1: int
    class2: int
    class3: int