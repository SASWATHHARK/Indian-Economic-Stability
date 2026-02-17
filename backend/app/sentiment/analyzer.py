"""
Sentiment analysis with VADER + source credibility and recency weights.
Supports filtering: positive / negative / neutral, date range.
"""
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
except ImportError:
    SentimentIntensityAnalyzer = None

# Source credibility weights (0–1). Higher = more trusted.
SOURCE_WEIGHTS = {
    "reuters": 1.0,
    "economic times": 0.95,
    "business standard": 0.9,
    "moneycontrol": 0.85,
    "livemint": 0.85,
    "bloomberg": 0.95,
    "the hindu": 0.9,
    "ndtv": 0.8,
    "google news": 0.7,
    "sample news": 0.3,
}


def _source_weight(source: str) -> float:
    s = (source or "").lower()
    for key, w in SOURCE_WEIGHTS.items():
        if key in s:
            return w
    return 0.7


def _recency_weight(published: Optional[str]) -> float:
    """Weight by recency: last 24h = 1.0, older decays."""
    if not published:
        return 0.8
    try:
        # Parse ISO or common RSS format
        if "T" in published:
            dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
        else:
            from dateutil import parser
            dt = parser.parse(published)
    except Exception:
        return 0.8
    age_hours = (datetime.utcnow() - dt.replace(tzinfo=None)).total_seconds() / 3600
    if age_hours <= 24:
        return 1.0
    if age_hours <= 72:
        return 0.9
    if age_hours <= 168:  # 1 week
        return 0.7
    return 0.5


class SentimentService:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer() if SentimentIntensityAnalyzer else None

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        text = re.sub(r"http\S+|www\S+", "", text)
        text = re.sub(r"[^\w\s]", "", text)
        return " ".join(text.split()).strip()

    def analyze_single(self, text: str) -> Dict:
        cleaned = self.clean_text(text)
        if not self.analyzer or not cleaned:
            return {"compound": 0.0, "positive": 0.0, "neutral": 1.0, "negative": 0.0, "label": "neutral"}
        scores = self.analyzer.polarity_scores(cleaned)
        c = scores["compound"]
        label = "positive" if c >= 0.05 else ("negative" if c <= -0.05 else "neutral")
        return {
            "compound": round(c, 3),
            "positive": round(scores["pos"], 3),
            "neutral": round(scores["neu"], 3),
            "negative": round(scores["neg"], 3),
            "label": label,
        }

    def analyze_batch_weighted(
        self,
        articles: List[Dict],
        title_key: str = "title",
        source_key: str = "source",
        published_key: str = "published",
    ) -> List[Dict]:
        """Each article: {title, source, published?, ...}. Returns list of sentiment dicts with weight."""
        results = []
        for a in articles:
            title = a.get(title_key, "")
            sent = self.analyze_single(title)
            w_src = _source_weight(a.get(source_key, ""))
            w_rec = _recency_weight(a.get(published_key))
            weight = w_src * w_rec
            sent["weight"] = round(weight, 3)
            results.append(sent)
        return results

    def get_aggregate_weighted(self, results: List[Dict], articles: List[Dict]) -> Dict:
        if not results:
            return {
                "avg_compound": 0.0,
                "positive_count": 0,
                "neutral_count": 0,
                "negative_count": 0,
                "overall_label": "neutral",
                "total_articles": 0,
            }
        weights = [r.get("weight", 1.0) for r in results]
        compounds = [r["compound"] for r in results]
        total_w = sum(weights) or 1
        avg_compound = sum(c * w for c, w in zip(compounds, weights)) / total_w
        labels = [r["label"] for r in results]
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
            "total_articles": len(results),
        }

    def normalize_score(self, aggregate: Dict) -> float:
        """0–100 score from aggregate."""
        c = aggregate.get("avg_compound", 0)
        score = (c + 1) / 2 * 100
        return round(min(100, max(0, score)), 2)

    def filter_articles(
        self,
        articles: List[Dict],
        sentiment_results: List[Dict],
        sentiment_filter: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> tuple:
        """Filter (articles, results) by sentiment (positive/negative/neutral) and date range."""
        out_arts = []
        out_res = []
        for i, (a, r) in enumerate(zip(articles, sentiment_results)):
            if sentiment_filter and r.get("label") != sentiment_filter:
                continue
            pub = a.get("published")
            if date_from or date_to:
                try:
                    if "T" in str(pub):
                        dt = datetime.fromisoformat(str(pub).replace("Z", "+00:00"))
                    else:
                        from dateutil import parser
                        dt = parser.parse(str(pub))
                    dt = dt.replace(tzinfo=None)
                    if date_from and dt < date_from:
                        continue
                    if date_to and dt > date_to:
                        continue
                except Exception:
                    pass
            out_arts.append(a)
            out_res.append(r)
        return out_arts, out_res
