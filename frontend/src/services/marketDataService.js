import { fetchLiveMarketData } from './liveMarketService';
import { generateMarketAlignedFallback } from './fallbackMarketGenerator';

const toFixedNumber = (value, decimals = 2) =>
  Number.parseFloat(Number(value || 0).toFixed(decimals));

function normalizeSnapshot(partial) {
  const base = partial || {};
  return {
    gold: toFixedNumber(base.gold, 0),
    silver: toFixedNumber(base.silver, 0),
    crudeOil: toFixedNumber(base.crudeOil, 2),
    usdInr: toFixedNumber(base.usdInr, 2),
    nifty: toFixedNumber(base.nifty, 0),
    sensex: toFixedNumber(base.sensex, 0),
  };
}

function buildResponse(payload) {
  const isLive = payload?.source === 'Live';
  return {
    success: true,
    source: isLive ? 'Live' : 'Fallback',
    sourceLabel: isLive ? 'Live Market Data' : 'Simulated (Market-Aligned)',
    data: normalizeSnapshot(payload?.data),
    lastUpdated: payload?.lastUpdated || new Date().toISOString(),
  };
}

/**
 * Public API used by the Economics page (and optionally Dashboard).
 *
 * Strategy:
 *  1) Try backend `/market-data`
 *  2) If that fails, try Yahoo Finance directly
 *  3) If everything fails, return offline sample constants
 *
 * This function NEVER throws – it always resolves to a structured response:
 * { success: true, data: {...}, source: "Live Data" | "Offline Sample Data", lastUpdated }
 */
export async function getEconomicSnapshot() {
  try {
    const liveOrFallback = await fetchLiveMarketData();
    return buildResponse(liveOrFallback);
  } catch (err) {
    // Defensive: the live service is already "never throw", but we still hard-guard.
    console.warn('Economic snapshot unexpected failure, forcing fallback:', err?.message || err);
    return buildResponse(generateMarketAlignedFallback());
  }
}

export default {
  getEconomicSnapshot,
};

