"""
Helpers to produce 0–100 inputs for the multi-factor stability formula.
- Inflation score from inflation_rate (target band 2–6%, optimal ~4%)
- Liquidity score: proxy from volume or default 50
"""
from typing import Optional


def inflation_score_0_100(inflation_rate: Optional[float] = None) -> float:
    """Normalize inflation into 0–100. Optimal around 4%."""
    r = inflation_rate if inflation_rate is not None else 4.5
    if 2 <= r <= 6:
        score = 100 - abs(r - 4) * 25  # 4% = 100
    else:
        score = max(0, 100 - abs(r - 4) * 15)
    return round(min(100, max(0, score)), 2)


def liquidity_score_0_100(volume_proxy: Optional[float] = None) -> float:
    """Liquidity proxy 0–100. If no data, return neutral 50."""
    if volume_proxy is None:
        return 50.0
    # Simple mapping: e.g. normalize log(volume) to 0-100 (tune as needed)
    import math
    v = max(1e6, volume_proxy)
    logv = math.log10(v)
    # Assume 7 (10M) = 50, 9 (1B) = 100
    score = 50 + (logv - 7) * 25
    return round(min(100, max(0, score)), 2)


def volatility_inverse_0_100(volatility_pct: Optional[float] = None) -> float:
    """Lower volatility = higher stability. volatility_pct is e.g. annualized % std."""
    if volatility_pct is None:
        return 50.0
    # 0% vol -> 100, 20% vol -> 0
    score = 100 - min(100, volatility_pct * 5)
    return round(max(0, score), 2)


def market_momentum_0_100(forecast_score_0_1: float) -> float:
    """Convert forecast score 0–1 to 0–100."""
    return round(min(100, max(0, forecast_score_0_1 * 100)), 2)
