const STORAGE_KEYS = {
  lastLiveSnapshot: 'esp:lastLiveMarketSnapshot:v1',
  monthlyBaseline: 'esp:marketBaselineMonthly:v1',
  niftyHistory: 'esp:niftyHistory:v1',
};

export const BASE_MARKET_LEVELS = {
  nifty: 22400,
  sensex: 73500,
  gold: 63000, // INR per 10g
  silver: 78000, // INR per kg
  crudeOil: 80, // USD
  usdInr: 83,
};

const VOLATILITY = {
  nifty: 1.2,
  sensex: 1.1,
  gold: 0.8,
  silver: 1.5,
  crudeOil: 2.0,
  usdInr: 0.4,
};

function safeJsonParse(raw) {
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function monthKey(d = new Date()) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  return `${y}-${m}`;
}

export function generateCloseToLive(base, volatilityPercent) {
  const b = Number(base);
  const v = Number(volatilityPercent);
  if (!Number.isFinite(b) || !Number.isFinite(v)) return null;
  const variation = b * (v / 100);
  const randomShift = (Math.random() - 0.5) * variation;
  return Math.round(b + randomShift);
}

function generateCloseToLiveFloat(base, volatilityPercent, decimals = 2) {
  const b = Number(base);
  const v = Number(volatilityPercent);
  if (!Number.isFinite(b) || !Number.isFinite(v)) return null;
  const variation = b * (v / 100);
  const randomShift = (Math.random() - 0.5) * variation;
  return Number((b + randomShift).toFixed(decimals));
}

function clamp(n, min, max) {
  if (!Number.isFinite(n)) return n;
  return Math.min(max, Math.max(min, n));
}

function normalizeBaseline(b) {
  const base = { ...BASE_MARKET_LEVELS, ...(b || {}) };
  return {
    nifty: clamp(Math.round(Number(base.nifty) || BASE_MARKET_LEVELS.nifty), 15000, 35000),
    sensex: clamp(Math.round(Number(base.sensex) || BASE_MARKET_LEVELS.sensex), 45000, 115000),
    gold: clamp(Math.round(Number(base.gold) || BASE_MARKET_LEVELS.gold), 35000, 95000),
    silver: clamp(Math.round(Number(base.silver) || BASE_MARKET_LEVELS.silver), 45000, 140000),
    crudeOil: clamp(Number(base.crudeOil) || BASE_MARKET_LEVELS.crudeOil, 35, 160),
    usdInr: clamp(Number(base.usdInr) || BASE_MARKET_LEVELS.usdInr, 65, 105),
  };
}

export function readLastLiveSnapshot() {
  if (typeof localStorage === 'undefined') return null;
  const raw = localStorage.getItem(STORAGE_KEYS.lastLiveSnapshot);
  const parsed = safeJsonParse(raw);
  if (!parsed || typeof parsed !== 'object') return null;
  if (!parsed.data || typeof parsed.data !== 'object') return null;
  return parsed;
}

export function writeLastLiveSnapshot(snapshot) {
  if (typeof localStorage === 'undefined') return;
  try {
    localStorage.setItem(
      STORAGE_KEYS.lastLiveSnapshot,
      JSON.stringify({
        ...snapshot,
        savedAt: new Date().toISOString(),
      })
    );
  } catch {
    // ignore quota / privacy mode
  }
}

export function getAdaptiveBaseline() {
  const nowMonth = monthKey();
  let baseline = null;

  if (typeof localStorage !== 'undefined') {
    const monthlyRaw = localStorage.getItem(STORAGE_KEYS.monthlyBaseline);
    const monthlyParsed = safeJsonParse(monthlyRaw);
    if (monthlyParsed && monthlyParsed.month === nowMonth && monthlyParsed.levels) {
      baseline = monthlyParsed.levels;
    }
  }

  // If we have a previously successful live snapshot, use it as baseline (monthly intelligence).
  const lastLive = readLastLiveSnapshot();
  const lastLiveMonth =
    lastLive?.lastUpdated ? monthKey(new Date(lastLive.lastUpdated)) : null;

  if (lastLive?.data && typeof lastLive.data === 'object') {
    // If month changed (or we never had one), refresh monthly baseline to stay aligned with trends.
    if (!baseline || (lastLiveMonth && lastLiveMonth !== nowMonth)) {
      baseline = lastLive.data;
      if (typeof localStorage !== 'undefined') {
        try {
          localStorage.setItem(
            STORAGE_KEYS.monthlyBaseline,
            JSON.stringify({ month: nowMonth, levels: baseline, updatedFrom: 'lastLive' })
          );
        } catch {
          // ignore
        }
      }
    }
  }

  return normalizeBaseline(baseline);
}

export function pushNiftyHistoryPoint(niftyValue) {
  const v = Number(niftyValue);
  if (!Number.isFinite(v) || v <= 0) return;
  if (typeof localStorage === 'undefined') return;

  const raw = localStorage.getItem(STORAGE_KEYS.niftyHistory);
  const parsed = safeJsonParse(raw);
  const arr = Array.isArray(parsed) ? parsed : [];

  arr.push({ date: new Date().toISOString().slice(0, 10), value: Math.round(v) });

  // Keep latest 10 points (enough for 5-day trend + buffer)
  const deduped = [];
  const seen = new Set();
  for (let i = arr.length - 1; i >= 0; i -= 1) {
    const p = arr[i];
    const k = `${p?.date}`;
    if (!p || !p.date || !Number.isFinite(p.value)) continue;
    if (seen.has(k)) continue;
    seen.add(k);
    deduped.push(p);
    if (deduped.length >= 10) break;
  }
  deduped.reverse();

  try {
    localStorage.setItem(STORAGE_KEYS.niftyHistory, JSON.stringify(deduped));
  } catch {
    // ignore
  }
}

export function readNiftyHistory() {
  if (typeof localStorage === 'undefined') return [];
  const raw = localStorage.getItem(STORAGE_KEYS.niftyHistory);
  const parsed = safeJsonParse(raw);
  return Array.isArray(parsed) ? parsed : [];
}

export function generateMarketAlignedFallback(customBaseLevels) {
  const base = normalizeBaseline(customBaseLevels || getAdaptiveBaseline());
  const data = {
    nifty: generateCloseToLive(base.nifty, VOLATILITY.nifty),
    sensex: generateCloseToLive(base.sensex, VOLATILITY.sensex),
    gold: generateCloseToLive(base.gold, VOLATILITY.gold),
    silver: generateCloseToLive(base.silver, VOLATILITY.silver),
    crudeOil: generateCloseToLiveFloat(base.crudeOil, VOLATILITY.crudeOil, 2),
    usdInr: generateCloseToLiveFloat(base.usdInr, VOLATILITY.usdInr, 2),
  };

  // Ensure decimals are preserved even if generator returned null
  data.usdInr = Number((Number(data.usdInr) || base.usdInr).toFixed(2));
  data.crudeOil = Number((Number(data.crudeOil) || base.crudeOil).toFixed(2));

  pushNiftyHistoryPoint(data.nifty);

  return {
    success: true,
    source: 'Fallback',
    data,
    lastUpdated: new Date().toISOString(),
  };
}

export default {
  BASE_MARKET_LEVELS,
  generateCloseToLive,
  getAdaptiveBaseline,
  generateMarketAlignedFallback,
  readLastLiveSnapshot,
  writeLastLiveSnapshot,
  readNiftyHistory,
  pushNiftyHistoryPoint,
};

