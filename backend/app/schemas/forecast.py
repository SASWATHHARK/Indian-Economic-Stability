from pydantic import BaseModel
from typing import List, Optional


class ForecastPoint(BaseModel):
    date: str
    predicted: float
    upper: Optional[float] = None
    lower: Optional[float] = None
    confidence: Optional[float] = None


class ForecastResponse(BaseModel):
    status: str = "success"
    forecast: List[ForecastPoint]
    summary: Optional[dict] = None
    forecast_score: Optional[float] = None
    current_value: Optional[float] = None
    model: str = "Facebook Prophet"
    note: Optional[str] = None
    uptrend_probability: Optional[float] = None
    downtrend_probability: Optional[float] = None
    confidence_level: Optional[str] = None
    data_source: Optional[str] = None
    demo_mode: Optional[bool] = None
    sample_data_date: Optional[str] = None

    class Config:
        extra = "allow"


class ModelMetricsResponse(BaseModel):
    mae: float
    rmse: float
    r2_score: float
    confidence_level: str  # High / Medium / Low
    model: str = "Facebook Prophet"
    note: Optional[str] = None
