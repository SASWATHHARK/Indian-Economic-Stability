# Offline Fallback System

## Folder Structure

```
backend/app/
├── services/
│   ├── live_data_service.py   # Fetches from yfinance / news APIs
│   ├── sample_data_service.py # Loads JSON + optional ±0.5% simulation
│   ├── data_router.py         # try live → on exception use sample, add data_source/demo_mode
│   └── __init__.py
├── sample_data/
│   ├── indices.json           # NIFTY/SENSEX 30-day, current_value, change, trend, historical
│   ├── commodities.json        # Gold, Silver, Crude, USD/INR (price, change, trend, volatility)
│   ├── macro.json             # Inflation, Repo, GDP, FII, DII, IIP
│   ├── news.json              # 10 headlines with sentiment, compound_score, confidence
│   ├── stability.json         # stability_score, classification, factors, confidence
│   └── forecast.json          # 7-day NIFTY forecast, forecast_trend, model_accuracy
```

## Behaviour

- **Live path**: `live_data_service` calls existing `DataFetcher` (yfinance, news RSS). On success, response gets `data_source: "live"`, `demo_mode: false`.
- **Fallback**: On any exception (no network, API down, timeout), `data_router` logs `"⚠ Using Offline Sample Data Mode"` and returns data from `sample_data_service` with `data_source: "offline_sample"`, `demo_mode: true`.
- Response shape is unchanged so the frontend and charts do not break.

## Config (app/config.py)

- `OFFLINE_FALLBACK_ENABLED`: default `True`.
- `DEMO_MODE_WHEN_OFFLINE`: default `True` (sets `demo_mode` in fallback responses).
- `SAMPLE_DATA_SEMI_DYNAMIC`: default `False`. If `True`, sample values get ±0.5% random variation (random-walk style).
- `FORCE_SAMPLE_DATA`: default `False`. If `True` (or `1` via env), skip live APIs entirely – instant load, no timeouts. Use when yfinance/Prophet/news are slow or unavailable.

## Logging

- `app.utils.log.get_logger(__name__)` used in `live_data_service`, `sample_data_service`, `data_router`.
- Fallback is logged at WARNING: `"⚠ Using Offline Sample Data Mode (market): <exception>"`.

## Routes (no hardcoded fallback in route files)

- **Market**: `data_router.get_market_data(period="5d")`; cache only when `data_source == "live"`.
- **Sentiment**: `data_router.get_news_then_sentiment(..., sentiment_analyzer=sentiment_svc)`.
- **Stability**: `data_router.get_stability(stability_svc=..., cache_getter=get_stability_cache, ...)`.
- **Forecast**: `data_router.get_forecast(data_fetcher=..., forecaster=...)`.

All responses include `data_source` and `demo_mode`.

## Frontend badge

- **Component**: `DataSourceBadge` in `frontend/src/components/DataSourceBadge.js`.
- **Logic**: If any of the dashboard responses has `data_source === 'offline_sample'` or `demo_mode === true`, show yellow **Demo Mode**; otherwise green **Live Data**.
- **Usage**: Pass the API responses (e.g. `marketData`, `stabilityData`) as props; the badge derives state from them.

```jsx
<DataSourceBadge
  marketData={marketData}
  forecastData={forecastData}
  sentimentData={sentimentData}
  stabilityData={stabilityData}
/>
```

## Semi-dynamic sample (optional)

Set `SAMPLE_DATA_SEMI_DYNAMIC=True` in config or env. `sample_data_service` then applies ±0.5% variation to numeric sample values so repeated calls return slightly different but realistic numbers without network.
