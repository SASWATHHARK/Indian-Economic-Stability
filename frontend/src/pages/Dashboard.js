import React, { useState, useEffect } from 'react';
import { getForecast, getSentiment, getStabilityScore, getMarketData } from '../services/api';
import StabilityGauge from '../components/StabilityGauge';
import MarketForecast from '../components/MarketForecast';
import SentimentAnalysis from '../components/SentimentAnalysis';
import MarketDashboard from '../components/MarketDashboard';
import './Dashboard.css';

const Dashboard = () => {
  // State for all 4 data points
  const [marketData, setMarketData] = useState(null);
  const [forecastData, setForecastData] = useState(null);
  const [sentimentData, setSentimentData] = useState(null);
  const [stabilityData, setStabilityData] = useState(null);

  // Loading states - default true
  const [loading, setLoading] = useState({
    market: true,
    forecast: true,
    sentiment: true,
    stability: true
  });

  // Error states
  const [error, setError] = useState({
    market: null,
    forecast: null,
    sentiment: null,
    stability: null
  });

  useEffect(() => {
    // Helper for safe fetching
    const fetchData = async (fn, setData, key) => {
      try {
        console.log(`Fetching ${key}...`);
        const res = await fn();
        console.log(`${key} Response:`, res.data);
        setData(res.data);
        setError(prev => ({ ...prev, [key]: null }));
      } catch (err) {
        console.error(`${key} Error:`, err);
        const isTimeout = err.code === 'ECONNABORTED' || err.message?.includes('timeout');
        const msg = isTimeout
          ? "Request timed out. Backend may be busy (first load can take a minute). Try refreshing."
          : (err.response?.data?.detail || err.message || "Failed to load data");
        setError(prev => ({ ...prev, [key]: msg }));
      } finally {
        setLoading(prev => ({ ...prev, [key]: false }));
      }
    };

    // Parallel specific fetches
    fetchData(getMarketData, setMarketData, 'market');
    fetchData(getForecast, setForecastData, 'forecast');
    fetchData(getSentiment, setSentimentData, 'sentiment');
    fetchData(getStabilityScore, setStabilityData, 'stability');
  }, []);

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Indian Economic Stability Dashboard</h1>
        <p>AI-Powered Predictive Framework utilizing Market Data, Sentiment Analysis, and Macroeconomic Indicators.</p>
      </header>
      
      <div className="dashboard-grid">
        {/* Section 1: Economic Stability Score (Main Hero) */}
        <div className="grid-item stability-section">
          <StabilityGauge 
            data={stabilityData} 
            loading={loading.stability} 
            error={error.stability} 
          />
        </div>

        {/* Section 2: Market Overview (NIFTY & SENSEX) */}
        <div className="grid-item market-section">
             {/* Note: MarketDashboard renders its own white cards internally */}
             <MarketDashboard
                data={marketData}
                loading={loading.market}
                error={error.market}
             />
        </div>

        {/* Section 3: 7-Day Market Forecast */}
        <div className="grid-item forecast-section">
          <MarketForecast 
            data={forecastData} 
            loading={loading.forecast} 
            error={error.forecast} 
          />
        </div>
        
        {/* Section 4: Economic Sentiment Analysis */}
        <div className="grid-item sentiment-section">
          <SentimentAnalysis 
            data={sentimentData} 
            loading={loading.sentiment} 
            error={error.sentiment} 
          />
        </div>
      </div>
      
      <footer className="dashboard-footer">
        <p>&copy; {new Date().getFullYear()} Final Year Project. Data simulated/fetched for academic demonstration.</p>
      </footer>
    </div>
  );
};

export default Dashboard;
