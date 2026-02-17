from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.common import RefreshResponse
from app.database import get_db
from app.database import crud
from app.services import DataFetcher
from app.sentiment import SentimentService
from app.ml.stability import StabilityScoreService
from app.ml.forecast import ForecastService
from app.utils.stability_helpers import inflation_score_0_100, liquidity_score_0_100
from app.utils.stability_cache import update_stability_cache, get_stability_cache

router = APIRouter()
data_fetcher = DataFetcher()
sentiment_svc = SentimentService()
stability_svc = StabilityScoreService()
forecaster = ForecastService()

def do_refresh(db: Session) -> dict:
    """Core refresh logic (call from route or scheduler)."""
    market_stored = sentiment_stored = stability_stored = False
    today = date.today()

    try:
        data = data_fetcher.fetch_market_data(period="5d")
        if data.get("nifty") and data["nifty"].get("current"):
            crud.upsert_market_data(
                db,
                today,
                nifty_close=data.get("nifty", {}).get("current"),
                sensex_close=data.get("sensex", {}).get("current"),
                gold_close=data.get("gold", {}).get("current"),
                silver_close=data.get("silver", {}).get("current"),
                oil_close=data.get("oil", {}).get("current"),
                inr_close=data.get("inr", {}).get("current"),
                nifty_volatility=data.get("nifty", {}).get("volatility"),
            )
            market_stored = True
    except Exception:
        pass

    try:
        headlines = data_fetcher.fetch_news_headlines("India economy RBI inflation", max_results=20)
        if headlines:
            results = sentiment_svc.analyze_batch_weighted(headlines)
            agg = sentiment_svc.get_aggregate_weighted(results, headlines)
            score = sentiment_svc.normalize_score(agg)
            crud.create_sentiment_score(
                db, today, score,
                positive_count=agg.get("positive_count", 0),
                neutral_count=agg.get("neutral_count", 0),
                negative_count=agg.get("negative_count", 0),
                total_articles=agg.get("total_articles", 0),
                raw_aggregate=agg,
            )
            sentiment_stored = True
            update_stability_cache(50.0, score, None)
    except Exception:
        pass

    try:
        nifty_df = data_fetcher.get_historical_dataframe("^NSEI", "3mo")
        if not nifty_df.empty and len(nifty_df) >= 30:
            if not forecaster.is_trained:
                forecaster.train_model(nifty_df)
            forecast_df = forecaster.forecast(days=7)
            up_prob, down_prob = forecaster.get_uptrend_downtrend_probability(forecast_df)
            current_val = float(nifty_df["Close"].iloc[-1])
            vol = nifty_df["Close"].pct_change().std() * 100 if len(nifty_df) > 1 else None
            update_stability_cache(up_prob, 50.0, vol)
        cache = get_stability_cache()
        res = stability_svc.calculate(
            market_momentum_score=cache.get("forecast_score") or 50,
            sentiment_score=cache.get("sentiment_score") or 50,
            volatility_inverse_score=cache.get("volatility") or 50,
            inflation_score=inflation_score_0_100(None),
            liquidity_score=liquidity_score_0_100(None),
        )
        crud.create_stability_history(
            db, today,
            stability_score=res["stability_score"],
            category=res["category"],
            risk_level=res["risk_level"],
            components=res.get("components"),
            explanation=res.get("explanation"),
        )
        stability_stored = True
    except Exception:
        pass

    return {
        "status": "success",
        "message": "Refresh completed.",
        "market_stored": market_stored,
        "sentiment_stored": sentiment_stored,
        "stability_stored": stability_stored,
    }


@router.post("/refresh-data", response_model=RefreshResponse)
def refresh_data(db: Session = Depends(get_db)):
    """Trigger daily data refresh: fetch live data and store in DB."""
    return RefreshResponse(**do_refresh(db))
