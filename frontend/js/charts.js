// Advanced Chart Functionality for Stock Dashboard

class ChartManager {
    constructor() {
        this.charts = {};
        this.chartConfigs = {
            priceChart: {
                type: 'line',
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        intersect: false,
                        mode: 'index'
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            grid: {
                                color: 'rgba(0, 0, 0, 0.1)'
                            },
                            ticks: {
                                callback: function(value) {
                                    return '$' + value.toFixed(2);
                                }
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
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: '#fff',
                            bodyColor: '#fff',
                            borderColor: '#2563eb',
                            borderWidth: 1,
                            callbacks: {
                                label: function(context) {
                                    return '$' + context.parsed.y.toFixed(2);
                                }
                            }
                        }
                    },
                    elements: {
                        point: {
                            radius: 0,
                            hoverRadius: 6
                        }
                    }
                }
            },
            sentimentChart: {
                type: 'doughnut',
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '70%',
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                usePointStyle: true,
                                padding: 20
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return context.label + ': ' + context.parsed + '%';
                                }
                            }
                        }
                    }
                }
            },
            volumeChart: {
                type: 'bar',
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(0, 0, 0, 0.1)'
                            },
                            ticks: {
                                callback: function(value) {
                                    return (value / 1000000).toFixed(1) + 'M';
                                }
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            }
        };
    }

    createPriceChart(elementId, data) {
        const ctx = document.getElementById(elementId).getContext('2d');
        
        // Destroy existing chart if it exists
        if (this.charts[elementId]) {
            this.charts[elementId].destroy();
        }

        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, 'rgba(37, 99, 235, 0.3)');
        gradient.addColorStop(1, 'rgba(37, 99, 235, 0.05)');

        this.charts[elementId] = new Chart(ctx, {
            type: this.chartConfigs.priceChart.type,
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Price',
                    data: data.prices,
                    borderColor: '#2563eb',
                    backgroundColor: gradient,
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: this.chartConfigs.priceChart.options
        });

        return this.charts[elementId];
    }

    createSentimentChart(elementId, data) {
        const ctx = document.getElementById(elementId).getContext('2d');
        
        // Destroy existing chart if it exists
        if (this.charts[elementId]) {
            this.charts[elementId].destroy();
        }

        this.charts[elementId] = new Chart(ctx, {
            type: this.chartConfigs.sentimentChart.type,
            data: {
                labels: ['Positive', 'Negative', 'Neutral'],
                datasets: [{
                    data: [data.positive, data.negative, data.neutral],
                    backgroundColor: [
                        '#10b981',
                        '#ef4444',
                        '#64748b'
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: this.chartConfigs.sentimentChart.options
        });

        return this.charts[elementId];
    }

    createVolumeChart(elementId, data) {
        const ctx = document.getElementById(elementId).getContext('2d');
        
        // Destroy existing chart if it exists
        if (this.charts[elementId]) {
            this.charts[elementId].destroy();
        }

        this.charts[elementId] = new Chart(ctx, {
            type: this.chartConfigs.volumeChart.type,
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Volume',
                    data: data.volumes,
                    backgroundColor: 'rgba(37, 99, 235, 0.6)',
                    borderColor: '#2563eb',
                    borderWidth: 1
                }]
            },
            options: this.chartConfigs.volumeChart.options
        });

        return this.charts[elementId];
    }

    createCandlestickChart(elementId, data) {
        const ctx = document.getElementById(elementId).getContext('2d');
        
        // Destroy existing chart if it exists
        if (this.charts[elementId]) {
            this.charts[elementId].destroy();
        }

        // Generate candlestick data
        const candlestickData = this.generateCandlestickData(data);

        this.charts[elementId] = new Chart(ctx, {
            type: 'candlestick',
            data: {
                datasets: [{
                    label: 'Stock Price',
                    data: candlestickData
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
                        type: 'time',
                        time: {
                            unit: 'day'
                        },
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

        return this.charts[elementId];
    }

    generateCandlestickData(data) {
        const candlestickData = [];
        
        for (let i = 0; i < data.labels.length; i++) {
            const basePrice = data.prices[i];
            const volatility = basePrice * 0.02; // 2% volatility
            
            const open = basePrice + (Math.random() - 0.5) * volatility;
            const close = basePrice + (Math.random() - 0.5) * volatility;
            const high = Math.max(open, close) + Math.random() * volatility;
            const low = Math.min(open, close) - Math.random() * volatility;
            
            candlestickData.push({
                x: data.labels[i],
                o: open,
                h: high,
                l: low,
                c: close
            });
        }
        
        return candlestickData;
    }

    updateChart(elementId, newData) {
        const chart = this.charts[elementId];
        if (!chart) return;

        chart.data.datasets[0].data = newData;
        chart.update('none');
    }

    animateChart(elementId) {
        const chart = this.charts[elementId];
        if (!chart) return;

        chart.update('active');
    }

    destroyChart(elementId) {
        if (this.charts[elementId]) {
            this.charts[elementId].destroy();
            delete this.charts[elementId];
        }
    }

    destroyAllCharts() {
        Object.keys(this.charts).forEach(elementId => {
            this.destroyChart(elementId);
        });
    }

    // Advanced chart configurations
    createRealTimeChart(elementId, maxDataPoints = 50) {
        const ctx = document.getElementById(elementId).getContext('2d');
        
        this.charts[elementId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Real-time Price',
                    data: [],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 0
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        type: 'time',
                        time: {
                            unit: 'second'
                        },
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

        // Set up real-time data updating
        this.setupRealTimeUpdates(elementId, maxDataPoints);
        
        return this.charts[elementId];
    }

    setupRealTimeUpdates(elementId, maxDataPoints) {
        const chart = this.charts[elementId];
        if (!chart) return;

        // This would connect to your real-time data source
        setInterval(() => {
            const now = new Date();
            const price = Math.random() * 50 + 150; // Random price for demo
            
            chart.data.labels.push(now);
            chart.data.datasets[0].data.push(price);
            
            // Remove old data points
            if (chart.data.labels.length > maxDataPoints) {
                chart.data.labels.shift();
                chart.data.datasets[0].data.shift();
            }
            
            chart.update('none');
        }, 1000); // Update every second
    }

    // Technical indicators
    addMovingAverage(elementId, periods = 20) {
        const chart = this.charts[elementId];
        if (!chart) return;

        const data = chart.data.datasets[0].data;
        const movingAverage = this.calculateMovingAverage(data, periods);
        
        chart.data.datasets.push({
            label: `MA(${periods})`,
            data: movingAverage,
            borderColor: '#f59e0b',
            backgroundColor: 'transparent',
            borderWidth: 1,
            fill: false,
            tension: 0.4
        });
        
        chart.update();
    }

    calculateMovingAverage(data, periods) {
        const movingAverage = [];
        
        for (let i = 0; i < data.length; i++) {
            if (i < periods - 1) {
                movingAverage.push(null);
            } else {
                const sum = data.slice(i - periods + 1, i + 1).reduce((a, b) => a + b, 0);
                movingAverage.push(sum / periods);
            }
        }
        
        return movingAverage;
    }

    addBollingerBands(elementId, periods = 20, multiplier = 2) {
        const chart = this.charts[elementId];
        if (!chart) return;

        const data = chart.data.datasets[0].data;
        const movingAverage = this.calculateMovingAverage(data, periods);
        const standardDeviation = this.calculateStandardDeviation(data, periods);
        
        const upperBand = movingAverage.map((ma, i) => 
            ma !== null ? ma + (standardDeviation[i] * multiplier) : null
        );
        
        const lowerBand = movingAverage.map((ma, i) => 
            ma !== null ? ma - (standardDeviation[i] * multiplier) : null
        );
        
        chart.data.datasets.push(
            {
                label: 'Upper Band',
                data: upperBand,
                borderColor: 'rgba(239, 68, 68, 0.5)',
                backgroundColor: 'transparent',
                borderWidth: 1,
                fill: false
            },
            {
                label: 'Lower Band',
                data: lowerBand,
                borderColor: 'rgba(239, 68, 68, 0.5)',
                backgroundColor: 'transparent',
                borderWidth: 1,
                fill: false
            }
        );
        
        chart.update();
    }

    calculateStandardDeviation(data, periods) {
        const standardDeviation = [];
        
        for (let i = 0; i < data.length; i++) {
            if (i < periods - 1) {
                standardDeviation.push(null);
            } else {
                const slice = data.slice(i - periods + 1, i + 1);
                const mean = slice.reduce((a, b) => a + b, 0) / periods;
                const variance = slice.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / periods;
                standardDeviation.push(Math.sqrt(variance));
            }
        }
        
        return standardDeviation;
    }
}

// Export for use in other files
window.ChartManager = ChartManager;
