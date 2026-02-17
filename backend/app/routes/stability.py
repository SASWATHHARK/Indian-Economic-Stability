from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime
from app.ml.stability import StabilityScoreService
from app.utils.stability_helpers import inflation_score_0_100, liquidity_score_0_100, volatility_inverse_0_100
from app.utils.stability_cache import get_stability_cache
from app.schemas.stability import StabilityResponse, StabilityComponents
from app.config import settings

router = APIRouter()
stability_svc = StabilityScoreService()

@router.get("/stability-score", response_model=StabilityResponse)
def get_stability_score(
    inflation_rate: Optional[float] = Query(None),
    repo_rate: Optional[float] = Query(None),
):
    now = datetime.utcnow()
    cache = get_stability_cache()
    cache_ok = (
        cache["ts"] is not None
        and (now - cache["ts"]).total_seconds() < settings.STABILITY_CACHE_TTL
    )
    if cache_ok and cache["forecast_score"] is not None and cache["sentiment_score"] is not None:
        market_momentum = cache["forecast_score"]
        sentiment_score = cache["sentiment_score"]
        volatility_inverse = cache.get("volatility") or 50.0
    else:
        market_momentum = sentiment_score = volatility_inverse = 50.0

    inflation = inflation_score_0_100(inflation_rate)
    liquidity = liquidity_score_0_100(None)

    result = stability_svc.calculate(
        market_momentum_score=market_momentum,
        sentiment_score=sentiment_score,
        volatility_inverse_score=volatility_inverse,
        inflation_score=inflation,
        liquidity_score=liquidity,
    )
    return StabilityResponse(
        status="success",
        stability_score=result["stability_score"],
        category=result["category"],
        risk_level=result["risk_level"],
        explanation=result["explanation"],
        components=StabilityComponents(**result["components"]),
        breakdown=result.get("breakdown"),
        timestamp=now.isoformat(),
        disclaimer="Educational project. Not financial advice.",
    )
