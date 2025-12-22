# System Architecture

## Overview

The system follows a three-layer architecture pattern, separating concerns between presentation, business logic, and machine learning components.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│                  (React Frontend)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │Dashboard │  │Forecast  │  │Sentiment │  │  About  │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP/REST API
                       │ (JSON)
┌──────────────────────▼──────────────────────────────────┐
│                  API Layer                               │
│                (FastAPI Backend)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │/market-data  │  │  /forecast   │  │  /sentiment  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────────────────────────────────────────┐   │
│  │         /stability-score                         │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│              Business Logic Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │Data Fetcher  │  │   Forecast   │  │  Sentiment   │  │
│  │   Service    │  │    Model     │  │   Analyzer   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────────────────────────────────────────┐   │
│  │         Stability Score Calculator               │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│              External Data Sources                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │Yahoo Finance │  │ Google News  │  │  Economic    │  │
│  │   (yfinance) │  │     RSS      │  │  Indicators  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└──────────────────────────────────────────────────────────┘
```

## Layer Details

### 1. Frontend Layer (React)

**Technology Stack:**
- React 18.2.0
- React Router 6.20.0
- Recharts 2.10.3
- Axios 1.6.2

**Components:**
- `Navbar`: Navigation component
- `StabilityGauge`: Circular gauge for stability score
- `Dashboard`: Main dashboard page
- `Forecast`: Forecast visualization page
- `Sentiment`: Sentiment analysis page
- `About`: Project documentation page

**Features:**
- Responsive design
- Real-time data updates
- Interactive charts
- Error handling
- Loading states

### 2. Backend Layer (FastAPI)

**Technology Stack:**
- FastAPI 0.104.1
- Uvicorn 0.24.0
- Python 3.9+

**Structure:**
```
backend/
├── main.py                 # FastAPI app, route handlers
├── ml_models/
│   ├── forecast.py         # Prophet model wrapper
│   ├── sentiment.py        # VADER analyzer wrapper
│   └── stability_score.py  # Score calculator
└── services/
    └── data_fetcher.py     # External API integration
```

**API Endpoints:**
- `GET /`: API information
- `GET /market-data`: Current market data
- `GET /forecast`: 7-day forecast
- `GET /sentiment`: Sentiment analysis
- `GET /stability-score`: Overall stability score
- `GET /health`: Health check

**Features:**
- CORS middleware for frontend
- Error handling
- JSON responses
- Async operations

### 3. ML Layer

**Models:**

1. **MarketForecaster (Prophet)**
   - Input: Historical OHLCV data (3 months)
   - Output: 7-day forecast with confidence intervals
   - Features: Trend, seasonality, uncertainty

2. **SentimentAnalyzer (VADER)**
   - Input: News headlines (text)
   - Output: Sentiment scores and labels
   - Features: Compound score, polarity distribution

3. **StabilityScoreCalculator**
   - Input: Normalized scores from models
   - Output: Stability score (0-100) and category
   - Features: Weighted combination, interpretability

## Data Flow

### Request Flow:
1. User interacts with React frontend
2. Frontend makes HTTP request to FastAPI backend
3. Backend routes request to appropriate handler
4. Handler calls service/ML layer
5. Service fetches data from external sources
6. ML models process data
7. Results returned as JSON
8. Frontend renders visualization

### Data Processing:
```
Raw Data → Cleaning → Feature Extraction → Model Inference → Normalization → Aggregation → Score
```

## Design Patterns

### 1. Service Layer Pattern
- Separates business logic from API routes
- `DataFetcher` handles all external API calls
- `ML Models` are independent, reusable components

### 2. Dependency Injection
- Services initialized once in `main.py`
- Passed to route handlers
- Enables testing and mocking

### 3. Separation of Concerns
- Frontend: Presentation only
- Backend: Business logic and API
- ML Layer: Model-specific logic

## Scalability Considerations

### Current Design:
- Single-threaded Python (suitable for academic project)
- In-memory model training (lightweight)
- Synchronous API calls

### Future Enhancements:
- Background task queue (Celery)
- Model caching (Redis)
- Database for historical data
- Microservices architecture

## Security Considerations

### Current:
- CORS configured for development
- No authentication (academic project)
- Input validation on API endpoints

### Production Recommendations:
- API authentication (JWT)
- Rate limiting
- Input sanitization
- HTTPS only
- Environment variable management

## Deployment Architecture

### Development:
```
Local Machine
├── React Dev Server (port 3000)
└── FastAPI Server (port 8000)
```

### Production:
```
┌─────────────┐         ┌─────────────┐
│   Netlify   │  ────→  │   Render    │
│  (Frontend) │         │  (Backend)  │
└─────────────┘         └─────────────┘
```

## Technology Choices Rationale

### Frontend: React
- **Why:** Industry standard, large community, component-based
- **Alternatives Considered:** Vue.js, Angular (React chosen for simplicity)

### Backend: FastAPI
- **Why:** Fast, modern, automatic API documentation, Python-native
- **Alternatives Considered:** Flask, Django (FastAPI chosen for performance)

### Forecasting: Prophet
- **Why:** Beginner-friendly, handles seasonality, provides uncertainty
- **Alternatives Considered:** ARIMA, LSTM (Prophet chosen for ease of use)

### Sentiment: VADER
- **Why:** No training required, works well with news text, fast
- **Alternatives Considered:** TextBlob, BERT (VADER chosen for simplicity)

## Performance Metrics

### Expected Performance:
- API Response Time: < 2 seconds
- Forecast Generation: < 5 seconds
- Sentiment Analysis: < 1 second
- Frontend Load Time: < 3 seconds

### Optimization:
- Model caching (future)
- Data caching (future)
- Lazy loading (frontend)
- Code splitting (frontend)

