from fastapi import APIRouter
from .market import router as market_router
from .forecast import router as forecast_router
from .sentiment import router as sentiment_router
from .stability import router as stability_router
from .health import router as health_router
from .refresh import router as refresh_router

# Mount at root so we get GET /market-data, GET /forecast, GET /health, etc.
api_router = APIRouter()

api_router.include_router(market_router)
api_router.include_router(forecast_router)
api_router.include_router(sentiment_router)
api_router.include_router(stability_router)
api_router.include_router(health_router)
api_router.include_router(refresh_router)
