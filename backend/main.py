"""
AI-Based Indian Economic Stability Analyzer - Production API.
FastAPI with CORS, clean endpoints.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from database import get_db, init_db, SessionLocal
from models import MarketData, NewsData, StabilityScore
from schemas import (
    MarketLatestResponse,
    NewsListResponse,
    NewsItem,
    SentimentTodayResponse,
    StabilityLatestResponse,
    Forecast7DaysResponse,
    ForecastPoint,
)
from services.market_service import fetch_and_store_market_data, get_latest_market
from services.news_service import fetch_and_store_news, get_news
from services.sentiment_service import get_sentiment_today
from services.stability_service import compute_and_store, get_latest
from services.forecast_service import get_7day_forecast
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCHEDULER_ENABLED = True


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("Database initialized")
    if SCHEDULER_ENABLED:
        try:
            from scheduler import start_scheduler
            start_scheduler()
        except Exception as e:
            logger.warning("Scheduler not started: %s", e)
    yield
    logger.info("Shutdown")


app = FastAPI(
    title="AI-Based Indian Economic Stability API",
    description="Production-ready economic stability framework: NIFTY/SENSEX, sentiment, forecast.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Economic Stability API running",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": [
            "GET /market/latest",
            "GET /sentiment/today",
            "GET /stability/latest",
            "GET /forecast/7days",
            "GET /news?filter=positive|negative|all",
            "POST /refresh",
            "GET /health",
        ],
    }


@app.get("/market/latest", response_model=MarketLatestResponse)
def market_latest(db: Session = Depends(get_db)):
    data = get_latest_market(db)
    if not data:
        fetch_and_store_market_data(db)
        data = get_latest_market(db)
    if not data:
        raise HTTPException(status_code=503, detail="No market data available")
    return MarketLatestResponse(
        status="success",
        nifty=data["nifty"],
        sensex=data["sensex"],
        last_updated=data["date"],
        source="database",
    )


@app.get("/sentiment/today", response_model=SentimentTodayResponse)
def sentiment_today(db: Session = Depends(get_db)):
    agg = get_sentiment_today(db)
    if agg["total_articles"] == 0:
        fetch_and_store_news(db)
        agg = get_sentiment_today(db)
    return SentimentTodayResponse(
        status="success",
        average_score=agg["average_score"],
        pct_positive=agg["pct_positive"],
        pct_negative=agg["pct_negative"],
        pct_neutral=agg["pct_neutral"],
        total_articles=agg["total_articles"],
        date=agg["date"],
    )


@app.get("/stability/latest", response_model=StabilityLatestResponse)
def stability_latest(db: Session = Depends(get_db)):
    data = get_latest(db)
    if not data:
        compute_and_store(db)
        data = get_latest(db)
    if not data:
        raise HTTPException(status_code=503, detail="No stability data")
    return StabilityLatestResponse(
        status="success",
        score=data["score"],
        category=data["category"],
        market_score=data["market_score"],
        sentiment_score=data["sentiment_score"],
        volatility_score=data["volatility_score"],
        date=data["date"],
    )


@app.get("/forecast/7days", response_model=Forecast7DaysResponse)
def forecast_7days(db: Session = Depends(get_db)):
    result = get_7day_forecast(db)
    return Forecast7DaysResponse(
        status="success",
        forecast=[ForecastPoint(**p) for p in result["forecast"]],
        current_value=result["current_value"],
        mae=result.get("mae"),
        rmse=result.get("rmse"),
        model=result.get("model", "Prophet"),
    )


@app.get("/news", response_model=NewsListResponse)
def news_list(
    filter: str = Query("all", description="positive|negative|neutral|all"),
    db: Session = Depends(get_db),
):
    rows = get_news(db, filter_sentiment=None if filter == "all" else filter)
    if not rows:
        fetch_and_store_news(db)
        rows = get_news(db, filter_sentiment=None if filter == "all" else filter)
    items = [
        NewsItem(
            id=r.id,
            headline=r.headline,
            source=r.source,
            date=r.date.isoformat(),
            sentiment_score=r.sentiment_score,
            sentiment_label="positive" if (r.sentiment_score or 0) > 0.05 else ("negative" if (r.sentiment_score or 0) < -0.05 else "neutral"),
        )
        for r in rows
    ]
    return NewsListResponse(status="success", news=items, filter=filter)


@app.post("/refresh")
def refresh(db: Session = Depends(get_db)):
    """Trigger full data refresh: market, news, stability."""
    try:
        fetch_and_store_market_data(db)
        fetch_and_store_news(db)
        compute_and_store(db)
        return {"status": "success", "message": "Refresh completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "healthy"}


# Backward-compatible aliases
@app.get("/market-data")
def market_data_legacy(db: Session = Depends(get_db)):
    data = get_latest_market(db)
    if not data:
        fetch_and_store_market_data(db)
        data = get_latest_market(db)
    if not data:
        raise HTTPException(status_code=503, detail="No market data")
    def _mk(m):
        ch = (m["close"] - m["open"]) if m.get("open") else 0
        pct = (ch / m["open"] * 100) if m.get("open") else 0
        return {"current": m["close"], "open": m["open"], "high": m["high"], "low": m["low"], "volume": data.get("volume"), "volatility": 0.95, "change": round(ch, 2), "change_percent": round(pct, 2)}
    return {
        "status": "success",
        "is_live": True,
        "nifty": _mk(data["nifty"]),
        "sensex": _mk(data["sensex"]),
        "date": data["date"],
    }


@app.get("/forecast")
def forecast_legacy(db: Session = Depends(get_db)):
    r = get_7day_forecast(db)
    return {
        "status": "success",
        "forecast": r["forecast"],
        "current_value": r["current_value"],
        "mae": r.get("mae"),
        "rmse": r.get("rmse"),
        "model": r.get("model", "Prophet"),
    }


@app.get("/sentiment")
def sentiment_legacy(db: Session = Depends(get_db)):
    agg = get_sentiment_today(db)
    if agg["total_articles"] == 0:
        fetch_and_store_news(db)
        agg = get_sentiment_today(db)
    rows = get_news(db, filter_sentiment=None, limit=50)
    articles = [
        {"title": r.headline, "source": r.source, "link": r.link, "sentiment": {"compound": r.sentiment_score or 0, "label": "positive" if (r.sentiment_score or 0) > 0.05 else ("negative" if (r.sentiment_score or 0) < -0.05 else "neutral")}}
        for r in rows
    ]
    return {
        "status": "success",
        "sentiment_score": round((agg["average_score"] + 1) / 2 * 100, 2),
        "aggregate": agg,
        "articles": articles,
        "analyzer": "VADER",
    }


@app.get("/stability-score")
def stability_legacy(db: Session = Depends(get_db)):
    data = get_latest(db)
    if not data:
        compute_and_store(db)
        data = get_latest(db)
    if not data:
        raise HTTPException(status_code=503, detail="No stability data")
    ms, ss, vs = data["market_score"], data["sentiment_score"], data["volatility_score"]
    interp = f"{data['category']}: Market strength {ms:.0f}%, sentiment {ss:.0f}%, volatility {vs:.0f}%."
    return {
        "status": "success",
        "stability_score": data["score"],
        "category": data["category"],
        "interpretation": interp,
        "components": {"market_trend": round(ms, 1), "sentiment": round(ss, 1), "economic_indicators": round(vs, 1)},
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
