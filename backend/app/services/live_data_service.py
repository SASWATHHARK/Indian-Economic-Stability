"""
Live data service – fetches from external APIs (yfinance, news RSS).
Used by data_router; never called directly from routes.
"""
from typing import Any, Dict, List

from app.utils.log import get_logger

logger = get_logger(__name__)

# Lazy import to avoid loading yfinance/feedparser when using offline only
_data_fetcher = None


def _get_fetcher():
    global _data_fetcher
    if _data_fetcher is None:
        try:
            from services.data_fetcher import DataFetcher
            _data_fetcher = DataFetcher()
        except Exception as e:
            logger.warning("DataFetcher not available: %s", e)
    return _data_fetcher


def fetch_live_market_data(period: str = "5d") -> Dict[str, Any]:
    """Fetch live market data. Raises on failure."""
    fetcher = _get_fetcher()
    if fetcher is None:
        raise RuntimeError("Live data fetcher not available")
    data = fetcher.fetch_market_data(period=period, use_sample=False)
    if not data or data.get("is_live") is False and not data.get("note", "").startswith("Live"):
        raise ValueError("Live fetch returned non-live or empty data")
    return data


def fetch_live_news(query: str = "India economy RBI inflation stock market", max_results: int = 20) -> List[Dict]:
    """Fetch live news headlines. Raises on failure."""
    fetcher = _get_fetcher()
    if fetcher is None:
        raise RuntimeError("Live data fetcher not available")
    headlines = fetcher.fetch_news_headlines(query=query, max_results=max_results)
    if not headlines:
        raise ValueError("No live news returned")
    return headlines


def fetch_live_historical_dataframe(ticker: str, period: str = "3mo"):
    """Fetch live historical OHLCV for ML. Raises on failure."""
    fetcher = _get_fetcher()
    if fetcher is None:
        raise RuntimeError("Live data fetcher not available")
    df = fetcher.get_historical_dataframe(ticker, period=period)
    if df is None or df.empty or len(df) < 30:
        raise ValueError("Insufficient live historical data")
    return df
