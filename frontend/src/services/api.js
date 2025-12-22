import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getMarketData = () => api.get('/market-data');
export const getForecast = () => api.get('/forecast');
export const getSentiment = () => api.get('/sentiment');
export const getStabilityScore = (inflationRate, repoRate) => 
  api.get('/stability-score', {
    params: {
      inflation_rate: inflationRate,
      repo_rate: repoRate,
    },
  });

export default api;

