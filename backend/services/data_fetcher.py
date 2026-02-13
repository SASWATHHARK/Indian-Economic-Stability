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
import concurrent.futures
import threading


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
            # Check Cache (1 day validity - refresh once per day as requested)
            if hasattr(self, "_market_data_cache"):
                cache_time, cache_data = self._market_data_cache
                if (datetime.now() - cache_time).total_seconds() < 86400:  # 1 day = 86400 seconds
                    print(f"Returning cached market data (age: {(datetime.now() - cache_time).total_seconds() / 60:.1f} minutes)")
                    return cache_data

            # Use 5d for dashboard "current" price – faster and often more up-to-date
            fetch_period = period if period in ("1d", "5d", "1mo", "3mo") else "5d"

            def fetch_single(ticker_symbol):
                return yf.Ticker(ticker_symbol).history(period=fetch_period)

            # Ticker map (primary symbols)
            tickers = {
                "nifty": self.nifty_ticker,
                "sensex": self.sensex_ticker,
                "gold": self.gold_ticker,
                "silver": self.silver_ticker,
                "oil": self.oil_ticker,
                "inr": self.inr_ticker
            }

            print(f"Fetching live market data (period={fetch_period})...")
            results = {}
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
                future_to_key = {executor.submit(fetch_single, symbol): key for key, symbol in tickers.items()}
                for future in concurrent.futures.as_completed(future_to_key):
                    key = future_to_key[future]
                    try:
                        df = future.result(timeout=15)
                        if df is not None and not df.empty:
                            results[key] = df
                            print(f"✓ Successfully fetched {key}")
                        else:
                            print(f"✗ {key} returned empty DataFrame")
                            results[key] = pd.DataFrame()
                    except Exception as e:
                        print(f"✗ Failed to fetch {key}: {e}")
                        results[key] = pd.DataFrame()

            # Fallback tickers for assets that failed
            # NIFTY fallback
            if results.get("nifty", pd.DataFrame()).empty:
                try:
                    print("Trying NIFTY fallback: NSEI.NS")
                    nifty_df = yf.Ticker("NSEI.NS").history(period=fetch_period)
                    if not nifty_df.empty:
                        results["nifty"] = nifty_df
                        print("✓ NIFTY fallback succeeded")
                except Exception as e:
                    print(f"✗ NIFTY fallback failed: {e}")

            # Gold fallback (try XAUUSD=X for spot gold)
            if results.get("gold", pd.DataFrame()).empty:
                try:
                    print("Trying Gold fallback: XAUUSD=X")
                    gold_df = yf.Ticker("XAUUSD=X").history(period=fetch_period)
                    if not gold_df.empty:
                        results["gold"] = gold_df
                        print("✓ Gold fallback succeeded")
                except Exception as e:
                    print(f"✗ Gold fallback failed: {e}")

            # Silver fallback (try XAGUSD=X for spot silver)
            if results.get("silver", pd.DataFrame()).empty:
                try:
                    print("Trying Silver fallback: XAGUSD=X")
                    silver_df = yf.Ticker("XAGUSD=X").history(period=fetch_period)
                    if not silver_df.empty:
                        results["silver"] = silver_df
                        print("✓ Silver fallback succeeded")
                except Exception as e:
                    print(f"✗ Silver fallback failed: {e}")

            # Process Results
            def safe_format(df):
                if df is None or df.empty: 
                    return None
                df = df.copy()
                df["Returns"] = df["Close"].pct_change()
                return self._format_index_data(df)

            # Count how many assets we successfully fetched
            live_count = sum(1 for key in ["nifty", "sensex", "gold", "silver", "oil", "inr"] 
                           if results.get(key, pd.DataFrame()) is not None 
                           and not results.get(key, pd.DataFrame()).empty)

            # Only return sample if we got NO live data at all
            if live_count == 0:
                print("⚠ No live data fetched - returning sample data")
                return self.get_sample_market_data()

            # Return live data (even if some assets failed, return what we got)
            final_data = {
                "status": "success",
                "is_live": True,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "nifty": safe_format(results.get("nifty")),
                "sensex": safe_format(results.get("sensex")),
                "gold": safe_format(results.get("gold")),
                "silver": safe_format(results.get("silver")),
                "oil": safe_format(results.get("oil")),
                "inr": safe_format(results.get("inr")),
                "note": f"Live data fetched ({live_count}/6 assets successful)"
            }
            
            # Cache the successful live result
            self._market_data_cache = (datetime.now(), final_data)
            print(f"✓ Cached live market data ({live_count}/6 assets)")
            return final_data

        except Exception as e:
            print(f"⚠ Market Data Fetch Error: {e}")
            import traceback
            traceback.print_exc()
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
        Sample market data when live fetch fails. Values kept near current levels for demo.
        """
        return {
            "status": "success",
            "is_live": False,
            "note": "Sample data used (Live API failed or limited)",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "nifty": {
                "current": 25800.00,
                "open": 25750.00,
                "high": 25850.00,
                "low": 25700.00,
                "volume": 250000000,
                "change": 50.00,
                "change_percent": 0.19,
                "volatility": 0.95,
            },
            "sensex": {
                "current": 84800.00,
                "open": 84600.00,
                "high": 85000.00,
                "low": 84500.00,
                "volume": 80000000,
                "change": 200.00,
                "change_percent": 0.24,
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

    def get_historical_dataframe(self, ticker: str, period: str = "3mo", timeout_sec: int = 20) -> pd.DataFrame:
        """
        Historical OHLCV data for ML models. Uses timeout to avoid hanging on yfinance.
        """
        result = [None]  # use list so inner thread can mutate

        def _fetch():
            try:
                out = yf.Ticker(ticker).history(period=period)
                result[0] = out if out is not None and not out.empty else None
            except Exception:
                result[0] = None

        thread = threading.Thread(target=_fetch, daemon=True)
        thread.start()
        thread.join(timeout=timeout_sec)
        if thread.is_alive() or result[0] is None:
            return self.get_sample_dataframe(period)
        return result[0]

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
