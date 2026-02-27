"""
Data router – try live first, fallback to sample on failure.
Adds data_source, demo_mode, sample_data_date to every response.
When FORCE_SAMPLE_DATA: try live with short timeout; use sample if live fails.
"""
import threading
from typing import Any, Dict, List, Optional

from app.config import settings
from app.utils.log import get_logger
import app.services.live_data_service as live_data_service
import app.services.sample_data_service as sample_data_service

logger = get_logger(__name__)

OFFLINE_MSG = "⚠ Using Offline Sample Data Mode"
LIVE_ATTEMPT_TIMEOUT = 12  # seconds when FORCE_SAMPLE_DATA – try live first


def _enrich(response: Dict[str, Any], data_source: str, demo_mode: bool) -> Dict[str, Any]:
    from datetime import datetime
    if response is None:
        response = {}
    out = dict(response)
    out["data_source"] = data_source
    out["demo_mode"] = demo_mode
    if data_source == "offline_sample":
        out["sample_data_date"] = datetime.now().strftime("%Y-%m-%d %H:%M IST")
    return out


def get_market_data(period: str = "5d") -> Dict[str, Any]:
    force_sample = getattr(settings, "FORCE_SAMPLE_DATA", False)

    def _try_live():
        try:
            return live_data_service.fetch_live_market_data(period=period)
        except Exception:
            return None

    if force_sample:
        # Try live first (with timeout) – show live data as much as possible
        result = [None]
        def run():
            try:
                result[0] = _try_live()
            except Exception:
                pass
        t = threading.Thread(target=run, daemon=True)
        t.start()
        t.join(timeout=LIVE_ATTEMPT_TIMEOUT)
        if result[0] is not None:
            return _enrich(result[0], "live", False)
        try:
            semi = True
            data = sample_data_service.build_market_response(semi_dynamic=semi)
        except Exception as fallback_err:
            logger.warning("Sample market data failed (%s), using minimal fallback", fallback_err)
            data = sample_data_service._build_market_response_minimal()
        return _enrich(data, "offline_sample", getattr(settings, "DEMO_MODE_WHEN_OFFLINE", True))

    try:
        data = live_data_service.fetch_live_market_data(period=period)
        return _enrich(data, "live", False)
    except Exception as e:
        logger.warning("%s (market): %s", OFFLINE_MSG, e)
        try:
            semi = getattr(settings, "SAMPLE_DATA_SEMI_DYNAMIC", False)
            data = sample_data_service.build_market_response(semi_dynamic=semi)
        except Exception as fallback_err:
            logger.warning("Sample market data failed (%s), using minimal fallback", fallback_err)
            data = sample_data_service._build_market_response_minimal()
        return _enrich(data, "offline_sample", getattr(settings, "DEMO_MODE_WHEN_OFFLINE", True))


