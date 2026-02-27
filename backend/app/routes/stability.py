from fastapi import APIRouter, Query
from typing import Optional
from app.services import data_router
from app.ml.stability import StabilityScoreService
from app.utils.stability_cache import get_stability_cache
from app.schemas.stability import StabilityResponse, StabilityComponents

router = APIRouter()
stability_svc = StabilityScoreService()

@router.get("/stability-score", response_model=StabilityResponse)
def get_stability_score(
    inflation_rate: Optional[float] = Query(None),
    repo_rate: Optional[float] = Query(None),
):
    payload = data_router.get_stability(
        stability_svc=stability_svc,
        cache_getter=get_stability_cache,
        inflation_rate=inflation_rate,
        repo_rate=repo_rate,
    )
    return StabilityResponse(
        status=payload.get("status", "success"),
        stability_score=payload["stability_score"],
        category=payload["category"],
        risk_level=payload["risk_level"],
        explanation=payload["explanation"],
        components=StabilityComponents(**payload["components"]),
        breakdown=payload.get("breakdown"),
        timestamp=payload["timestamp"],
        disclaimer=payload.get("disclaimer"),
        data_source=payload.get("data_source"),
        demo_mode=payload.get("demo_mode"),
        sample_data_date=payload.get("sample_data_date"),
    )
