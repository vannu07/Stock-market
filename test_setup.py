#!/usr/bin/env python3
"""
Quick test script to verify the real-time stock market ML project setup.
Run this script to check if all components are working correctly.
"""

import sys
import os
import traceback
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_warning(text):
    print(f"⚠️  {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def test_imports():
    """Test if all required modules can be imported"""
    print_header("Testing Module Imports")
    
    required_modules = [
        'numpy', 'pandas', 'requests', 'flask', 'yfinance', 
        'textblob', 'vaderSentiment', 'nltk', 'sklearn', 'sqlite3'
    ]
    
    success_count = 0
    for module in required_modules:
        try:
            __import__(module)
            print_success(f"{module} imported successfully")
            success_count += 1
        except ImportError as e:
            print_error(f"{module} import failed: {e}")
    
    print(f"\n📊 Import Test Results: {success_count}/{len(required_modules)} modules imported successfully")
    
    if success_count < len(required_modules):
        print_warning("Some modules are missing. Run: pip install -r requirements.txt")
    
    return success_count == len(required_modules)

def test_configuration():
    """Test configuration setup"""
    print_header("Testing Configuration")
    
    try:
        from utils.config import Config
        config = Config()
        print_success("Configuration loaded successfully")
        
        # Test API keys
        alpha_key = config.get_api_key('alpha_vantage')
        news_key = config.get_api_key('news_api')
        
        if alpha_key and alpha_key != 'demo':
            print_success("Alpha Vantage API key configured")
        else:
            print_warning("Alpha Vantage API key not configured (will use simulated data)")
        
        if news_key and news_key != 'your_news_api_key':
            print_success("News API key configured")
        else:
            print_warning("News API key not configured (will use simulated data)")
        
        return True
        
    except Exception as e:
        print_error(f"Configuration test failed: {e}")
        return False

def test_database():
    """Test database functionality"""
    print_header("Testing Database")
    
    try:
        from utils.database_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        # Initialize database
        db_manager.initialize_database()
        print_success("Database initialized successfully")
        
        # Test database stats
        stats = db_manager.get_database_stats()
        print_info(f"Database size: {stats.get('database_size_bytes', 0)} bytes")
        
        return True
        
    except Exception as e:
        print_error(f"Database test failed: {e}")
        traceback.print_exc()
        return False

def test_stock_data_collection():
    """Test stock data collection"""
    print_header("Testing Stock Data Collection")
    
    try:
        from data_collectors.stock_data_collector import StockDataCollector
        collector = StockDataCollector()
        
        # Test connections
        connections = collector.test_connection()
        for service, status in connections.items():
            if status:
                print_success(f"{service} connection successful")
            else:
                print_warning(f"{service} connection failed (will use fallback)")
        
        # Test data collection
        data = collector.get_current_data('AAPL')
        if data:
            print_success(f"AAPL data collected: ${data['current_price']:.2f}")
            print_info(f"Data source: {data['source']}")
        
        # Test historical data
        hist_data = collector.get_historical_data('AAPL', 5)
        if hist_data:
            print_success(f"Historical data collected: {len(hist_data)} days")
        
        return True
        
    except Exception as e:
        print_error(f"Stock data collection test failed: {e}")
        traceback.print_exc()
        return False

def test_sentiment_analysis():
    """Test sentiment analysis"""
    print_header("Testing Sentiment Analysis")
    
    try:
        from data_collectors.news_sentiment_collector import NewsSentimentCollector
        collector = NewsSentimentCollector()
        
        # Test connections
        connections = collector.test_connection()
        for service, status in connections.items():
            if status:
                print_success(f"{service} connection successful")
            else:
                print_warning(f"{service} connection failed (will use simulated data)")
        
        # Test sentiment analysis
        sentiment = collector.get_sentiment_for_stock('AAPL')
        if sentiment:
            print_success(f"AAPL sentiment: {sentiment['sentiment_label']} ({sentiment['compound_score']:.3f})")
            print_info(f"Sentiment source: {sentiment['source']}")
        
        return True
        
    except Exception as e:
        print_error(f"Sentiment analysis test failed: {e}")
        traceback.print_exc()
        return False

def test_web_application():
    """Test if Flask app can be imported and configured"""
    print_header("Testing Web Application")
    
    try:
        from app import app
        print_success("Flask application imported successfully")
        
        # Test app configuration
        if app.config.get('SECRET_KEY'):
            print_success("Secret key configured")
        else:
            print_warning("Secret key not configured")
        
        print_info("To start the server, run: python backend/app.py")
        
        return True
        
    except Exception as e:
        print_error(f"Web application test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print_header("🚀 Real-Time Stock Market ML Project Setup Test")
    print_info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_configuration),
        ("Database", test_database),
        ("Stock Data Collection", test_stock_data_collection),
        ("Sentiment Analysis", test_sentiment_analysis),
        ("Web Application", test_web_application)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests += 1
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {e}")
    
    # Final results
    print_header("📊 Final Test Results")
    print(f"Tests passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print_success("🎉 All tests passed! Your setup is ready to go!")
        print_info("Next steps:")
        print_info("1. Run: python backend/app.py")
        print_info("2. Open: http://localhost:5000")
        print_info("3. Explore the dashboard!")
    elif passed_tests >= total_tests - 2:
        print_warning("⚠️  Most tests passed. Minor issues detected.")
        print_info("Your setup should work, but check the warnings above.")
    else:
        print_error("❌ Several tests failed. Please check the setup guide.")
        print_info("See SETUP_GUIDE.md for detailed instructions.")
    
    print_info(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
