# Use existing DataFetcher from backend/services (run uvicorn from backend root)
try:
    from services.data_fetcher import DataFetcher
except Exception:
    DataFetcher = None

import app.services.data_router as data_router

__all__ = ["DataFetcher", "data_router"]
