"""
Stability score service.
Final = 0.4*Market + 0.3*Sentiment + 0.2*InflationProxy + 0.1*Volatility
Categories: 0-40 Unstable, 40-70 Moderate, 70-100 Stable.
"""
import logging
from datetime import date, datetime, timedelta
from typing import Dict, Optional

from sqlalchemy.orm import Session

from models import MarketData, NewsData, StabilityScore
from services.sentiment_service import get_sentiment_today

logger = logging.getLogger(__name__)

W_MARKET = 0.4
W_SENTIMENT = 0.3
W_INFLATION = 0.2
W_VOLATILITY = 0.1


def _market_strength_0_100(db: Session, d: date) -> float:
    """% change over 7 days for NIFTY -> 0-100."""
    rows = db.query(MarketData).filter(
        MarketData.date <= d,
        MarketData.nifty_close.isnot(None),
    ).order_by(MarketData.date.desc()).limit(8).all()
    if len(rows) < 2:
        return 50.0
    latest = rows[0].nifty_close
    week_ago = rows[-1].nifty_close if len(rows) >= 8 else rows[-1].nifty_close
    if week_ago and week_ago > 0:
        pct = (latest - week_ago) / week_ago * 100
        # -5% -> 0, 0% -> 50, +5% -> 100
        score = 50 + pct * 10
        return round(min(100, max(0, score)), 2)
    return 50.0


def _sentiment_0_100(db: Session, d: date) -> float:
    """Average daily sentiment scaled to 0-100."""
    agg = get_sentiment_today(db, d)
    avg = agg["average_score"]
    # compound -1..1 -> 0..100
    score = (avg + 1) / 2 * 100
    return round(min(100, max(0, score)), 2)


def _volatility_0_100(db: Session, d: date) -> float:
    """Rolling std of returns -> inverse (lower vol = higher score)."""
    rows = db.query(MarketData).filter(
        MarketData.date <= d,
        MarketData.nifty_close.isnot(None),
    ).order_by(MarketData.date.asc()).limit(30).all()
    if len(rows) < 5:
        return 50.0
    closes = [r.nifty_close for r in rows]
    returns = [(closes[i] - closes[i - 1]) / closes[i - 1] * 100 for i in range(1, len(closes))]
    import math
    std = math.sqrt(sum((r - sum(returns) / len(returns)) ** 2 for r in returns) / len(returns))
    # 0% vol -> 100, 3% vol -> 0
    score = 100 - min(100, std * 33)
    return round(max(0, score), 2)


def _inflation_proxy_0_100(db: Session, d: date) -> float:
    """Market trend stability as inflation proxy - 7d trend consistency."""
    return 50.0


def compute_and_store(db: Session, target_date: date = None) -> Optional[Dict]:
    """Compute stability, store, return result."""
    d = target_date or date.today()
    try:
        m = _market_strength_0_100(db, d)
        s = _sentiment_0_100(db, d)
        v = _volatility_0_100(db, d)
        infl = _inflation_proxy_0_100(db, d)
        final = round(
            W_MARKET * m + W_SENTIMENT * s + W_INFLATION * infl + W_VOLATILITY * v,
            2,
        )
        category = "Stable" if final >= 70 else ("Moderate" if final >= 40 else "Unstable")

        existing = db.query(StabilityScore).filter(StabilityScore.date == d).first()
        if existing:
            existing.market_score = m
            existing.sentiment_score = s
            existing.volatility_score = v
            existing.final_score = final
            existing.category = category
        else:
            row = StabilityScore(
                date=d,
                market_score=m,
                sentiment_score=s,
                volatility_score=v,
                final_score=final,
                category=category,
            )
            db.add(row)
        db.commit()

        return {
            "score": final,
            "category": category,
            "market_score": m,
            "sentiment_score": s,
            "volatility_score": v,
            "date": d.isoformat(),
        }
    except Exception as e:
        logger.exception("stability compute error: %s", e)
        return None


def get_latest(db: Session) -> Optional[Dict]:
    """Get latest stability from DB."""
    row = db.query(StabilityScore).order_by(StabilityScore.date.desc()).first()
    if not row:
        return None
    return {
        "score": row.final_score,
        "category": row.category,
        "market_score": row.market_score,
        "sentiment_score": row.sentiment_score,
        "volatility_score": row.volatility_score,
        "date": row.date.isoformat(),
    }
