"""
Sample data service – loads static/semi-dynamic data from app/sample_data/.
Ensures identical response shape to live APIs for frontend compatibility.
"""
import json
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.utils.log import get_logger

logger = get_logger(__name__)

_BASE = Path(__file__).resolve().parent.parent / "sample_data"
_SIMULATION_VARIATION = 0.005  # ±0.5% for semi-dynamic mode


def _load_json(name: str) -> Dict[str, Any]:
    path = _BASE / name
    if not path.exists():
        raise FileNotFoundError(f"Sample data not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _apply_variation(value: float, variation: float = _SIMULATION_VARIATION) -> float:
    """Apply ±variation (e.g. 0.005 = ±0.5%)."""
    delta = value * (2 * random.random() - 1) * variation
    return round(value + delta, 2)


def get_indices(semi_dynamic: bool = False) -> Dict[str, Any]:
    data = _load_json("indices.json")
    if not semi_dynamic:
        return data
    out = {}
    for key in ("nifty", "sensex"):
        item = data[key].copy()
        cv = item["current_value"]
        item["current_value"] = _apply_variation(cv)
        item["change"] = round(item["current_value"] - cv + item["change"], 2)
        item["change_percent"] = round(item["change"] / (cv or 1) * 100, 2)
        if "historical" in item and item["historical"]:
            item["historical"] = [_apply_variation(v) for v in item["historical"][-30:]]
        out[key] = item
    return out


def get_commodities(semi_dynamic: bool = False) -> Dict[str, Any]:
    data = _load_json("commodities.json")
    if not semi_dynamic:
        return data
    out = {}
    for key, item in data.items():
        o = item.copy()
        o["price"] = _apply_variation(o["price"])
        out[key] = o
    return out


def get_macro() -> Dict[str, Any]:
    return _load_json("macro.json")


def get_news_sample() -> List[Dict[str, Any]]:
    return _load_json("news.json")


def get_stability_sample(semi_dynamic: bool = False) -> Dict[str, Any]:
    data = _load_json("stability.json")
    if semi_dynamic:
        data = data.copy()
        data["stability_score"] = _apply_variation(data["stability_score"], 0.01)
        if "factors" in data:
            data["factors"] = {k: _apply_variation(v, 0.01) for k, v in data["factors"].items()}
    return data


def get_forecast_sample(semi_dynamic: bool = False) -> Dict[str, Any]:
    data = _load_json("forecast.json")
    if semi_dynamic and "forecast" in data:
        data = data.copy()
        data["forecast"] = [
            {**p, "predicted": _apply_variation(p["predicted"])}
            for p in data["forecast"]
        ]
    return data


def _build_market_response_minimal() -> Dict[str, Any]:
    """Inline fallback when sample_data/*.json are not loaded. Same shape as build_market_response."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    inr_rate = 83.42
    # NIFTY/SENSEX placeholder
    def _index(cv: float, ch: float, pct: float) -> Dict:
        return {
            "current": cv,
            "open": round(cv - ch, 2),
            "high": round(cv + abs(ch) * 0.5, 2),
            "low": round(cv - ch - abs(ch) * 0.5, 2),
            "volume": 250_000_000,
            "change": ch,
            "change_percent": pct,
            "volatility": 0.95,
        }
    # Gold/silver in USD/oz; oil in USD; INR
    def _commodity(p: float, ch: float, pct: float, vol: float) -> Dict:
        return {
            "current": p,
            "open": round(p - ch, 2),
            "high": round(p + abs(ch), 2),
            "low": round(p - abs(ch), 2),
            "volume": 12000,
            "change": ch,
            "change_percent": pct,
            "volatility": vol,
        }
    gold_usd = (64250 / 10) * 31.1035 / inr_rate
    silver_usd = (76200 / 1000) * 31.1035 / inr_rate
    return {
        "status": "success",
        "is_live": False,
        "date": date_str,
        "nifty": _index(24500.0, 120.0, 0.49),
        "sensex": _index(80500.0, 380.0, 0.47),
        "gold": _commodity(gold_usd, 2.5, 0.5, 0.68),
        "silver": _commodity(silver_usd, -0.15, -0.24, 1.12),
        "oil": _commodity(82.45, 1.25, 1.54, 1.85),
        "inr": _commodity(inr_rate, 0.08, 0.1, 0.12),
        "note": "Offline sample data (sample dataset not loaded or API unavailable)",
    }


def build_market_response(semi_dynamic: bool = False) -> Dict[str, Any]:
    """Build full market response matching live API shape (nifty, sensex, gold, silver, oil, inr)."""
    try:
        indices = get_indices(semi_dynamic)
        commodities = get_commodities(semi_dynamic)
    except FileNotFoundError as e:
        logger.warning("Sample data files not found (%s), using minimal fallback", e)
        return _build_market_response_minimal()

    date_str = datetime.now().strftime("%Y-%m-%d")

    def nifty_sensex(item: Dict) -> Dict:
        cv = item["current_value"]
        ch = item["change"]
        open_ = cv - ch
        return {
            "current": cv,
            "open": round(open_, 2),
            "high": round(cv + abs(ch) * 0.5, 2),
            "low": round(open_ - abs(ch) * 0.5, 2),
            "volume": 250_000_000,
            "change": ch,
            "change_percent": item["change_percent"],
            "volatility": 0.95,
        }

    def commodity(p: float, ch: float, pct: float, vol: float) -> Dict:
        return {
            "current": p,
            "open": round(p - ch, 2),
            "high": round(p + abs(ch), 2),
            "low": round(p - abs(ch), 2),
            "volume": 12000,
            "change": ch,
            "change_percent": pct,
            "volatility": vol,
        }

    gold = commodities.get("gold", {})
    silver = commodities.get("silver", {})
    oil = commodities.get("crude_oil", {})
    inr = commodities.get("usd_inr", {})
    # Frontend expects gold/silver in USD/oz; sample has INR/10g and INR/kg -> convert to USD/oz
    inr_rate = inr.get("price", 83.42) or 83.42
    gold_usd_oz = (gold.get("price", 64250) / 10) * 31.1035 / inr_rate
    silver_usd_oz = (silver.get("price", 76200) / 1000) * 31.1035 / inr_rate

    return {
        "status": "success",
        "is_live": False,
        "date": date_str,
        "nifty": nifty_sensex(indices["nifty"]),
        "sensex": nifty_sensex(indices["sensex"]),
        "gold": commodity(gold_usd_oz, round(gold.get("change", 320) / inr_rate, 2), gold.get("change_percent", 0.5), gold.get("volatility", 0.68)),
        "silver": commodity(silver_usd_oz, round(silver.get("change", -180) / inr_rate, 2), silver.get("change_percent", -0.24), silver.get("volatility", 1.12)),
        "oil": commodity(oil.get("price", 82.45), oil.get("change", 1.25), oil.get("change_percent", 1.54), oil.get("volatility", 1.85)),
        "inr": commodity(inr.get("price", 83.42), inr.get("change", 0.08), inr.get("change_percent", 0.1), inr.get("volatility", 0.12)),
        "note": "Offline sample data (no internet or API unavailable)",
    }


def build_sentiment_response_from_news(
    news_list: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    """Build SentimentResponse-shaped dict from news.json for offline fallback."""
    if news_list is None:
        news_list = get_news_sample()
    compounds = [n.get("compound_score", 0) for n in news_list]
    avg = sum(compounds) / len(compounds) if compounds else 0
    # 0-100 score from compound -1..1
    score = round((avg + 1) / 2 * 100, 2)
    pos = sum(1 for c in compounds if c > 0.05)
    neg = sum(1 for c in compounds if c < -0.05)
    neu = len(compounds) - pos - neg
    n = len(compounds) or 1
    articles = [
        {
            "title": n["headline"],
            "source": "Sample News",
            "link": "#",
            "sentiment": {"compound": n.get("compound_score", 0), "label": n.get("sentiment", "neutral")},
            "published": datetime.now().isoformat(),
            "weight": n.get("confidence", 0.8),
        }
        for n in news_list
    ]
    return {
        "status": "success",
        "sentiment_score": score,
        "aggregate": {
            "compound": round(avg, 3),
            "avg_compound": round(avg, 3),
            "positive_count": pos,
            "neutral_count": neu,
            "negative_count": neg,
            "total_articles": len(news_list),
        },
        "articles": articles,
        "analyzer": "VADER",
        "filters_applied": None,
    }


def build_stability_response(semi_dynamic: bool = False) -> Dict[str, Any]:
    data = get_stability_sample(semi_dynamic)
    classification = data.get("classification", "Moderately Stable")
    if "Very Stable" in classification or "Stable" in classification:
        category, risk = "Stable", "Low"
    elif "Volatile" in classification or "Risky" in classification:
        category, risk = "Unstable", "High"
    else:
        category, risk = "Moderate", "Medium"
    components = data.get("factors", {})
    comp = {
        "market_momentum": components.get("market_momentum"),
        "sentiment": components.get("sentiment"),
        "volatility_inverse": components.get("volatility_inverse"),
        "inflation": components.get("inflation"),
        "liquidity": components.get("liquidity"),
    }
    return {
        "status": "success",
        "stability_score": data["stability_score"],
        "category": category,
        "risk_level": data.get("risk_level", risk),
        "explanation": data.get("explanation", f"{category}: Sample data."),
        "components": comp,
        "breakdown": None,
        "timestamp": datetime.utcnow().isoformat(),
        "disclaimer": "Educational project. Not financial advice.",
    }


def build_forecast_response(semi_dynamic: bool = False) -> Dict[str, Any]:
    data = get_forecast_sample(semi_dynamic)
    # Generate dates from today (next 7 days) for up-to-date sample
    base_value = data.get("current_value", 25850)
    from datetime import timedelta
    today = datetime.now().date()
    forecast = []
    cur = float(base_value)
    for i in range(1, 8):
        d = today + timedelta(days=i)
        delta = cur * 0.002 if data.get("forecast_trend") == "upward" else -cur * 0.001
        cur = cur + delta
        pred = round(cur, 2)
        forecast.append({
            "date": d.strftime("%Y-%m-%d"),
            "predicted": pred,
            "upper": round(pred * 1.008, 2),
            "lower": round(pred * 0.992, 2),
            "confidence": round(0.78 - i * 0.01, 2),
        })
    return {
        "status": "success",
        "forecast": forecast,
        "summary": {"trend": data.get("forecast_trend", "upward"), "model_accuracy": data.get("model_accuracy", 0.78)},
        "forecast_score": data.get("uptrend_probability", 62),
        "current_value": base_value,
        "model": "Facebook Prophet",
        "note": "Forecast from offline sample data (generated as of today).",
        "uptrend_probability": data.get("uptrend_probability", 62),
        "downtrend_probability": data.get("downtrend_probability", 38),
        "confidence_level": data.get("confidence_level", "Medium"),
    }
