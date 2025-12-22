import React from 'react';
import './About.css';

function About() {
  return (
    <div className="about-page">
      <div className="container">
        <h1 className="page-title">About the Project</h1>

        <div className="card">
          <h2>Project Overview</h2>
          <p>
            <strong>Predictive Framework to Indicate India's Economic Stability 
            using Market Indicators and Sentiment Analysis</strong>
          </p>
          <p>
            This project aims to provide a comprehensive framework for understanding 
            India's economic stability by combining market data, sentiment analysis, 
            and machine learning predictions. It is designed as an academic project 
            for final year students to demonstrate the integration of data science, 
            web development, and economic analysis.
          </p>
        </div>

        <div className="card">
          <h2>Methodology</h2>
          <h3>1. Data Collection</h3>
          <ul>
            <li><strong>Market Data:</strong> NIFTY 50 and SENSEX indices from Yahoo Finance</li>
            <li><strong>News Data:</strong> Economic news headlines from Google News RSS feeds</li>
            <li><strong>Economic Indicators:</strong> Inflation rate and Repo rate (configurable)</li>
          </ul>

          <h3>2. Machine Learning Models</h3>
          <ul>
            <li>
              <strong>Time Series Forecasting (Facebook Prophet):</strong>
              <ul>
                <li>Predicts 7-day market trends</li>
                <li>Provides confidence intervals</li>
                <li>Handles seasonality and trends</li>
              </ul>
            </li>
            <li>
              <strong>Sentiment Analysis (VADER):</strong>
              <ul>
                <li>Analyzes news headline sentiment</li>
                <li>Classifies as Positive, Neutral, or Negative</li>
                <li>Provides compound sentiment scores</li>
              </ul>
            </li>
          </ul>

          <h3>3. Stability Score Calculation</h3>
          <p>
            The Economic Stability Score (0-100) is calculated using a weighted combination:
          </p>
          <ul>
            <li><strong>Market Trend (40%):</strong> Based on forecast predictions and volatility</li>
            <li><strong>Sentiment Score (30%):</strong> Based on aggregate news sentiment</li>
            <li><strong>Economic Indicators (30%):</strong> Based on inflation and repo rates</li>
          </ul>
        </div>

        <div className="card">
          <h2>System Architecture</h2>
          <div className="architecture-diagram">
            <div className="arch-layer">
              <h3>Frontend Layer (React)</h3>
              <p>Dashboard, Forecast visualization, Sentiment display, About page</p>
            </div>
            <div className="arch-layer">
              <h3>Backend Layer (FastAPI)</h3>
              <p>REST APIs, Data processing, Model inference, Caching</p>
            </div>
            <div className="arch-layer">
              <h3>ML Layer</h3>
              <p>Prophet forecasting, VADER sentiment, Score calculation</p>
            </div>
          </div>
        </div>

        <div className="card">
          <h2>Technologies Used</h2>
          <div className="tech-grid">
            <div className="tech-category">
              <h3>Frontend</h3>
              <ul>
                <li>React 18</li>
                <li>React Router</li>
                <li>Recharts</li>
                <li>Axios</li>
              </ul>
            </div>
            <div className="tech-category">
              <h3>Backend</h3>
              <ul>
                <li>FastAPI</li>
                <li>Python 3.9+</li>
                <li>Uvicorn</li>
              </ul>
            </div>
            <div className="tech-category">
              <h3>Machine Learning</h3>
              <ul>
                <li>Facebook Prophet</li>
                <li>VADER Sentiment</li>
                <li>Pandas</li>
                <li>NumPy</li>
              </ul>
            </div>
            <div className="tech-category">
              <h3>Data Sources</h3>
              <ul>
                <li>Yahoo Finance (yfinance)</li>
                <li>Google News RSS</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="card">
          <h2>Limitations</h2>
          <ul>
            <li>
              <strong>Real-time Events:</strong> Market conditions are influenced by 
              real-time global events that cannot be fully predicted.
            </li>
            <li>
              <strong>Probabilistic Predictions:</strong> All forecasts are probabilistic 
              and should be interpreted as trends, not exact predictions.
            </li>
            <li>
              <strong>Model Updates:</strong> Models require periodic retraining with 
              new data to maintain accuracy.
            </li>
            <li>
              <strong>Data Availability:</strong> Dependent on external APIs which 
              may have rate limits or downtime.
            </li>
            <li>
              <strong>Sentiment Context:</strong> Sentiment analysis is based on headlines 
              and may not capture full article context.
            </li>
            <li>
              <strong>Not Financial Advice:</strong> This system is for educational and 
              trend understanding purposes only. Not a substitute for professional 
              financial advice.
            </li>
          </ul>
        </div>

        <div className="card">
          <h2>Future Enhancements</h2>
          <ul>
            <li>Integration of more economic indicators (GDP, unemployment, etc.)</li>
            <li>Real-time data streaming and updates</li>
            <li>Historical trend analysis and comparison</li>
            <li>User authentication and personalized dashboards</li>
            <li>Export functionality for reports</li>
            <li>Mobile app development</li>
            <li>Advanced ML models (LSTM, Transformer-based sentiment)</li>
            <li>Multi-country economic stability comparison</li>
          </ul>
        </div>

        <div className="card">
          <h2>Conclusion</h2>
          <p>
            This project demonstrates the integration of machine learning, web development, 
            and economic analysis to create a predictive framework for understanding economic 
            stability. While the system provides valuable insights, it is important to 
            remember that economic predictions are inherently uncertain and should be used 
            as one of many tools in economic analysis.
          </p>
          <p>
            The project is designed to be educational, transparent, and explainable, making 
            it suitable for academic evaluation and demonstration.
          </p>
        </div>
      </div>
    </div>
  );
}

export default About;

