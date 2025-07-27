#!/usr/bin/env python3
"""
Complete setup test for Real-time ML Stock Dashboard
This script tests all components to ensure the project is fully functional.
"""

import sys
import os
import time
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_configuration():
    """Test configuration loading"""
    print("🔧 Testing Configuration...")
    try:
        from utils.config import Config
        config = Config()
        print(f"✅ Configuration loaded successfully")
        print(f"   - Default stocks: {config.DEFAULT_STOCKS}")
        print(f"   - Log level: {config.LOG_LEVEL}")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_database():
    """Test database operations"""
    print("\n💾 Testing Database...")
    try:
        from utils.database_manager import DatabaseManager
        db = DatabaseManager()
        db.initialize_database()
        print("✅ Database initialized successfully")
        
        # Test portfolio operations
        result = db.get_portfolio()
        print(f"✅ Portfolio query successful: {len(result)} holdings")
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_stock_data_collection():
    """Test stock data collection"""
    print("\n📈 Testing Stock Data Collection...")
    try:
        from data_collectors.stock_data_collector import StockDataCollector
        collector = StockDataCollector()
        
        # Test connection
        connections = collector.test_connection()
        print(f"✅ Connection test completed: {connections}")
        
        # Test data collection
        data = collector.get_current_data('AAPL')
        print(f"✅ Stock data retrieved: AAPL @ ${data['current_price']}")
        
        return True
    except Exception as e:
        print(f"❌ Stock data collection test failed: {e}")
        return False

def test_sentiment_analysis():
    """Test sentiment analysis"""
    print("\n🧠 Testing Sentiment Analysis...")
    try:
        from data_collectors.news_sentiment_collector import NewsSentimentCollector
        collector = NewsSentimentCollector()
        
        # Test connection
        connections = collector.test_connection()
        print(f"✅ Sentiment connection test: {connections}")
        
        # Test sentiment analysis
        sentiment = collector.get_sentiment_for_stock('AAPL')
        print(f"✅ Sentiment analysis: AAPL score = {sentiment['compound_score']}")
        
        return True
    except Exception as e:
        print(f"❌ Sentiment analysis test failed: {e}")
        return False

def test_ml_predictions():
    """Test ML predictions"""
    print("\n🤖 Testing ML Predictions...")
    try:
        from ml_models.ensemble_predictor import EnsemblePredictor
        predictor = EnsemblePredictor()
        
        # Test prediction
        stock_data = {'current_price': 150.0}
        sentiment_data = {'compound_score': 0.1}
        
        prediction = predictor.predict_price('AAPL', stock_data, sentiment_data)
        print(f"✅ ML prediction: AAPL predicted @ ${prediction['predicted_price']}")
        
        return True
    except Exception as e:
        print(f"❌ ML prediction test failed: {e}")
        return False

def test_frontend_files():
    """Test frontend files exist"""
    print("\n🎨 Testing Frontend Files...")
    try:
        frontend_files = [
            'frontend/index.html',
            'frontend/css/styles.css',
            'frontend/js/app.js',
            'frontend/js/charts.js',
            'frontend/js/trading.js'
        ]
        
        for file_path in frontend_files:
            if os.path.exists(file_path):
                print(f"✅ {file_path} exists")
            else:
                print(f"❌ {file_path} missing")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Frontend files test failed: {e}")
        return False

def test_environment_setup():
    """Test environment setup"""
    print("\n🌍 Testing Environment Setup...")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        required_dirs = ['backend', 'frontend', 'database', 'backend/logs']
        for dir_path in required_dirs:
            if os.path.exists(dir_path):
                print(f"✅ {dir_path} directory exists")
            else:
                print(f"❌ {dir_path} directory missing")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Environment setup test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 REAL-TIME ML STOCK DASHBOARD - COMPLETE SETUP TEST")
    print("=" * 60)
    
    test_results = []
    
    # Run all tests
    test_results.append(test_environment_setup())
    test_results.append(test_configuration())
    test_results.append(test_database())
    test_results.append(test_stock_data_collection())
    test_results.append(test_sentiment_analysis())
    test_results.append(test_ml_predictions())
    test_results.append(test_frontend_files())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Your project is 100% complete and ready to run!")
        print("\n🚀 To start the application:")
        print("   1. cd backend")
        print("   2. python app.py")
        print("   3. Open http://localhost:5000 in your browser")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
