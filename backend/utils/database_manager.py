import sqlite3
import os
from datetime import datetime
import json
import pandas as pd

class DatabaseManager:
    def __init__(self, db_path='../database/stock_market.db'):
        self.db_path = os.path.abspath(db_path)
        self.ensure_directory_exists()
    
    def ensure_directory_exists(self):
        """Ensure database directory exists"""
        directory = os.path.dirname(self.db_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def initialize_database(self):
        """Initialize all database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Stock data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    open_price REAL,
                    close_price REAL,
                    high_price REAL,
                    low_price REAL,
                    volume INTEGER,
                    change_percent REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Sentiment data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sentiment_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    source TEXT NOT NULL,
                    content TEXT,
                    sentiment_score REAL,
                    sentiment_label TEXT,
                    compound_score REAL,
                    positive_score REAL,
                    negative_score REAL,
                    neutral_score REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Predictions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    model_name TEXT NOT NULL,
                    prediction_price REAL,
                    confidence_score REAL,
                    prediction_horizon INTEGER,
                    actual_price REAL,
                    accuracy REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Portfolio table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolio (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    buy_price REAL,
                    current_price REAL,
                    total_value REAL,
                    profit_loss REAL,
                    profit_loss_percent REAL,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # News articles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS news_articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT,
                    source TEXT,
                    published_date DATETIME,
                    content TEXT,
                    sentiment_score REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Model performance table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS model_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    accuracy REAL,
                    mse REAL,
                    rmse REAL,
                    mae REAL,
                    r2_score REAL,
                    last_trained DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_stock_symbol_timestamp ON stock_data(symbol, timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sentiment_symbol_timestamp ON sentiment_data(symbol, timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictions_symbol_timestamp ON predictions(symbol, timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_portfolio_symbol ON portfolio(symbol)')
            
            conn.commit()
    
    def insert_stock_data(self, symbol, data):
        """Insert stock data into database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO stock_data (symbol, timestamp, open_price, close_price, 
                                      high_price, low_price, volume, change_percent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                symbol,
                data['timestamp'],
                data['open_price'],
                data['close_price'],
                data['high_price'],
                data['low_price'],
                data['volume'],
                data['change_percent']
            ))
            conn.commit()
    
    def insert_sentiment_data(self, symbol, sentiment_data):
        """Insert sentiment data into database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO sentiment_data (symbol, timestamp, source, content, 
                                          sentiment_score, sentiment_label, compound_score,
                                          positive_score, negative_score, neutral_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                symbol,
                sentiment_data['timestamp'],
                sentiment_data['source'],
                sentiment_data['content'],
                sentiment_data['sentiment_score'],
                sentiment_data['sentiment_label'],
                sentiment_data['compound_score'],
                sentiment_data['positive_score'],
                sentiment_data['negative_score'],
                sentiment_data['neutral_score']
            ))
            conn.commit()
    
    def insert_prediction(self, symbol, prediction_data):
        """Insert prediction into database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO predictions (symbol, timestamp, model_name, prediction_price,
                                       confidence_score, prediction_horizon)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                symbol,
                prediction_data['timestamp'],
                prediction_data['model_name'],
                prediction_data['prediction_price'],
                prediction_data['confidence_score'],
                prediction_data['prediction_horizon']
            ))
            conn.commit()
    
    def update_prediction_accuracy(self, prediction_id, actual_price):
        """Update prediction accuracy when actual price is known"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE predictions 
                SET actual_price = ?, 
                    accuracy = ABS(1 - (ABS(prediction_price - ?) / prediction_price))
                WHERE id = ?
            ''', (actual_price, actual_price, prediction_id))
            conn.commit()
    
    def get_historical_data(self, symbol, days=30):
        """Get historical stock data"""
        with self.get_connection() as conn:
            query = '''
                SELECT timestamp, open_price, close_price, high_price, low_price, volume
                FROM stock_data 
                WHERE symbol = ? AND timestamp >= datetime('now', '-{} days')
                ORDER BY timestamp
            '''.format(days)
            
            return pd.read_sql_query(query, conn, params=(symbol,))
    
    def get_sentiment_history(self, symbol, days=7):
        """Get sentiment history for a stock"""
        with self.get_connection() as conn:
            query = '''
                SELECT timestamp, compound_score, positive_score, negative_score, neutral_score
                FROM sentiment_data 
                WHERE symbol = ? AND timestamp >= datetime('now', '-{} days')
                ORDER BY timestamp
            '''.format(days)
            
            return pd.read_sql_query(query, conn, params=(symbol,))
    
    def get_model_performance(self, model_name=None):
        """Get model performance metrics"""
        with self.get_connection() as conn:
            if model_name:
                query = '''
                    SELECT * FROM model_performance 
                    WHERE model_name = ? 
                    ORDER BY created_at DESC
                '''
                return pd.read_sql_query(query, conn, params=(model_name,))
            else:
                query = '''
                    SELECT * FROM model_performance 
                    ORDER BY created_at DESC
                '''
                return pd.read_sql_query(query, conn)
    
    def update_portfolio(self, symbol, quantity, action, current_price=None):
        """Update portfolio holdings"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if stock exists in portfolio
            cursor.execute('SELECT * FROM portfolio WHERE symbol = ?', (symbol,))
            existing = cursor.fetchone()
            
            if existing:
                current_quantity = existing[2]  # quantity column
                
                if action == 'buy':
                    new_quantity = current_quantity + quantity
                elif action == 'sell':
                    new_quantity = max(0, current_quantity - quantity)
                
                # Update existing record
                cursor.execute('''
                    UPDATE portfolio 
                    SET quantity = ?, current_price = ?, last_updated = CURRENT_TIMESTAMP
                    WHERE symbol = ?
                ''', (new_quantity, current_price, symbol))
            else:
                # Insert new record
                if action == 'buy':
                    cursor.execute('''
                        INSERT INTO portfolio (symbol, quantity, buy_price, current_price)
                        VALUES (?, ?, ?, ?)
                    ''', (symbol, quantity, current_price, current_price))
            
            conn.commit()
            return {'success': True, 'message': f'Portfolio updated for {symbol}'}
    
    def get_portfolio(self):
        """Get current portfolio"""
        with self.get_connection() as conn:
            query = '''
                SELECT symbol, quantity, buy_price, current_price, 
                       (quantity * current_price) as total_value,
                       ((current_price - buy_price) * quantity) as profit_loss,
                       (((current_price - buy_price) / buy_price) * 100) as profit_loss_percent
                FROM portfolio 
                WHERE quantity > 0
                ORDER BY total_value DESC
            '''
            return pd.read_sql_query(query, conn).to_dict('records')
    
    def insert_news_article(self, article_data):
        """Insert news article into database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO news_articles (symbol, title, url, source, published_date, 
                                         content, sentiment_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                article_data['symbol'],
                article_data['title'],
                article_data['url'],
                article_data['source'],
                article_data['published_date'],
                article_data['content'],
                article_data['sentiment_score']
            ))
            conn.commit()
    
    def get_recent_news(self, symbol, limit=10):
        """Get recent news for a stock"""
        with self.get_connection() as conn:
            query = '''
                SELECT title, url, source, published_date, sentiment_score
                FROM news_articles 
                WHERE symbol = ? 
                ORDER BY published_date DESC 
                LIMIT ?
            '''
            return pd.read_sql_query(query, conn, params=(symbol, limit)).to_dict('records')
    
    def cleanup_old_data(self, days=90):
        """Clean up old data to keep database size manageable"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Clean up old stock data
            cursor.execute('''
                DELETE FROM stock_data 
                WHERE timestamp < datetime('now', '-{} days')
            '''.format(days))
            
            # Clean up old sentiment data
            cursor.execute('''
                DELETE FROM sentiment_data 
                WHERE timestamp < datetime('now', '-{} days')
            '''.format(days))
            
            # Clean up old predictions
            cursor.execute('''
                DELETE FROM predictions 
                WHERE timestamp < datetime('now', '-{} days')
            '''.format(days))
            
            conn.commit()
    
    def get_database_stats(self):
        """Get database statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Table row counts
            tables = ['stock_data', 'sentiment_data', 'predictions', 'portfolio', 'news_articles']
            for table in tables:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                stats[f'{table}_count'] = cursor.fetchone()[0]
            
            # Database size
            cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
            stats['database_size_bytes'] = cursor.fetchone()[0]
            
            return stats
