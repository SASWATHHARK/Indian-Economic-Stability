import React, { useState, useEffect } from 'react';
import { getMarketData } from '../services/api';
import MarketDashboard from '../components/MarketDashboard';
import './EconomicIndicators.css';

const EconomicIndicators = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const response = await getMarketData();
      setData(response.data);
      setError(null);
    } catch (err) {
      console.error("Economics Fetch Error:", err);
      setError(err.message || "Failed to load economic data");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="economics-page">
      <div className="container">
        <h1 className="page-title">Economic Indicators</h1>
        <p className="page-subtitle">
          Real-time tracking of Commodities, Forex, and Market Indices.
        </p>

        {/* Render MarketDashboard with showDetails=true to see ALL 6 cards */}
        <MarketDashboard 
          data={data} 
          loading={loading} 
          error={error} 
          showDetails={true} 
        />
        
        <div className="card info-card">
          <h3>Why these indicators?</h3>
          <ul className="indicator-list">
             <li><strong>Gold & Silver:</strong> Safe-haven assets that often rise during economic uncertainty/inflation.</li>
             <li><strong>Crude Oil:</strong> A key input for the Indian economy; high prices can increase the import bill and inflation.</li>
             <li><strong>USD/INR:</strong> Indicates the strength of the Rupee. A weaker Rupee affects imports and exports.</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default EconomicIndicators;
