# Methodology

## 1. Data Collection

### 1.1 Market Data
- **Source:** Yahoo Finance API (via yfinance library)
- **Indices:** NIFTY 50 (^NSEI) and SENSEX (^BSESN)
- **Data Points:**
  - Open, High, Low, Close prices
  - Volume
  - Historical data (3 months for training)
- **Frequency:** Daily updates

### 1.2 News Data
- **Source:** Google News RSS feeds
- **Query:** "India economy RBI inflation stock market"
- **Processing:** Extract headlines, remove URLs and special characters
- **Volume:** 20 articles per analysis

### 1.3 Economic Indicators
- **Inflation Rate:** Configurable parameter (default: 4.5%)
- **Repo Rate:** Configurable parameter (default: 6.5%)
- **Note:** Can be updated manually or fetched from RBI APIs

## 2. Machine Learning Models

### 2.1 Time Series Forecasting (Facebook Prophet)

**Why Prophet?**
- Beginner-friendly, no extensive hyperparameter tuning
- Handles seasonality automatically
- Provides uncertainty intervals
- Works well with daily data

**Implementation:**
1. Fetch 3 months of historical NIFTY 50 data
2. Prepare data in Prophet format (ds: date, y: close price)
3. Train model with:
   - Daily seasonality: True
   - Weekly seasonality: True
   - Yearly seasonality: False (short-term forecast)
   - Changepoint prior scale: 0.05 (conservative)
4. Generate 7-day forecast
5. Calculate confidence intervals

**Output:**
- Predicted values for next 7 days
- Upper and lower bounds
- Confidence scores
- Trend direction (upward/downward)

**Normalization:**
- Trend score: 0.7 for upward, 0.3 for downward
- Confidence score: Based on uncertainty intervals
- Volatility score: Inverse of volatility
- Final: Weighted combination (0-1 scale)

### 2.2 Sentiment Analysis (VADER)

**Why VADER?**
- Specifically designed for social media and news text
- No training data required
- Provides compound scores (-1 to 1)
- Fast and efficient

**Implementation:**
1. Fetch news headlines from RSS feed
2. Clean text (remove URLs, special characters)
3. Analyze each headline:
   - Compound score: Overall sentiment (-1 to 1)
   - Positive, Neutral, Negative scores
   - Label classification:
     - Positive: compound ≥ 0.05
     - Negative: compound ≤ -0.05
     - Neutral: otherwise
4. Aggregate results:
   - Average compound score
   - Count by category
   - Overall label

**Normalization:**
- Compound score: Normalize from [-1, 1] to [0, 1]
- Positive ratio: Count of positive articles / total
- Negative ratio: Count of negative articles / total
- Final: Weighted combination

**Example:**
- "RBI announces rate cut" → Positive (+0.6)
- "Inflation rises to 6%" → Negative (-0.3)
- "Market remains stable" → Neutral (+0.05)

### 2.3 Economic Stability Score

**Formula:**
```
Stability Score = (Market_Trend × 0.4) + (Sentiment × 0.3) + (Economic_Indicators × 0.3)
```

**Component Calculation:**

1. **Market Trend (40%):**
   - From Prophet forecast normalization
   - Considers trend direction, confidence, volatility

2. **Sentiment (30%):**
   - From VADER aggregate normalization
   - Considers compound score and distribution

3. **Economic Indicators (30%):**
   - Inflation normalization: Optimal range 2-6% (peak at 4%)
   - Repo rate normalization: Optimal range 4-7% (peak at 5.5%)
   - Average of both indicators

**Category Classification:**
- **Stable (71-100):** Positive indicators, stable trends
- **Moderate (41-70):** Mixed signals, moderate stability
- **Unstable (0-40):** Concerning indicators

## 3. System Architecture

### 3.1 Frontend (React)
- **Pages:**
  - Dashboard: Stability score, market summary
  - Forecast: 7-day prediction charts
  - Sentiment: News articles with sentiment labels
  - About: Project documentation
- **Libraries:**
  - React Router: Navigation
  - Recharts: Data visualization
  - Axios: API calls

### 3.2 Backend (FastAPI)
- **Endpoints:**
  - `/market-data`: Fetch current market data
  - `/forecast`: Generate 7-day forecast
  - `/sentiment`: Analyze news sentiment
  - `/stability-score`: Calculate overall score
- **Features:**
  - CORS enabled for frontend
  - Error handling
  - JSON responses

### 3.3 Data Flow
1. User requests data from frontend
2. Frontend calls backend API
3. Backend fetches data from external sources
4. Backend processes data through ML models
5. Backend returns JSON response
6. Frontend renders visualizations

## 4. Evaluation Metrics

### 4.1 Forecast Accuracy
- Confidence intervals (wider = less certain)
- Trend direction accuracy (requires historical validation)
- Volatility estimation

### 4.2 Sentiment Analysis
- Distribution of positive/neutral/negative articles
- Average compound score
- Consistency across articles

### 4.3 Stability Score
- Component breakdown transparency
- Category classification accuracy
- Interpretability

## 5. Limitations & Assumptions

### Assumptions:
1. Historical patterns continue in short-term (7 days)
2. News headlines reflect overall economic sentiment
3. Inflation and repo rate are primary economic indicators
4. Market indices (NIFTY/SENSEX) represent economic health

### Limitations:
1. Cannot predict black swan events
2. Sentiment from headlines may miss article context
3. Economic indicators may lag real-time conditions
4. Model performance degrades over time without retraining
5. Dependent on external API availability

## 6. Future Improvements

1. **Enhanced Models:**
   - LSTM for time series
   - Transformer-based sentiment (BERT)
   - Ensemble methods

2. **More Data Sources:**
   - Additional economic indicators (GDP, unemployment)
   - Social media sentiment (Twitter)
   - International market correlations

3. **Real-time Updates:**
   - WebSocket connections
   - Automated retraining schedules
   - Alert system for significant changes

4. **User Features:**
   - Historical trend comparison
   - Custom indicator weights
   - Export reports

