import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import './MarketForecast.css';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    const dataPoint = payload[0].payload;
    return (
      <div className="custom-tooltip" style={{ background: '#fff', padding: '10px', border: '1px solid #ccc' }}>
        <p className="label">{`Date: ${label}`}</p>
        <p className="intro" style={{ color: '#8884d8' }}>
            {`Predicted: ₹${dataPoint.predicted}`}
        </p>
        {dataPoint.upper !== undefined && (
          <p className="intro" style={{ color: '#82ca9d' }}>{`Upper: ₹${dataPoint.upper}`}</p>
        )}
        {dataPoint.lower !== undefined && (
           <p className="intro" style={{ color: '#ff7300' }}>{`Lower: ₹${dataPoint.lower}`}</p>
        )}
        {dataPoint.confidence !== undefined && (
           <p className="intro" style={{ fontWeight: 'bold' }}>{`Confidence: ${dataPoint.confidence}%`}</p>
        )}
      </div>
    );
  }
  return null;
};

const MarketForecast = ({ data, loading, error }) => {
  // Console log before rendering
  if (data) {
    console.log("MarketForecast Data:", data);
  }

  if (loading) return <div className="card loading">Loading Forecast...</div>;
  if (error) return <div className="card error">Error: {error}</div>;
  
  if (!data || !data.forecast || data.forecast.length === 0) {
    return <div className="card no-data">No forecast data available</div>;
  }

  const { forecast, current_value, forecast_score, summary, note } = data;

  const currentVal = current_value !== undefined ? current_value : '--';
  const score = forecast_score !== undefined ? forecast_score : '--';
  const summaryTrend = summary?.trend || "Forecast created";

  return (
    <div className="card forecast-card">
      <h3 className="card-title">7-Day Market Forecast (NIFTY 50)</h3>
      
      <div className="forecast-summary">
        <div className="metric">
          <span className="label">Current Value</span>
          <span className="value">₹{currentVal.toLocaleString()}</span>
        </div>
        <div className="metric">
          <span className="label">Forecast Score</span>
          <span className="value score">{score}</span>
        </div>
      </div>
      
      <p className="summary-text">Trend: {summaryTrend}</p>

      <div className="chart-container">
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={forecast} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tick={{fontSize: 12}} />
            <YAxis domain={['auto', 'auto']} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Line type="monotone" dataKey="predicted" stroke="#8884d8" name="Predicted" strokeWidth={2} activeDot={{ r: 8 }} />
            <Line type="monotone" dataKey="upper" stroke="#82ca9d" name="Upper CI" strokeDasharray="5 5" />
            <Line type="monotone" dataKey="lower" stroke="#ff7300" name="Lower CI" strokeDasharray="5 5" />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <small className="note">{note || "AI-generated prediction"}</small>
    </div>
  );
};

export default MarketForecast;
