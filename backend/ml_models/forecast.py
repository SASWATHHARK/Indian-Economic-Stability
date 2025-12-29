"""
Time Series Forecasting Module
Uses Facebook Prophet for 7-day market trend prediction
"""

import pandas as pd
import numpy as np
from prophet import Prophet
import warnings

warnings.filterwarnings("ignore")


class MarketForecaster:
    """
    Forecasts market trends using Prophet
    """

    def __init__(self):
        self.model = None
        self.is_trained = False
        self.last_training_date = None

    # --------------------------------------------------
    # Data Preparation
    # --------------------------------------------------

    def prepare_data(self, historical_data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare data for Prophet (ds, y)
        """
        df = historical_data.copy()

        # Ensure datetime index
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)

        prophet_df = pd.DataFrame({
            "ds": df.index,
            "y": df["Close"].astype(float)
        }).dropna()

        return prophet_df

    # --------------------------------------------------
    # Model Training
    # --------------------------------------------------

    def train_model(self, historical_data: pd.DataFrame):
        """
        Train Prophet model
        """
        try:
            prophet_df = self.prepare_data(historical_data)

            if len(prophet_df) < 30:
                return False, "Insufficient data for training (min 30 days required)"

            self.model = Prophet(
                daily_seasonality=True,
                weekly_seasonality=True,
                yearly_seasonality=False,
                changepoint_prior_scale=0.05
            )

            self.model.fit(prophet_df)

            self.is_trained = True
            self.last_training_date = prophet_df["ds"].max()

            return True, "Model trained successfully"

        except Exception as e:
            self.is_trained = False
            return False, f"Training error: {str(e)}"

    # --------------------------------------------------
    # Forecasting
    # --------------------------------------------------

    def forecast(self, days: int = 7) -> pd.DataFrame:
        """
        Generate forecast for next N days
        """
        if not self.is_trained or self.model is None:
            raise ValueError("Model not trained")

        future = self.model.make_future_dataframe(periods=days)
        forecast = self.model.predict(future)

        future_forecast = forecast.tail(days).copy()

        # Confidence score (0–1)
        uncertainty = future_forecast["yhat_upper"] - future_forecast["yhat_lower"]
        future_forecast["confidence"] = (
            1 - (uncertainty / (future_forecast["yhat"].abs() + 1e-6))
        ).clip(0, 1)

        return future_forecast

    # --------------------------------------------------
    # Forecast Summary
    # --------------------------------------------------

    def get_forecast_summary(self, forecast_df: pd.DataFrame) -> dict:
        """
        Summary metrics from forecast
        """
        return {
            "trend": "upward"
            if forecast_df["yhat"].iloc[-1] > forecast_df["yhat"].iloc[0]
            else "downward",
            "avg_predicted_value": float(forecast_df["yhat"].mean()),
            "min_predicted": float(forecast_df["yhat_lower"].min()),
            "max_predicted": float(forecast_df["yhat_upper"].max()),
            "avg_confidence": float(forecast_df["confidence"].mean()),
            "volatility": float(
                (forecast_df["yhat_upper"] - forecast_df["yhat_lower"]).mean()
            ),
        }


# --------------------------------------------------
# Forecast Score Normalization
# --------------------------------------------------

def normalize_forecast_score(forecast_summary: dict, current_value: float) -> float:
    """
    Normalize forecast result into 0–1 stability score
    """
    trend_score = 0.7 if forecast_summary["trend"] == "upward" else 0.3
    confidence_score = forecast_summary["avg_confidence"]

    volatility = forecast_summary["volatility"]
    volatility_score = max(
        0.0, 1 - (volatility / (current_value * 0.1))
    )

    score = (
        trend_score * 0.4
        + confidence_score * 0.4
        + volatility_score * 0.2
    )

    return round(min(1.0, max(0.0, score)), 3)
