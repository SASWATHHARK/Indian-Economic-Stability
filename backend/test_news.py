
import feedparser
from urllib.parse import quote_plus
from datetime import datetime

def fetch_news_headlines(query: str, max_results: int = 5):
    print(f"Fetching news for query: {query}")
    try:
        encoded_query = quote_plus(query)
        rss_url = (
            f"https://news.google.com/rss/search?q={encoded_query}"
            "&hl=en-IN&gl=IN&ceid=IN:en"
        )
        print(f"URL: {rss_url}")

        feed = feedparser.parse(rss_url)
        
        if feed.bozo:
             print(f"Feed malformed: {feed.bozo_exception}")

        if not feed.entries:
            print("No entries found in feed.")
            return

        print(f"Found {len(feed.entries)} entries.")
        for i, entry in enumerate(feed.entries[:max_results]):
            print(f"--- Article {i+1} ---")
            print(f"Title: {entry.get('title')}")
            print(f"Published: {entry.get('published')}")
            print(f"Source: {entry.get('source', {}).get('title')}")
            print(f"Link: {entry.get('link')}")

    except Exception as e:
        print(f"Error fetching news: {e}")

if __name__ == "__main__":
    fetch_news_headlines("India economy RBI inflation stock market")
