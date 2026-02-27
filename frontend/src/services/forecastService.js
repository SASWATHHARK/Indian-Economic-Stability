import { getForecast } from './api';
import { getEconomicSnapshot } from './marketDataService';
import { getAdaptiveBaseline, readNiftyHistory } from './fallbackMarketGenerator';

function safeNumber(x) {
  const n = Number(x);
  return Number.isFinite(n) ? n : null;
}

function randomBetween(min, max) {
  return min + Math.random() * (max - min);
}

function computeTrendFactor(historyPoints) {
  const pts = Array.isArray(historyPoints) ? historyPoints : [];
  const values = pts.map((p) => safeNumber(p?.value)).filter((v) => v && v > 0);
  if (values.length >= 2) {
    const today = values[values.length - 1];
    const yesterday = values[values.length - 2];
    return (today - yesterday) / yesterday;
  }
  return 0;
}

function computeVolatilityScore(historyPoints) {
  const pts = Array.isArray(historyPoints) ? historyPoints : [];
  const values = pts.map((p) => safeNumber(p?.value)).filter((v) => v && v > 0);
  if (values.length < 3) return 0;
  const rets = [];
  for (let i = 1; i < values.length; i += 1) {
    rets.push((values[i] - values[i - 1]) / values[i - 1]);
  }
  const mean = rets.reduce((a, b) => a + b, 0) / rets.length;
  const variance =
    rets.reduce((acc, r) => acc + (r - mean) * (r - mean), 0) / rets.length;
  return Math.sqrt(variance);
}

/**
 * Generate a synthetic NIFTY 7‑day forecast so charts always have data.
 * Keeps numbers realistic while adding small random variation.
 */
export function generateSyntheticForecast(baseValue, days = 7, historyPoints = []) {
  const today = new Date();
  let base = safeNumber(baseValue) || getAdaptiveBaseline().nifty;
  const out = [];

  const trendFactor = computeTrendFactor(historyPoints);
  const volatilityScore = computeVolatilityScore(historyPoints);
  const volatilityFactor = 0.008 + Math.min(0.01, volatilityScore); // base + score

  for (let i = 1; i <= days; i += 1) {
    const predicted =
      base * (1 + trendFactor + randomBetween(-volatilityFactor, volatilityFactor));
    const upper = predicted * 1.01;
    const lower = predicted * 0.99;
    const confidence = 65 + Math.random() * 15;

    const d = new Date(today);
    d.setDate(d.getDate() + i);

    out.push({
      date: d.toISOString().slice(0, 10),
      predicted: Number(predicted.toFixed(2)),
      lower: Number(lower.toFixed(2)),
      upper: Number(upper.toFixed(2)),
      confidence: Number(confidence.toFixed(1)),
    });

    base = predicted;
  }

  return out;
}

/**
 * Safe forecast fetcher used by Dashboard + Forecast page.
 * Never throws; always returns:
 * { success: true, data: {...}, source: "Live" | "Offline" }
 */
export async function getSafeForecast() {
  let raw = null;
  let source = 'Live';

  try {
    const res = await getForecast();
    raw = res?.data || null;
  } catch (err) {
    console.warn('Forecast API failed, using simulated forecast:', err?.message || err);
    source = 'Offline';
  }

  const hasLiveForecastArray =
    raw && Array.isArray(raw.forecast) && raw.forecast.length > 0;

  let baseValue =
    (raw && typeof raw.current_value === 'number' && raw.current_value) || null;

  if (!baseValue) {
    try {
      const snap = await getEconomicSnapshot();
      baseValue = snap?.data?.nifty || null;
    } catch {
      baseValue = null;
    }
  }
  if (!baseValue) {
    baseValue = getAdaptiveBaseline().nifty;
  }

  let forecast = hasLiveForecastArray ? raw.forecast : [];

  // If API did not return a usable forecast array, synthesize one
  if (!forecast || forecast.length === 0) {
    forecast = generateSyntheticForecast(baseValue, 7, readNiftyHistory());
    source = 'Offline';
  }

  const data = {
    ...(raw || {}),
    forecast,
    current_value: baseValue,
    note:
      (raw && raw.note) ||
      (source === 'Offline'
        ? 'Simulated, market-aligned forecast (offline mode).'
        : 'AI-generated prediction'),
    // Helpful flag for UI badges
    simulated: source === 'Offline',
  };

  return {
    success: true,
    data,
    source,
  };
}

export default {
  getSafeForecast,
  generateSyntheticForecast,
};

