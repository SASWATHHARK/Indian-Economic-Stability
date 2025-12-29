"""
Sentiment Analysis Module
Uses VADER Sentiment Analyzer for news headline analysis
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
from typing import List, Dict


class SentimentAnalyzer:
    """
    Analyzes sentiment of news headlines using VADER
    """

    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    # --------------------------------------------------
    # Text Cleaning
    # --------------------------------------------------

    def clean_text(self, text: str) -> str:
        """
        Clean and preprocess text
        """
        if not text:
            return ""

        text = re.sub(r"http\S+|www\S+", "", text)   # remove URLs
        text = re.sub(r"[^\w\s]", "", text)          # remove special chars
        text = " ".join(text.split())                # remove extra spaces

        return text.strip()

    # --------------------------------------------------
    # Sentiment Analysis
    # --------------------------------------------------

    def analyze_single(self, text: str) -> Dict:
        """
        Analyze sentiment of a single headline
        """
        cleaned_text = self.clean_text(text)

        if not cleaned_text:
            return self._neutral_result()

        scores = self.analyzer.polarity_scores(cleaned_text)
        compound = scores["compound"]

        if compound >= 0.05:
            label = "positive"
        elif compound <= -0.05:
            label = "negative"
        else:
            label = "neutral"

        return {
            "compound": round(compound, 3),
            "positive": round(scores["pos"], 3),
            "neutral": round(scores["neu"], 3),
            "negative": round(scores["neg"], 3),
            "label": label
        }

    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        """
        Analyze sentiment for multiple headlines
        """
        return [self.analyze_single(text) for text in texts]

    # --------------------------------------------------
    # Aggregate Sentiment
    # --------------------------------------------------

    def get_aggregate_sentiment(self, results: List[Dict]) -> Dict:
        """
        Aggregate sentiment results
        """
        if not results:
            return {
                "avg_compound": 0.0,
                "positive_count": 0,
                "neutral_count": 0,
                "negative_count": 0,
                "overall_label": "neutral",
                "total_articles": 0
            }

        compounds = [r["compound"] for r in results]
        labels = [r["label"] for r in results]

        avg_compound = sum(compounds) / len(compounds)

        if avg_compound >= 0.05:
            overall_label = "positive"
        elif avg_compound <= -0.05:
            overall_label = "negative"
        else:
            overall_label = "neutral"

        return {
            "avg_compound": round(avg_compound, 3),
            "positive_count": labels.count("positive"),
            "neutral_count": labels.count("neutral"),
            "negative_count": labels.count("negative"),
            "overall_label": overall_label,
            "total_articles": len(results)
        }

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def _neutral_result(self) -> Dict:
        return {
            "compound": 0.0,
            "positive": 0.0,
            "neutral": 1.0,
            "negative": 0.0,
            "label": "neutral"
        }


# --------------------------------------------------
# Normalization
# --------------------------------------------------

def normalize_sentiment_score(aggregate_sentiment: Dict) -> float:
    """
    Normalize sentiment into 0–1 score
    """
    compound = aggregate_sentiment["avg_compound"]          # -1 to 1
    compound_score = (compound + 1) / 2                      # 0 to 1

    total = max(1, aggregate_sentiment["total_articles"])
    positive_ratio = aggregate_sentiment["positive_count"] / total
    negative_ratio = aggregate_sentiment["negative_count"] / total

    score = (
        compound_score * 0.6
        + positive_ratio * 0.3
        - negative_ratio * 0.1
    )

    return round(min(1.0, max(0.0, score)), 3)
