"""
News service - fetch India economy, Nifty, RBI headlines.
Uses Google News RSS; optional NewsAPI/GNews via env.
"""
import logging
from datetime import date, datetime
from typing import List, Optional
from urllib.parse import quote_plus

import feedparser
import requests
from sqlalchemy.orm import Session

from models import NewsData
from services.sentiment_service import analyze_headline

logger = logging.getLogger(__name__)

QUERIES = ["India economy", "Nifty", "RBI"]
MAX_PER_QUERY = 10


def _fetch_google_news(query: str, max_results: int = 10) -> List[dict]:
    try:
        encoded = quote_plus(query)
        url = f"https://news.google.com/rss/search?q={encoded}&hl=en-IN&gl=IN&ceid=IN:en"
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries[:max_results]:
            pub = entry.get("published", "")
            try:
                from dateutil import parser as date_parser
                dt = date_parser.parse(pub)
                d = dt.date()
            except Exception:
                d = date.today()
            articles.append({
                "headline": entry.get("title", ""),
                "source": entry.get("source", {}).get("title", "Google News"),
                "date": d,
                "link": entry.get("link", ""),
            })
        return articles
    except Exception as e:
        logger.warning("Google News fetch failed for %s: %s", query, e)
        return []


def _fetch_gnews(query: str, max_results: int = 10) -> List[dict]:
    """GNews API - requires GNEWS_API_KEY env."""
    api_key = __import__("os").environ.get("GNEWS_API_KEY")
    if not api_key:
        return []
    try:
        url = "https://gnews.io/api/v4/search"
        r = requests.get(url, params={
            "q": query,
            "token": api_key,
            "max": max_results,
            "country": "in",
        }, timeout=10)
        if r.status_code != 200:
            return []
        data = r.json()
        articles = []
        for a in data.get("articles", []):
            pub = a.get("publishedAt", "")
            try:
                from dateutil import parser as date_parser
                dt = date_parser.parse(pub)
                d = dt.date()
            except Exception:
                d = date.today()
            articles.append({
                "headline": a.get("title", ""),
                "source": a.get("source", {}).get("name", "GNews"),
                "date": d,
                "link": a.get("url", ""),
            })
        return articles
    except Exception as e:
        logger.warning("GNews fetch failed: %s", e)
        return []


def fetch_and_store_news(db: Session) -> int:
    """Fetch news, run sentiment, store in NewsData. Return count stored."""
    seen = set()
    stored = 0
    for q in QUERIES:
        articles = _fetch_gnews(q, MAX_PER_QUERY)
        if not articles:
            articles = _fetch_google_news(q, MAX_PER_QUERY)
        for a in articles:
            key = (a["headline"][:100], a["date"].isoformat())
            if key in seen:
                continue
            seen.add(key)
            score, label = analyze_headline(a["headline"])
            row = NewsData(
                headline=a["headline"],
                source=a["source"],
                date=a["date"],
                sentiment_score=score,
                link=a.get("link"),
            )
            db.add(row)
            stored += 1
    db.commit()
    return stored


def get_news(
    db: Session,
    filter_sentiment: Optional[str] = None,
    limit: int = 50,
) -> List[NewsData]:
    """Get news, optional filter: positive|negative|all."""
    q = db.query(NewsData).order_by(NewsData.date.desc(), NewsData.id.desc())
    if filter_sentiment == "positive":
        q = q.filter(NewsData.sentiment_score > 0.05)
    elif filter_sentiment == "negative":
        q = q.filter(NewsData.sentiment_score < -0.05)
    elif filter_sentiment == "neutral":
        q = q.filter(
            NewsData.sentiment_score >= -0.05,
            NewsData.sentiment_score <= 0.05,
        )
    return q.limit(limit).all()
