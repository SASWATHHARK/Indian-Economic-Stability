from fastapi import APIRouter, HTTPException
from app.services import DataFetcher
from app.ml.forecast import ForecastService, get_model_metrics
from app.schemas.forecast import ForecastResponse, ModelMetricsResponse
from app.utils.stability_cache import update_stability_cache

router = APIRouter()
data_fetcher = DataFetcher()
forecaster = ForecastService()

@router.get("/forecast", response_model=ForecastResponse)
def get_forecast():
    try:
        try:
            nifty_df = data_fetcher.get_historical_dataframe("^NSEI", "3mo")
        except Exception:
            nifty_df = data_fetcher.get_sample_dataframe("3mo")
        if nifty_df.empty or len(nifty_df) < 30:
            nifty_df = data_fetcher.get_sample_dataframe("3mo")

        if not forecaster.is_trained:
            ok, msg = forecaster.train_model(nifty_df)
            if not ok:
                raise HTTPException(status_code=500, detail=msg)

        forecast_df = forecaster.forecast(days=7)
        summary = forecaster.get_forecast_summary(forecast_df)
        current_value = float(nifty_df["Close"].iloc[-1])

        forecast_data = [
            {
                "date": row["ds"].strftime("%Y-%m-%d"),
                "predicted": round(float(row["yhat"]), 2),
                "upper": round(float(row["yhat_upper"]), 2),
                "lower": round(float(row["yhat_lower"]), 2),
                "confidence": round(float(row["confidence"]), 2),
            }
            for _, row in forecast_df.iterrows()
        ]
        up_prob, down_prob = forecaster.get_uptrend_downtrend_probability(forecast_df)
        conf_level = forecaster.get_confidence_level()
        vol = nifty_df["Close"].pct_change().std() * 100 if len(nifty_df) > 1 else None
        update_stability_cache(up_prob, 50.0, vol)

        return ForecastResponse(
            status="success",
            forecast=forecast_data,
            summary=summary,
            forecast_score=round((up_prob / 100.0) * 100, 2),
            current_value=round(current_value, 2),
            model="Facebook Prophet",
            note="Forecast represents market trend, not exact values.",
            uptrend_probability=up_prob,
            downtrend_probability=down_prob,
            confidence_level=conf_level,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model-metrics", response_model=ModelMetricsResponse)
def model_metrics():
    if not forecaster.is_trained:
        try:
            nifty_df = data_fetcher.get_historical_dataframe("^NSEI", "3mo")
            if nifty_df.empty or len(nifty_df) < 30:
                nifty_df = data_fetcher.get_sample_dataframe("3mo")
            forecaster.train_model(nifty_df)
        except Exception:
            pass
    m = get_model_metrics(forecaster)
    return ModelMetricsResponse(**m)
