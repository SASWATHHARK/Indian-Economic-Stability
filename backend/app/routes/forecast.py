from fastapi import APIRouter, HTTPException
from app.services import data_router
from app.services import DataFetcher
from app.ml.forecast import ForecastService, get_model_metrics
from app.schemas.forecast import ForecastResponse, ModelMetricsResponse

router = APIRouter()
_data_fetcher = DataFetcher() if DataFetcher else None
forecaster = ForecastService()

@router.get("/forecast", response_model=ForecastResponse)
def get_forecast():
    try:
        payload = data_router.get_forecast(
            data_fetcher=_data_fetcher,
            forecaster=forecaster,
        )
        return ForecastResponse(
            status=payload.get("status", "success"),
            forecast=payload["forecast"],
            summary=payload.get("summary"),
            forecast_score=payload.get("forecast_score"),
            current_value=payload.get("current_value"),
            model=payload.get("model", "Facebook Prophet"),
            note=payload.get("note"),
            uptrend_probability=payload.get("uptrend_probability"),
            downtrend_probability=payload.get("downtrend_probability"),
            confidence_level=payload.get("confidence_level"),
            data_source=payload.get("data_source"),
            demo_mode=payload.get("demo_mode"),
            sample_data_date=payload.get("sample_data_date"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model-metrics", response_model=ModelMetricsResponse)
def model_metrics():
    if not forecaster.is_trained and _data_fetcher:
        try:
            nifty_df = _data_fetcher.get_historical_dataframe("^NSEI", "3mo")
            if nifty_df is not None and not nifty_df.empty and len(nifty_df) >= 30:
                forecaster.train_model(nifty_df)
            else:
                nifty_df = _data_fetcher.get_sample_dataframe("3mo")
                forecaster.train_model(nifty_df)
        except Exception:
            pass
    m = get_model_metrics(forecaster)
    return ModelMetricsResponse(**m)
