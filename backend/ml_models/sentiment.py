"""
Sentiment Analysis Module
Uses VADER Sentiment Analyzer for news headline analysis
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import re
from typing import List, Dict


class SentimentAnalyzer:
    """
    Analyzes sentiment of news headlines using VADER
    """
    
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
    
    def clean_text(self, text: str) -> str:
        """
        Clean and preprocess text
        """
        if not text:
            return ""
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def analyze_single(self, text: str) -> Dict:
        """
        Analyze sentiment of a single text
        Returns: {
            'compound': float,  # Overall sentiment (-1 to 1)
            'positive': float,
            'neutral': float,
            'negative': float,
            'label': str  # 'positive', 'neutral', 'negative'
        }
        """
        cleaned_text = self.clean_text(text)
        
        if not cleaned_text:
            return {
                'compound': 0.0,
                'positive': 0.0,
                'neutral': 1.0,
                'negative': 0.0,
                'label': 'neutral'
            }
        
        scores = self.analyzer.polarity_scores(cleaned_text)
        
        # Determine label
        compound = scores['compound']
        if compound >= 0.05:
            label = 'positive'
        elif compound <= -0.05:
            label = 'negative'
        else:
            label = 'neutral'
        
        return {
            'compound': compound,
            'positive': scores['pos'],
            'neutral': scores['neu'],
            'negative': scores['neg'],
            'label': label
        }
    
    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        """
        Analyze sentiment of multiple texts
        """
        results = []
        for text in texts:
            result = self.analyze_single(text)
            result['text'] = text
            results.append(result)
        
        return results
    
    def get_aggregate_sentiment(self, results: List[Dict]) -> Dict:
        """
        Calculate aggregate sentiment from multiple analyses
        """
        if not results:
            return {
                'avg_compound': 0.0,
                'positive_count': 0,
                'neutral_count': 0,
                'negative_count': 0,
                'overall_label': 'neutral',
                'total_articles': 0
            }
        
        compounds = [r['compound'] for r in results]
        labels = [r['label'] for r in results]
        
        return {
            'avg_compound': sum(compounds) / len(compounds),
            'positive_count': labels.count('positive'),
            'neutral_count': labels.count('neutral'),
            'negative_count': labels.count('negative'),
            'overall_label': 'positive' if sum(compounds) > 0.1 else ('negative' if sum(compounds) < -0.1 else 'neutral'),
            'total_articles': len(results)
        }


def normalize_sentiment_score(aggregate_sentiment: Dict) -> float:
    """
    Normalize sentiment into 0-1 score
    Higher score = more positive sentiment
    """
    # Compound score ranges from -1 to 1, normalize to 0-1
    compound_score = (aggregate_sentiment['avg_compound'] + 1) / 2
    
    # Weight by distribution
    positive_ratio = aggregate_sentiment['positive_count'] / max(1, aggregate_sentiment['total_articles'])
    negative_ratio = aggregate_sentiment['negative_count'] / max(1, aggregate_sentiment['total_articles'])
    
    # Final score: compound score adjusted by distribution
    normalized_score = compound_score * 0.7 + positive_ratio * 0.3 - negative_ratio * 0.2
    
    return min(1.0, max(0.0, normalized_score))

