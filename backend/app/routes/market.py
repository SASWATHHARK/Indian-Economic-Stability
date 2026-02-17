from fastapi import APIRouter, HTTPException
from app.services import DataFetcher
from app.schemas.market import MarketDataResponse
from app.utils.cache import cache_get, cache_set
from app.config import settings

router = APIRouter()
data_fetcher = DataFetcher()

@router.get("/market-data", response_model=MarketDataResponse)
def get_market_data():
    cached = cache_get("market_data", ttl_sec=settings.MARKET_CACHE_TTL)
    if cached is not None:
        return cached
    try:
        data = data_fetcher.fetch_market_data(period="5d")
        cache_set("market_data", data)
        return data
    except Exception as e:
        try:
            data = data_fetcher.fetch_market_data(period="5d", use_sample=True)
            return data
        except Exception:
            raise HTTPException(status_code=503, detail=str(e))
