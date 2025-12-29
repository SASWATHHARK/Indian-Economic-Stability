"""
FastAPI Backend for Economic Stability Prediction System
Clean & Stable API Design (Final Year Project Version)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional

from services.data_fetcher import DataFetcher
from ml_models.forecast import MarketForecaster, normalize_forecast_score
from ml_models.sentiment import SentimentAnalyzer, normalize_sentiment_score
from ml_models.stability_score import (
    StabilityScoreCalculator,
    get_economic_indicators_score
)

# --------------------------------------------------
# App Initialization
# --------------------------------------------------

app = FastAPI(
    title="Economic Stability Prediction API",
    description="Predictive framework to analyze India's economic stability",
    version="1.0.0"
)

# CORS (Open for demo & academic use)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Service Initialization (Single Instance)
# --------------------------------------------------

data_fetcher = DataFetcher()
forecaster = MarketForecaster()
sentiment_analyzer = SentimentAnalyzer()
stability_calculator = StabilityScoreCalculator()

# --------------------------------------------------
# Root Endpoint
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Economic Stability Prediction API is running",
        "version": "1.0.0",
        "available_endpoints": [
            "/market-data",
            "/forecast",
            "/sentiment",
            "/stability-score",
            "/health"
        ]
    }

# --------------------------------------------------
# Market Data Endpoint
# --------------------------------------------------

@app.get("/market-data")
def get_market_data():
    """
    Fetch NIFTY & SENSEX market data.
    Uses sample data if live fetch fails.
    """
    try:
        data = data_fetcher.fetch_market_data(period="3mo")
        return data
    except Exception:
        return data_fetcher.fetch_market_data(
            period="3mo",
            use_sample=True
        )

# --------------------------------------------------
# Forecast Endpoint
# --------------------------------------------------

@app.get("/forecast")
def get_forecast():
    """
    Generate 7-day market forecast using Prophet model
    """
    try:
        # Get historical data
        try:
            nifty_df = data_fetcher.get_historical_dataframe("^NSEI", "3mo")
        except Exception:
            nifty_df = data_fetcher.get_sample_dataframe("3mo")

        # Safety check
        if nifty_df.empty or len(nifty_df) < 30:
            nifty_df = data_fetcher.get_sample_dataframe("3mo")

        # Train model only once
        if not forecaster.is_trained:
            success, msg = forecaster.train_model(nifty_df)
            if not success:
                raise HTTPException(status_code=500, detail=msg)

        # Forecast
        forecast_df = forecaster.forecast(days=7)
        summary = forecaster.get_forecast_summary(forecast_df)

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

        current_value = float(nifty_df["Close"].iloc[-1])
        forecast_score = normalize_forecast_score(summary, current_value)

        return {
            "status": "success",
            "forecast": forecast_data,
            "summary": summary,
            "forecast_score": round(forecast_score * 100, 2),
            "current_value": round(current_value, 2),
            "model": "Facebook Prophet",
            "note": "Forecast represents market trend, not exact values"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --------------------------------------------------
# Sentiment Analysis Endpoint
# --------------------------------------------------

@app.get("/sentiment")
def get_sentiment():
    """
    Analyze sentiment from Indian economic news headlines
    """
    try:
        headlines = data_fetcher.fetch_news_headlines(
            query="India economy RBI inflation stock market",
            max_results=20
        )

        if not headlines:
            raise Exception("No news available")

        titles = [h["title"] for h in headlines]
        sentiment_results = sentiment_analyzer.analyze_batch(titles)
        aggregate = sentiment_analyzer.get_aggregate_sentiment(sentiment_results)

        sentiment_score = normalize_sentiment_score(aggregate)

        articles = [
            {
                "title": headlines[i]["title"],
                "source": headlines[i]["source"],
                "link": headlines[i]["link"],
                "sentiment": sentiment_results[i]
            }
            for i in range(len(sentiment_results))
        ]

        return {
            "status": "success",
            "sentiment_score": round(sentiment_score * 100, 2),
            "aggregate": aggregate,
            "articles": articles,
            "analyzer": "VADER"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --------------------------------------------------
# Stability Score Endpoint
# --------------------------------------------------

@app.get("/stability-score")
def get_stability_score(
    inflation_rate: Optional[float] = None,
    repo_rate: Optional[float] = None
):
    """
    Final Economic Stability Score (0–100)
    """
    try:
        # Market Trend Score
        forecast_data = get_forecast()
        market_score = forecast_data["forecast_score"] / 100

        # Sentiment Score
        sentiment_data = get_sentiment()
        sentiment_score = sentiment_data["sentiment_score"] / 100

        # Economic Indicators
        economic_score = get_economic_indicators_score(
            inflation_rate,
            repo_rate
        )

        # Final Stability Score
        result = stability_calculator.calculate(
            market_trend_score=market_score,
            sentiment_score=sentiment_score,
            economic_indicators_score=economic_score
        )

        return {
            "status": "success",
            "stability_score": result["stability_score"],
            "category": result["category"],
            "interpretation": result["interpretation"],
            "components": result["components"],
            "timestamp": datetime.now().isoformat(),
            "disclaimer": "Educational project. Not financial advice."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

# --------------------------------------------------
# Run Server
# --------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
