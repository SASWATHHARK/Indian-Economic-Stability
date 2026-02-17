from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import date, datetime
from app.services import DataFetcher
from app.sentiment import SentimentService
from app.schemas.sentiment import SentimentResponse, SentimentArticle
from app.utils.stability_cache import update_stability_cache

router = APIRouter()
data_fetcher = DataFetcher()
sentiment_svc = SentimentService()

@router.get("/sentiment", response_model=SentimentResponse)
def get_sentiment(
    sentiment: Optional[str] = Query(None, description="Filter: positive | negative | neutral"),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
):
    try:
        headlines = data_fetcher.fetch_news_headlines(
            query="India economy RBI inflation stock market",
            max_results=20,
        )
        if not headlines:
            raise Exception("No news available")
        results = sentiment_svc.analyze_batch_weighted(
            headlines, title_key="title", source_key="source", published_key="published",
        )
        aggregate = sentiment_svc.get_aggregate_weighted(results, headlines)
        score = sentiment_svc.normalize_score(aggregate)
        update_stability_cache(50.0, score, None)

        if sentiment or date_from or date_to:
            df = datetime.combine(date_from, datetime.min.time()) if date_from else None
            dt_end = datetime.combine(date_to, datetime.max.time()) if date_to else None
            headlines, results = sentiment_svc.filter_articles(
                headlines, results,
                sentiment_filter=sentiment,
                date_from=df,
                date_to=dt_end,
            )
            if headlines:
                aggregate = sentiment_svc.get_aggregate_weighted(results, headlines)
                score = sentiment_svc.normalize_score(aggregate)

        articles = [
            SentimentArticle(
                title=headlines[i]["title"],
                source=headlines[i]["source"],
                link=headlines[i]["link"],
                sentiment=results[i],
                published=headlines[i].get("published"),
                weight=results[i].get("weight"),
            )
            for i in range(len(results))
        ]
        return SentimentResponse(
            status="success",
            sentiment_score=round(score, 2),
            aggregate=aggregate,
            articles=articles,
            analyzer="VADER",
            filters_applied={"sentiment": sentiment, "date_from": str(date_from) if date_from else None, "date_to": str(date_to) if date_to else None},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