def get_news_then_sentiment(
    query: str = "India economy RBI inflation stock market",
    max_results: int = 20,
    sentiment_analyzer=None,
    sentiment_filter: Optional[str] = None,
    date_from=None,
    date_to=None,
):
    """
    Try live news + sentiment; on failure return sample sentiment response.
    If sentiment_analyzer is provided, use it for live path; else fallback only.
    """
    force_sample = getattr(settings, "FORCE_SAMPLE_DATA", False)
    if force_sample and sentiment_analyzer:
        result = [None]
        def _try_sentiment():
            try:
                headlines = live_data_service.fetch_live_news(query=query, max_results=max_results)
                if headlines and sentiment_analyzer:
                    results = sentiment_analyzer.analyze_batch_weighted(
                        headlines, title_key="title", source_key="source", published_key="published"
                    )
                    aggregate = sentiment_analyzer.get_aggregate_weighted(results, headlines)
                    score = sentiment_analyzer.normalize_score(aggregate)
                    articles = [
                        {"title": headlines[i]["title"], "source": headlines[i].get("source", "Unknown"),
                         "link": headlines[i].get("link", "#"), "sentiment": results[i],
                         "published": headlines[i].get("published"), "weight": results[i].get("weight")}
                        for i in range(len(results))
                    ]
                    return {"status": "success", "sentiment_score": round(score, 2), "aggregate": aggregate,
                            "articles": articles, "analyzer": "VADER", "filters_applied": None}
            except Exception:
                return None
        def run():
            result[0] = _try_sentiment()
        t = threading.Thread(target=run, daemon=True)
        t.start()
        t.join(timeout=LIVE_ATTEMPT_TIMEOUT)
        if result[0] is not None:
            return _enrich(result[0], "live", False)
    if force_sample:
        news_list = sample_data_service.get_news_sample()
        payload = sample_data_service.build_sentiment_response_from_news(news_list)
        return _enrich(payload, "offline_sample", getattr(settings, "DEMO_MODE_WHEN_OFFLINE", True))
    try:
        headlines = live_data_service.fetch_live_news(query=query, max_results=max_results)
        if sentiment_analyzer and headlines:
            results = sentiment_analyzer.analyze_batch_weighted(
                headlines, title_key="title", source_key="source", published_key="published"
            )
            aggregate = sentiment_analyzer.get_aggregate_weighted(results, headlines)
            score = sentiment_analyzer.normalize_score(aggregate)
            if sentiment_filter or date_from or date_to:
                headlines, results = sentiment_analyzer.filter_articles(
                    headlines, results,
                    sentiment_filter=sentiment_filter,
                    date_from=date_from,
                    date_to=date_to,
                )
                if headlines:
                    aggregate = sentiment_analyzer.get_aggregate_weighted(results, headlines)
                    score = sentiment_analyzer.normalize_score(aggregate)
            articles = [
                {
                    "title": headlines[i]["title"],
                    "source": headlines[i].get("source", "Unknown"),
                    "link": headlines[i].get("link", "#"),
                    "sentiment": results[i],
                    "published": headlines[i].get("published"),
                    "weight": results[i].get("weight"),
                }
                for i in range(len(results))
            ]
            payload = {
                "status": "success",
                "sentiment_score": round(score, 2),
                "aggregate": aggregate,
                "articles": articles,
                "analyzer": "VADER",
                "filters_applied": {"sentiment": sentiment_filter, "date_from": str(date_from) if date_from else None, "date_to": str(date_to) if date_to else None},
            }
            return _enrich(payload, "live", False)
    except Exception as e:
        logger.warning("%s (sentiment): %s", OFFLINE_MSG, e)

    news_list = sample_data_service.get_news_sample()
    payload = sample_data_service.build_sentiment_response_from_news(news_list)
    return _enrich(payload, "offline_sample", getattr(settings, "DEMO_MODE_WHEN_OFFLINE", True))


def get_stability(
    stability_svc=None,
    cache_getter=None,
    inflation_rate: Optional[float] = None,
    repo_rate: Optional[float] = None,
) -> Dict[str, Any]:
    """Try live stability (cache + service); on failure return sample."""
    force_sample = getattr(settings, "FORCE_SAMPLE_DATA", False)
    if force_sample and stability_svc and cache_getter:
        result = [None]
        def _try_stability():
            try:
                from datetime import datetime
                now = datetime.utcnow()
                cache = cache_getter()
                cache_ok = (cache.get("ts") and (now - cache["ts"]).total_seconds() < getattr(settings, "STABILITY_CACHE_TTL", 300))
                if cache_ok and cache.get("forecast_score") is not None and cache.get("sentiment_score") is not None:
                    market_momentum, sentiment_score = cache["forecast_score"], cache["sentiment_score"]
                else:
                    market_momentum = sentiment_score = 50.0
                volatility_inverse = cache.get("volatility") or 50.0
                from app.utils.stability_helpers import inflation_score_0_100, liquidity_score_0_100
                infl = inflation_score_0_100(inflation_rate)
                liq = liquidity_score_0_100(None)
                r = stability_svc.calculate(market_momentum_score=market_momentum, sentiment_score=sentiment_score,
                    volatility_inverse_score=volatility_inverse, inflation_score=infl, liquidity_score=liq)
                return {"status": "success", "stability_score": r["stability_score"], "category": r["category"],
                    "risk_level": r["risk_level"], "explanation": r["explanation"], "components": r["components"],
                    "breakdown": r.get("breakdown"), "timestamp": now.isoformat(),
                    "disclaimer": "Educational project. Not financial advice."}
            except Exception:
                return None
        def run():
            result[0] = _try_stability()
        t = threading.Thread(target=run, daemon=True)
        t.start()
        t.join(timeout=5)  # stability is fast
        if result[0] is not None:
            return _enrich(result[0], "live", False)
    if force_sample:
        payload = sample_data_service.build_stability_response(semi_dynamic=True)
        return _enrich(payload, "offline_sample", getattr(settings, "DEMO_MODE_WHEN_OFFLINE", True))
    try:
        if stability_svc and cache_getter:
            from datetime import datetime
            now = datetime.utcnow()
            cache = cache_getter()
            cache_ok = (
                cache.get("ts") is not None
                and (now - cache["ts"]).total_seconds() < getattr(settings, "STABILITY_CACHE_TTL", 300)
            )
            if cache_ok and cache.get("forecast_score") is not None and cache.get("sentiment_score") is not None:
                market_momentum = cache["forecast_score"]
                sentiment_score = cache["sentiment_score"]
                volatility_inverse = cache.get("volatility") or 50.0
            else:
                market_momentum = sentiment_score = volatility_inverse = 50.0
            from app.utils.stability_helpers import inflation_score_0_100, liquidity_score_0_100
            inflation = inflation_score_0_100(inflation_rate)
            liquidity = liquidity_score_0_100(None)
            result = stability_svc.calculate(
                market_momentum_score=market_momentum,
                sentiment_score=sentiment_score,
                volatility_inverse_score=volatility_inverse,
                inflation_score=inflation,
                liquidity_score=liquidity,
            )
            payload = {
                "status": "success",
                "stability_score": result["stability_score"],
                "category": result["category"],
                "risk_level": result["risk_level"],
                "explanation": result["explanation"],
                "components": result["components"],
                "breakdown": result.get("breakdown"),
                "timestamp": now.isoformat(),
                "disclaimer": "Educational project. Not financial advice.",
            }
            return _enrich(payload, "live", False)
    except Exception as e:
        logger.warning("%s (stability): %s", OFFLINE_MSG, e)

    semi = getattr(settings, "SAMPLE_DATA_SEMI_DYNAMIC", False)
    payload = sample_data_service.build_stability_response(semi_dynamic=semi)
    return _enrich(payload, "offline_sample", getattr(settings, "DEMO_MODE_WHEN_OFFLINE", True))


