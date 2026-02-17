# AI-Based Indian Economic Stability Analyzer – Restructure

## 1. Updated Folder Structure

```
Indian_Economic_Stability_Project/
├── backend/
│   ├── main.py              # FastAPI app, CORS, lifespan
│   ├── database.py          # SQLAlchemy engine, Base, get_db, init_db
│   ├── models.py            # MarketData, NewsData, StabilityScore
│   ├── schemas.py           # Pydantic request/response models
│   ├── scheduler.py         # APScheduler daily 6 PM job
│   ├── run.py               # uvicorn main:app
│   ├── requirements.txt     # pip dependencies
│   └── services/
│       ├── __init__.py
│       ├── market_service.py   # yfinance NIFTY/SENSEX, DB store
│       ├── news_service.py     # Google News / GNews, DB store
│       ├── sentiment_service.py # VADER, compound score, classify
│       ├── stability_service.py # Score formula, categories
│       └── forecast_service.py  # Prophet 7-day forecast
├── frontend/
│   └── src/
│       └── services/
│           └── api.js       # Axios API client
└── docs/
    └── RESTRUCTURE.md
```

## 2. pip install

```bash
cd backend
pip install -r requirements.txt
```

Or:

```bash
pip install fastapi uvicorn pandas numpy yfinance prophet vaderSentiment requests python-dotenv pydantic pydantic-settings sqlalchemy apscheduler python-dateutil feedparser
```

## 3. Database Models

**MarketData**

| Column      | Type   |
|------------|--------|
| id         | Integer |
| date       | Date   |
| nifty_close| Float  |
| sensex_close| Float |
| volume     | Float  |
| nifty_open, nifty_high, nifty_low | Float |
| sensex_open, sensex_high, sensex_low | Float |

**NewsData**

| Column        | Type  |
|---------------|-------|
| id            | Integer |
| headline      | Text  |
| source        | String |
| date          | Date  |
| sentiment_score| Float |

**StabilityScore**

| Column         | Type  |
|----------------|-------|
| id             | Integer |
| date           | Date  |
| market_score   | Float |
| sentiment_score| Float |
| volatility_score| Float |
| final_score    | Float |
| category       | String (Stable|Moderate|Unstable) |

## 4. Stability Score Formula

```
Final = 0.4 × Market Strength + 0.3 × Sentiment + 0.2 × Inflation Proxy + 0.1 × Volatility
```

- **Market Strength**: 7-day % change NIFTY → 0–100
- **Sentiment**: VADER compound → 0–100
- **Volatility**: inverse rolling std → 0–100
- **Categories**: 0–40 Unstable, 40–70 Moderate, 70–100 Stable

## 5. API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /market/latest | Latest NIFTY & SENSEX from DB |
| GET | /sentiment/today | Avg sentiment, % pos/neg/neutral |
| GET | /stability/latest | Latest stability score |
| GET | /forecast/7days | 7-day Prophet forecast, MAE, RMSE |
| GET | /news?filter=positive\|negative\|all | News with sentiment filter |
| POST | /refresh | Trigger full refresh (market, news, stability) |
| GET | /health | Health check |

Legacy aliases: /market-data, /forecast, /sentiment, /stability-score

## 6. Example API Responses

**GET /market/latest**

```json
{
  "status": "success",
  "nifty": { "close": 24500.5, "open": 24400.0, "high": 24550.0, "low": 24380.0 },
  "sensex": { "close": 80500.0, "open": 80300.0, "high": 80600.0, "low": 80200.0 },
  "last_updated": "2025-02-17",
  "source": "database"
}
```

**GET /stability/latest**

```json
{
  "status": "success",
  "score": 62.5,
  "category": "Moderate",
  "market_score": 58.0,
  "sentiment_score": 65.0,
  "volatility_score": 55.0,
  "date": "2025-02-17"
}
```

**GET /forecast/7days**

```json
{
  "status": "success",
  "forecast": [
    { "date": "2025-02-18", "predicted": 24550.0, "lower": 24400.0, "upper": 24700.0 }
  ],
  "current_value": 24500.5,
  "mae": 125.5,
  "rmse": 158.2,
  "model": "Prophet"
}
```

**GET /sentiment/today**

```json
{
  "status": "success",
  "average_score": 0.12,
  "pct_positive": 45.0,
  "pct_negative": 20.0,
  "pct_neutral": 35.0,
  "total_articles": 25,
  "date": "2025-02-17"
}
```

## 7. React API Integration Example

```javascript
// frontend/src/services/api.js
import axios from 'axios';
const api = axios.create({ baseURL: 'http://127.0.0.1:8000', timeout: 60000 });

export const getMarketLatest = () => api.get('/market/latest');
export const getStabilityLatest = () => api.get('/stability/latest');
export const getForecast7Days = () => api.get('/forecast/7days');
export const getSentimentToday = () => api.get('/sentiment/today');
export const getNews = (filter = 'all') => api.get('/news', { params: { filter } });
export const postRefresh = () => api.post('/refresh');
```

## 8. Run Commands

**Backend**

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Or: `python run.py`

**Frontend**

```bash
cd frontend
npm start
```

## 9. Scheduler (Daily 6 PM)

APScheduler runs daily at 18:00:

- Fetch NIFTY & SENSEX (yfinance, 2 years)
- Fetch news (India economy, Nifty, RBI)
- Compute sentiment and store
- Compute stability score and store
