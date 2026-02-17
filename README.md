# Predictive Framework to Indicate India's Economic Stability

## 📋 Project Overview

This project is a comprehensive full-stack application that predicts India's economic stability using market indicators and sentiment analysis. It combines machine learning models, REST APIs, and a modern React frontend to provide an intuitive dashboard for understanding economic trends.

**Target Audience:** Final Year College Students (Beginner-Intermediate Level)

## 🏗️ System Architecture

```
┌─────────────────┐
│  React Frontend │  (Dashboard, Forecast, Sentiment, About)
└────────┬────────┘
         │ HTTP/REST
┌────────▼────────┐
│  FastAPI Backend│  (REST APIs, Data Processing)
└────────┬────────┘
         │
┌────────▼────────┐
│   ML Layer      │  (Prophet, VADER, Score Calculator)
└─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Node.js 16 or higher
- npm or yarn

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
```

3. Activate virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r ../requirements.txt
```

5. Run the backend server:
   - **Legacy (single-file)**: `python main.py`
   - **Production (modular v2)**: from project root, `cd backend` then `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

The API will be available at `http://localhost:8000`. v2 adds database, GET /model-metrics, POST /refresh-data, and multi-factor stability score.

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## 📁 Project Structure

```
Indian_Economic_Stability_Project/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── ml_models/
│   │   ├── forecast.py         # Prophet forecasting model
│   │   ├── sentiment.py        # VADER sentiment analyzer
│   │   └── stability_score.py  # Score calculator
│   └── services/
│       └── data_fetcher.py     # Data fetching service
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── pages/              # Page components
│   │   └── services/           # API service
│   └── public/
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🔌 API Endpoints

### GET `/market-data`
Returns current NIFTY 50 and SENSEX market data.

**Response:**
```json
{
  "status": "success",
  "date": "2024-01-15",
  "nifty": {
    "current": 22000.50,
    "change_percent": 0.75,
    ...
  },
  "sensex": { ... }
}
```

### GET `/forecast`
Returns 7-day market forecast using Prophet model.

**Response:**
```json
{
  "status": "success",
  "forecast": [...],
  "summary": {...},
  "forecast_score": 72.5
}
```

### GET `/sentiment`
Returns sentiment analysis of recent news headlines.

**Response:**
```json
{
  "status": "success",
  "articles": [...],
  "aggregate": {...},
  "sentiment_score": 65.3
}
```

### GET `/stability-score`
Returns overall Economic Stability Score (0-100).

**Query Parameters:**
- `inflation_rate` (optional): Current inflation rate
- `repo_rate` (optional): Current repo rate

**Response:**
```json
{
  "stability_score": 68.5,
  "category": "Moderate",
  "components": {...},
  "breakdown": {...}
}
```

## 🤖 Machine Learning Models

### 1. Time Series Forecasting (Facebook Prophet)
- **Purpose:** Predict 7-day market trends
- **Input:** Historical NIFTY 50 data (3 months)
- **Output:** Forecasted values with confidence intervals
- **Why Prophet?** Beginner-friendly, handles seasonality, provides uncertainty estimates

### 2. Sentiment Analysis (VADER)
- **Purpose:** Analyze news headline sentiment
- **Input:** News headlines from Google News RSS
- **Output:** Sentiment scores (positive/neutral/negative)
- **Why VADER?** Works well with social media/news text, no training required

### 3. Stability Score Calculator
- **Formula:** Weighted combination of:
  - Market Trend: 40%
  - Sentiment: 30%
  - Economic Indicators: 30%
- **Output:** Score 0-100 with category (Stable/Moderate/Unstable)

## 📊 Features

- **Dashboard:** Real-time stability score with gauge visualization
- **Forecast:** 7-day market trend predictions with confidence intervals
- **Sentiment:** News sentiment analysis with article cards
- **About:** Comprehensive project documentation

## 🛡️ Limitations

1. **Real-time Events:** Market conditions change rapidly with global events
2. **Probabilistic Predictions:** Forecasts are trends, not exact values
3. **Model Updates:** Requires periodic retraining
4. **Data Dependencies:** Relies on external APIs
5. **Not Financial Advice:** Educational tool only

## 📚 Documentation

See `docs/` directory for:
- Abstract
- Methodology
- Literature Review
- System Architecture
- Results & Screenshots

## 🧪 Testing

### Test Backend API:
```bash
curl http://localhost:8000/health
```

### Test Frontend:
Open browser and navigate to `http://localhost:3000`

## 🚢 Deployment

### Backend (Render/Railway):
1. Push code to GitHub
2. Connect repository to Render/Railway
3. Set Python version: 3.9
4. Install command: `pip install -r requirements.txt`
5. Start command: `python backend/main.py`

### Frontend (Netlify/Vercel):
1. Build: `npm run build`
2. Deploy `build/` folder
3. Set environment variable: `REACT_APP_API_URL` to backend URL

## 📝 License

This project is for academic purposes only.

## 👥 Author

Final Year Academic Project

## 🙏 Acknowledgments

- Yahoo Finance for market data
- Google News for news feeds
- Facebook Prophet team
- VADER Sentiment team

---

**⚠️ Disclaimer:** This system is for educational and trend understanding purposes only. Not financial advice. Always consult with financial experts before making investment decisions.

