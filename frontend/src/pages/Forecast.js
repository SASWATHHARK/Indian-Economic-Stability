import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { getForecast } from '../services/api';
import './Forecast.css';

function Forecast() {
  const [forecastData, setForecastData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchForecast();
  }, []);

  const fetchForecast = async () => {
    try {
      const response = await getForecast();
      setForecastData(response.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch forecast');
      console.error('Error fetching forecast:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="forecast-page">
        <div className="container">
          <div className="loading-container">
            <div className="spinner"></div>
            <div className="loading-text">Generating 7-Day Market Forecast...</div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  if (!forecastData) {
    return <div className="error">No forecast data available</div>;
  }

  // Prepare chart data with safety checks
  const chartData = (forecastData.forecast || []).map(item => ({
    date: item.date ? new Date(item.date).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' }) : '',
    predicted: item.predicted,
    upper: item.upper !== undefined ? item.upper : item.upper_bound, // Handle both potential field names
    lower: item.lower !== undefined ? item.lower : item.lower_bound,
  }));

  const safeSummary = forecastData.summary || {};

  return (
    <div className="forecast-page">
      <div className="container">
        <h1 className="page-title">7-Day Market Forecast</h1>

        <div className="card">
          <h2>NIFTY 50 Forecast</h2>
          <p className="subtitle">
            Current Value: ₹{forecastData.current_value?.toLocaleString() || '--'} | 
            Forecast Score: {forecastData.forecast_score || '--'}%
          </p>

          <div className="chart-container">
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis domain={['auto', 'auto']} />
                <Tooltip formatter={(value) => `₹${value.toLocaleString()}`} />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="predicted" 
                  stroke="#4F46E5" 
                  strokeWidth={3}
                  name="Predicted"
                />
                <Line 
                  type="monotone" 
                  dataKey="upper" 
                  stroke="#82ca9d" 
                  strokeDasharray="5 5"
                  name="Upper Bound"
                />
                <Line 
                  type="monotone" 
                  dataKey="lower" 
                  stroke="#ffc658" 
                  strokeDasharray="5 5"
                  name="Lower Bound"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="forecast-summary">
            <h3>Forecast Summary</h3>
            <div className="summary-grid">
              <div className="summary-item">
                <span className="label">Trend:</span>
                <span className="value">{safeSummary.trend || '--'}</span>
              </div>
              <div className="summary-item">
                <span className="label">Average Confidence:</span>
                <span className="value">{safeSummary.avg_confidence ? safeSummary.avg_confidence.toFixed(1) : '--'}%</span>
              </div>
              <div className="summary-item">
                <span className="label">Volatility:</span>
                <span className="value">{safeSummary.volatility ? safeSummary.volatility.toFixed(2) : '--'}</span>
              </div>
            </div>
          </div>

          <div className="model-info">
            <h3>Model Information</h3>
            <ul>
              {/* Backend returns 'model' at top level, not in model_info object */}
              <li><strong>Model:</strong> {forecastData.model || 'Unknown'}</li>
              <li><strong>Note:</strong> {forecastData.note || '--'}</li>
            </ul>
          </div>
        </div>

        <div className="card">
          <h3>Forecast Details</h3>
          <div className="forecast-table">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Predicted Value</th>
                  <th>Lower Bound</th>
                  <th>Upper Bound</th>
                  <th>Confidence</th>
                </tr>
              </thead>
              <tbody>
                {(forecastData.forecast || []).map((item, idx) => (
                  <tr key={idx}>
                    <td>{item.date ? new Date(item.date).toLocaleDateString('en-IN') : '--'}</td>
                    <td>₹{item.predicted?.toLocaleString() || '--'}</td>
                    <td>₹{item.lower?.toLocaleString() || item.lower_bound?.toLocaleString() || '--'}</td>
                    <td>₹{item.upper?.toLocaleString() || item.upper_bound?.toLocaleString() || '--'}</td>
                    <td>{item.confidence ? item.confidence.toFixed(1) : '--'}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Forecast;

