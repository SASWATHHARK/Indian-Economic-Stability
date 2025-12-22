# Abstract

## Predictive Framework to Indicate India's Economic Stability using Market Indicators and Sentiment Analysis

### Problem Statement

India's economic health is influenced by multiple factors including stock market indices (NIFTY 50, SENSEX), macroeconomic indicators (inflation, repo rate), and news sentiment from global events. Existing platforms provide raw data but fail to combine market trends, sentiment analysis, and forecasting into a single interpretable Economic Stability Score that is accessible to students and general users.

### Objective

This project aims to develop a comprehensive predictive framework that:
1. Collects real-time market data and news headlines
2. Applies machine learning models for forecasting and sentiment analysis
3. Calculates a unified Economic Stability Score (0-100)
4. Provides an intuitive web interface for visualization and interpretation

### Methodology

The system employs a three-layer architecture:
- **Frontend Layer:** React-based dashboard with interactive visualizations
- **Backend Layer:** FastAPI REST APIs for data processing and model inference
- **ML Layer:** Facebook Prophet for time-series forecasting and VADER for sentiment analysis

The Economic Stability Score is calculated using a weighted combination:
- Market Trend (40%): Based on 7-day forecast predictions
- Sentiment Score (30%): Aggregate news headline sentiment
- Economic Indicators (30%): Inflation and repo rate normalization

### Results

The system successfully:
- Fetches real-time market data from Yahoo Finance
- Generates 7-day market forecasts with confidence intervals
- Analyzes sentiment from 20+ news headlines
- Calculates interpretable stability scores with category classification (Stable/Moderate/Unstable)
- Provides an intuitive web interface for all features

### Limitations

The framework acknowledges that:
- Market conditions are influenced by unpredictable real-time events
- Predictions are probabilistic, not deterministic
- Models require periodic retraining
- The system is advisory, not financial advice

### Conclusion

This project demonstrates the successful integration of machine learning, web development, and economic analysis to create a predictive framework for understanding economic stability. The system is designed to be educational, transparent, and explainable, making it suitable for academic evaluation and demonstration.

**Keywords:** Economic Stability, Market Forecasting, Sentiment Analysis, Machine Learning, Web Application

