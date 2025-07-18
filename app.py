from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from datetime import datetime, timedelta
import yfinance as yf
from stock_analyzer import StockAnalyzer
from news_scraper import NewsScraper
from apscheduler.schedulers.background import BackgroundScheduler
import os
import json
from functools import wraps
from database import Database
import time

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')

# Initialize components
stock_analyzer = StockAnalyzer()
news_scraper = NewsScraper()
db = Database()

# Global variable to store trending stocks
trending_stocks = []

# Storage for alerts (per user)
stock_alerts = {}

def update_trending_stocks():
    """Update the list of trending stocks based on analysis"""
    global trending_stocks
    
    # List of stocks to analyze (you can expand this)
    stock_symbols = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 
        'META', 'NVDA', 'JPM', 'V', 'JNJ',
        'WMT', 'PG', 'UNH', 'HD', 'DIS',
        'PYPL', 'NFLX', 'ADBE', 'CRM', 'PFE'
    ]
    
    analyzed_stocks = []
    
    # Batch process stocks to reduce API calls
    batch_size = 5
    for i in range(0, len(stock_symbols), batch_size):
        batch = stock_symbols[i:i+batch_size]
        
        for symbol in batch:
            try:
                # Get stock data
                stock = yf.Ticker(symbol)
                
                # Get news sentiment (now with caching)
                news_sentiment = news_scraper.get_stock_sentiment(symbol)
                
                # Analyze trend
                trend_score = stock_analyzer.analyze_trend(symbol)
                
                # Combine scores
                overall_score = (news_sentiment * 0.4) + (trend_score * 0.6)
                
                if overall_score > 0.6:  # Threshold for trending
                    info = stock.info
                    current_price = info.get('currentPrice', 0)
                    
                    analyzed_stocks.append({
                        'symbol': symbol,
                        'name': info.get('longName', symbol),
                        'current_price': current_price,
                        'score': overall_score,
                        'sentiment': news_sentiment,
                        'trend': trend_score
                    })
            except Exception as e:
                print(f"Error analyzing {symbol}: {e}")
        
        # Add delay between batches to avoid overwhelming APIs
        if i + batch_size < len(stock_symbols):
            time.sleep(2)
    
    # Sort by score and take top 10
    trending_stocks = sorted(analyzed_stocks, key=lambda x: x['score'], reverse=True)[:10]
    print(f"Updated trending stocks at {datetime.now()} - Found {len(trending_stocks)} trending stocks")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not all([username, email, password]):
        return jsonify({'success': False, 'error': 'All fields are required'}), 400
    
    if len(password) < 6:
        return jsonify({'success': False, 'error': 'Password must be at least 6 characters'}), 400
    
    result = db.create_user(username, email, password)
    
    if result['success']:
        # Automatically log in the user
        session['user'] = {
            'id': result['user_id'],
            'username': username,
            'email': email
        }
        return jsonify({'success': True, 'user': session['user']})
    else:
        return jsonify(result), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not all([username, password]):
        return jsonify({'success': False, 'error': 'Username and password required'}), 400
    
    result = db.verify_user(username, password)
    
    if result['success']:
        session['user'] = result['user']
        return jsonify({'success': True, 'user': result['user']})
    else:
        return jsonify(result), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout user"""
    session.pop('user', None)
    return jsonify({'success': True})

@app.route('/api/auth/status')
def auth_status():
    """Check authentication status"""
    if 'user' in session:
        return jsonify({'authenticated': True, 'user': session['user']})
    else:
        return jsonify({'authenticated': False})

@app.route('/api/trending-stocks')
def get_trending_stocks():
    """API endpoint to get trending stocks"""
    stocks_data = []
    
    for stock in trending_stocks:
        try:
            ticker = yf.Ticker(stock['symbol'])
            
            # Get historical data for chart
            hist = ticker.history(period="1mo")
            
            # Prepare chart data
            chart_data = {
                'dates': hist.index.strftime('%Y-%m-%d').tolist(),
                'prices': hist['Close'].tolist()
            }
            
            stocks_data.append({
                'symbol': stock['symbol'],
                'name': stock['name'],
                'current_price': stock['current_price'],
                'chart_data': chart_data,
                'score': stock['score']
            })
        except Exception as e:
            print(f"Error fetching data for {stock['symbol']}: {e}")
    
    return jsonify(stocks_data)

@app.route('/api/upcoming-stocks')
def get_upcoming_stocks():
    """API endpoint to get upcoming stocks with potential"""
    # Stocks that people think will blow up (but aren't currently trending)
    upcoming_stocks = [
        {'symbol': 'PLTR', 'name': 'Palantir Technologies Inc.'},
        {'symbol': 'RBLX', 'name': 'Roblox Corporation'},
        {'symbol': 'AI', 'name': 'C3.ai, Inc.'},
        {'symbol': 'SOFI', 'name': 'SoFi Technologies'},
        {'symbol': 'LCID', 'name': 'Lucid Group Inc.'},
        {'symbol': 'RIVN', 'name': 'Rivian Automotive'},
        {'symbol': 'NIO', 'name': 'NIO Inc.'},
        {'symbol': 'HOOD', 'name': 'Robinhood Markets'},
        {'symbol': 'DKNG', 'name': 'DraftKings Inc.'},
        {'symbol': 'BBBY', 'name': 'Bed Bath & Beyond'}
    ]
    
    stocks_data = []
    
    for stock in upcoming_stocks:
        try:
            ticker = yf.Ticker(stock['symbol'])
            info = ticker.info
            
            # Get historical data for chart
            hist = ticker.history(period="1mo")
            
            if not hist.empty:
                current_price = info.get('currentPrice', hist['Close'].iloc[-1])
                
                # Prepare chart data
                chart_data = {
                    'dates': hist.index.strftime('%Y-%m-%d').tolist(),
                    'prices': hist['Close'].tolist()
                }
                
                stocks_data.append({
                    'symbol': stock['symbol'],
                    'name': stock['name'],
                    'current_price': current_price,
                    'chart_data': chart_data
                })
        except Exception as e:
            print(f"Error fetching upcoming stock {stock['symbol']}: {e}")
    
    return jsonify(stocks_data[:10])  # Return top 10

@app.route('/api/stock/<symbol>')
def get_stock_details(symbol):
    """API endpoint to get detailed stock information"""
    from flask import request
    
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Check if stock exists
        if not info or 'longName' not in info:
            return jsonify({'error': 'Stock not found'}), 404
        
        # Get historical data for detailed chart
        hist = ticker.history(period="3mo")
        
        # Get company summary
        summary = stock_analyzer.get_company_summary(symbol)
        
        # Get recent news
        recent_news = news_scraper.get_recent_news(symbol)
        
        response_data = {
            'symbol': symbol,
            'name': info.get('longName', symbol),
            'current_price': info.get('currentPrice', hist['Close'].iloc[-1] if not hist.empty else 0),
            'summary': summary,
            'chart_data': {
                'dates': hist.index.strftime('%Y-%m-%d').tolist(),
                'prices': hist['Close'].tolist(),
                'volume': hist['Volume'].tolist()
            },
            'news': recent_news,
            'market_cap': info.get('marketCap', 0),
            'pe_ratio': info.get('trailingPE', 0),
            'dividend_yield': info.get('dividendYield', 0)
        }
        
        # If analyze parameter is true, add AI analysis
        if request.args.get('analyze') == 'true':
            # Get news sentiment
            news_sentiment = news_scraper.get_stock_sentiment(symbol)
            
            # Get trend analysis
            trend_score = stock_analyzer.analyze_trend(symbol)
            
            # Calculate future prediction
            future_prediction = (news_sentiment * 0.5) + (trend_score * 0.5)
            
            # Generate AI analysis text
            ai_analysis = generate_ai_analysis(symbol, news_sentiment, trend_score, info)
            
            response_data['future_prediction'] = future_prediction
            response_data['ai_analysis'] = ai_analysis
            response_data['sentiment_score'] = news_sentiment
            response_data['trend_score'] = trend_score
        
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_ai_analysis(symbol, sentiment_score, trend_score, info):
    """Generate AI analysis text based on scores"""
    analysis_parts = []
    
    # Sentiment analysis
    if sentiment_score > 0.7:
        analysis_parts.append(f"Recent news sentiment for {symbol} is very positive, indicating strong market confidence.")
    elif sentiment_score > 0.55:
        analysis_parts.append(f"News sentiment for {symbol} is moderately positive, suggesting favorable market perception.")
    elif sentiment_score < 0.3:
        analysis_parts.append(f"Recent news sentiment for {symbol} is negative, indicating potential concerns in the market.")
    elif sentiment_score < 0.45:
        analysis_parts.append(f"News sentiment for {symbol} is slightly negative, suggesting some market uncertainty.")
    else:
        analysis_parts.append(f"News sentiment for {symbol} is neutral, with mixed market signals.")
    
    # Technical analysis
    if trend_score > 0.7:
        analysis_parts.append("Technical indicators show strong upward momentum with prices above key moving averages.")
    elif trend_score > 0.55:
        analysis_parts.append("Technical analysis reveals positive trends with moderate buying pressure.")
    elif trend_score < 0.3:
        analysis_parts.append("Technical indicators suggest bearish conditions with downward price pressure.")
    elif trend_score < 0.45:
        analysis_parts.append("Technical analysis shows weakness with prices below key support levels.")
    else:
        analysis_parts.append("Technical indicators are mixed, suggesting a consolidation phase.")
    
    # Overall recommendation
    combined_score = (sentiment_score + trend_score) / 2
    if combined_score > 0.65:
        analysis_parts.append("Overall outlook is bullish. Consider this stock for potential growth opportunities.")
    elif combined_score < 0.35:
        analysis_parts.append("Overall outlook is bearish. Exercise caution and consider risk management strategies.")
    else:
        analysis_parts.append("The stock shows mixed signals. Monitor closely for clearer directional trends.")
    
    return " ".join(analysis_parts)

@app.route('/api/watchlist', methods=['GET', 'POST', 'DELETE'])
@login_required
def manage_watchlist():
    """Manage user's watchlist"""
    user_id = session['user']['id']
    
    if request.method == 'GET':
        # Get user's watchlist with current data
        watchlist_symbols = db.get_user_watchlist(user_id)
        watchlist_data = []
        
        for symbol in watchlist_symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="1mo")
                
                if not hist.empty:
                    current_price = info.get('currentPrice', hist['Close'].iloc[-1])
                    first_price = hist['Close'].iloc[0]
                    price_change = ((current_price - first_price) / first_price) * 100
                    
                    watchlist_data.append({
                        'symbol': symbol,
                        'name': info.get('longName', symbol),
                        'current_price': current_price,
                        'price_change': price_change,
                        'alert_triggered': check_alert_conditions(symbol, price_change)
                    })
            except Exception as e:
                print(f"Error fetching watchlist data for {symbol}: {e}")
        
        return jsonify(watchlist_data)
    
    elif request.method == 'POST':
        # Add stock to watchlist
        data = request.get_json()
        symbol = data.get('symbol', '').upper()
        
        if symbol:
            # Verify the stock exists
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                if info and 'longName' in info:
                    result = db.add_to_watchlist(user_id, symbol)
                    if result['success']:
                        return jsonify({'success': True, 'message': f'{symbol} added to watchlist'})
                    else:
                        return jsonify({'success': False, 'message': result['error']}), 400
                else:
                    return jsonify({'success': False, 'message': 'Invalid stock symbol'}), 400
            except:
                return jsonify({'success': False, 'message': 'Error verifying stock'}), 400
        else:
            return jsonify({'success': False, 'message': 'Stock symbol required'}), 400
    
    elif request.method == 'DELETE':
        # Remove stock from watchlist
        symbol = request.args.get('symbol', '').upper()
        
        if symbol:
            result = db.remove_from_watchlist(user_id, symbol)
            if result['success']:
                return jsonify({'success': True, 'message': f'{symbol} removed from watchlist'})
            else:
                return jsonify({'success': False, 'message': result['error']}), 400
        else:
            return jsonify({'success': False, 'message': 'Stock symbol required'}), 400

