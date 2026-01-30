import os
import sqlite3
import sys
import threading
import time
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler

import schedule
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# Add backend folder to sys.path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

# Import custom modules
from data_collectors.news_sentiment_collector import NewsSentimentCollector
from data_collectors.stock_data_collector import StockDataCollector
from ml_models.ensemble_predictor import EnsemblePredictor
from utils.config import Config
from utils.database_manager import DatabaseManager

# Configure logging
log_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
logging.basicConfig(
    level=log_level,
    format=Config.LOG_FORMAT,
    handlers=[
        RotatingFileHandler(Config.LOG_FILE, maxBytes=10485760, backupCount=5),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# Initialize Flask app with proper configuration
app = Flask(
    __name__,
    template_folder="/Stock-market/frontend",
    static_folder="/Stock-market/frontend",
    static_url_path="/static",
)
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY", "realtime-ml-stock-dashboard-secret-key-2025"
)
app.config["DEBUG"] = os.getenv("FLASK_DEBUG", "True").lower() == "true"
CORS(app)
socketio = SocketIO(
    app,
    cors_allowed_origins=os.getenv("WEBSOCKET_CORS_ALLOWED_ORIGINS", "*"),
    async_mode=os.getenv("WEBSOCKET_ASYNC_MODE", "threading"),
)

# Initialize components
db_manager = DatabaseManager()
stock_collector = StockDataCollector()
sentiment_collector = NewsSentimentCollector()
ensemble_predictor = EnsemblePredictor()

# Global variables
active_stocks = Config.DEFAULT_STOCKS
prediction_cache = {}
sentiment_cache = {}

logger.info(f"Starting Real-time ML Stock Dashboard...")
logger.info(f"Active stocks: {active_stocks}")
logger.info(f"Log level: {Config.LOG_LEVEL}")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/stocks")
def get_stocks():
    """Get list of available stocks"""
    return jsonify({"stocks": active_stocks})


@app.route("/api/stock/<symbol>")
def get_stock_data(symbol):
    """Get current stock data and predictions"""
    try:
        # Get current stock data
        stock_data = stock_collector.get_current_data(symbol)

        # Get sentiment analysis
        sentiment_data = sentiment_collector.get_sentiment_for_stock(symbol)

        # Get price prediction
        if symbol not in prediction_cache or _is_cache_expired(symbol):
            prediction = ensemble_predictor.predict_price(
                symbol, stock_data, sentiment_data
            )
            prediction_cache[symbol] = {
                "prediction": prediction,
                "timestamp": datetime.now(),
            }

        result = {
            "symbol": symbol,
            "current_price": stock_data["current_price"],
            "change_percent": stock_data["change_percent"],
            "volume": stock_data["volume"],
            "prediction": prediction_cache[symbol]["prediction"],
            "sentiment": sentiment_data,
            "timestamp": datetime.now().isoformat(),
        }

        return jsonify(result)

    except Exception as e:
        safe_symbol = (symbol or "").replace("\r", "").replace("\n", "")
        logger.exception(f"Exception in get_stock_data for symbol '{safe_symbol}'")
        return jsonify({"error": "An internal error has occurred."}), 500


@app.route("/api/historical/<symbol>")
def get_historical_data(symbol):
    """Get historical data for charts"""
    try:
        days = request.args.get("days", 30, type=int)
        data = stock_collector.get_historical_data(symbol, days)
        return jsonify(data)
    except Exception as e:
        safe_symbol = (symbol or "").replace("\r", "").replace("\n", "")
        logger.exception(f"Exception in get_historical_data for symbol '{safe_symbol}'")
        return jsonify({"error": "An internal error has occurred."}), 500


@app.route("/api/sentiment/<symbol>")
def get_sentiment_analysis(symbol):
    """Get detailed sentiment analysis"""
    try:
        sentiment_data = sentiment_collector.get_detailed_sentiment(symbol)
        return jsonify(sentiment_data)
    except Exception as e:
        safe_symbol = (symbol or "").replace("\r", "").replace("\n", "")
        logger.exception(
            f"Exception in get_sentiment_analysis for symbol '{safe_symbol}'"
        )
        return jsonify({"error": "An internal error has occurred."}), 500


@app.route("/api/predictions/<symbol>")
def get_predictions(symbol):
    """Get price predictions from different models"""
    try:
        predictions = ensemble_predictor.get_all_predictions(symbol)
        return jsonify(predictions)
    except Exception as e:
        safe_symbol = (symbol or "").replace("\r", "").replace("\n", "")
        logger.exception(f"Exception in get_predictions for symbol '{safe_symbol}'")
        return jsonify({"error": "An internal error has occurred."}), 500


@app.route("/api/news/<symbol>")
def get_news(symbol):
    """Get news articles for a specific stock"""
    try:
        # Get news articles (this would come from the news collector)
        news_articles = sentiment_collector._get_news_api_data(symbol)
        rss_news = sentiment_collector._get_rss_news(symbol)

        all_news = news_articles + rss_news

        # Sort by date and limit to recent articles
        all_news = sorted(
            all_news, key=lambda x: x.get("published_date", ""), reverse=True
        )[:10]

        return jsonify({"symbol": symbol, "articles": all_news, "count": len(all_news)})
    except Exception as e:
        safe_symbol = (symbol or "").replace("\r", "").replace("\n", "")
        logger.error(f"Error getting news for {safe_symbol}: {e}")
        return jsonify({"symbol": symbol, "articles": [], "count": 0})


@app.route("/api/portfolio", methods=["GET", "POST"])
def handle_portfolio():
    """Handle portfolio operations"""
    if request.method == "GET":
        portfolio = db_manager.get_portfolio()
        return jsonify(portfolio)

    elif request.method == "POST":
        data = request.json
        symbol = data.get("symbol")
        quantity = data.get("quantity")
        action = data.get("action")  # 'buy' or 'sell'

        result = db_manager.update_portfolio(symbol, quantity, action)
        return jsonify(result)


@socketio.on("connect")
def handle_connect():
    """Handle client connection"""
    logger.info("Client connected")
    emit("connected", {"data": "Connected to real-time stock updates"})


@socketio.on("subscribe")
def handle_subscribe(data):
    """Handle subscription to stock updates"""
    symbol = data.get("symbol")
    if symbol in active_stocks:
        safe_symbol = (symbol or "").replace("\r", "").replace("\n", "")
        logger.info(f"Client subscribed to {safe_symbol}")
        emit("subscribed", {"symbol": symbol})


@socketio.on("disconnect")
def handle_disconnect():
    """Handle client disconnection"""
    logger.info("Client disconnected")


def _is_cache_expired(symbol, expiry_minutes=5):
    """Check if cache is expired"""
    if symbol not in prediction_cache:
        return True

    cache_time = prediction_cache[symbol]["timestamp"]
    return datetime.now() - cache_time > timedelta(minutes=expiry_minutes)


def broadcast_updates():
    """Broadcast real-time updates to all clients"""
    while True:
        try:
            for symbol in active_stocks:
                # Get latest data
                stock_data = stock_collector.get_current_data(symbol)
                sentiment_data = sentiment_collector.get_sentiment_for_stock(symbol)

                # Prepare update
                update = {
                    "symbol": symbol,
                    "price": stock_data["current_price"],
                    "change": stock_data["change_percent"],
                    "volume": stock_data["volume"],
                    "sentiment_score": sentiment_data["compound_score"],
                    "timestamp": datetime.now().isoformat(),
                }

                # Broadcast to all clients
                socketio.emit("stock_update", update)

            time.sleep(10)  # Update every 10 seconds

        except Exception as e:
            logger.error(f"Error in broadcast_updates: {e}")
            time.sleep(30)


def schedule_model_retraining():
    """Schedule periodic model retraining"""
    try:
        schedule.every(6).hours.do(ensemble_predictor.retrain_models)
        # schedule.every(1).hour.do(sentiment_collector.update_sentiment_models)  # Commented out for now

        while True:
            schedule.run_pending()
            time.sleep(3600)  # Check every hour
    except Exception as e:
        logger.error(f"Error in schedule_model_retraining: {e}")


if __name__ == "__main__":
    logger.info("Initializing Real-time ML Stock Dashboard...")

    # Initialize database
    try:
        db_manager.initialize_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

    # Start background threads
    update_thread = threading.Thread(target=broadcast_updates)
    update_thread.daemon = True
    update_thread.start()
    logger.info("Background update thread started")

    schedule_thread = threading.Thread(target=schedule_model_retraining)
    schedule_thread.daemon = True
    schedule_thread.start()
    logger.info("Model retraining scheduler started")

    # Run the app
    flask_host = os.getenv("FLASK_HOST", "127.0.0.1")
    flask_port = int(os.getenv("FLASK_PORT", 5000))
    flask_debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"

    logger.info(f"Starting Flask server on {flask_host}:{flask_port}")
    socketio.run(app, debug=flask_debug, host=flask_host, port=flask_port)
