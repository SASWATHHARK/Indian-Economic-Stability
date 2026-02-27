from pydantic import BaseModel
from typing import Optional


class StabilityComponents(BaseModel):
    market_momentum: Optional[float] = None
    sentiment: Optional[float] = None
    volatility_inverse: Optional[float] = None
    inflation: Optional[float] = None
    liquidity: Optional[float] = None


class StabilityResponse(BaseModel):
    status: str = "success"
    stability_score: float
    category: str
    risk_level: str
    explanation: str
    components: StabilityComponents
    breakdown: Optional[dict] = None
    timestamp: str
    disclaimer: Optional[str] = None
    data_source: Optional[str] = None
    demo_mode: Optional[bool] = None
    sample_data_date: Optional[str] = None    class Config:
        extra = "allow"