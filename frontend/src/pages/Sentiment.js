import React, { useState, useEffect } from 'react';
import { getSentiment } from '../services/api';
import './Sentiment.css';

function Sentiment() {
  const [sentimentData, setSentimentData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSentiment();
  }, []);

  const fetchSentiment = async () => {
    try {
      const response = await getSentiment();
      setSentimentData(response.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch sentiment data');
      console.error('Error fetching sentiment:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="sentiment-page">
        <div className="container">
          <div className="loading-container">
             <div className="spinner"></div>
             <div className="loading-text">Processing Economic News...</div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  if (!sentimentData) {
    return <div className="error">No sentiment data available</div>;
  }

  const getSentimentColor = (label) => {
    if (label === 'positive') return '#4caf50';
    if (label === 'negative') return '#f44336';
    return '#ff9800';
  };

  const getSentimentIcon = (label) => {
    if (label === 'positive') return '📈';
    if (label === 'negative') return '📉';
    return '➡️';
  };

  return (
    <div className="sentiment-page">
      <div className="container">
        <h1 className="page-title">News Sentiment Analysis</h1>

        <div className="card">
          <h2>Overall Sentiment</h2>
          <div className="sentiment-overview">
            <div className="sentiment-score">
              <div className="score-value">
                {sentimentData.sentiment_score.toFixed(1)}
                <span className="score-unit"> / 100</span>
              </div>
              <div className="score-label">Sentiment Score</div>
            </div>
            <div className="sentiment-stats">
              <div className="stat-item">
                <span className="stat-label">Positive:</span>
                <span className="stat-value positive">
                  {sentimentData.aggregate.positive_count}
                </span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Neutral:</span>
                <span className="stat-value neutral">
                  {sentimentData.aggregate.neutral_count}
                </span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Negative:</span>
                <span className="stat-value negative">
                  {sentimentData.aggregate.negative_count}
                </span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Total Articles:</span>
                <span className="stat-value">
                  {sentimentData.aggregate.total_articles}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <h2>News Articles</h2>
          <div className="articles-grid">
            {sentimentData.articles.map((article, idx) => (
              <div key={idx} className="article-card">
                <div className="article-header">
                  <span 
                    className="sentiment-badge"
                    style={{ backgroundColor: getSentimentColor(article.sentiment.label) }}
                  >
                    {getSentimentIcon(article.sentiment.label)} {article.sentiment.label.toUpperCase()}
                  </span>
                  <span className="article-source">{article.source}</span>
                </div>
                <h3 className="article-title">{article.title}</h3>
                <div className="sentiment-details">
                  {/* Visual bar only if detailed scores exist */}
                  {(article.sentiment.positive !== undefined) ? (
                  <div className="sentiment-bar">
                    <div 
                      className="sentiment-fill positive"
                      style={{ width: `${(article.sentiment.positive || 0) * 100}%` }}
                    />
                    <div 
                      className="sentiment-fill neutral"
                      style={{ width: `${(article.sentiment.neutral || 0) * 100}%` }}
                    />
                    <div 
                      className="sentiment-fill negative"
                      style={{ width: `${(article.sentiment.negative || 0) * 100}%` }}
                    />
                  </div>
                  ) : (
                    <div className="sentiment-bar" style={{background: '#eee'}}>
                        {/* Fallback bar based on label */}
                         <div 
                            className={`sentiment-fill ${article.sentiment.label}`}
                            style={{ width: '100%' }}
                        />
                    </div>
                  )}
                  <div className="sentiment-metrics">
                    <span>Compound: {article.sentiment.compound ? article.sentiment.compound.toFixed(3) : 'N/A'}</span>
                  </div>
                </div>
                {article.link && article.link !== '#' && (
                  <a 
                    href={article.link} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="article-link"
                  >
                    Read More →
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h3>Analysis Information</h3>
          <div className="analysis-info">
             {/* Fallback if analysis_info is missing, which it appears to be in the current API version */}
            <p><strong>Analyzer:</strong> {sentimentData.analysis_info?.analyzer || 'VADER Sentiment Analysis'}</p>
            <p><strong>Total Articles Analyzed:</strong> {sentimentData.aggregate?.total_articles || 0}</p>
            <p className="note">{sentimentData.analysis_info?.note || 'Sentiment derived from recent economic news headlines.'}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Sentiment;

