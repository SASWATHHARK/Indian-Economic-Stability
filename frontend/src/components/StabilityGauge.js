import React from 'react';
import './StabilityGauge.css';

function StabilityGauge({ score, category }) {
  // Calculate rotation for gauge (0-180 degrees for 0-100 score)
  const rotation = (score / 100) * 180;
  
  // Determine color based on category
  const getColor = () => {
    if (category === 'Stable') return '#4caf50';
    if (category === 'Moderate') return '#ff9800';
    return '#f44336';
  };

  return (
    <div className="gauge-container">
      <div className="gauge">
        <div 
          className="gauge-circle"
          style={{
            borderTopColor: getColor(),
            borderRightColor: score > 50 ? getColor() : '#e0e0e0',
            transform: `rotate(${rotation - 90}deg)`,
          }}
        />
        <div className="gauge-value">{score.toFixed(1)}</div>
        <div className="gauge-label">{category}</div>
      </div>
    </div>
  );
}

export default StabilityGauge;

