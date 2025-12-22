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
    return <div className="loading">Generating forecast...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  if (!forecastData) {
    return <div className="error">No forecast data available</div>;
  }

  // Prepare chart data
  const chartData = forecastData.forecast.map(item => ({
    date: new Date(item.date).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' }),
    predicted: item.predicted,
    upper: item.upper_bound,
    lower: item.lower_bound,
  }));

  return (
    <div className="forecast-page">
      <div className="container">
        <h1 className="page-title">7-Day Market Forecast</h1>

        <div className="card">
          <h2>NIFTY 50 Forecast</h2>
          <p className="subtitle">
            Current Value: ₹{forecastData.current_value.toLocaleString()} | 
            Forecast Score: {forecastData.forecast_score}%
          </p>

          <div className="chart-container">
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip formatter={(value) => `₹${value.toLocaleString()}`} />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="predicted" 
                  stroke="#667eea" 
                  strokeWidth={2}
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
                <span className="value">{forecastData.summary.trend}</span>
              </div>
              <div className="summary-item">
                <span className="label">Average Confidence:</span>
                <span className="value">{forecastData.summary.avg_confidence.toFixed(1)}%</span>
              </div>
              <div className="summary-item">
                <span className="label">Volatility:</span>
                <span className="value">{forecastData.summary.volatility.toFixed(2)}</span>
              </div>
            </div>
          </div>

          <div className="model-info">
            <h3>Model Information</h3>
            <ul>
              <li><strong>Model:</strong> {forecastData.model_info.model}</li>
              <li><strong>Training Period:</strong> {forecastData.model_info.training_period}</li>
              <li><strong>Forecast Horizon:</strong> {forecastData.model_info.forecast_horizon}</li>
            </ul>
            <p className="note">{forecastData.model_info.note}</p>
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
                {forecastData.forecast.map((item, idx) => (
                  <tr key={idx}>
                    <td>{new Date(item.date).toLocaleDateString('en-IN')}</td>
                    <td>₹{item.predicted.toLocaleString()}</td>
                    <td>₹{item.lower_bound.toLocaleString()}</td>
                    <td>₹{item.upper_bound.toLocaleString()}</td>
                    <td>{item.confidence.toFixed(1)}%</td>
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

