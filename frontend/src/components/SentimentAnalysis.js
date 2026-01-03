import React from 'react';
import './SentimentAnalysis.css';

const SentimentAnalysis = ({ data, loading, error }) => {
  if (loading) return (
    <div className="card loading">
      <div className="spinner"></div>
      <div className="loading-text">Analyzing Sentiment...</div>
    </div>
  );
  if (error) return <div className="card error">Error loading sentiment: {error}</div>;
  if (!data) return <div className="card no-data">No sentiment data</div>;

  const getSentimentColor = (compoundScore) => {
    if (compoundScore >= 0.05) return 'positive';
    if (compoundScore <= -0.05) return 'negative';
    return 'neutral';
  };

  return (
    <div className="card sentiment-card">
      <h3 className="card-title">Economic Sentiment Analysis</h3>
      
      <div className="sentiment-header">
        <div className={`sentiment-score-box ${getSentimentColor(data.aggregate?.compound || 0)}`}>
          <div className="score-label">Sentiment Score</div>
          <div className="score-value">
            {data.sentiment_score}
            <span className="score-denominator">/100</span>
          </div>
          <div className="score-desc">
            {data.aggregate?.compound >= 0.05 ? "Positive Outlook" : 
             data.aggregate?.compound <= -0.05 ? "Negative Outlook" : "Neutral Outlook"}
          </div>
        </div>
      </div>

      <div className="headlines-section">
        <h4>Recent Headlines</h4>
        <div className="headlines-list">
          {data.articles?.slice(0, 5).map((article, index) => (
            <div key={index} className="headline-item">
              <a href={article.link} target="_blank" rel="noopener noreferrer" className="headline-link">
                {article.title}
              </a>
              <span className={`sentiment-tag ${getSentimentColor(article.sentiment.compound)}`}>
                {article.sentiment.compound.toFixed(2)}
              </span>
              <div className="source-tag">{article.source}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SentimentAnalysis;