def get_forecast(
    data_fetcher=None,
    forecaster=None,
) -> Dict[str, Any]:
    """Try live forecast (historical + Prophet); on failure return sample."""
    if getattr(settings, "FORCE_SAMPLE_DATA", False):
        semi = True
        payload = sample_data_service.build_forecast_response(semi_dynamic=semi)
        return _enrich(payload, "offline_sample", getattr(settings, "DEMO_MODE_WHEN_OFFLINE", True))
    try:
        if data_fetcher and forecaster:
            nifty_df = live_data_service.fetch_live_historical_dataframe("^NSEI", "3mo")
            if nifty_df is not None and not nifty_df.empty and len(nifty_df) >= 30:
                if not forecaster.is_trained:
                    ok, _ = forecaster.train_model(nifty_df)
                    if not ok:
                        raise ValueError("Forecast model training failed")
                forecast_df = forecaster.forecast(days=7)
                summary = forecaster.get_forecast_summary(forecast_df)
                current_value = float(nifty_df["Close"].iloc[-1])
                forecast_data = [
                    {
                        "date": row["ds"].strftime("%Y-%m-%d"),
                        "predicted": round(float(row["yhat"]), 2),
                        "upper": round(float(row["yhat_upper"]), 2),
                        "lower": round(float(row["yhat_lower"]), 2),
                        "confidence": round(float(row.get("confidence", 0.75)), 2),
                    }
                    for _, row in forecast_df.iterrows()
                ]
                from app.utils.stability_cache import update_stability_cache
                up_prob, down_prob = forecaster.get_uptrend_downtrend_probability(forecast_df)
                conf_level = forecaster.get_confidence_level()
                vol = nifty_df["Close"].pct_change().std() * 100 if len(nifty_df) > 1 else None
                update_stability_cache(up_prob, 50.0, vol)
                payload = {
                    "status": "success",
                    "forecast": forecast_data,
                    "summary": summary,
                    "forecast_score": round((up_prob / 100.0) * 100, 2),
                    "current_value": round(current_value, 2),
                    "model": "Facebook Prophet",
                    "note": "Forecast represents market trend, not exact values.",
                    "uptrend_probability": up_prob,
                    "downtrend_probability": down_prob,
                    "confidence_level": conf_level,
                }
                return _enrich(payload, "live", False)
    except Exception as e:
        logger.warning("%s (forecast): %s", OFFLINE_MSG, e)

    semi = getattr(settings, "SAMPLE_DATA_SEMI_DYNAMIC", False)
    payload = sample_data_service.build_forecast_response(semi_dynamic=semi)
    return _enrich(payload, "offline_sample", getattr(settings, "DEMO_MODE_WHEN_OFFLINE", True))
