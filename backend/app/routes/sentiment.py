from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import date, datetime
from app.services import data_router
from app.sentiment import SentimentService
from app.schemas.sentiment import SentimentResponse, SentimentArticle
from app.utils.stability_cache import update_stability_cache

router = APIRouter()
sentiment_svc = SentimentService()

@router.get("/sentiment", response_model=SentimentResponse)
def get_sentiment(
    sentiment: Optional[str] = Query(None, description="Filter: positive | negative | neutral"),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
):
    try:
        df = datetime.combine(date_from, datetime.min.time()) if date_from else None
        dt_end = datetime.combine(date_to, datetime.max.time()) if date_to else None
        payload = data_router.get_news_then_sentiment(
            query="India economy RBI inflation stock market",
            max_results=20,
            sentiment_analyzer=sentiment_svc,
            sentiment_filter=sentiment,
            date_from=df,
            date_to=dt_end,
        )
        if payload.get("data_source") == "live" and payload.get("aggregate"):
            update_stability_cache(50.0, payload["sentiment_score"], None)
        articles = [SentimentArticle(**a) for a in payload.get("articles", [])]
        return SentimentResponse(
            status=payload.get("status", "success"),
            sentiment_score=payload["sentiment_score"],
            aggregate=payload.get("aggregate", {}),
            articles=articles,
            analyzer=payload.get("analyzer", "VADER"),
            filters_applied=payload.get("filters_applied"),
            data_source=payload.get("data_source"),
            demo_mode=payload.get("demo_mode"),
            sample_data_date=payload.get("sample_data_date"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
