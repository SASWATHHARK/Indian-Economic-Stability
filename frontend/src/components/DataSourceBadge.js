import React from 'react';
import './DataSourceBadge.css';

/**
 * Shows "Live Data" (green) or "Demo Mode" (yellow) based on API response.
 * Use: <DataSourceBadge dataSource="live" demoMode={false} />
 * Or pass any response: <DataSourceBadge marketData={...} stabilityData={...} />
 */
const DataSourceBadge = ({ dataSource, demoMode, marketData, forecastData, sentimentData, stabilityData }) => {
  let isOffline = demoMode === true || dataSource === 'offline_sample' || dataSource === 'fallback';
  let sampleDate = null;
  const sources = [marketData, forecastData, sentimentData, stabilityData].filter(Boolean);
  if (isOffline === undefined && sources.length) {
    const d = sources[0];
    isOffline =
      d.demo_mode === true ||
      d.data_source === 'offline_sample' ||
      d.data_source === 'fallback' ||
      d.is_live === false;
  }
  if (isOffline && sources.length) {
    sampleDate = sources.find(s => s.sample_data_date)?.sample_data_date;
  }

  return (
    <div
      className={`data-source-badge ${isOffline ? 'demo' : 'live'}`}
      title={isOffline ? (sampleDate ? `Sample data as of ${sampleDate}` : 'Using offline sample data') : 'Using live API data'}
    >
      <span className="data-source-dot" />
      {isOffline ? (
        <>
          Demo Mode
          {sampleDate && <span className="sample-date"> • Data as of {sampleDate}</span>}
        </>
      ) : (
        'Live Data'
      )}
    </div>
  );
};

export default DataSourceBadge;
