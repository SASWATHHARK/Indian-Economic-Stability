"""
SQLAlchemy ORM models.
Tables: market_data, news_data, stability_score.
PostgreSQL-ready (SQLite for now).
"""
from datetime import date, datetime
from sqlalchemy import Column, Integer, Float, String, Date, DateTime, Text, Index

from database import Base


class MarketData(Base):
    """Daily NIFTY & SENSEX OHLCV snapshot."""
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, index=True)
    nifty_close = Column(Float, nullable=True)
    sensex_close = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    nifty_open = Column(Float, nullable=True)
    nifty_high = Column(Float, nullable=True)
    nifty_low = Column(Float, nullable=True)
    sensex_open = Column(Float, nullable=True)
    sensex_high = Column(Float, nullable=True)
    sensex_low = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("ix_market_data_date", "date", unique=True),)


class NewsData(Base):
    """News headlines with sentiment."""
    __tablename__ = "news_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    headline = Column(Text, nullable=False)
    source = Column(String(255), nullable=True)
    date = Column(Date, nullable=False, index=True)
    sentiment_score = Column(Float, nullable=True)
    link = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class StabilityScore(Base):
    """Daily stability score components and final."""
    __tablename__ = "stability_score"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, index=True)
    market_score = Column(Float, nullable=False)
    sentiment_score = Column(Float, nullable=False)
    volatility_score = Column(Float, nullable=False)
    final_score = Column(Float, nullable=False)
    category = Column(String(32), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("ix_stability_score_date", "date", unique=True),)
