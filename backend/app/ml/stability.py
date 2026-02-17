"""
Multi-Factor Economic Stability Index (0–100).

Formula (academically justified, explainable):

  Stability Score =
    (0.30 × Market Momentum Score) +
    (0.25 × Sentiment Score) +
    (0.20 × Volatility Inverse Score) +
    (0.15 × Inflation Score) +
    (0.10 × Liquidity Score)

All factors normalized 0–100. Risk level and explanation derived from components.
"""
from typing import Dict, Optional


class StabilityScoreService:
    """
    Multi-factor stability index with transparency and academic justification.
    """

    # Weights (sum = 1.0)
    W_MARKET_MOMENTUM = 0.30   # Trend strength and direction
    W_SENTIMENT = 0.25         # News/social sentiment
    W_VOLATILITY_INVERSE = 0.20  # Lower volatility = higher stability
    W_INFLATION = 0.15         # Inflation within target band
    W_LIQUIDITY = 0.10         # Market depth / liquidity proxy

    STABLE_THRESHOLD = 71
    MODERATE_THRESHOLD = 41

    def __init__(self):
        pass

    def _clamp(self, x: float) -> float:
        return max(0.0, min(100.0, x))

    def calculate(
        self,
        market_momentum_score: float,
        sentiment_score: float,
        volatility_inverse_score: float,
        inflation_score: float,
        liquidity_score: float,
    ) -> Dict:
        """
        All inputs should be 0–100. Returns stability_score, category, risk_level, explanation, components.
        """
        m = self._clamp(market_momentum_score)
        s = self._clamp(sentiment_score)
        v = self._clamp(volatility_inverse_score)
        i = self._clamp(inflation_score)
        lq = self._clamp(liquidity_score)

        stability_score = round(
            m * self.W_MARKET_MOMENTUM
            + s * self.W_SENTIMENT
            + v * self.W_VOLATILITY_INVERSE
            + i * self.W_INFLATION
            + lq * self.W_LIQUIDITY,
            2,
        )
        category = self._category(stability_score)
        risk_level = self._risk_level(stability_score)
        explanation = self._explanation(m, s, v, i, lq, category)

        return {
            "stability_score": stability_score,
            "category": category,
            "risk_level": risk_level,
            "explanation": explanation,
            "components": {
                "market_momentum": round(m, 2),
                "sentiment": round(s, 2),
                "volatility_inverse": round(v, 2),
                "inflation": round(i, 2),
                "liquidity": round(lq, 2),
            },
            "breakdown": {
                "market_contribution": round(m * self.W_MARKET_MOMENTUM, 2),
                "sentiment_contribution": round(s * self.W_SENTIMENT, 2),
                "volatility_contribution": round(v * self.W_VOLATILITY_INVERSE, 2),
                "inflation_contribution": round(i * self.W_INFLATION, 2),
                "liquidity_contribution": round(lq * self.W_LIQUIDITY, 2),
            },
        }

    def _category(self, score: float) -> str:
        if score >= self.STABLE_THRESHOLD:
            return "Stable"
        if score >= self.MODERATE_THRESHOLD:
            return "Moderate"
        return "Unstable"

    def _risk_level(self, score: float) -> str:
        if score >= self.STABLE_THRESHOLD:
            return "Low"
        if score >= self.MODERATE_THRESHOLD:
            return "Medium"
        return "High"

    def _explanation(
        self,
        m: float,
        s: float,
        v: float,
        i: float,
        lq: float,
        category: str,
    ) -> str:
        parts = []
        if s >= 55:
            parts.append("Positive sentiment")
        elif s < 45:
            parts.append("Negative sentiment")
        if v >= 55:
            parts.append("low volatility")
        elif v < 45:
            parts.append("elevated volatility")
        if m >= 55:
            parts.append("supportive market momentum")
        elif m < 45:
            parts.append("weak market momentum")
        if not parts:
            parts.append("Mixed signals across factors")
        return (category + ": " + ", ".join(parts) + ".").capitalize()
