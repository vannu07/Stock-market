import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for API keys and settings"""
    
    # Database Configuration
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'database', 'stock_market.db')
    
    # API Keys (You'll need to get these from respective providers)
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
    POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')
    IEX_API_KEY = os.getenv('IEX_API_KEY', 'Optional: Not needed if using Yahoo Finance')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # API URLs
    ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"
    NEWS_API_BASE_URL = "https://newsapi.org/v2"
    TWITTER_API_BASE_URL = "https://api.twitter.com/2"
    POLYGON_BASE_URL = "https://api.polygon.io"
    
    # Data Update Intervals (in seconds)
    STOCK_DATA_UPDATE_INTERVAL = int(os.getenv('STOCK_UPDATE_INTERVAL', 60))
    NEWS_UPDATE_INTERVAL = int(os.getenv('NEWS_UPDATE_INTERVAL', 300))
    SENTIMENT_UPDATE_INTERVAL = int(os.getenv('SENTIMENT_UPDATE_INTERVAL', 180))
    
    # Default Stock Symbols
    DEFAULT_STOCKS = os.getenv('DEFAULT_STOCKS', 'AAPL,GOOGL,MSFT,AMZN,TSLA,META,NVDA,NFLX').split(',')
    
    # Model Configuration
    MODEL_RETRAIN_INTERVAL = 21600  # 6 hours in seconds
    PREDICTION_HORIZON = 24  # hours
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    
    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE = 60
    
    @staticmethod
    def get_api_key(service):
        """Get API key for a specific service"""
        keys = {
            'alpha_vantage': Config.ALPHA_VANTAGE_API_KEY,
            'news_api': Config.NEWS_API_KEY,
            'twitter': Config.TWITTER_BEARER_TOKEN,
            'polygon': Config.POLYGON_API_KEY
        }
        return keys.get(service, None)
    
    @staticmethod
    def validate_config():
        """Validate configuration settings"""
        required_keys = [
            'ALPHA_VANTAGE_API_KEY',
            'NEWS_API_KEY'
        ]
        
        missing_keys = []
        for key in required_keys:
            if not os.getenv(key):
                missing_keys.append(key)
        
        if missing_keys:
            print(f"Warning: Missing API keys: {', '.join(missing_keys)}")
            print("Please set these environment variables or update the .env file")
        
        return len(missing_keys) == 0
