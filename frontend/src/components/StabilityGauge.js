import React from 'react';
import './StabilityGauge.css';

function StabilityGauge({ data, loading, error }) {
  // Console log before rendering as required
  if (data) {
    console.log("StabilityGauge Data:", data);
  }

  if (loading) return <div className="card loading">Calculating Stability...</div>;
  
  // Show error if failed, but if we have partial data we might want to render?
  // User asked to "Show loading state instead of error if delayed".
  // Note: If error exists but loading is false, it's failed.
  if (error) return <div className="card error">Error: {error}</div>;
  if (!data) return <div className="card no-data">Stability data unavailable</div>;

  // STRICT MAPPING
  const { stability_score, category, interpretation, components } = data;
  
  // Safety check
  if (stability_score === undefined || stability_score === null) {
     return <div className="card error">Invalid Data: Missing stability_score</div>;
  }
  
  // Rotation: 0 to 180 degrees
  const rotation = (stability_score / 100) * 180;

  const getColor = (cat) => {
    const c = cat ? cat.toLowerCase() : '';
    if (c === 'stable') return '#4caf50'; 
    if (c === 'moderate') return '#ff9800'; 
    return '#f44336'; 
  };

  const color = getColor(category);

  return (
    <div className="card stability-card">
      <h3 className="card-title">Economic Stability Score</h3>
      
      <div className="gauge-container">
        <div className="gauge">
          <svg viewBox="0 0 200 100" className="gauge-svg">
            <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#e0e0e0" strokeWidth="20" />
            <path 
              d="M 20 100 A 80 80 0 0 1 180 100" 
              fill="none" 
              stroke={color} 
              strokeWidth="20" 
              strokeDasharray={251.2} 
              strokeDashoffset={251.2 * (1 - stability_score / 100)}
            />
          </svg>
          <div className="gauge-overlay">
            <div className="gauge-value" style={{ color }}>{stability_score.toFixed(1)}</div>
            <div className={`gauge-badge ${category ? category.toLowerCase() : 'unknown'}`}>
              {category || 'Unknown'}
            </div>
          </div>
        </div>
      </div>

      <div className="interpretation-box">
        <p>{interpretation}</p>
      </div>

      {components && (
        <div className="components-list">
          <h4>Score Components</h4>
          <div className="component-item">
            <div className="component-label-row">
                <span>Market Trend</span>
                <span className="component-pct">{components.market_trend}%</span>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${components.market_trend}%`, background: '#2196f3' }}
              ></div>
            </div>
          </div>
          <div className="component-item">
            <div className="component-label-row">
                <span>Sentiment</span>
                <span className="component-pct">{components.sentiment}%</span>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${components.sentiment}%`, background: '#9c27b0' }}
              ></div>
            </div>
          </div>
          <div className="component-item">
            <div className="component-label-row">
                <span>Economic Indicators</span>
                <span className="component-pct">{components.economic_indicators}%</span>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${components.economic_indicators}%`, background: '#009688' }}
              ></div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default StabilityGauge;