def check_alert_conditions(symbol, price_change):
    """Check if alert conditions are met"""
    alerts = []
    
    if price_change >= 25:
        alerts.append({
            'type': 'high_gain',
            'message': f'{symbol} is up {price_change:.1f}% in the past month!',
            'severity': 'success'
        })
    elif price_change <= -15:
        alerts.append({
            'type': 'high_loss',
            'message': f'{symbol} is down {abs(price_change):.1f}% in the past month.',
            'severity': 'warning'
        })
    
    return alerts

@app.route('/api/alerts')
@login_required
def get_alerts():
    """Get all alerts for user's watchlist"""
    user_id = session['user']['id']
    
    # Get alerts from database
    db_alerts = db.get_user_alerts(user_id)
    
    # Also check current watchlist for new alerts
    watchlist_symbols = db.get_user_watchlist(user_id)
    current_alerts = []
    
    for symbol in watchlist_symbols:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1mo")
            
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                first_price = hist['Close'].iloc[0]
                price_change = ((current_price - first_price) / first_price) * 100
                
                alerts = check_alert_conditions(symbol, price_change)
                if alerts:
                    for alert in alerts:
                        alert_data = {**alert, 'symbol': symbol, 'timestamp': datetime.now().isoformat()}
                        current_alerts.append(alert_data)
                        # Save new alerts to database
                        db.add_alert(user_id, symbol, alert['type'], alert['message'])
        except Exception as e:
            print(f"Error checking alerts for {symbol}: {e}")
    
    # Combine database alerts with current alerts
    all_alerts = db_alerts + current_alerts
    
    # Remove duplicates based on symbol and type
    unique_alerts = {}
    for alert in all_alerts:
        key = f"{alert['symbol']}_{alert.get('type', 'unknown')}"
        if key not in unique_alerts:
            unique_alerts[key] = alert
    
    return jsonify(list(unique_alerts.values()))

