# Use existing DataFetcher from backend/services (run uvicorn from backend root)
from services.data_fetcher import DataFetcher

__all__ = ["DataFetcher"]
