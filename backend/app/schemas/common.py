from pydantic import BaseModel
from typing import Optional


class HealthResponse(BaseModel):
    status: str = "healthy"
    timestamp: str
    version: Optional[str] = None
    database: Optional[str] = "connected"


class RefreshResponse(BaseModel):
    status: str
    message: str
    market_stored: bool = False
    sentiment_stored: bool = False
    stability_stored: bool = False
