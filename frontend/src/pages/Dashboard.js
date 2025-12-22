import React, { useState, useEffect } from 'react';
import { getMarketData, getStabilityScore } from '../services/api';
import StabilityGauge from '../components/StabilityGauge';
import './Dashboard.css';

function Dashboard() {
  const [marketData, setMarketData] = useState(null);
  const [stabilityData, setStabilityData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      // Fetch data separately to handle partial failures
      const results = await Promise.allSettled([
        getMarketData(),
        getStabilityScore()
      ]);
      
      // Handle market data
      if (results[0].status === 'fulfilled') {
        setMarketData(results[0].value.data);
      } else {
        console.error('Market data error:', results[0].reason);
      }
      
      // Handle stability score
      if (results[1].status === 'fulfilled') {
        setStabilityData(results[1].value.data);
      } else {
        console.error('Stability score error:', results[1].reason);
        // Show specific error if stability score fails
        const errorDetail = results[1].reason?.response?.data?.detail || results[1].reason?.message;
        if (errorDetail && errorDetail.includes('historical data')) {
          setError('Stability score unavailable: Forecast data not available. Market data may still be shown below.');
        } else if (errorDetail) {
          setError(`Stability score error: ${errorDetail}`);
        }
      }
      
      // Only show error if BOTH failed
      if (results[0].status === 'rejected' && results[1].status === 'rejected') {
        let errorMessage = 'Failed to fetch data';
        const firstError = results[0].reason;
        
        if (firstError.code === 'ECONNREFUSED' || firstError.message?.includes('Network Error')) {
          errorMessage = 'Backend server is not running. Please start the backend server on port 8000.';
        } else if (firstError.response?.data?.detail) {
          errorMessage = firstError.response.data.detail;
        } else if (firstError.message) {
          errorMessage = firstError.message;
        }
        
        setError(errorMessage);
      } else {
        // Clear error if at least one succeeded
        setError(null);
      }
    } catch (err) {
      // Fallback error handling
      let errorMessage = 'Failed to fetch data';
      
      if (err.code === 'ECONNREFUSED' || err.message.includes('Network Error')) {
        errorMessage = 'Backend server is not running. Please start the backend server on port 8000.';
      } else if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading dashboard data...</div>;
  }

  // Show error banner if there's an error, but still show available data
  const showErrorBanner = error && !marketData && !stabilityData;
  
  if (showErrorBanner) {
    return (
      <div className="dashboard">
        <div className="container">
          <div className="error" style={{
            padding: '20px',
            background: '#fee',
            border: '1px solid #f44336',
            borderRadius: '8px',
            margin: '20px 0'
          }}>
            <h2 style={{ color: '#f44336', marginTop: 0 }}>⚠️ Connection Error</h2>
            <p style={{ color: '#c33', marginBottom: '15px' }}>{error}</p>
            
            <div style={{
              background: '#fff3cd',
              padding: '15px',
              borderRadius: '8px',
              borderLeft: '4px solid #ffc107',
              marginTop: '20px'
            }}>
              <h3 style={{ marginTop: 0, color: '#856404' }}>Troubleshooting Steps:</h3>
              <ol style={{ color: '#856404', lineHeight: '1.8' }}>
                <li><strong>Check if backend is running:</strong>
                  <ul>
                    <li>Open a terminal/command prompt</li>
                    <li>Navigate to: <code>cd backend</code></li>
                    <li>Activate virtual environment: <code>venv\Scripts\activate</code> (Windows) or <code>source venv/bin/activate</code> (Mac/Linux)</li>
                    <li>Run: <code>python main.py</code></li>
                    <li>You should see: "Uvicorn running on http://0.0.0.0:8000"</li>
                  </ul>
                </li>
                <li><strong>Verify backend is accessible:</strong>
                  <ul>
                    <li>Open browser and go to: <a href="http://localhost:8000/health" target="_blank" rel="noopener noreferrer">http://localhost:8000/health</a></li>
                    <li>You should see: {"{"}"status": "healthy"{"}"}</li>
                  </ul>
                </li>
                <li><strong>Check API URL:</strong>
                  <ul>
                    <li>Current API URL: <code>{process.env.REACT_APP_API_URL || 'http://localhost:8000'}</code></li>
                    <li>If backend runs on different port, create <code>.env</code> file in frontend folder with: <code>REACT_APP_API_URL=http://localhost:YOUR_PORT</code></li>
                  </ul>
                </li>
                <li><strong>Restart frontend:</strong>
                  <ul>
                    <li>Stop the frontend (Ctrl+C)</li>
                    <li>Restart: <code>npm start</code></li>
                  </ul>
                </li>
              </ol>
            </div>
            
            <button 
              onClick={fetchData}
              style={{
                marginTop: '20px',
                padding: '10px 20px',
                background: '#667eea',
                color: 'white',
                border: 'none',
                borderRadius: '5px',
                cursor: 'pointer',
                fontSize: '16px'
              }}
            >
              🔄 Retry Connection
            </button>
          </div>
        </div>
      </div>
    );
  }

  const getBadgeClass = (category) => {
    if (category === 'Stable') return 'badge-stable';
    if (category === 'Moderate') return 'badge-moderate';
    return 'badge-unstable';
  };

  return (
    <div className="dashboard">
      <div className="container">
        <h1 className="page-title">Economic Stability Dashboard</h1>
        
        {/* Show warning if stability score failed but market data is available */}
        {error && (marketData || stabilityData) && (
          <div className="card" style={{
            background: '#fff3cd',
            borderLeft: '4px solid #ffc107',
            marginBottom: '20px'
          }}>
            <h3 style={{ color: '#856404', marginTop: 0 }}>⚠️ Partial Data Available</h3>
            <p style={{ color: '#856404' }}>{error}</p>
            <p style={{ color: '#856404', fontSize: '14px', marginTop: '10px' }}>
              Some data may be unavailable. The information shown below is what we could retrieve.
            </p>
          </div>
        )}
        
        {/* Stability Score Section */}
        {stabilityData && (
          <div className="card">
            <h2>
              Economic Stability Score
              <span className={`success-badge ${getBadgeClass(stabilityData.category)}`}>
                {stabilityData.category}
              </span>
            </h2>
            <StabilityGauge 
              score={stabilityData.stability_score} 
              category={stabilityData.category}
            />
            <p className="interpretation">{stabilityData.interpretation}</p>
            
            <div className="breakdown">
              <h3>Score Breakdown</h3>
              <div className="breakdown-grid">
                <div className="breakdown-item">
                  <span className="label">Market Trend:</span>
                  <span className="value">{stabilityData.components.market_trend}%</span>
                </div>
                <div className="breakdown-item">
                  <span className="label">Sentiment:</span>
                  <span className="value">{stabilityData.components.sentiment}%</span>
                </div>
                <div className="breakdown-item">
                  <span className="label">Economic Indicators:</span>
                  <span className="value">{stabilityData.components.economic_indicators}%</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Market Data Section */}
        {marketData && (
          <div className="card">
            <h2>Market Summary - {marketData.date}</h2>
            <div className="stats-grid">
              <div className="stat-card">
                <h3>NIFTY 50</h3>
                <div className="value">₹{marketData.nifty.current.toLocaleString()}</div>
                <div className={`change ${marketData.nifty.change >= 0 ? 'positive' : 'negative'}`}>
                  {marketData.nifty.change >= 0 ? '↑' : '↓'} 
                  {Math.abs(marketData.nifty.change_percent).toFixed(2)}%
                </div>
                <div className="details">
                  High: ₹{marketData.nifty.high.toLocaleString()} | 
                  Low: ₹{marketData.nifty.low.toLocaleString()}
                </div>
              </div>
              
              <div className="stat-card">
                <h3>SENSEX</h3>
                <div className="value">₹{marketData.sensex.current.toLocaleString()}</div>
                <div className={`change ${marketData.sensex.change >= 0 ? 'positive' : 'negative'}`}>
                  {marketData.sensex.change >= 0 ? '↑' : '↓'} 
                  {Math.abs(marketData.sensex.change_percent).toFixed(2)}%
                </div>
                <div className="details">
                  High: ₹{marketData.sensex.high.toLocaleString()} | 
                  Low: ₹{marketData.sensex.low.toLocaleString()}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Disclaimer */}
        <div className="card disclaimer">
          <h3>⚠️ Important Disclaimer</h3>
          <p>
            This system is an advisory tool for understanding economic trends. 
            It is not financial advice. Predictions are probabilistic and market 
            conditions can change rapidly. Always consult with financial experts 
            before making investment decisions.
          </p>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;

