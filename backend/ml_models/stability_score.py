"""
Economic Stability Score Calculator
Combines market trends, sentiment, and economic indicators
"""

from typing import Dict, Optional


class StabilityScoreCalculator:
    """
    Calculates Economic Stability Score (0–100)
    """

    STABLE_THRESHOLD = 71
    MODERATE_THRESHOLD = 41

    def __init__(self):
        self.weights = {
            "market_trend": 0.40,
            "sentiment": 0.30,
            "economic_indicators": 0.30,
        }

    # --------------------------------------------------
    # Final Score Calculation
    # --------------------------------------------------

    def calculate(
        self,
        market_trend_score: float,
        sentiment_score: float,
        economic_indicators_score: Optional[float] = None,
    ) -> Dict:
        """
        Calculate overall economic stability score
        """
        if economic_indicators_score is None:
            economic_indicators_score = 0.5  # neutral assumption

        # Clamp values to 0–1
        market_trend_score = self._clamp(market_trend_score)
        sentiment_score = self._clamp(sentiment_score)
        economic_indicators_score = self._clamp(economic_indicators_score)

        final_score = (
            market_trend_score * self.weights["market_trend"]
            + sentiment_score * self.weights["sentiment"]
            + economic_indicators_score * self.weights["economic_indicators"]
        )

        stability_score = round(final_score * 100, 2)
        category = self._get_category(stability_score)

        return {
            "stability_score": stability_score,
            "category": category,
            "interpretation": self._get_interpretation(category),
            "breakdown": {
                "market_contribution": round(
                    market_trend_score * self.weights["market_trend"] * 100, 2
                ),
                "sentiment_contribution": round(
                    sentiment_score * self.weights["sentiment"] * 100, 2
                ),
                "economic_contribution": round(
                    economic_indicators_score
                    * self.weights["economic_indicators"]
                    * 100,
                    2,
                ),
            },
            "components": {
                "market_trend": round(market_trend_score * 100, 2),
                "sentiment": round(sentiment_score * 100, 2),
                "economic_indicators": round(economic_indicators_score * 100, 2),
            },
        }

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def _clamp(self, value: float) -> float:
        return max(0.0, min(1.0, value))

    def _get_category(self, score: float) -> str:
        if score >= self.STABLE_THRESHOLD:
            return "Stable"
        elif score >= self.MODERATE_THRESHOLD:
            return "Moderate"
        else:
            return "Unstable"

    def _get_interpretation(self, category: str) -> str:
        interpretations = {
            "Stable": "Economic indicators suggest a stable environment with positive market trends.",
            "Moderate": "Economic conditions show mixed signals; close monitoring is advised.",
            "Unstable": "Economic indicators suggest instability; trends require careful observation.",
        }
        return interpretations.get(category, "Status unclear.")


# --------------------------------------------------
# Economic Indicators Score
# --------------------------------------------------

def get_economic_indicators_score(
    inflation_rate: Optional[float] = None,
    repo_rate: Optional[float] = None,
) -> float:
    """
    Normalize inflation & repo rate into a 0–1 score
    """
    inflation_rate = inflation_rate if inflation_rate is not None else 4.5
    repo_rate = repo_rate if repo_rate is not None else 6.5

    # Inflation normalization (optimal ≈ 4%)
    if 2 <= inflation_rate <= 6:
        inflation_score = 1 - abs(inflation_rate - 4) / 2
    else:
        inflation_score = max(0.0, 1 - abs(inflation_rate - 4) / 4)

    # Repo rate normalization (optimal ≈ 5.5%)
    if 4 <= repo_rate <= 7:
        repo_score = 1 - abs(repo_rate - 5.5) / 1.5
    else:
        repo_score = max(0.0, 1 - abs(repo_rate - 5.5) / 3)

    return round((inflation_score + repo_score) / 2, 3)
