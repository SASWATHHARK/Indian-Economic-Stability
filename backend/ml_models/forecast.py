"""
Time Series Forecasting Module
Uses Facebook Prophet for 7-day market trend prediction
"""

import pandas as pd
import numpy as np
from prophet import Prophet
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class MarketForecaster:
    """
    Forecasts market trends using Prophet time series model
    """
    
    def __init__(self):
        self.model = None
        self.last_training_date = None
    
    def prepare_data(self, historical_data: pd.DataFrame):
        """
        Prepare data for Prophet model
        Prophet requires columns: 'ds' (date) and 'y' (value)
        """
        df = historical_data.copy()
        df.reset_index(inplace=True)
        
        # Prophet expects 'ds' and 'y' columns
        if 'Date' in df.columns:
            df['ds'] = pd.to_datetime(df['Date'])
        elif 'Datetime' in df.columns:
            df['ds'] = pd.to_datetime(df['Datetime'])
        else:
            df['ds'] = df.index
        
        # Use Close price as target
        df['y'] = df['Close'].astype(float)
        
        # Select only required columns
        prophet_df = df[['ds', 'y']].copy()
        prophet_df = prophet_df.dropna()
        
        return prophet_df
    
    def train_model(self, historical_data: pd.DataFrame):
        """
        Train Prophet model on historical data
        """
        try:
            prophet_df = self.prepare_data(historical_data)
            
            if len(prophet_df) < 30:  # Need minimum data points
                return False, "Insufficient historical data (need at least 30 days)"
            
            # Initialize and fit Prophet model
            self.model = Prophet(
                daily_seasonality=True,
                weekly_seasonality=True,
                yearly_seasonality=False,  # Disable for short-term forecasts
                changepoint_prior_scale=0.05  # More conservative predictions
            )
            
            self.model.fit(prophet_df)
            self.last_training_date = prophet_df['ds'].max()
            
            return True, "Model trained successfully"
            
        except Exception as e:
            return False, f"Training error: {str(e)}"
    
    def forecast(self, days: int = 7):
        """
        Generate forecast for next N days
        Returns: DataFrame with predictions and confidence intervals
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train_model() first.")
        
        # Create future dataframe
        future = self.model.make_future_dataframe(periods=days)
        
        # Generate forecast
        forecast = self.model.predict(future)
        
        # Extract only future predictions
        future_forecast = forecast.tail(days).copy()
        
        # Calculate confidence score based on uncertainty intervals
        future_forecast['confidence'] = (
            1 - (future_forecast['yhat_upper'] - future_forecast['yhat_lower']) / 
            (future_forecast['yhat'].abs() + 1e-6)
        ).clip(0, 1) * 100
        
        return future_forecast
    
    def get_forecast_summary(self, forecast_df: pd.DataFrame):
        """
        Extract summary statistics from forecast
        """
        return {
            'trend': 'upward' if forecast_df['yhat'].iloc[-1] > forecast_df['yhat'].iloc[0] else 'downward',
            'avg_predicted_value': float(forecast_df['yhat'].mean()),
            'min_predicted': float(forecast_df['yhat_lower'].min()),
            'max_predicted': float(forecast_df['yhat_upper'].max()),
            'avg_confidence': float(forecast_df['confidence'].mean()),
            'volatility': float(forecast_df['yhat_upper'].sub(forecast_df['yhat_lower']).mean())
        }


def normalize_forecast_score(forecast_summary: dict, current_value: float) -> float:
    """
    Normalize forecast into 0-1 score
    Higher score = more stable/predictable trend
    """
    trend_score = 0.7 if forecast_summary['trend'] == 'upward' else 0.3
    confidence_score = forecast_summary['avg_confidence'] / 100
    
    # Lower volatility = higher stability
    volatility = forecast_summary['volatility']
    volatility_score = max(0, 1 - (volatility / (current_value * 0.1)))  # Normalize
    
    # Weighted combination
    normalized_score = (trend_score * 0.4 + confidence_score * 0.4 + volatility_score * 0.2)
    
    return min(1.0, max(0.0, normalized_score))

