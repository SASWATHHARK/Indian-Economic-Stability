"""
Data Fetching Service
Handles market data and news retrieval with fallback sample data
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import feedparser
from urllib.parse import quote_plus
from typing import Dict, List


class DataFetcher:
    """
    Service class for fetching market data and news headlines
    """

    def __init__(self):
        self.nifty_ticker = "^NSEI"
        self.sensex_ticker = "^BSESN"

    # --------------------------------------------------
    # Market Data
    # --------------------------------------------------

    def fetch_market_data(self, period: str = "3mo", use_sample: bool = False) -> Dict:
        """
        Fetch NIFTY & SENSEX market data
        """
        if use_sample:
            return self.get_sample_market_data()

        try:
            nifty = yf.Ticker(self.nifty_ticker)
            sensex = yf.Ticker(self.sensex_ticker)

            nifty_df = nifty.history(period=period)
            sensex_df = sensex.history(period=period)

            if nifty_df.empty or sensex_df.empty:
                return self.get_sample_market_data()

            nifty_df["Returns"] = nifty_df["Close"].pct_change()
            sensex_df["Returns"] = sensex_df["Close"].pct_change()

            return {
                "status": "success",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "nifty": self._format_index_data(nifty_df),
                "sensex": self._format_index_data(sensex_df),
            }

        except Exception:
            return self.get_sample_market_data()

    def _format_index_data(self, df: pd.DataFrame) -> Dict:
        latest = df.iloc[-1]
        volatility = df["Returns"].std() * 100

        return {
            "current": round(float(latest["Close"]), 2),
            "open": round(float(latest["Open"]), 2),
            "high": round(float(latest["High"]), 2),
            "low": round(float(latest["Low"]), 2),
            "volume": int(latest["Volume"]),
            "change": round(float(latest["Close"] - latest["Open"]), 2),
            "change_percent": round(
                ((latest["Close"] - latest["Open"]) / latest["Open"]) * 100, 2
            ),
            "volatility": round(volatility, 2),
        }

    def get_sample_market_data(self) -> Dict:
        """
        Sample market data for demo purposes
        """
        return {
            "status": "success",
            "note": "Sample data used (live API unavailable)",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "nifty": {
                "current": 22000,
                "open": 21950,
                "high": 22100,
                "low": 21890,
                "volume": 150000000,
                "change": 50,
                "change_percent": 0.23,
                "volatility": 1.2,
            },
            "sensex": {
                "current": 73000,
                "open": 72800,
                "high": 73200,
                "low": 72700,
                "volume": 50000000,
                "change": 200,
                "change_percent": 0.27,
                "volatility": 1.1,
            },
        }

    # --------------------------------------------------
    # Historical Data for ML
    # --------------------------------------------------

    def get_historical_dataframe(self, ticker: str, period: str = "3mo") -> pd.DataFrame:
        """
        Historical OHLCV data for ML models
        """
        try:
            df = yf.Ticker(ticker).history(period=period)
            if df.empty:
                return self.get_sample_dataframe(period)
            return df
        except Exception:
            return self.get_sample_dataframe(period)

    def get_sample_dataframe(self, period: str = "3mo") -> pd.DataFrame:
        """
        Generate sample historical data
        """
        days_map = {"1mo": 30, "3mo": 90, "6mo": 180, "1y": 365}
        days = days_map.get(period, 90)

        dates = pd.date_range(end=datetime.now(), periods=days)
        price = 22000
        prices = []

        for _ in range(days):
            price += np.random.randn() * 50
            prices.append(max(price, 20000))

        return pd.DataFrame(
            {
                "Open": prices,
                "High": [p * 1.01 for p in prices],
                "Low": [p * 0.99 for p in prices],
                "Close": prices,
                "Volume": np.random.randint(90_000_000, 160_000_000, size=days),
            },
            index=dates,
        )

    # --------------------------------------------------
    # News Headlines
    # --------------------------------------------------

    def fetch_news_headlines(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        Fetch news headlines using Google News RSS
        """
        try:
            encoded_query = quote_plus(query)
            rss_url = (
                f"https://news.google.com/rss/search?q={encoded_query}"
                "&hl=en-IN&gl=IN&ceid=IN:en"
            )

            feed = feedparser.parse(rss_url)

            articles = []
            for entry in feed.entries[:max_results]:
                articles.append({
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "source": entry.get("source", {}).get("title", "Google News"),
                })

            return articles if articles else self.get_sample_news()

        except Exception:
            return self.get_sample_news()

    def get_sample_news(self) -> List[Dict]:
        """
        Sample news fallback
        """
        return [
            {
                "title": "RBI reviews monetary policy amid inflation concerns",
                "link": "#",
                "published": datetime.now().isoformat(),
                "source": "Sample News",
            }
        ]
