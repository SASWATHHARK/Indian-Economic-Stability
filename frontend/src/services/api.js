import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 120000,  // 2 min – first load (Prophet training, yfinance) can take 60–90s
});

api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// New endpoints
export const getMarketLatest = () => api.get('/market/latest');
export const getSentimentToday = () => api.get('/sentiment/today');
export const getStabilityLatest = () => api.get('/stability/latest');
export const getForecast7Days = () => api.get('/forecast/7days');
export const getNews = (filter = 'all') => api.get('/news', { params: { filter } });
export const postRefresh = () => api.post('/refresh');
export const getHealth = () => api.get('/health');

// Legacy aliases (backward compatible)
export const getMarketData = () => api.get('/market-data');
export const getForecast = () => api.get('/forecast');
export const getModelMetrics = () => api.get('/forecast/7days');
export const getSentiment = (params) => api.get('/sentiment', { params: params || {} });
export const getStabilityScore = () => api.get('/stability-score');
export const postRefreshData = () => api.post('/refresh');

export default api;
