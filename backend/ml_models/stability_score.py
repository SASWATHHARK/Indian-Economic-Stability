"""
Economic Stability Score Calculator
Combines market trends, sentiment, and economic indicators
"""

from typing import Dict, Optional
import numpy as np


class StabilityScoreCalculator:
    """
    Calculates Economic Stability Score (0-100) from multiple indicators
    """
    
    def __init__(self):
        # Component weights
        self.weights = {
            'market_trend': 0.40,  # 40%
            'sentiment': 0.30,      # 30%
            'economic_indicators': 0.30  # 30%
        }
    
    def calculate(
        self,
        market_trend_score: float,
        sentiment_score: float,
        economic_indicators_score: Optional[float] = None
    ) -> Dict:
        """
        Calculate final stability score
        
        Args:
            market_trend_score: Normalized score 0-1 from forecast
            sentiment_score: Normalized score 0-1 from sentiment analysis
            economic_indicators_score: Normalized score 0-1 (optional, defaults to 0.5)
        
        Returns:
            Dictionary with score, category, and breakdown
        """
        # Default economic indicators score if not provided
        if economic_indicators_score is None:
            economic_indicators_score = 0.5  # Neutral assumption
        
        # Ensure all scores are in [0, 1] range
        market_trend_score = max(0.0, min(1.0, market_trend_score))
        sentiment_score = max(0.0, min(1.0, sentiment_score))
        economic_indicators_score = max(0.0, min(1.0, economic_indicators_score))
        
        # Weighted sum
        final_score = (
            market_trend_score * self.weights['market_trend'] +
            sentiment_score * self.weights['sentiment'] +
            economic_indicators_score * self.weights['economic_indicators']
        )
        
        # Convert to 0-100 scale
        stability_score = final_score * 100
        
        # Determine category
        category = self._get_category(stability_score)
        
        # Calculate component contributions
        breakdown = {
            'market_contribution': market_trend_score * self.weights['market_trend'] * 100,
            'sentiment_contribution': sentiment_score * self.weights['sentiment'] * 100,
            'economic_contribution': economic_indicators_score * self.weights['economic_indicators'] * 100
        }
        
        return {
            'stability_score': round(stability_score, 2),
            'category': category,
            'breakdown': breakdown,
            'components': {
                'market_trend': round(market_trend_score * 100, 2),
                'sentiment': round(sentiment_score * 100, 2),
                'economic_indicators': round(economic_indicators_score * 100, 2)
            },
            'interpretation': self._get_interpretation(category)
        }
    
    def _get_category(self, score: float) -> str:
        """
        Categorize stability score
        """
        if score >= 71:
            return "Stable"
        elif score >= 41:
            return "Moderate"
        else:
            return "Unstable"
    
    def _get_interpretation(self, category: str) -> str:
        """
        Get human-readable interpretation
        """
        interpretations = {
            "Stable": "The economy shows positive indicators with stable market trends and favorable sentiment. However, this is an advisory system and not financial advice.",
            "Moderate": "The economy shows mixed signals with moderate stability. Monitor trends closely as conditions may change.",
            "Unstable": "The economy shows concerning indicators. This is a predictive framework for understanding trends, not a definitive assessment."
        }
        return interpretations.get(category, "Unable to determine stability status.")


def get_economic_indicators_score(
    inflation_rate: Optional[float] = None,
    repo_rate: Optional[float] = None
) -> float:
    """
    Calculate economic indicators score from inflation and repo rate
    Uses default values if not provided
    
    Args:
        inflation_rate: Current inflation rate (e.g., 4.5 for 4.5%)
        repo_rate: Current repo rate (e.g., 6.5 for 6.5%)
    
    Returns:
        Normalized score 0-1
    """
    # Default values (typical Indian economy ranges)
    if inflation_rate is None:
        inflation_rate = 4.5  # RBI target: 4% ± 2%
    if repo_rate is None:
        repo_rate = 6.5  # Typical range: 4-8%
    
    # Normalize inflation (optimal range: 2-6%, score decreases outside)
    if 2 <= inflation_rate <= 6:
        inflation_score = 1.0 - abs(inflation_rate - 4) / 2  # Peak at 4%
    else:
        inflation_score = max(0, 1.0 - abs(inflation_rate - 4) / 4)
    
    # Normalize repo rate (moderate range: 4-7%, score decreases outside)
    if 4 <= repo_rate <= 7:
        repo_score = 1.0 - abs(repo_rate - 5.5) / 1.5  # Peak at 5.5%
    else:
        repo_score = max(0, 1.0 - abs(repo_rate - 5.5) / 3)
    
    # Average of both indicators
    final_score = (inflation_score + repo_score) / 2
    
    return min(1.0, max(0.0, final_score))

