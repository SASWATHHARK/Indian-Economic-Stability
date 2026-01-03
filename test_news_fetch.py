
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from services.data_fetcher import DataFetcher
import json

def test_fetch_news():
    fetcher = DataFetcher()
    print("Fetching news headlines...")
    try:
        headlines = fetcher.fetch_news_headlines(query="India economy RBI inflation stock market", max_results=5)
        print(f"Fetched {len(headlines)} headlines.")
        print(json.dumps(headlines, indent=2))
    except Exception as e:
        print(f"Error fetching news: {e}")

if __name__ == "__main__":
    test_fetch_news()
