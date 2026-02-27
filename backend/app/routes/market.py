from fastapi import APIRouter, HTTPException
from app.services import data_router
from app.schemas.market import MarketDataResponse
from app.utils.cache import cache_get, cache_set
from app.config import settings

router = APIRouter()

@router.get("/market-data", response_model=MarketDataResponse)
def get_market_data():
    cached = cache_get("market_data", ttl_sec=settings.MARKET_CACHE_TTL)
    if cached is not None:
        return cached
    try:
        data = data_router.get_market_data(period="5d")
        if data.get("data_source") == "live":
            cache_set("market_data", data)
        return data
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
