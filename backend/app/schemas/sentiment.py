from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class SentimentArticle(BaseModel):
    title: str
    source: str
    link: str
    sentiment: dict
    published: Optional[str] = None
    weight: Optional[float] = None


class SentimentResponse(BaseModel):
    status: str = "success"
    sentiment_score: float
    aggregate: dict
    articles: List[SentimentArticle]
    analyzer: str = "VADER"
    filters_applied: Optional[dict] = None
    data_source: Optional[str] = None
    demo_mode: Optional[bool] = None
    sample_data_date: Optional[str] = None

    class Config:
        extra = "allow"


class SentimentFilterParams(BaseModel):
    sentiment: Optional[str] = None   # positive | negative | neutral
    date_from: Optional[date] = None
    date_to: Optional[date] = None
