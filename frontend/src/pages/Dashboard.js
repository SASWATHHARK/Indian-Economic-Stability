import React, { useState, useEffect } from 'react';
import { getSentiment, getStabilityScore } from '../services/api';
import StabilityGauge from '../components/StabilityGauge';
import MarketForecast from '../components/MarketForecast';
import SentimentAnalysis from '../components/SentimentAnalysis';
import MarketDashboard from '../components/MarketDashboard';
import DataSourceBadge from '../components/DataSourceBadge';
import { getSafeForecast } from '../services/forecastService';
import { getEconomicSnapshot } from '../services/marketDataService';
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
    const adaptSnapshotToDashboardShape = (snapshot) => {
      const normalized = snapshot?.data || null;
      const isLive = snapshot?.source === 'Live';
      if (!normalized) return null;

      const today = new Date(snapshot?.lastUpdated || Date.now())
        .toISOString()
        .slice(0, 10);

      return {
        // For MarketDashboard + existing badge logic
        is_live: isLive,
        demo_mode: !isLive,
        data_source: isLive ? 'live' : 'fallback',
        date: today,
        nifty: {
          current: normalized.nifty,
          open: normalized.nifty,
          high: normalized.nifty,
          low: normalized.nifty,
          volatility: 0.9,
          change: 0,
          change_percent: 0,
        },
        sensex: {
          current: normalized.sensex,
          open: normalized.sensex,
          high: normalized.sensex,
          low: normalized.sensex,
          volatility: 0.9,
          change: 0,
          change_percent: 0,
        },
        inr: {
          current: normalized.usdInr,
          open: normalized.usdInr,
          high: normalized.usdInr,
          low: normalized.usdInr,
          volatility: 0.2,
          change: 0,
          change_percent: 0,
        },
        note: snapshot?.sourceLabel,
      };
    };

    // Helper for safe fetching of simple axios-backed endpoints
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
    (async () => {
      try {
        console.log('Fetching market (safe)...');
        const snapshot = await getEconomicSnapshot();
        setMarketData(adaptSnapshotToDashboardShape(snapshot));
        setError(prev => ({ ...prev, market: null }));
      } catch (err) {
        // getEconomicSnapshot should never throw; keep UI resilient regardless.
        console.warn('Market fetch failed (unexpected):', err?.message || err);
        setMarketData(null);
        setError(prev => ({ ...prev, market: null }));
      } finally {
        setLoading(prev => ({ ...prev, market: false }));
      }
    })();
    // Forecast uses a custom wrapper that always returns data (live or simulated)
    (async () => {
      try {
        console.log('Fetching forecast (safe)...');
        const safe = await getSafeForecast();
        console.log('forecast Response:', safe);
        setForecastData(safe.data);
        setError(prev => ({ ...prev, forecast: null }));
      } catch (err) {
        // getSafeForecast should never throw, but guard just in case
        console.error('forecast Error (unexpected):', err);
        setError(prev => ({ ...prev, forecast: 'Unable to generate forecast' }));
      } finally {
        setLoading(prev => ({ ...prev, forecast: false }));
      }
    })();
    fetchData(getSentiment, setSentimentData, 'sentiment');
    fetchData(getStabilityScore, setStabilityData, 'stability');
  }, []);

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h1>Indian Economic Stability Dashboard</h1>
            <p>AI-Powered Predictive Framework utilizing Market Data, Sentiment Analysis, and Macroeconomic Indicators.</p>
          </div>
          <DataSourceBadge
            marketData={marketData}
            forecastData={forecastData}
            sentimentData={sentimentData}
            stabilityData={stabilityData}
          />
        </div>
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
        <p>
          &copy; {new Date().getFullYear()} Final Year Project. Data simulated/fetched for academic demonstration.
          {(marketData?.sample_data_date || forecastData?.sample_data_date || sentimentData?.sample_data_date || stabilityData?.sample_data_date) && (
            <span style={{ display: 'block', marginTop: '6px', fontSize: '0.85rem', color: '#78350F' }}>
              Sample data as of {(marketData?.sample_data_date || forecastData?.sample_data_date || sentimentData?.sample_data_date || stabilityData?.sample_data_date)}
            </span>
          )}
        </p>
      </footer>
    </div>
  );
};

export default Dashboard;
