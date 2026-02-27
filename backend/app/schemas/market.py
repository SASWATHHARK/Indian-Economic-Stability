from pydantic import BaseModel
from typing import Optional, Dict, Any


class MarketDataItem(BaseModel):
    current: float
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    volume: Optional[int] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    volatility: Optional[float] = None


class MarketDataResponse(BaseModel):
    status: str = "success"
    is_live: bool = True
    date: str
    nifty: Optional[MarketDataItem] = None
    sensex: Optional[MarketDataItem] = None
    gold: Optional[MarketDataItem] = None
    silver: Optional[MarketDataItem] = None
    oil: Optional[MarketDataItem] = None
    inr: Optional[MarketDataItem] = None
    note: Optional[str] = None
    data_source: Optional[str] = None  # "live" | "offline_sample"
    demo_mode: Optional[bool] = None
    sample_data_date: Optional[str] = None  # e.g. "2025-02-20 14:30 IST" when demo

    class Config:
        extra = "allow"
