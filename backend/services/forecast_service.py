"""
7-day forecast using Prophet.
Returns: next 7 predicted, confidence interval, MAE, RMSE.
"""
import logging
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from services.market_service import get_historical_dataframe

logger = logging.getLogger(__name__)

try:
    from prophet import Prophet
    HAS_PROPHET = True
except ImportError:
    HAS_PROPHET = False

TEST_RATIO = 0.2


def _train_and_forecast(
    db: Session,
) -> Tuple[Optional[pd.DataFrame], float, float, Optional[object]]:
    """Train on NIFTY history, return (forecast_df, mae, rmse, model)."""
    df = get_historical_dataframe(db, "^NSEI", days=730)
    if df.empty or len(df) < 30:
        return None, 0.0, 0.0, None

    prophet_df = pd.DataFrame({
        "ds": df.index,
        "y": df["Close"].astype(float),
    }).dropna()
    if len(prophet_df) < 30:
        return None, 0.0, 0.0, None

    if not HAS_PROPHET:
        return _fallback_forecast(prophet_df), 0.0, 0.0, None

    n = len(prophet_df)
    test_size = max(1, int(n * TEST_RATIO))
    train = prophet_df.iloc[:-test_size]
    model = Prophet(
        daily_seasonality=True,
        weekly_seasonality=True,
        yearly_seasonality=False,
        changepoint_prior_scale=0.05,
    )
    model.fit(train)

    future = pd.DataFrame({"ds": prophet_df["ds"].iloc[-test_size:].values})
    pred = model.predict(future)
    y_true = prophet_df["y"].iloc[-test_size:].values
    y_pred = pred["yhat"].values
    mae = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))

    future_7 = model.make_future_dataframe(periods=7)
    forecast = model.predict(future_7)
    out = forecast.tail(7)
    return out, mae, rmse, model


def _fallback_forecast(prophet_df: pd.DataFrame) -> pd.DataFrame:
    """Simple trend extrapolation when Prophet unavailable."""
    last = prophet_df["y"].iloc[-1]
    last_dt = prophet_df["ds"].iloc[-1]
    dates = pd.date_range(start=last_dt, periods=8, freq="D")[1:]
    vals = [last * (1.001 ** i) for i in range(1, 8)]
    return pd.DataFrame({
        "ds": dates,
        "yhat": vals,
        "yhat_lower": [v * 0.98 for v in vals],
        "yhat_upper": [v * 1.02 for v in vals],
    })


def get_7day_forecast(db: Session) -> Dict:
    """
    Get 7-day forecast.
    Returns: forecast list, current_value, mae, rmse.
    """
    from services.market_service import fetch_and_store_market_data
    hist = get_historical_dataframe(db, "^NSEI", days=730)
    if hist.empty or len(hist) < 30:
        fetch_and_store_market_data(db)
    forecast_df, mae, rmse, _ = _train_and_forecast(db)
    df = get_historical_dataframe(db, "^NSEI", days=5)
    current = float(df["Close"].iloc[-1]) if not df.empty else 0.0

    if forecast_df is None or forecast_df.empty:
        return {
            "forecast": [],
            "current_value": current,
            "mae": None,
            "rmse": None,
            "model": "Prophet" if HAS_PROPHET else "Fallback",
        }

    forecast_list = []
    for _, row in forecast_df.iterrows():
        d = row["ds"]
        if hasattr(d, "strftime"):
            dstr = d.strftime("%Y-%m-%d")
        else:
            dstr = pd.Timestamp(d).strftime("%Y-%m-%d")
        forecast_list.append({
            "date": dstr,
            "predicted": round(float(row["yhat"]), 2),
            "lower": round(float(row.get("yhat_lower", row["yhat"] * 0.98)), 2),
            "upper": round(float(row.get("yhat_upper", row["yhat"] * 1.02)), 2),
        })

    return {
        "forecast": forecast_list,
        "current_value": round(current, 2),
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "model": "Prophet" if HAS_PROPHET else "Fallback",
    }
