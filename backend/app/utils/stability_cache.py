"""Shared cache for stability inputs (forecast/sentiment scores)."""
from datetime import datetime
from typing import Optional

_stability_cache = {
    "forecast_score": None,
    "sentiment_score": None,
    "volatility": None,
    "ts": None,
}

def get_stability_cache():
    return _stability_cache

def update_stability_cache(
    forecast_score_0_100: float,
    sentiment_score_0_100: float,
    volatility_pct: Optional[float] = None,
) -> None:
    from app.utils.stability_helpers import volatility_inverse_0_100
    _stability_cache["forecast_score"] = forecast_score_0_100
    _stability_cache["sentiment_score"] = sentiment_score_0_100
    _stability_cache["volatility"] = volatility_inverse_0_100(volatility_pct) if volatility_pct is not None else 50.0
    _stability_cache["ts"] = datetime.utcnow()
