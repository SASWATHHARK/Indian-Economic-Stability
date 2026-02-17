"""
CRUD operations for daily_market_data, sentiment_scores, stability_history, forecast_history.
"""
from datetime import date, datetime, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session

from app.database.models import (
    DailyMarketData,
    SentimentScore,
    StabilityHistory,
    ForecastHistory,
)


# ---------- Daily Market Data ----------
def upsert_market_data(
    db: Session,
    record_date: date,
    nifty_close: Optional[float] = None,
    sensex_close: Optional[float] = None,
    gold_close: Optional[float] = None,
    silver_close: Optional[float] = None,
    oil_close: Optional[float] = None,
    inr_close: Optional[float] = None,
    nifty_volatility: Optional[float] = None,
) -> DailyMarketData:
    row = db.query(DailyMarketData).filter(DailyMarketData.record_date == record_date).first()
    if row:
        if nifty_close is not None: row.nifty_close = nifty_close
        if sensex_close is not None: row.sensex_close = sensex_close
        if gold_close is not None: row.gold_close = gold_close
        if silver_close is not None: row.silver_close = silver_close
        if oil_close is not None: row.oil_close = oil_close
        if inr_close is not None: row.inr_close = inr_close
        if nifty_volatility is not None: row.nifty_volatility = nifty_volatility
    else:
        row = DailyMarketData(
            record_date=record_date,
            nifty_close=nifty_close,
            sensex_close=sensex_close,
            gold_close=gold_close,
            silver_close=silver_close,
            oil_close=oil_close,
            inr_close=inr_close,
            nifty_volatility=nifty_volatility,
        )
        db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_market_data_by_date(db: Session, record_date: date) -> Optional[DailyMarketData]:
    return db.query(DailyMarketData).filter(DailyMarketData.record_date == record_date).first()


def get_market_data_range(db: Session, start: date, end: date) -> List[DailyMarketData]:
    return db.query(DailyMarketData).filter(
        DailyMarketData.record_date >= start,
        DailyMarketData.record_date <= end,
    ).order_by(DailyMarketData.record_date).all()


# ---------- Sentiment ----------
def create_sentiment_score(
    db: Session,
    record_date: date,
    score: float,
    positive_count: int = 0,
    neutral_count: int = 0,
    negative_count: int = 0,
    total_articles: int = 0,
    raw_aggregate: Optional[dict] = None,
) -> SentimentScore:
    row = SentimentScore(
        record_date=record_date,
        score=score,
        positive_count=positive_count,
        neutral_count=neutral_count,
        negative_count=negative_count,
        total_articles=total_articles,
        raw_aggregate=raw_aggregate,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_sentiment_range(
    db: Session,
    start: date,
    end: date,
    sentiment_filter: Optional[str] = None,
) -> List[SentimentScore]:
    q = db.query(SentimentScore).filter(
        SentimentScore.record_date >= start,
        SentimentScore.record_date <= end,
    )
    if sentiment_filter == "positive":
        q = q.filter(SentimentScore.score >= 55)
    elif sentiment_filter == "negative":
        q = q.filter(SentimentScore.score <= 45)
    elif sentiment_filter == "neutral":
        q = q.filter(SentimentScore.score > 45, SentimentScore.score < 55)
    return q.order_by(SentimentScore.record_date.desc()).all()


# ---------- Stability ----------
def create_stability_history(
    db: Session,
    record_date: date,
    stability_score: float,
    category: str,
    risk_level: str,
    components: Optional[dict] = None,
    explanation: Optional[str] = None,
) -> StabilityHistory:
    row = StabilityHistory(
        record_date=record_date,
        stability_score=stability_score,
        category=category,
        risk_level=risk_level,
        components=components,
        explanation=explanation,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_stability_range(db: Session, start: date, end: date) -> List[StabilityHistory]:
    return db.query(StabilityHistory).filter(
        StabilityHistory.record_date >= start,
        StabilityHistory.record_date <= end,
    ).order_by(StabilityHistory.record_date.desc()).all()


# ---------- Forecast ----------
def create_forecast_history(
    db: Session,
    forecast_date: date,
    target_dates: list,
    predictions: list,
    current_value: float,
    uptrend_probability: float,
    downtrend_probability: float,
    confidence_level: str,
    model_metrics: Optional[dict] = None,
) -> ForecastHistory:
    row = ForecastHistory(
        forecast_date=forecast_date,
        target_dates=target_dates,
        predictions=predictions,
        current_value=current_value,
        uptrend_probability=uptrend_probability,
        downtrend_probability=downtrend_probability,
        confidence_level=confidence_level,
        model_metrics=model_metrics,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_latest_forecast(db: Session) -> Optional[ForecastHistory]:
    return db.query(ForecastHistory).order_by(ForecastHistory.created_at.desc()).first()
