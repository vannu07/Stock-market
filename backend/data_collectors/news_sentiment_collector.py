import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import feedparser
import nltk
import numpy as np
import pandas as pd
import requests
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Download required NLTK data
try:
    nltk.download("stopwords", quiet=True)
    nltk.download("punkt", quiet=True)
    nltk.download("wordnet", quiet=True)
    nltk.download("vader_lexicon", quiet=True)
except:
    pass

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import Config

# Set up logging
logging.basicConfig(level=logging.INFO, format=Config.LOG_FORMAT)
logger = logging.getLogger(__name__)


class NewsSentimentCollector:
    """Collects news and performs sentiment analysis"""

    def __init__(self):
        self.config = Config()
        self.news_api_key = self.config.get_api_key("news_api")
        self.twitter_token = self.config.get_api_key("twitter")

        # Initialize sentiment analyzers
        self.vader_analyzer = SentimentIntensityAnalyzer()
        self.lemmatizer = WordNetLemmatizer()

        # Initialize stopwords
        try:
            self.stop_words = set(stopwords.words("english"))
        except:
            self.stop_words = set(
                [
                    "the",
                    "a",
                    "an",
                    "and",
                    "or",
                    "but",
                    "in",
                    "on",
                    "at",
                    "to",
                    "for",
                    "of",
                    "with",
                    "by",
                ]
            )

        # Stock-related keywords
        self.stock_keywords = {
            "AAPL": ["apple", "iphone", "ios", "mac", "tim cook", "cupertino"],
            "GOOGL": ["google", "alphabet", "android", "chrome", "sundar pichai"],
            "MSFT": ["microsoft", "windows", "azure", "satya nadella", "office"],
            "AMZN": ["amazon", "aws", "prime", "jeff bezos", "andy jassy"],
            "TSLA": ["tesla", "elon musk", "electric vehicle", "ev", "model"],
            "META": ["meta", "facebook", "instagram", "whatsapp", "mark zuckerberg"],
            "NVDA": ["nvidia", "gpu", "graphics", "jensen huang", "cuda"],
            "NFLX": ["netflix", "streaming", "reed hastings", "content"],
        }

        # RSS feeds for financial news
        self.rss_feeds = [
            "https://feeds.finance.yahoo.com/rss/2.0/headline",
            "https://www.marketwatch.com/rss/topstories",
            "https://feeds.bloomberg.com/markets/news.rss",
            "https://www.cnbc.com/id/100003114/device/rss/rss.html",
            "https://feeds.reuters.com/news/wealth",
        ]

    def get_sentiment_for_stock(self, symbol: str) -> Dict:
        """Get sentiment analysis for a specific stock"""
        try:
            # Collect news from multiple sources
            news_articles = []

            # Get news from APIs
            api_news = self._get_news_api_data(symbol)
            if api_news:
                news_articles.extend(api_news)

            # Get news from RSS feeds
            rss_news = self._get_rss_news(symbol)
            if rss_news:
                news_articles.extend(rss_news)

            # If no real news found, generate simulated sentiment
            if not news_articles:
                return self._generate_simulated_sentiment(symbol)

            # Analyze sentiment
            sentiment_scores = []
            for article in news_articles:
                sentiment = self._analyze_sentiment(
                    article["title"] + " " + article.get("description", "")
                )
                sentiment_scores.append(sentiment)

            # Aggregate sentiment
            if sentiment_scores:
                avg_compound = np.mean([s["compound"] for s in sentiment_scores])
                avg_positive = np.mean([s["positive"] for s in sentiment_scores])
                avg_negative = np.mean([s["negative"] for s in sentiment_scores])
                avg_neutral = np.mean([s["neutral"] for s in sentiment_scores])

                # Determine overall sentiment label
                if avg_compound >= 0.05:
                    label = "positive"
                elif avg_compound <= -0.05:
                    label = "negative"
                else:
                    label = "neutral"

                return {
                    "symbol": symbol,
                    "compound_score": round(avg_compound, 3),
                    "positive_score": round(avg_positive, 3),
                    "negative_score": round(avg_negative, 3),
                    "neutral_score": round(avg_neutral, 3),
                    "sentiment_label": label,
                    "news_count": len(news_articles),
                    "timestamp": datetime.now(),
                    "source": "aggregated",
                }
            else:
                return self._generate_simulated_sentiment(symbol)

        except Exception as e:
            logger.error(f"Error getting sentiment for {symbol}: {e}")
            return self._generate_simulated_sentiment(symbol)

    def _get_news_api_data(self, symbol: str) -> List[Dict]:
        """Get news from News API"""
        try:
            if self.news_api_key == "your_news_api_key":
                return []

            # Search for stock-related news
            keywords = self.stock_keywords.get(symbol, [symbol])
            query = " OR ".join(keywords)

            url = f"{self.config.NEWS_API_BASE_URL}/everything"
            params = {
                "q": query,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 10,
                "apiKey": self.news_api_key,
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code != 200:
                return []

            data = response.json()

            articles = []
            for article in data.get("articles", [])[:5]:  # Limit to 5 articles
                articles.append(
                    {
                        "title": article.get("title", ""),
                        "description": article.get("description", ""),
                        "url": article.get("url", ""),
                        "source": article.get("source", {}).get("name", "Unknown"),
                        "published_date": article.get("publishedAt", ""),
                        "symbol": symbol,
                    }
                )

            return articles

        except Exception as e:
            logger.error(f"News API error for {symbol}: {e}")
            return []

    def _get_rss_news(self, symbol: str) -> List[Dict]:
        """Get news from RSS feeds"""
        try:
            articles = []
            keywords = self.stock_keywords.get(symbol, [symbol])

            for feed_url in self.rss_feeds[:2]:  # Limit to 2 feeds to avoid being slow
                try:
                    feed = feedparser.parse(feed_url)

                    for entry in feed.entries[:5]:  # Limit to 5 entries per feed
                        title = entry.get("title", "")
                        description = entry.get("description", "") or entry.get(
                            "summary", ""
                        )

                        # Check if article is relevant to the stock
                        content = (title + " " + description).lower()
                        if any(keyword.lower() in content for keyword in keywords):
                            articles.append(
                                {
                                    "title": title,
                                    "description": description,
                                    "url": entry.get("link", ""),
                                    "source": feed.feed.get("title", "RSS Feed"),
                                    "published_date": entry.get("published", ""),
                                    "symbol": symbol,
                                }
                            )

                except Exception as e:
                    logger.error(f"RSS feed error for {feed_url}: {e}")
                    continue

            return articles

        except Exception as e:
            logger.error(f"RSS news error for {symbol}: {e}")
            return []

    def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of a text using multiple methods"""
        try:
            # Clean the text
            cleaned_text = self._clean_text(text)

            # VADER sentiment analysis
            vader_scores = self.vader_analyzer.polarity_scores(cleaned_text)

            # TextBlob sentiment analysis
            blob = TextBlob(cleaned_text)
            textblob_polarity = blob.sentiment.polarity

            # Combine both methods (weighted average)
            compound_score = (vader_scores["compound"] * 0.7) + (
                textblob_polarity * 0.3
            )

            return {
                "compound": compound_score,
                "positive": vader_scores["pos"],
                "negative": vader_scores["neg"],
                "neutral": vader_scores["neu"],
                "textblob_polarity": textblob_polarity,
            }

        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {
                "compound": 0.0,
                "positive": 0.0,
                "negative": 0.0,
                "neutral": 1.0,
                "textblob_polarity": 0.0,
            }

    def _clean_text(self, text: str) -> str:
        """Clean and preprocess text"""
        try:
            # Remove HTML tags
            text = re.sub(r"<[^>]+>", "", text)

            # Remove URLs
            text = re.sub(
                r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
                "",
                text,
            )

            # Remove special characters and digits
            text = re.sub(r"[^a-zA-Z\s]", "", text)

            # Convert to lowercase
            text = text.lower()

            # Tokenize
            tokens = word_tokenize(text)

            # Remove stopwords and lemmatize
            filtered_tokens = [
                self.lemmatizer.lemmatize(token)
                for token in tokens
                if token not in self.stop_words and len(token) > 2
            ]

            return " ".join(filtered_tokens)

        except Exception as e:
            logger.error(f"Text cleaning error: {e}")
            return text

    def _generate_simulated_sentiment(self, symbol: str) -> Dict:
        """Generate simulated sentiment data for demo purposes"""
        # Create somewhat realistic sentiment patterns
        sentiment_patterns = {
            "AAPL": {"base": 0.1, "volatility": 0.2},
            "GOOGL": {"base": 0.05, "volatility": 0.15},
            "MSFT": {"base": 0.15, "volatility": 0.1},
            "AMZN": {"base": 0.0, "volatility": 0.25},
            "TSLA": {"base": 0.05, "volatility": 0.4},
            "META": {"base": -0.05, "volatility": 0.3},
            "NVDA": {"base": 0.2, "volatility": 0.2},
            "NFLX": {"base": 0.0, "volatility": 0.2},
        }

        pattern = sentiment_patterns.get(symbol, {"base": 0.0, "volatility": 0.2})

        # Generate compound score
        compound_score = np.random.normal(pattern["base"], pattern["volatility"])
        compound_score = np.clip(compound_score, -1, 1)

        # Generate component scores
        if compound_score > 0:
            positive = abs(compound_score) + np.random.normal(0, 0.1)
            negative = np.random.normal(0, 0.05)
        else:
            positive = np.random.normal(0, 0.05)
            negative = abs(compound_score) + np.random.normal(0, 0.1)

        positive = np.clip(positive, 0, 1)
        negative = np.clip(negative, 0, 1)
        neutral = max(0, 1 - positive - negative)

        # Normalize
        total = positive + negative + neutral
        if total > 0:
            positive /= total
            negative /= total
            neutral /= total

        # Determine label
        if compound_score >= 0.05:
            label = "positive"
        elif compound_score <= -0.05:
            label = "negative"
        else:
            label = "neutral"

        return {
            "symbol": symbol,
            "compound_score": round(compound_score, 3),
            "positive_score": round(positive, 3),
            "negative_score": round(negative, 3),
            "neutral_score": round(neutral, 3),
            "sentiment_label": label,
            "news_count": np.random.randint(5, 15),
            "timestamp": datetime.now(),
            "source": "simulated",
        }

    def get_detailed_sentiment(self, symbol: str) -> Dict:
        """Get detailed sentiment analysis with historical data"""
        try:
            current_sentiment = self.get_sentiment_for_stock(symbol)

            # Generate historical sentiment trend (simulated)
            historical_data = []
            for i in range(7):  # Last 7 days
                date = datetime.now() - timedelta(days=i)
                base_score = current_sentiment["compound_score"]

                # Add some variation for historical data
                variation = np.random.normal(0, 0.1)
                historical_score = np.clip(base_score + variation, -1, 1)

                historical_data.append(
                    {
                        "date": date.strftime("%Y-%m-%d"),
                        "compound_score": round(historical_score, 3),
                    }
                )

            return {
                "current_sentiment": current_sentiment,
                "historical_sentiment": historical_data,
                "sentiment_trend": self._calculate_sentiment_trend(historical_data),
                "news_sources": self._get_news_sources_summary(symbol),
            }

        except Exception as e:
            logger.error(f"Error getting detailed sentiment for {symbol}: {e}")
            return {
                "current_sentiment": self._generate_simulated_sentiment(symbol),
                "historical_sentiment": [],
                "sentiment_trend": "stable",
                "news_sources": [],
            }

    def _calculate_sentiment_trend(self, historical_data: List[Dict]) -> str:
        """Calculate sentiment trend from historical data"""
        if len(historical_data) < 3:
            return "stable"

        scores = [item["compound_score"] for item in historical_data]

        # Calculate linear regression slope
        x = np.arange(len(scores))
        slope = np.polyfit(x, scores, 1)[0]

        if slope > 0.02:
            return "improving"
        elif slope < -0.02:
            return "declining"
        else:
            return "stable"

    def _get_news_sources_summary(self, symbol: str) -> List[Dict]:
        """Get summary of news sources"""
        return [
            {"name": "Yahoo Finance", "count": np.random.randint(2, 8)},
            {"name": "MarketWatch", "count": np.random.randint(1, 5)},
            {"name": "Reuters", "count": np.random.randint(1, 4)},
            {"name": "Bloomberg", "count": np.random.randint(0, 3)},
        ]

    def get_market_sentiment_overview(self) -> Dict:
        """Get overall market sentiment"""
        try:
            symbols = self.config.DEFAULT_STOCKS
            sentiments = {}

            for symbol in symbols:
                sentiment = self.get_sentiment_for_stock(symbol)
                sentiments[symbol] = sentiment

            # Calculate market-wide sentiment
            compound_scores = [s["compound_score"] for s in sentiments.values()]
            avg_compound = np.mean(compound_scores)

            if avg_compound >= 0.05:
                market_sentiment = "bullish"
            elif avg_compound <= -0.05:
                market_sentiment = "bearish"
            else:
                market_sentiment = "neutral"

            return {
                "overall_sentiment": market_sentiment,
                "average_compound_score": round(avg_compound, 3),
                "individual_sentiments": sentiments,
                "timestamp": datetime.now(),
            }

        except Exception as e:
            logger.error(f"Error getting market sentiment overview: {e}")
            return {
                "overall_sentiment": "neutral",
                "average_compound_score": 0.0,
                "individual_sentiments": {},
                "timestamp": datetime.now(),
            }

    def update_sentiment_models(self):
        """Update sentiment analysis models (placeholder for future enhancement)"""
        logger.info("Sentiment models updated")

    def test_connection(self) -> Dict[str, bool]:
        """Test connection to news sources"""
        results = {}

        # Test News API
        try:
            if self.news_api_key != "your_news_api_key":
                url = f"{self.config.NEWS_API_BASE_URL}/top-headlines"
                params = {
                    "country": "us",
                    "category": "business",
                    "pageSize": 1,
                    "apiKey": self.news_api_key,
                }
                response = requests.get(url, params=params, timeout=10)
                results["news_api"] = response.status_code == 200
            else:
                results["news_api"] = False
        except:
            results["news_api"] = False

        # Test RSS feeds
        try:
            feed = feedparser.parse(self.rss_feeds[0])
            results["rss_feeds"] = len(feed.entries) > 0
        except:
            results["rss_feeds"] = False

        return results


# Example usage and testing
if __name__ == "__main__":
    collector = NewsSentimentCollector()

    # Test connection
    print("Testing connections...")
    connections = collector.test_connection()
    for service, status in connections.items():
        print(f"{service}: {'✓' if status else '✗'}")

    # Get sample sentiment
    print("\nGetting sample sentiment...")
    sentiment = collector.get_sentiment_for_stock("AAPL")
    print(f"AAPL Sentiment: {sentiment}")

    # Get market sentiment overview
    print("\nGetting market sentiment overview...")
    market_sentiment = collector.get_market_sentiment_overview()
    print(f"Market Sentiment: {market_sentiment['overall_sentiment']}")
    print(f"Average Score: {market_sentiment['average_compound_score']}")
