# Simplified version for free hosting (Replit/Glitch)
from flask import Flask, render_template, jsonify
import yfinance as yf
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Simple stock list (no heavy AI/ML)
DEFAULT_STOCKS = [
    {'symbol': 'AAPL', 'name': 'Apple Inc.'},
    {'symbol': 'MSFT', 'name': 'Microsoft Corporation'},
    {'symbol': 'GOOGL', 'name': 'Alphabet Inc.'},
    {'symbol': 'AMZN', 'name': 'Amazon.com Inc.'},
    {'symbol': 'TSLA', 'name': 'Tesla Inc.'},
    {'symbol': 'META', 'name': 'Meta Platforms Inc.'},
    {'symbol': 'NVDA', 'name': 'NVIDIA Corporation'},
    {'symbol': 'JPM', 'name': 'JPMorgan Chase & Co.'},
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/trending-stocks')
def get_trending_stocks():
    """Get trending stocks with real prices"""
    stocks_data = []
    
    for stock_info in DEFAULT_STOCKS[:5]:  # Top 5 for trending
        try:
            ticker = yf.Ticker(stock_info['symbol'])
            hist = ticker.history(period="5d")
            
            if not hist.empty:
                current_price = float(hist['Close'].iloc[-1])
                price_change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                
                stocks_data.append({
                    'symbol': stock_info['symbol'],
                    'name': stock_info['name'],
                    'current_price': round(current_price, 2),
                    'price_change': round(price_change, 2),
                    'chart_data': {
                        'dates': hist.index.strftime('%Y-%m-%d').tolist(),
                        'prices': hist['Close'].round(2).tolist()
                    }
                })
        except:
            # Fallback data if API fails
            stocks_data.append({
                'symbol': stock_info['symbol'],
                'name': stock_info['name'],
                'current_price': 100.00,
                'price_change': 0.0,
                'chart_data': {'dates': [], 'prices': []}
            })
    
    return jsonify(stocks_data)

@app.route('/api/stock/<symbol>')
def get_stock_details(symbol):
    """Get stock details"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="1mo")
        
        if not hist.empty:
            return jsonify({
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'current_price': round(float(hist['Close'].iloc[-1]), 2),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': round(info.get('trailingPE', 0), 2),
                'chart_data': {
                    'dates': hist.index.strftime('%Y-%m-%d').tolist(),
                    'prices': hist['Close'].round(2).tolist()
                }
            })
    except:
        pass
    
    return jsonify({'error': 'Stock not found'}), 404

@app.route('/api/search/<query>')
def search_stocks(query):
    """Search for stocks"""
    results = []
    query = query.upper()
    
    # Search in default stocks
    for stock in DEFAULT_STOCKS:
        if query in stock['symbol'] or query in stock['name'].upper():
            results.append(stock)
    
    # Try direct lookup
    if not results:
        try:
            ticker = yf.Ticker(query)
            info = ticker.info
            if info.get('longName'):
                results.append({
                    'symbol': query,
                    'name': info.get('longName', query)
                })
        except:
            pass
    
    return jsonify(results[:5])

if __name__ == '__main__':
    # For Replit
    app.run(host='0.0.0.0', port=5000)
