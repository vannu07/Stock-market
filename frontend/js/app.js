// Real-time Stock Market Dashboard - Main Application
class StockDashboard {
    constructor() {
        this.socket = null;
        this.currentStock = 'AAPL';
        this.updateInterval = null;
        this.charts = {};
        this.isLoading = false;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupWebSocket();
        this.loadInitialData();
        this.startAutoUpdates();
        
        // Hide loading screen after 2 seconds
        setTimeout(() => {
            this.hideLoadingScreen();
        }, 2000);
    }

    setupEventListeners() {
        // Stock selector
        document.getElementById('stock-selector').addEventListener('change', (e) => {
            this.currentStock = e.target.value;
            this.loadStockData();
        });

        // Refresh button
        document.getElementById('refresh-btn').addEventListener('click', () => {
            this.refreshData();
        });

        // Chart period buttons
        document.querySelectorAll('[data-period]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('[data-period]').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.updateChartPeriod(e.target.dataset.period);
            });
        });

        // Modal controls
        document.getElementById('close-modal').addEventListener('click', () => {
            this.closeModal();
        });

        document.getElementById('cancel-trade').addEventListener('click', () => {
            this.closeModal();
        });

        document.getElementById('execute-trade').addEventListener('click', () => {
            this.executeTrade();
        });
    }

    setupWebSocket() {
        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('Connected to WebSocket');
            this.updateConnectionStatus('Connected');
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from WebSocket');
            this.updateConnectionStatus('Disconnected');
        });

        this.socket.on('stock_update', (data) => {
            this.handleStockUpdate(data);
        });

        this.socket.on('sentiment_update', (data) => {
            this.handleSentimentUpdate(data);
        });
    }

    async loadInitialData() {
        try {
            this.showLoading();
            
            // Load available stocks
            await this.loadStocks();
            
            // Load market overview
            await this.loadMarketOverview();
            
            // Load initial stock data
            await this.loadStockData();
            
            // Load portfolio
            await this.loadPortfolio();
            
            this.hideLoading();
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showError('Failed to load initial data');
        }
    }

    async loadStocks() {
        try {
            const response = await fetch('/api/stocks');
            const data = await response.json();
            
            this.updateWatchlist(data.stocks);
            this.updateStockSelector(data.stocks);
        } catch (error) {
            console.error('Error loading stocks:', error);
        }
    }

    async loadMarketOverview() {
        // Simulate market data - in real implementation, this would come from API
        const marketData = [
            { label: 'S&P 500', value: '4,567.89', change: '+0.45%', positive: true },
            { label: 'NASDAQ', value: '14,234.56', change: '+0.78%', positive: true },
            { label: 'DOW', value: '34,567.12', change: '-0.23%', positive: false },
            { label: 'VIX', value: '18.45', change: '+2.34%', positive: false }
        ];

        this.updateMarketIndicators(marketData);
    }

    async loadStockData() {
        try {
            this.showLoading();
            
            const response = await fetch(`/api/stock/${this.currentStock}`);
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.updateStockInfo(data);
            this.updatePredictions(data.prediction);
            this.updateSentiment(data.sentiment);
            
            // Load historical data for chart
            await this.loadHistoricalData();
            
            this.hideLoading();
        } catch (error) {
            console.error('Error loading stock data:', error);
            this.showError(`Failed to load data for ${this.currentStock}`);
        }
    }

    async loadHistoricalData() {
        try {
            const response = await fetch(`/api/historical/${this.currentStock}?days=30`);
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.updatePriceChart(data);
        } catch (error) {
            console.error('Error loading historical data:', error);
        }
    }

    async loadPortfolio() {
        try {
            const response = await fetch('/api/portfolio');
            const data = await response.json();
            
            this.updatePortfolio(data);
        } catch (error) {
            console.error('Error loading portfolio:', error);
        }
    }

    updateWatchlist(stocks) {
        const watchlist = document.getElementById('watchlist');
        watchlist.innerHTML = '';
        
        stocks.forEach(stock => {
            const item = document.createElement('div');
            item.className = 'watchlist-item';
            item.innerHTML = `
                <div class="stock-symbol">${stock}</div>
                <div class="stock-price" id="price-${stock}">$0.00</div>
                <div class="stock-change" id="change-${stock}">+0.00%</div>
            `;
            
            item.addEventListener('click', () => {
                this.selectStock(stock);
            });
            
            watchlist.appendChild(item);
        });
    }

    updateStockSelector(stocks) {
        const selector = document.getElementById('stock-selector');
        selector.innerHTML = '';
        
        stocks.forEach(stock => {
            const option = document.createElement('option');
            option.value = stock;
            option.textContent = `${stock}`;
            selector.appendChild(option);
        });
    }

    updateMarketIndicators(indicators) {
        const container = document.getElementById('market-indicators');
        container.innerHTML = '';
        
        indicators.forEach(indicator => {
            const item = document.createElement('div');
            item.className = 'market-indicator';
            item.innerHTML = `
                <div class="indicator-value ${indicator.positive ? 'positive' : 'negative'}">${indicator.value}</div>
                <div class="indicator-label">${indicator.label}</div>
                <div class="indicator-change ${indicator.positive ? 'positive' : 'negative'}">${indicator.change}</div>
            `;
            container.appendChild(item);
        });
    }

    updateStockInfo(data) {
        document.getElementById('current-price').textContent = `$${data.current_price.toFixed(2)}`;
        
        const changeElement = document.getElementById('price-change');
        const changePercent = data.change_percent;
        const changeClass = changePercent >= 0 ? 'positive' : 'negative';
        const changeSymbol = changePercent >= 0 ? '+' : '';
        
        changeElement.textContent = `${changeSymbol}${changePercent.toFixed(2)}%`;
        changeElement.className = `price-change ${changeClass}`;
        
        document.getElementById('volume').textContent = this.formatNumber(data.volume);
        
        // Update market cap and P/E ratio (simulated)
        document.getElementById('market-cap').textContent = this.formatNumber(data.current_price * 1000000000);
        document.getElementById('pe-ratio').textContent = (Math.random() * 30 + 10).toFixed(2);
        
        // Update last update time
        document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
    }

    updatePredictions(predictions) {
        if (!predictions) return;
        
        // Update individual model predictions (simulated)
        document.getElementById('lstm-prediction').textContent = `$${(predictions.predicted_price * 1.02).toFixed(2)}`;
        document.getElementById('lstm-confidence').textContent = `${(predictions.confidence * 0.9 * 100).toFixed(0)}%`;
        
        document.getElementById('rf-prediction').textContent = `$${(predictions.predicted_price * 0.98).toFixed(2)}`;
        document.getElementById('rf-confidence').textContent = `${(predictions.confidence * 0.85 * 100).toFixed(0)}%`;
        
        document.getElementById('xgb-prediction').textContent = `$${(predictions.predicted_price * 1.01).toFixed(2)}`;
        document.getElementById('xgb-confidence').textContent = `${(predictions.confidence * 0.88 * 100).toFixed(0)}%`;
        
        // Update ensemble prediction
        document.getElementById('ensemble-prediction').textContent = `$${predictions.predicted_price.toFixed(2)}`;
        document.getElementById('ensemble-confidence').textContent = `${(predictions.confidence * 100).toFixed(0)}%`;
    }

    updateSentiment(sentiment) {
        if (!sentiment) return;
        
        const score = sentiment.compound_score || Math.random() * 2 - 1; // -1 to 1
        const scoreElement = document.getElementById('sentiment-score');
        const circleElement = document.getElementById('sentiment-circle');
        
        scoreElement.textContent = score.toFixed(2);
        
        // Update circle color based on sentiment
        if (score > 0.1) {
            circleElement.style.background = 'linear-gradient(135deg, #10b981, #059669)';
        } else if (score < -0.1) {
            circleElement.style.background = 'linear-gradient(135deg, #ef4444, #dc2626)';
        } else {
            circleElement.style.background = 'linear-gradient(135deg, #64748b, #475569)';
        }
        
        // Update breakdown (simulated)
        const positive = Math.max(0, score * 50 + 50);
        const negative = Math.max(0, -score * 50 + 50);
        const neutral = 100 - positive - negative;
        
        document.getElementById('positive-percent').textContent = `${positive.toFixed(0)}%`;
        document.getElementById('negative-percent').textContent = `${negative.toFixed(0)}%`;
        document.getElementById('neutral-percent').textContent = `${neutral.toFixed(0)}%`;
    }

    updatePortfolio(portfolio) {
        // Update portfolio summary (simulated)
        document.getElementById('portfolio-value').textContent = '$25,430.50';
        document.getElementById('portfolio-pnl').textContent = '+$1,234.56';
    }

    updatePriceChart(data) {
        const ctx = document.getElementById('priceChart').getContext('2d');
        
        // Destroy existing chart if it exists
        if (this.charts.priceChart) {
            this.charts.priceChart.destroy();
        }
        
        // Generate sample data if no real data
        const labels = [];
        const prices = [];
        const now = new Date();
        
        for (let i = 29; i >= 0; i--) {
            const date = new Date(now);
            date.setDate(date.getDate() - i);
            labels.push(date.toLocaleDateString());
            prices.push(Math.random() * 50 + 150); // Random price between 150-200
        }
        
        this.charts.priceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: this.currentStock,
                    data: prices,
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    handleStockUpdate(data) {
        // Update watchlist prices
        const priceElement = document.getElementById(`price-${data.symbol}`);
        const changeElement = document.getElementById(`change-${data.symbol}`);
        
        if (priceElement) {
            priceElement.textContent = `$${data.price.toFixed(2)}`;
        }
        
        if (changeElement) {
            const changeClass = data.change >= 0 ? 'positive' : 'negative';
            const changeSymbol = data.change >= 0 ? '+' : '';
            changeElement.textContent = `${changeSymbol}${data.change.toFixed(2)}%`;
            changeElement.className = `stock-change ${changeClass}`;
        }
        
        // Update current stock if it matches
        if (data.symbol === this.currentStock) {
            this.updateStockInfo(data);
        }
    }

    handleSentimentUpdate(data) {
        if (data.symbol === this.currentStock) {
            this.updateSentiment(data);
        }
    }

    selectStock(stock) {
        this.currentStock = stock;
        document.getElementById('stock-selector').value = stock;
        
        // Update active watchlist item
        document.querySelectorAll('.watchlist-item').forEach(item => {
            item.classList.remove('active');
        });
        
        document.querySelectorAll('.watchlist-item').forEach(item => {
            if (item.querySelector('.stock-symbol').textContent === stock) {
                item.classList.add('active');
            }
        });
        
        this.loadStockData();
    }

    async refreshData() {
        this.showLoading();
        await this.loadStockData();
        await this.loadMarketOverview();
        this.hideLoading();
    }

    startAutoUpdates() {
        this.updateInterval = setInterval(() => {
            this.refreshData();
        }, 60000); // Update every minute
    }

    showLoading() {
        this.isLoading = true;
        document.querySelector('.loading-screen').style.display = 'flex';
    }

    hideLoading() {
        this.isLoading = false;
        document.querySelector('.loading-screen').style.display = 'none';
    }

    hideLoadingScreen() {
        document.querySelector('.loading-screen').style.display = 'none';
        document.querySelector('.dashboard-container').classList.add('active');
    }

    showError(message) {
        console.error(message);
        // You can implement a toast notification here
    }

    updateConnectionStatus(status) {
        document.getElementById('market-status').textContent = status.toUpperCase();
    }

    formatNumber(num) {
        if (num >= 1e9) {
            return (num / 1e9).toFixed(1) + 'B';
        } else if (num >= 1e6) {
            return (num / 1e6).toFixed(1) + 'M';
        } else if (num >= 1e3) {
            return (num / 1e3).toFixed(1) + 'K';
        }
        return num.toString();
    }

    updateChartPeriod(period) {
        // Update chart based on selected period
        this.loadHistoricalData();
    }

    openTradeModal(symbol) {
        document.getElementById('trade-symbol').value = symbol;
        document.getElementById('trading-modal').classList.add('active');
    }

    closeModal() {
        document.getElementById('trading-modal').classList.remove('active');
    }

    async executeTrade() {
        const symbol = document.getElementById('trade-symbol').value;
        const action = document.getElementById('trade-action').value;
        const quantity = document.getElementById('trade-quantity').value;
        
        try {
            const response = await fetch('/api/portfolio', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    symbol: symbol,
                    action: action,
                    quantity: parseInt(quantity)
                })
            });
            
            const result = await response.json();
            
            if (result.error) {
                throw new Error(result.error);
            }
            
            this.closeModal();
            this.loadPortfolio();
        } catch (error) {
            console.error('Error executing trade:', error);
            this.showError('Failed to execute trade');
        }
    }
}

// Initialize the dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new StockDashboard();
});
