"""
SQLAlchemy ORM models for persistence and historical analysis.
Tables: daily_market_data, sentiment_scores, stability_history, forecast_history.
"""
from datetime import date, datetime
from sqlalchemy import Column, Integer, Float, String, Date, DateTime, Text, JSON, Index

from app.database.base import Base


class DailyMarketData(Base):
    """Daily snapshot of market indices (NIFTY, SENSEX, etc.) to avoid repeated API calls."""
    __tablename__ = "daily_market_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    record_date = Column(Date, nullable=False, index=True)
    nifty_close = Column(Float, nullable=True)
    sensex_close = Column(Float, nullable=True)
    gold_close = Column(Float, nullable=True)
    silver_close = Column(Float, nullable=True)
    oil_close = Column(Float, nullable=True)
    inr_close = Column(Float, nullable=True)
    nifty_volatility = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("ix_daily_market_record_date", "record_date", unique=True),)


class SentimentScore(Base):
    """Stored sentiment scores for history and filtering."""
    __tablename__ = "sentiment_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    record_date = Column(Date, nullable=False, index=True)
    score = Column(Float, nullable=False)  # 0-100
    positive_count = Column(Integer, default=0)
    neutral_count = Column(Integer, default=0)
    negative_count = Column(Integer, default=0)
    total_articles = Column(Integer, default=0)
    raw_aggregate = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class StabilityHistory(Base):
    """Historical stability scores for trend analysis."""
    __tablename__ = "stability_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    record_date = Column(Date, nullable=False, index=True)
    stability_score = Column(Float, nullable=False)
    category = Column(String(32), nullable=True)
    risk_level = Column(String(32), nullable=True)
    components = Column(JSON, nullable=True)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ForecastHistory(Base):
    """Stored forecast runs for backtesting and audit."""
    __tablename__ = "forecast_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    forecast_date = Column(Date, nullable=False, index=True)  # date of run
    target_dates = Column(JSON, nullable=True)   # list of forecast dates
    predictions = Column(JSON, nullable=True)    # list of {date, predicted, upper, lower}
    current_value = Column(Float, nullable=True)
    uptrend_probability = Column(Float, nullable=True)
    downtrend_probability = Column(Float, nullable=True)
    confidence_level = Column(String(32), nullable=True)
    model_metrics = Column(JSON, nullable=True)    # mae, rmse, r2
    created_at = Column(DateTime, default=datetime.utcnow)
