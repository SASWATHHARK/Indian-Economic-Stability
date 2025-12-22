"""
Data Fetching Service
Fetches market data and news from various sources
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import feedparser
import requests
from typing import Dict, List, Optional
import time
from urllib.parse import quote_plus


class DataFetcher:
    """
    Fetches market data and news headlines
    """
    
    def __init__(self):
        self.nifty_ticker = "^NSEI"
        self.sensex_ticker = "^BSESN"
    
    def fetch_market_data(self, period: str = "3mo", use_sample: bool = False) -> Dict:
        """
        Fetch NIFTY 50 and SENSEX data from Yahoo Finance
        
        Args:
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, etc.)
            use_sample: If True, return sample data instead of fetching from API
        
        Returns:
            Dictionary with historical data and current values
        """
        # Return sample data for demonstration if requested
        if use_sample:
            return self._get_sample_market_data()
        
        try:
            nifty = yf.Ticker(self.nifty_ticker)
            sensex = yf.Ticker(self.sensex_ticker)
            
            # Fetch historical data with timeout
            nifty_data = nifty.history(period=period, timeout=10)
            sensex_data = sensex.history(period=period, timeout=10)
            
            if nifty_data.empty or sensex_data.empty:
                print(f"Warning: Empty data from Yahoo Finance, using sample data")
                return self._get_sample_market_data()
            
            # Get latest values
            latest_nifty = nifty_data.iloc[-1]
            latest_sensex = sensex_data.iloc[-1]
            
            # Calculate daily returns
            nifty_data['Returns'] = nifty_data['Close'].pct_change()
            sensex_data['Returns'] = sensex_data['Close'].pct_change()
            
            # Calculate volatility (standard deviation of returns)
            nifty_volatility = nifty_data['Returns'].std() * 100
            sensex_volatility = sensex_data['Returns'].std() * 100
            
            return {
                "status": "success",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "nifty": {
                    "current": float(latest_nifty['Close']),
                    "open": float(latest_nifty['Open']),
                    "high": float(latest_nifty['High']),
                    "low": float(latest_nifty['Low']),
                    "volume": int(latest_nifty['Volume']),
                    "change": float(latest_nifty['Close'] - latest_nifty['Open']),
                    "change_percent": float((latest_nifty['Close'] - latest_nifty['Open']) / latest_nifty['Open'] * 100),
                    "volatility": round(nifty_volatility, 2)
                },
                "sensex": {
                    "current": float(latest_sensex['Close']),
                    "open": float(latest_sensex['Open']),
                    "high": float(latest_sensex['High']),
                    "low": float(latest_sensex['Low']),
                    "volume": int(latest_sensex['Volume']),
                    "change": float(latest_sensex['Close'] - latest_sensex['Open']),
                    "change_percent": float((latest_sensex['Close'] - latest_sensex['Open']) / latest_sensex['Open'] * 100),
                    "volatility": round(sensex_volatility, 2)
                },
                "historical": {
                    "nifty": nifty_data[['Close', 'Volume', 'Returns']].to_dict('records'),
                    "sensex": sensex_data[['Close', 'Volume', 'Returns']].to_dict('records')
                }
            }
            
        except Exception as e:
            print(f"Error fetching market data: {str(e)}")
            print("Using sample data for demonstration")
            return self._get_sample_market_data()
    
    def _get_sample_market_data(self) -> Dict:
        """
        Return sample market data for demonstration when Yahoo Finance is unavailable
        """
        return {
            "status": "success",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "note": "Sample data - Yahoo Finance API unavailable",
            "nifty": {
                "current": 22000.50,
                "open": 21950.25,
                "high": 22100.75,
                "low": 21900.00,
                "volume": 150000000,
                "change": 50.25,
                "change_percent": 0.23,
                "volatility": 1.2
            },
            "sensex": {
                "current": 73000.25,
                "open": 72800.50,
                "high": 73200.00,
                "low": 72700.00,
                "volume": 50000000,
                "change": 199.75,
                "change_percent": 0.27,
                "volatility": 1.1
            },
            "historical": {
                "nifty": [],
                "sensex": []
            }
        }
    
    def fetch_news_headlines(self, query: str = "India economy RBI inflation", max_results: int = 20) -> List[Dict]:
        """
        Fetch news headlines from Google News RSS feed
        
        Args:
            query: Search query
            max_results: Maximum number of headlines to fetch
        
        Returns:
            List of news articles with title, link, and published date
        """
        try:
            # URL encode the query to handle spaces and special characters properly
            # Use quote_plus which converts spaces to + and handles special chars
            encoded_query = quote_plus(query)
            # Google News RSS feed - ensure proper URL encoding
            rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
            
            feed = feedparser.parse(rss_url)
            
            articles = []
            for entry in feed.entries[:max_results]:
                articles.append({
                    "title": entry.get('title', ''),
                    "link": entry.get('link', ''),
                    "published": entry.get('published', ''),
                    "source": entry.get('source', {}).get('title', 'Unknown')
                })
            
            if not articles:
                raise ValueError("No articles found in RSS feed")
            
            return articles
            
        except Exception as e:
            # Return sample data if RSS fails
            print(f"News fetch error: {str(e)}")
            return [
                {
                    "title": "Sample: RBI announces monetary policy review",
                    "link": "#",
                    "published": datetime.now().isoformat(),
                    "source": "Sample Source"
                }
            ]
    
    def get_historical_dataframe(self, ticker: str, period: str = "3mo") -> pd.DataFrame:
        """
        Get historical data as DataFrame for ML models
        
        Args:
            ticker: Stock ticker symbol
            period: Time period
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period=period, timeout=10)
            
            if data.empty:
                # Generate sample data for demonstration
                print(f"Warning: No data for {ticker}, generating sample data")
                return self._generate_sample_dataframe(period)
            
            return data
        except Exception as e:
            print(f"Error fetching data for {ticker}: {str(e)}")
            print("Generating sample data for demonstration")
            return self._generate_sample_dataframe(period)
    
    def _generate_sample_dataframe(self, period: str = "3mo") -> pd.DataFrame:
        """
        Generate sample historical data for demonstration
        """
        # Calculate number of days based on period
        days_map = {
            "1d": 1, "5d": 5, "1mo": 30, "3mo": 90, "6mo": 180, "1y": 365
        }
        days = days_map.get(period, 90)
        
        # Generate dates
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        # Generate sample price data (starting around 22000 for NIFTY)
        base_price = 22000
        prices = []
        current_price = base_price
        
        for i in range(days):
            # Random walk with slight upward trend
            change = (i * 0.5) + (np.random.randn() * 50)
            current_price = max(20000, current_price + change)
            prices.append(current_price)
        
        # Create DataFrame
        df = pd.DataFrame({
            'Open': prices,
            'High': [p * 1.01 for p in prices],
            'Low': [p * 0.99 for p in prices],
            'Close': prices,
            'Volume': [100000000 + int(np.random.randn() * 10000000) for _ in prices]
        }, index=dates)
        
        return df

