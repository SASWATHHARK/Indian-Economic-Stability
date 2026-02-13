import React from 'react';
import './MarketDashboard.css';

const MarketDashboard = ({ data, loading, error, showDetails = false }) => {
  if (loading) return (
    <div className="card loading">
      <div className="spinner"></div>
      <div className="loading-text">Fetching Market Data...</div>
    </div>
  );
  if (error) return <div className="card error">Error loading market data: {error}</div>;
  
  // Guard clause for data
  if (!data) {
    return (
      <div className="card error">
        Market data unavailable.
      </div>
    );
  }

  const renderMarketCard = (title, marketData, type = 'standard') => {
    // Extra safety for individual fields
    if (!marketData) return null;

    const { current, open, high, low, volatility, change, change_percent } = marketData;
    const isPositive = change >= 0;

    // --- UNIT CONVERSION & LOCALIZATION ---
    const inrRate = data.inr?.current || 89.20;
    const taxFactor = 1.22; // ~22% for Import Duty (15%) + GST (3%) + Premium
    
    let displayPrice = current;
    let displayUnit = title.includes("USD") || title.includes("Oil") ? '$' : '₹';
    let subInfo = null;

    if (title.includes("Gold")) {
        // Gold Standard: INR per 10 Grams (24K)
        // Formula: (USD/oz * INR) / 31.1035 * 10 * Tax
        const perGram = ((current * inrRate) / 31.1035) * taxFactor;
        const per10g = perGram * 10;
        const perSov = perGram * 8;
        
        displayPrice = Math.round(per10g); // Main Hero Price (10g)
        displayUnit = '₹';
        
        subInfo = (
          <div className="indian-price-grid" style={{ background: '#FFFBEB', padding: '8px', borderRadius: '6px', marginBottom: '10px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '6px' }}>
                <div className="local-metric">
                   <span className="label" style={{ fontSize: '0.75rem', color: '#92400E' }}>10 Grams (24K)</span>
                   <div className="val" style={{ fontWeight: '700', color: '#B45309', fontSize: '1.1rem' }}>₹{displayPrice.toLocaleString()}</div>
                </div>
                <div className="local-metric">
                   <span className="label" style={{ fontSize: '0.75rem', color: '#92400E' }}>1 Sovereign (8g)</span>
                   <div className="val" style={{ fontWeight: '700', color: '#B45309' }}>₹{Math.round(perSov).toLocaleString()}</div>
                </div>
              </div>
              <div className="local-metric" style={{ borderTop: '1px solid #FCD34D', paddingTop: '4px' }}>
                 <span className="label" style={{ fontSize: '0.7rem', color: '#78350F' }}>Global Spot (Raw)</span>
                 <div className="val" style={{ fontWeight: '600', color: '#92400E' }}>${current.toLocaleString()} / oz</div>
              </div>
          </div>
        );
    } else if (title.includes("Silver")) {
        // Silver Standard: INR per 1 Kg
        const perGram = ((current * inrRate) / 31.1035) * taxFactor;
        const perKg = perGram * 1000;
        
        displayPrice = Math.round(perGram); // Main Hero Price (1 Gram - Users relate to this or Kg)
        // User asked specifically about "1 gram is ...". Let's show 1 Gram as Hero or per Kg?
        // Traditionally per Kg is the market quote, but user engaged on 1g. Let's show 1g Hero.
        displayUnit = '₹';
        
        subInfo = (
          <div className="indian-price-grid" style={{ background: '#F3F4F6', padding: '8px', borderRadius: '6px', marginBottom: '10px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '6px' }}>
                <div className="local-metric">
                   <span className="label" style={{ fontSize: '0.75rem', color: '#374151' }}>1 Gram</span>
                   <div className="val" style={{ fontWeight: '700', color: '#1F2937', fontSize: '1.1rem' }}>₹{perGram.toFixed(1)}</div>
                </div>
                <div className="local-metric">
                   <span className="label" style={{ fontSize: '0.75rem', color: '#374151' }}>1 Kilogram</span>
                   <div className="val" style={{ fontWeight: '700', color: '#1F2937' }}>₹{Math.round(perKg).toLocaleString()}</div>
                </div>
              </div>
              <div className="local-metric" style={{ borderTop: '1px solid #D1D5DB', paddingTop: '4px' }}>
                 <span className="label" style={{ fontSize: '0.7rem', color: '#4B5563' }}>Global Spot (Raw)</span>
                 <div className="val" style={{ fontWeight: '600', color: '#374151' }}>${current.toLocaleString()} / oz</div>
              </div>
          </div>
        );
    } // else standard

    return (
      <div className="market-card">
        <h4>{title.replace("(Global Spot)", "")} {title.includes("Gold") ? "(India 24K)" : title.includes("Silver") ? "(India)" : ""}</h4>
        <div className="price-row">
          <span className="current-price">
            {displayUnit}{displayPrice.toLocaleString()}
          </span>
          {change !== undefined && (
            <span className={`change ${isPositive ? 'positive' : 'negative'}`}>
              {isPositive ? '▲' : '▼'} {Math.abs(change).toFixed(2)} ({change_percent}%)
            </span>
          )}
        </div>

        {/* Localized Info Block */}
        {subInfo}

        <div className="metrics-grid">
          <div className="metric-item">
            <span className="label">Open</span>
            <span className="val">{title.includes("USD") || title.includes("Oil") ? '$' : '₹'}{open?.toLocaleString() || '--'}</span>
          </div>
          <div className="metric-item">
            <span className="label">High</span>
            <span className="val">{title.includes("USD") || title.includes("Oil") ? '$' : '₹'}{high?.toLocaleString() || '--'}</span>
          </div>
          <div className="metric-item">
            <span className="label">Low</span>
            <span className="val">{title.includes("USD") || title.includes("Oil") ? '$' : '₹'}{low?.toLocaleString() || '--'}</span>
          </div>
          <div className="metric-item">
            <span className="label">Volatility</span>
            <span className="val">{volatility?.toFixed(2) || '--'}%</span>
          </div>
        </div>
        
        {/* Historical Returns Section (For Gold/Silver) */}
        {marketData.history && (
          <div className="history-grid" style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px dashed #e5e7eb', display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px' }}>
             <div className="metric-item">
                <span className="label">1 Mo</span>
                <span className="val" style={{ color: '#16A34A', fontSize: '0.9rem' }}>+{marketData.history['1mo']}%</span>
             </div>
             <div className="metric-item">
                <span className="label">1 Yr</span>
                <span className="val" style={{ color: '#16A34A', fontSize: '0.9rem' }}>+{marketData.history['1y']}%</span>
             </div>
             <div className="metric-item">
                <span className="label">5 Yr</span>
                <span className="val" style={{ color: '#16A34A', fontSize: '0.9rem' }}>+{marketData.history['5y']}%</span>
             </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="card market-overview-parent">
      <div className="market-header-row" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div className="market-header" style={{ margin: 0 }}>
          {showDetails ? "Detailed Economic Indicators" : "Market Overview"}
          <span style={{ display: 'block', fontSize: '0.75rem', color: '#666', fontWeight: '400', marginTop: '4px' }}>
             Auto-updates: Market Close (3:30 PM IST)
          </span>
        </div>
        {data.is_live !== undefined && (
          <div className={`status-badge ${data.is_live ? 'live' : 'simulated'}`} 
               style={{ 
                 padding: '4px 12px', 
                 borderRadius: '20px', 
                 fontSize: '0.85rem', 
                 fontWeight: '600',
                 backgroundColor: data.is_live ? '#DCFCE7' : '#FEF3C7',
                 color: data.is_live ? '#166534' : '#92400E',
                 display: 'flex',
                 alignItems: 'center',
                 gap: '6px'
               }}>
            <span style={{ 
              width: '8px', 
              height: '8px', 
              borderRadius: '50%', 
              backgroundColor: data.is_live ? '#16A34A' : '#F59E0B',
              animation: data.is_live ? 'pulse 2s infinite' : 'none'
            }}></span>
            {data.is_live ? 'Live Data' : 'Simulated Data'}
          </div>
        )}
      </div>
      <div className="market-cards-container">
        {renderMarketCard('NIFTY 50', data.nifty)}
        {renderMarketCard('SENSEX', data.sensex)}
        
        {showDetails && (
          <>
            {renderMarketCard('Gold (Global Spot)', data.gold)}
            {renderMarketCard('Silver (Global Spot)', data.silver)}
            {renderMarketCard('Crude Oil (WTI)', data.oil)}
            {renderMarketCard('USD / INR', data.inr)}
          </>
        )}
      </div>
      <div className="market-footer">
        Data Sources: NSE, BSE, COMEX via Yahoo Finance • Last Updated: {data.date || new Date().toLocaleDateString()}
        {data.is_live === false && data.note && (
          <span style={{ display: 'block', marginTop: '6px', color: '#92400E', fontSize: '0.85rem' }}>
            {data.note}
          </span>
        )}
      </div>
    </div>
  );
};

export default MarketDashboard;
