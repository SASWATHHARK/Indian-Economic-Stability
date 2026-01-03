import axios from 'axios';

// Use 127.0.0.1 as per user request and to avoid Node v18+ localhost issues
const API_BASE_URL = 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // Increased to 30s to allow backend fallback to initialize
});

// Add response interceptor for better error handling
api.interceptors.response.use(
  response => response,
  error => {
    console.error("API Error:", error);
    // Return a custom object or reject to handle in components
    return Promise.reject(error);
  }
);

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
