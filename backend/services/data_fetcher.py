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
        self.gold_ticker = "GC=F"
        self.silver_ticker = "SI=F"
        self.oil_ticker = "CL=F"
        self.inr_ticker = "INR=X"

    # --------------------------------------------------
    # Market Data
    # --------------------------------------------------

    def fetch_market_data(self, period: str = "1d", use_sample: bool = False) -> Dict:
        """
        Fetch Current Market Data (Fast Mode: 1 Day History).
        Used for the Dashboard Cards to get real-time price.
        """
        if use_sample:
            return self.get_sample_market_data()

        try:
            import concurrent.futures

            # Define the fetch task: Use 1d period for speed
            def fetch_single(ticker_symbol):
                # Request 5 days just in case of weekend/holiday, but we only need the last row
                return yf.Ticker(ticker_symbol).history(period="5d")

            # Ticker map
            tickers = {
                "nifty": self.nifty_ticker,
                "sensex": self.sensex_ticker,
                "gold": self.gold_ticker,
                "silver": self.silver_ticker,
                "oil": self.oil_ticker,
                "inr": self.inr_ticker
            }

            # Execute in parallel
            results = {}
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
                future_to_key = {executor.submit(fetch_single, symbol): key for key, symbol in tickers.items()}
                for future in concurrent.futures.as_completed(future_to_key):
                    key = future_to_key[future]
                    try:
                        results[key] = future.result()
                    except Exception as e:
                        print(f"Failed to fetch {key}: {e}")
                        results[key] = pd.DataFrame() # Empty DF as fallback

            # Check primary indices
            if results.get("nifty", pd.DataFrame()).empty:
                return self.get_sample_market_data()

            # Process Results
            def safe_format(df):
                if df is None or df.empty: return None
                df["Returns"] = df["Close"].pct_change()
                return self._format_index_data(df)

            return {
                "status": "success",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "nifty": safe_format(results.get("nifty")),
                "sensex": safe_format(results.get("sensex")),
                "gold": safe_format(results.get("gold")),
                "silver": safe_format(results.get("silver")),
                "oil": safe_format(results.get("oil")),
                "inr": safe_format(results.get("inr"))
            }

        except Exception as e:
            print(f"Market Data Fetch Error: {e}")
            return self.get_sample_market_data()

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
        Sample market data for demo purposes (Updated to 2025 levels)
        """
        return {
            "status": "success",
            "note": "Sample data used (Live API failed or limited)",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "nifty": {
                "current": 25250.50,
                "open": 25100.00,
                "high": 25300.20,
                "low": 25050.80,
                "volume": 250000000,
                "change": 150.50,
                "change_percent": 0.60,
                "volatility": 0.95,
            },
            "sensex": {
                "current": 82100.40,
                "open": 81800.00,
                "high": 82500.00,
                "low": 81700.00,
                "volume": 80000000,
                "change": 300.40,
                "change_percent": 0.37,
                "volatility": 0.90,
            },
            "gold": {
                "current": 2650.80,
                "open": 2640.00,
                "high": 2660.00,
                "low": 2635.00,
                "volume": 12000,
                "change": 10.80,
                "change_percent": 0.41,
                "volatility": 0.65,
                "history": {
                    "1mo": 4.5,
                    "1y": 18.2,
                    "5y": 62.4
                }
            },
            "silver": {
                "current": 31.50,
                "open": 31.20,
                "high": 31.80,
                "low": 31.10,
                "volume": 6000,
                "change": 0.30,
                "change_percent": 0.96,
                "volatility": 1.2,
                "history": {
                    "1mo": 6.8,
                    "1y": 24.5,
                    "5y": 45.1
                }
            },
            "oil": {
                "current": 74.20,
                "open": 73.80,
                "high": 75.00,
                "low": 73.50,
                "volume": 250000,
                "change": 0.40,
                "change_percent": 0.54,
                "volatility": 1.9,
            },
            "inr": {
                "current": 89.20,
                "open": 89.10,
                "high": 89.30,
                "low": 89.05,
                "volume": 0,
                "change": 0.15,
                "change_percent": 0.17,
                "volatility": 0.05,
            }
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
        price = 25000 # Updated to 2025 levels
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
