import yfinance as yf
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import logging
from typing import Dict, List, Optional
import json
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import Config

# Set up logging
logging.basicConfig(level=logging.INFO, format=Config.LOG_FORMAT)
logger = logging.getLogger(__name__)

class StockDataCollector:
    """Collects real-time stock market data from multiple sources"""
    
    def __init__(self):
        self.config = Config()
        self.alpha_vantage_key = self.config.get_api_key('alpha_vantage')
        self.polygon_key = self.config.get_api_key('polygon')
        self.last_request_time = {}
        self.request_count = {}
        
    def get_current_data(self, symbol: str) -> Dict:
        """Get current stock data for a symbol"""
        try:
            # Try Yahoo Finance first (free and reliable)
            data = self._get_yahoo_data(symbol)
            if data:
                return data
                
            # Fallback to Alpha Vantage
            data = self._get_alpha_vantage_data(symbol)
            if data:
                return data
                
            # Fallback to simulated data for demo
            return self._get_simulated_data(symbol)
            
        except Exception as e:
            logger.error(f"Error getting current data for {symbol}: {e}")
            return self._get_simulated_data(symbol)
    
    def _get_yahoo_data(self, symbol: str) -> Optional[Dict]:
        """Get data from Yahoo Finance (Free)"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="2d")
            
            if hist.empty:
                return None
                
            current_price = hist['Close'].iloc[-1]
            previous_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            
            change = current_price - previous_price
            change_percent = (change / previous_price) * 100 if previous_price != 0 else 0
            
            return {
                'symbol': symbol,
                'current_price': float(current_price),
                'open_price': float(hist['Open'].iloc[-1]),
                'high_price': float(hist['High'].iloc[-1]),
                'low_price': float(hist['Low'].iloc[-1]),
                'volume': int(hist['Volume'].iloc[-1]),
                'change': float(change),
                'change_percent': float(change_percent),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'timestamp': datetime.now(),
                'source': 'yahoo_finance'
            }
            
        except Exception as e:
            logger.error(f"Yahoo Finance error for {symbol}: {e}")
            return None
    
    def _get_alpha_vantage_data(self, symbol: str) -> Optional[Dict]:
        """Get data from Alpha Vantage API"""
        try:
            # Rate limiting check
            if not self._check_rate_limit('alpha_vantage'):
                return None
                
            url = f"{self.config.ALPHA_VANTAGE_BASE_URL}?function=GLOBAL_QUOTE&symbol={symbol}&apikey={self.alpha_vantage_key}"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return None
                
            data = response.json()
            
            if 'Global Quote' not in data:
                return None
                
            quote = data['Global Quote']
            
            return {
                'symbol': symbol,
                'current_price': float(quote['05. price']),
                'open_price': float(quote['02. open']),
                'high_price': float(quote['03. high']),
                'low_price': float(quote['04. low']),
                'volume': int(quote['06. volume']),
                'change': float(quote['09. change']),
                'change_percent': float(quote['10. change percent'].replace('%', '')),
                'timestamp': datetime.now(),
                'source': 'alpha_vantage'
            }
            
        except Exception as e:
            logger.error(f"Alpha Vantage error for {symbol}: {e}")
            return None
    
    def _get_simulated_data(self, symbol: str) -> Dict:
        """Generate simulated stock data for demo purposes"""
        # Base prices for different stocks
        base_prices = {
            'AAPL': 150.0,
            'GOOGL': 2800.0,
            'MSFT': 330.0,
            'AMZN': 3400.0,
            'TSLA': 800.0,
            'META': 320.0,
            'NVDA': 450.0,
            'NFLX': 400.0
        }
        
        base_price = base_prices.get(symbol, 100.0)
        
        # Add some random variation
        variation = np.random.normal(0, 0.02)  # 2% standard deviation
        current_price = base_price * (1 + variation)
        
        # Generate other values
        open_price = current_price * (1 + np.random.normal(0, 0.01))
        high_price = max(current_price, open_price) * (1 + abs(np.random.normal(0, 0.01)))
        low_price = min(current_price, open_price) * (1 - abs(np.random.normal(0, 0.01)))
        volume = int(np.random.normal(1000000, 300000))
        
        # Calculate change
        previous_price = base_price
        change = current_price - previous_price
        change_percent = (change / previous_price) * 100
        
        return {
            'symbol': symbol,
            'current_price': round(current_price, 2),
            'open_price': round(open_price, 2),
            'high_price': round(high_price, 2),
            'low_price': round(low_price, 2),
            'volume': max(volume, 100000),
            'change': round(change, 2),
            'change_percent': round(change_percent, 2),
            'market_cap': int(current_price * 1000000000),  # Simulated market cap
            'pe_ratio': round(np.random.normal(25, 5), 2),
            'timestamp': datetime.now(),
            'source': 'simulated'
        }
    
    def get_historical_data(self, symbol: str, days: int = 30) -> List[Dict]:
        """Get historical stock data"""
        try:
            # Try Yahoo Finance first
            ticker = yf.Ticker(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            hist = ticker.history(start=start_date, end=end_date)
            
            if hist.empty:
                return self._get_simulated_historical_data(symbol, days)
            
            historical_data = []
            for date, row in hist.iterrows():
                historical_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                })
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            return self._get_simulated_historical_data(symbol, days)
    
    def _get_simulated_historical_data(self, symbol: str, days: int) -> List[Dict]:
        """Generate simulated historical data"""
        base_prices = {
            'AAPL': 150.0,
            'GOOGL': 2800.0,
            'MSFT': 330.0,
            'AMZN': 3400.0,
            'TSLA': 800.0,
            'META': 320.0,
            'NVDA': 450.0,
            'NFLX': 400.0
        }
        
        base_price = base_prices.get(symbol, 100.0)
        historical_data = []
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i)
            
            # Create a trend with some randomness
            trend = 0.001 * i  # Slight upward trend
            noise = np.random.normal(0, 0.02)
            
            close_price = base_price * (1 + trend + noise)
            open_price = close_price * (1 + np.random.normal(0, 0.01))
            high_price = max(close_price, open_price) * (1 + abs(np.random.normal(0, 0.01)))
            low_price = min(close_price, open_price) * (1 - abs(np.random.normal(0, 0.01)))
            volume = int(np.random.normal(1000000, 300000))
            
            historical_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': max(volume, 100000)
            })
        
        return historical_data
    
    def get_multiple_stocks_data(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get data for multiple stocks"""
        results = {}
        
        for symbol in symbols:
            try:
                data = self.get_current_data(symbol)
                if data:
                    results[symbol] = data
                    
                # Add small delay to avoid rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error getting data for {symbol}: {e}")
                continue
        
        return results
    
    def _check_rate_limit(self, service: str) -> bool:
        """Check if we're within rate limits for a service"""
        current_time = time.time()
        
        # Initialize tracking for service
        if service not in self.last_request_time:
            self.last_request_time[service] = current_time
            self.request_count[service] = 0
            return True
        
        # Reset counter if a minute has passed
        if current_time - self.last_request_time[service] > 60:
            self.request_count[service] = 0
            self.last_request_time[service] = current_time
        
        # Check if we're under the limit
        if self.request_count[service] < 5:  # Conservative limit
            self.request_count[service] += 1
            return True
        
        return False
    
    def get_market_overview(self) -> Dict:
        """Get overall market overview"""
        try:
            # Get major indices
            indices = ['^GSPC', '^DJI', '^IXIC']  # S&P 500, Dow Jones, NASDAQ
            market_data = {}
            
            for index in indices:
                try:
                    ticker = yf.Ticker(index)
                    hist = ticker.history(period="2d")
                    
                    if not hist.empty:
                        current = hist['Close'].iloc[-1]
                        previous = hist['Close'].iloc[-2] if len(hist) > 1 else current
                        change = current - previous
                        change_percent = (change / previous) * 100 if previous != 0 else 0
                        
                        market_data[index] = {
                            'value': round(current, 2),
                            'change': round(change, 2),
                            'change_percent': round(change_percent, 2)
                        }
                except Exception as e:
                    logger.error(f"Error getting data for {index}: {e}")
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error getting market overview: {e}")
            return {}
    
    def test_connection(self) -> Dict[str, bool]:
        """Test connection to all data sources"""
        results = {}
        
        # Test Yahoo Finance
        try:
            ticker = yf.Ticker('AAPL')
            hist = ticker.history(period="1d")
            results['yahoo_finance'] = not hist.empty
        except:
            results['yahoo_finance'] = False
        
        # Test Alpha Vantage
        try:
            if self.alpha_vantage_key != 'demo':
                url = f"{self.config.ALPHA_VANTAGE_BASE_URL}?function=GLOBAL_QUOTE&symbol=AAPL&apikey={self.alpha_vantage_key}"
                response = requests.get(url, timeout=10)
                results['alpha_vantage'] = response.status_code == 200
            else:
                results['alpha_vantage'] = False
        except:
            results['alpha_vantage'] = False
        
        return results

# Example usage and testing
if __name__ == "__main__":
    collector = StockDataCollector()
    
    # Test connection
    print("Testing connections...")
    connections = collector.test_connection()
    for service, status in connections.items():
        print(f"{service}: {'✓' if status else '✗'}")
    
    # Get sample data
    print("\nGetting sample data...")
    data = collector.get_current_data('AAPL')
    print(f"AAPL Data: {data}")
    
    # Get market overview
    print("\nGetting market overview...")
    market = collector.get_market_overview()
    print(f"Market Overview: {market}")
