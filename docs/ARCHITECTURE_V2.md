# Architecture – Indian Economic Stability Dashboard (v2)

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Frontend (React)                               │
│  Dashboard │ Forecast │ Sentiment │ Stability │ Economic Indicators     │
└─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ HTTP/REST
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Backend (FastAPI)                                 │
│  GET /market-data │ /forecast │ /model-metrics │ /sentiment              │
│  GET /stability-score │ POST /refresh-data │ GET /health                │
└─────────────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Services    │    │  ML / Sentiment  │    │  Database        │
│  DataFetcher│    │  Prophet, VADER   │    │  SQLAlchemy      │
│  (yfinance) │    │  Stability calc   │    │  SQLite/Postgres │
└──────────────┘    └──────────────────┘    └─────────────────┘
```

## Backend Module Layout

```
backend/
  app/
    main.py              # FastAPI app, lifespan, CORS, router
    config.py            # Settings (env)
    routes/              # API endpoints
      market.py          # GET /market-data
      forecast.py        # GET /forecast, GET /model-metrics
      sentiment.py       # GET /sentiment (filters)
      stability.py       # GET /stability-score
      health.py          # GET /health
      refresh.py         # POST /refresh-data
    services/            # External data
      (DataFetcher from backend/services)
    ml/                  # ML logic
      forecast.py        # Prophet, train/test, MAE/RMSE/R², probabilistic
      stability.py       # Multi-factor stability formula
    sentiment/           # Sentiment
      analyzer.py        # VADER + source/recency weights
    database/            # Persistence
      base.py            # Engine, Session, get_db
      models.py          # daily_market_data, sentiment_scores, stability_history, forecast_history
      crud.py            # CRUD for all tables
    schemas/             # Pydantic request/response
    utils/               # Logging, cache, stability helpers
  services/               # Legacy data fetcher (yfinance, news)
  ml_models/             # Legacy (optional compatibility)
```

## Data Flow

1. **Market data**: Client → GET /market-data → cache or DataFetcher → yfinance → response.
2. **Forecast**: Client → GET /forecast → historical data → Prophet train/predict → probabilistic output + cache update for stability.
3. **Sentiment**: Client → GET /sentiment → news RSS → VADER + weights → filter by sentiment/date → response.
4. **Stability**: Client → GET /stability-score → cached forecast/sentiment + inflation/liquidity helpers → multi-factor formula → response.
5. **Refresh**: POST /refresh-data or scheduler → fetch market/sentiment/forecast → persist to DB (daily_market_data, sentiment_scores, stability_history).

## Stability Score Formula (Multi-Factor)

All components normalized 0–100:

- **Market Momentum (30%)**: From forecast trend strength.
- **Sentiment (25%)**: From weighted news sentiment.
- **Volatility Inverse (20%)**: Lower volatility → higher score.
- **Inflation (15%)**: Optimal band around 4%.
- **Liquidity (10%)**: Volume proxy or neutral.

`Stability Score = 0.30×M + 0.25×S + 0.20×V + 0.15×I + 0.10×L`

Category: Stable (≥71), Moderate (41–70), Unstable (≤40).  
Risk level: Low / Medium / High derived from score.

## Deployment

- **Backend**: Render / Railway (Docker or `uvicorn app.main:app`).
- **Frontend**: Vercel (build from `frontend/`).
- **Database**: SQLite for demo; Supabase/Neon PostgreSQL for production. Set `DATABASE_URL`.
