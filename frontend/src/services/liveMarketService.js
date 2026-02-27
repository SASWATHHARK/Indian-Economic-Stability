import {
  generateMarketAlignedFallback,
  pushNiftyHistoryPoint,
  writeLastLiveSnapshot,
} from './fallbackMarketGenerator';

const OUNCE_IN_GRAMS = 31.1035;
const GOLD_TAX_FACTOR = 1.22; // import duty + GST + premium approximation

const YAHOO_SYMBOLS = {
  nifty: '^NSEI',
  sensex: '^BSESN',
  gold: 'GC=F',
  silver: 'SI=F',
  crudeOil: 'CL=F',
  usdInr: 'INR=X',
};

function toNumber(x) {
  const n = Number(x);
  return Number.isFinite(n) ? n : null;
}

function round2(n) {
  const x = Number(n);
  if (!Number.isFinite(x)) return null;
  return Number(x.toFixed(2));
}

function buildResponse({ source, data }) {
  return {
    success: true,
    source,
    data,
    lastUpdated: new Date().toISOString(),
  };
}

async function fetchYahooQuote() {
  const symbols = Object.values(YAHOO_SYMBOLS).join(',');
  const url = `https://query1.finance.yahoo.com/v7/finance/quote?symbols=${encodeURIComponent(
    symbols
  )}`;

  const res = await fetch(url);
  if (!res.ok) throw new Error(`Yahoo Finance HTTP ${res.status}`);
  const json = await res.json();
  const quotes = json?.quoteResponse?.result || [];
  if (!Array.isArray(quotes) || quotes.length === 0) {
    throw new Error('Yahoo Finance: empty result');
  }
  const bySymbol = {};
  for (const q of quotes) {
    if (q?.symbol) bySymbol[q.symbol] = q;
  }

  const nifty = toNumber(bySymbol[YAHOO_SYMBOLS.nifty]?.regularMarketPrice);
  const sensex = toNumber(bySymbol[YAHOO_SYMBOLS.sensex]?.regularMarketPrice);
  const usdInr = toNumber(bySymbol[YAHOO_SYMBOLS.usdInr]?.regularMarketPrice);

  const goldUsdOz = toNumber(bySymbol[YAHOO_SYMBOLS.gold]?.regularMarketPrice);
  const silverUsdOz = toNumber(bySymbol[YAHOO_SYMBOLS.silver]?.regularMarketPrice);
  const crudeOil = toNumber(bySymbol[YAHOO_SYMBOLS.crudeOil]?.regularMarketPrice);

  // Convert COMEX spot (USD/oz) into India-like INR units for UI consistency
  let gold = null;
  let silver = null;
  if (usdInr && goldUsdOz) {
    const perGramInInr = (goldUsdOz * usdInr) / OUNCE_IN_GRAMS;
    gold = Math.round(perGramInInr * 10 * GOLD_TAX_FACTOR); // INR / 10g
  }
  if (usdInr && silverUsdOz) {
    const perGramInInr = (silverUsdOz * usdInr) / OUNCE_IN_GRAMS;
    silver = Math.round(perGramInInr * 1000 * GOLD_TAX_FACTOR); // INR / kg
  }

  const data = {
    nifty: nifty ? Math.round(nifty) : null,
    sensex: sensex ? Math.round(sensex) : null,
    gold,
    silver,
    crudeOil: crudeOil ? round2(crudeOil) : null,
    usdInr: usdInr ? round2(usdInr) : null,
  };

  return data;
}

async function fetchAlphaVantageUsdInr(apiKey) {
  const url = `https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=INR&apikey=${encodeURIComponent(
    apiKey
  )}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Alpha Vantage HTTP ${res.status}`);
  const json = await res.json();
  const rate = toNumber(json?.['Realtime Currency Exchange Rate']?.['5. Exchange Rate']);
  if (!rate) throw new Error('Alpha Vantage: missing USDINR rate');
  return round2(rate);
}

async function fetchUsdInrExchangerateHost() {
  // Simple, unauthenticated USD->INR rate
  const url = 'https://api.exchangerate.host/latest?base=USD&symbols=INR';
  const res = await fetch(url);
  if (!res.ok) throw new Error(`exchangerate.host HTTP ${res.status}`);
  const json = await res.json();
  const rate = toNumber(json?.rates?.INR);
  if (!rate) throw new Error('exchangerate.host: missing INR rate');
  return round2(rate);
}

function isComplete(data) {
  return (
    data &&
    Number.isFinite(data.nifty) &&
    Number.isFinite(data.sensex) &&
    Number.isFinite(data.gold) &&
    Number.isFinite(data.silver) &&
    Number.isFinite(data.crudeOil) &&
    Number.isFinite(data.usdInr)
  );
}

function mergePreferExisting(primary, secondary) {
  const out = { ...(primary || {}) };
  for (const k of Object.keys(YAHOO_SYMBOLS)) {
    if (!Number.isFinite(out[k])) {
      const v = secondary?.[k];
      if (Number.isFinite(v)) out[k] = v;
    }
  }
  return out;
}

export async function fetchLiveMarketData() {
  const alphaKey =
    process.env.REACT_APP_ALPHA_VANTAGE_KEY ||
    process.env.REACT_APP_ALPHA_VANTAGE_API_KEY ||
    '';

  // Attempt sources in order, without ever throwing from the public API.
  // We still use Promise.allSettled so any single failure doesn't break the bundle.
  const yahooAttempt = Promise.allSettled([fetchYahooQuote()]);

  const [yahooSettled] = await yahooAttempt;
  const yahooData =
    yahooSettled?.[0]?.status === 'fulfilled' ? yahooSettled[0].value : null;

  // If yahoo gave partial data, try filling USDINR via fallbacks
  const tasks = [];

  if (alphaKey) {
    tasks.push(
      fetchAlphaVantageUsdInr(alphaKey).then((usdInr) => ({ usdInr })).catch(() => null)
    );
  } else {
    tasks.push(Promise.resolve(null));
  }

  tasks.push(
    fetchUsdInrExchangerateHost().then((usdInr) => ({ usdInr })).catch(() => null)
  );

  const settled = await Promise.allSettled(tasks);
  const fallbackRates = settled
    .filter((s) => s.status === 'fulfilled')
    .map((s) => s.value)
    .filter(Boolean);

  let combined = yahooData || {};
  for (const r of fallbackRates) {
    combined = mergePreferExisting(combined, r);
  }

  if (isComplete(combined)) {
    const resp = buildResponse({ source: 'Live', data: combined });
    writeLastLiveSnapshot(resp);
    pushNiftyHistoryPoint(combined.nifty);
    return resp;
  }

  // If live is incomplete or blocked (CORS/offline), return market-aligned simulation.
  const fallback = generateMarketAlignedFallback(combined);
  return buildResponse({ source: 'Fallback', data: fallback.data });
}

export default {
  fetchLiveMarketData,
};