def check_watchlist_alerts():
    """Background job to check watchlist alerts"""
    # Get all users with watchlists
    users = db.get_all_users()
    
    for user in users:
        user_id = user['id']
        watchlist_symbols = db.get_user_watchlist(user_id)
        
        for symbol in watchlist_symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1mo")
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    first_price = hist['Close'].iloc[0]
                    price_change = ((current_price - first_price) / first_price) * 100
                    
                    alerts = check_alert_conditions(symbol, price_change)
                    if alerts:
                        for alert in alerts:
                            # Check if similar alert was already sent recently (within 24 hours)
                            existing_alerts = db.get_user_alerts(user_id, hours=24)
                            duplicate = any(
                                a['symbol'] == symbol and a.get('type') == alert['type'] 
                                for a in existing_alerts
                            )
                            
                            if not duplicate:
                                db.add_alert(user_id, symbol, alert['type'], alert['message'])
            except Exception as e:
                print(f"Error checking alerts for {symbol}: {e}")
    
    print(f"Checked watchlist alerts at {datetime.now()}")

if __name__ == '__main__':
    # Initialize trending stocks on startup
    update_trending_stocks()
    
    # Schedule updates every hour
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=update_trending_stocks, trigger="interval", hours=1)
    scheduler.add_job(func=check_watchlist_alerts, trigger="interval", minutes=30)
    scheduler.start()
    
    # Run the app
    app.run(debug=True)
