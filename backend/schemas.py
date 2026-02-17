"""
Pydantic schemas for API request/response.
"""
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ---------- Market ----------
class MarketItem(BaseModel):
    date: str
    nifty_close: float
    sensex_close: float
    volume: Optional[float] = None


class MarketLatestResponse(BaseModel):
    status: str = "success"
    nifty: dict
    sensex: dict
    last_updated: str
    source: str = "database"


# ---------- News ----------
class NewsItem(BaseModel):
    id: int
    headline: str
    source: Optional[str] = None
    date: str
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None


class NewsListResponse(BaseModel):
    status: str = "success"
    news: List[NewsItem]
    filter: Optional[str] = None


# ---------- Sentiment ----------
class SentimentTodayResponse(BaseModel):
    status: str = "success"
    average_score: float
    pct_positive: float
    pct_negative: float
    pct_neutral: float
    total_articles: int
    date: str


# ---------- Stability ----------
class StabilityLatestResponse(BaseModel):
    status: str = "success"
    score: float
    category: str
    market_score: float
    sentiment_score: float
    volatility_score: float
    date: str


# ---------- Forecast ----------
class ForecastPoint(BaseModel):
    date: str
    predicted: float
    lower: float
    upper: float


class Forecast7DaysResponse(BaseModel):
    status: str = "success"
    forecast: List[ForecastPoint]
    current_value: float
    mae: Optional[float] = None
    rmse: Optional[float] = None
    model: str = "Prophet"
