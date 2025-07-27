# 🚀 Real-Time Stock Market AI Dashboard Setup Guide

This guide will help you set up all the necessary API keys and configure your real-time stock market sentiment and price prediction project.

## 📋 Prerequisites

- Python 3.8 or higher
- Internet connection for API access
- Text editor or IDE

## 🔑 API Keys Required

### 1. **Alpha Vantage API** (Stock Data) - FREE
- **Website**: https://www.alphavantage.co/support/#api-key
- **Free Tier**: 5 calls per minute, 500 calls per day
- **Steps**:
  1. Visit the Alpha Vantage website
  2. Click "Get your free API key today"
  3. Fill in your details and email
  4. Copy the API key from your email

### 2. **News API** (News Data) - FREE
- **Website**: https://newsapi.org/register
- **Free Tier**: 1,000 requests per day
- **Steps**:
  1. Visit NewsAPI.org
  2. Click "Get API Key"
  3. Register with your email
  4. Verify your email and log in
  5. Copy your API key from the dashboard

### 3. **Yahoo Finance** (Stock Data) - FREE
- **No API key required!**
- Using the `yfinance` Python library
- Unlimited free access to historical and current stock data

### 4. **RSS Feeds** (News Data) - FREE
- **No API key required!**
- Using public RSS feeds from major financial news sources
- Includes: Yahoo Finance, MarketWatch, Reuters, Bloomberg

## 🛠️ Installation Steps

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Set up Environment Variables

1. **Copy the environment template:**
   ```bash
   copy .env.template .env
   ```

2. **Edit the `.env` file** with your API keys:
   ```env
   # Required API Keys
   ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here
   NEWS_API_KEY=your_news_api_key_here
   
   # Optional (for advanced features)
   TWITTER_BEARER_TOKEN=your_twitter_token_here
   POLYGON_API_KEY=your_polygon_api_key_here
   
   # Flask Configuration
   FLASK_ENV=development
   SECRET_KEY=your_secret_key_here
   ```

### Step 3: Test Your Setup

Run the data collection test:
```bash
python backend/data_collectors/stock_data_collector.py
```

Run the sentiment analysis test:
```bash
python backend/data_collectors/news_sentiment_collector.py
```

## 📊 Data Sources Overview

### Stock Market Data:
1. **Yahoo Finance** (Primary) - Real-time stock prices, historical data
2. **Alpha Vantage** (Secondary) - Additional market data and technical indicators
3. **Simulated Data** (Fallback) - Demo data when APIs are unavailable

### News & Sentiment Data:
1. **News API** - Latest financial news articles
2. **RSS Feeds** - Real-time news from major financial outlets
3. **VADER Sentiment** - Built-in sentiment analysis (no API needed)
4. **TextBlob** - Additional sentiment analysis (no API needed)

## 🔧 Configuration Options

### Update Intervals (in `backend/utils/config.py`):
- **Stock Data**: 60 seconds
- **News Data**: 300 seconds (5 minutes)
- **Sentiment Analysis**: 180 seconds (3 minutes)

### Default Stocks:
- AAPL, GOOGL, MSFT, AMZN, TSLA, META, NVDA, NFLX

### Rate Limits:
- **Alpha Vantage**: 5 calls per minute (conservative)
- **News API**: Automatically handled
- **Yahoo Finance**: No limits (free)

## 🚀 Running the Application

### Development Mode:
```bash
python backend/app.py
```

### Production Mode:
```bash
gunicorn --bind 0.0.0.0:5000 backend.app:app
```

## 🌐 Accessing the Dashboard

Once running, open your browser and go to:
- **Local**: http://localhost:5000
- **Network**: http://your-ip-address:5000

## 📱 Features Available

### Without Any API Keys:
- ✅ Stock price simulation
- ✅ Basic sentiment analysis
- ✅ Historical data simulation
- ✅ Full dashboard functionality
- ✅ Machine learning predictions

### With Alpha Vantage API:
- ✅ Real-time stock prices
- ✅ Accurate historical data
- ✅ Market indicators
- ✅ Technical analysis data

### With News API:
- ✅ Real-time news articles
- ✅ Accurate sentiment analysis
- ✅ News source tracking
- ✅ Sentiment trending

## 🔍 Testing Your Setup

### Test Stock Data Collection:
```python
from backend.data_collectors.stock_data_collector import StockDataCollector

collector = StockDataCollector()
connections = collector.test_connection()
data = collector.get_current_data('AAPL')
print(f"AAPL Data: {data}")
```

### Test Sentiment Analysis:
```python
from backend.data_collectors.news_sentiment_collector import NewsSentimentCollector

collector = NewsSentimentCollector()
sentiment = collector.get_sentiment_for_stock('AAPL')
print(f"AAPL Sentiment: {sentiment}")
```

## 🛡️ Security Best Practices

1. **Never commit your `.env` file** to version control
2. **Use environment variables** for production deployment
3. **Rotate your API keys** regularly
4. **Monitor your API usage** to avoid exceeding limits
5. **Use HTTPS** in production

## 🐛 Troubleshooting

### Common Issues:

1. **"API key not found" errors**:
   - Check your `.env` file exists
   - Verify API keys are correctly copied
   - Restart the application after updating `.env`

2. **"Rate limit exceeded" errors**:
   - Wait a few minutes before retrying
   - Check your API usage on the provider's dashboard
   - The app will automatically fall back to simulated data

3. **"Connection timeout" errors**:
   - Check your internet connection
   - Try running the test scripts individually
   - Some APIs may be temporarily unavailable

4. **"Module not found" errors**:
   - Run `pip install -r requirements.txt` again
   - Check your Python environment is activated

## 📈 Advanced Setup (Optional)

### Twitter API Integration:
1. Apply for Twitter Developer Account
2. Create a new app in Twitter Developer Portal
3. Get your Bearer Token
4. Add to `.env` file

### Polygon.io Integration:
1. Sign up at polygon.io
2. Get your free API key
3. Add to `.env` file

### Database Configuration:
The SQLite database is automatically created in the `database/` folder. No additional setup required.

## 🎯 Next Steps

1. **Start the application**: `python backend/app.py`
2. **Open the dashboard**: http://localhost:5000
3. **Explore the features**: Check different stocks, view predictions, analyze sentiment
4. **Customize**: Modify the stock list, update intervals, or add new features

## 💡 Tips for Best Results

1. **Start with free APIs** to test the system
2. **Monitor your API usage** to avoid hitting limits
3. **Test with different stocks** to see varied data
4. **Check the logs** for any error messages
5. **Experiment with the ML models** for better predictions

## 📞 Support

If you encounter any issues:
1. Check the console logs for error messages
2. Verify your API keys are correct
3. Test individual components using the test scripts
4. The system works with simulated data even without API keys

---

**Remember**: Even without any API keys, the system will work with simulated data, allowing you to test and develop the ML models and frontend features!
