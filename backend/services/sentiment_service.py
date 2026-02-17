"""
Sentiment service - VADER.
> 0.05 Positive, < -0.05 Negative, else Neutral.
Returns: average daily score, % positive, % negative.
"""
import logging
from datetime import date
from typing import Dict, List, Tuple

from sqlalchemy.orm import Session

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    ANALYZER = SentimentIntensityAnalyzer()
except ImportError:
    ANALYZER = None

from models import NewsData

logger = logging.getLogger(__name__)


def analyze_headline(text: str) -> Tuple[float, str]:
    """Return (compound_score, label)."""
    if not text or not ANALYZER:
        return 0.0, "neutral"
    scores = ANALYZER.polarity_scores(text)
    c = scores["compound"]
    if c > 0.05:
        return round(c, 4), "positive"
    if c < -0.05:
        return round(c, 4), "negative"
    return round(c, 4), "neutral"


def get_sentiment_today(db: Session, target_date: date = None) -> Dict:
    """
    Aggregate sentiment for target date from NewsData.
    Returns: average_score, pct_positive, pct_negative, pct_neutral, total_articles.
    """
    d = target_date or date.today()
    rows = db.query(NewsData).filter(NewsData.date == d).all()
    if not rows:
        return {
            "average_score": 0.0,
            "pct_positive": 0.0,
            "pct_negative": 0.0,
            "pct_neutral": 100.0,
            "total_articles": 0,
            "date": d.isoformat(),
        }
    scores = [r.sentiment_score for r in rows if r.sentiment_score is not None]
    if not scores:
        scores = [0.0]
    avg = sum(scores) / len(scores)
    pos = sum(1 for s in scores if s > 0.05)
    neg = sum(1 for s in scores if s < -0.05)
    neu = len(scores) - pos - neg
    n = len(scores)
    return {
        "average_score": round(avg, 4),
        "pct_positive": round(100.0 * pos / n, 2),
        "pct_negative": round(100.0 * neg / n, 2),
        "pct_neutral": round(100.0 * neu / n, 2),
        "total_articles": n,
        "date": d.isoformat(),
    }
