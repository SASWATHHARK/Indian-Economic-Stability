import React, { useState, useEffect } from 'react';
import MarketDashboard from '../components/MarketDashboard';
import { getEconomicSnapshot } from '../services/marketDataService';
import './EconomicIndicators.css';

const EconomicIndicators = () => {
  const [snapshot, setSnapshot] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    async function load() {
      try {
        const result = await getEconomicSnapshot();
        if (!isMounted) return;
        setSnapshot(result);
      } finally {
        // Service never throws and always returns a structured response,
        // so we do not surface errors to the UI here.
        if (isMounted) setLoading(false);
      }
    }

    load();
    return () => {
      isMounted = false;
    };
  }, []);

  const normalized = snapshot?.data || null;
  const isLive = snapshot?.source === 'Live';

  // Adapt the lightweight economics snapshot into the richer shape
  // expected by MarketDashboard (nifty/sensex/commodities objects).
  const marketDashboardData = normalized
    ? {
        is_live: isLive,
        date: new Date(snapshot.lastUpdated).toISOString().slice(0, 10),
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
        gold: {
          current: normalized.gold,
          open: normalized.gold,
          high: normalized.gold,
          low: normalized.gold,
          volatility: 0.7,
          change: 0,
          change_percent: 0,
        },
        silver: {
          current: normalized.silver,
          open: normalized.silver,
          high: normalized.silver,
          low: normalized.silver,
          volatility: 1.1,
          change: 0,
          change_percent: 0,
        },
        oil: {
          current: normalized.crudeOil,
          open: normalized.crudeOil,
          high: normalized.crudeOil,
          low: normalized.crudeOil,
          volatility: 1.8,
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
        note:
          snapshot?.sourceLabel ||
          (isLive ? 'Live market snapshot' : 'Offline simulated snapshot'),
      }
    : null;

  return (
    <div className="economics-page">
      <div className="container">
        <div className="economics-header-row">
          <div>
            <h1 className="page-title">Economic Indicators</h1>
            <p className="page-subtitle">
              Real-time tracking of Commodities, Forex, and Market Indices.
            </p>
          </div>

          {snapshot && (
            <div
              className={`economics-badge ${
                isLive ? 'live' : 'simulated'
              }`}
            >
              <span className="economics-badge-dot" />
              {isLive ? 'Live Market Data' : 'Simulated (Market-Aligned)'}
            </div>
          )}
        </div>

        {/* Reuse MarketDashboard visuals with adapted economics snapshot.
            We never pass an error state so the card always renders. */}
        <MarketDashboard
          data={marketDashboardData}
          loading={loading}
          error={null}
          showDetails={true}
        />

        <div className="card info-card">
          <h3>Why these indicators?</h3>
          <ul className="indicator-list">
            <li>
              <strong>Gold &amp; Silver:</strong> Safe-haven assets that often
              rise during economic uncertainty and inflation.
            </li>
            <li>
              <strong>Crude Oil:</strong> A key input for the Indian economy;
              high prices can increase the import bill and domestic inflation.
            </li>
            <li>
              <strong>USD/INR:</strong> Indicates the strength of the Rupee. A
              weaker Rupee affects imports, exports, and external debt.
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default EconomicIndicators;

