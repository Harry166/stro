import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from newsapi import NewsApiClient
import os
from dotenv import load_dotenv
from cache_manager import CacheManager
import time

load_dotenv()

class NewsScraper:
    def __init__(self):
        # Initialize NewsAPI client (you'll need to get an API key)
        self.newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY', 'your_news_api_key_here'))
        
        # Will initialize analyzer when needed to avoid circular import
        self.analyzer = None
        
        # Initialize cache manager
        self.cache = CacheManager()
        
        # Rate limit tracking
        self.last_api_call = {}
        self.api_call_count = 0
        self.rate_limit_window_start = datetime.now()
        
    def get_stock_sentiment(self, symbol):
        """Get overall sentiment score for a stock based on recent news"""
        try:
            # Initialize analyzer if not already done
            if self.analyzer is None:
                from stock_analyzer import StockAnalyzer
                self.analyzer = StockAnalyzer()
            
            # Get recent news
            news_articles = self.get_recent_news(symbol)
            
            if not news_articles:
                return 0.5  # Neutral if no news
            
            # Extract article texts
            texts = []
            for article in news_articles[:10]:  # Analyze top 10 articles
                text = f"{article.get('title', '')} {article.get('description', '')}"
                if text.strip():
                    texts.append(text)
            
            # Analyze sentiment
            sentiment_score = self.analyzer.analyze_news_sentiment(texts)
            
            return sentiment_score
            
        except Exception as e:
            print(f"Error getting sentiment for {symbol}: {e}")
            return 0.5
    
    def _check_rate_limit(self):
        """Check if we're within rate limits"""
        # Reset counter if window has passed (12 hours)
        if datetime.now() - self.rate_limit_window_start > timedelta(hours=12):
            self.api_call_count = 0
            self.rate_limit_window_start = datetime.now()
        
        # Check if we've exceeded the limit (leaving some buffer)
        if self.api_call_count >= 45:  # Leave 5 calls as buffer
            return False
        
        return True
    
    def get_recent_news(self, symbol):
        """Get recent news articles for a stock"""
        cache_key = f"news_{symbol}"
        
        # Check cache first (cache for 2 hours for news)
        cached_data = self.cache.get(cache_key, max_age_minutes=120)
        if cached_data is not None:
            return cached_data
        
        # Check rate limit
        if not self._check_rate_limit():
            print(f"Rate limit approaching for news API, using cached data or default for {symbol}")
            # Return empty list or old cached data
            old_cached = self.cache.get(cache_key, max_age_minutes=720)  # 12 hours old cache
            return old_cached if old_cached else []
        
        try:
            # Add delay between API calls to avoid hitting rate limits
            time.sleep(0.5)
            
            # Search for news articles
            from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            # Get company name for better search results
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            company_name = ticker.info.get('longName', symbol)
            
            # Search query
            query = f"{company_name} OR {symbol} stock"
            
            # Get news from NewsAPI
            self.api_call_count += 1
            news_response = self.newsapi.get_everything(
                q=query,
                from_param=from_date,
                language='en',
                sort_by='relevancy',
                page_size=20
            )
            
            articles = news_response.get('articles', [])
            
            # Format articles
            formatted_articles = []
            for article in articles:
                formatted_articles.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'url': article.get('url', ''),
                    'published_at': article.get('publishedAt', ''),
                    'source': article.get('source', {}).get('name', '')
                })
            
            # Cache the results
            self.cache.set(cache_key, formatted_articles)
            
            return formatted_articles
            
        except Exception as e:
            error_str = str(e)
            if 'rateLimited' in error_str:
                print(f"Rate limit hit for {symbol}, using cached data")
                # Try to get older cached data
                old_cached = self.cache.get(cache_key, max_age_minutes=720)  # 12 hours old cache
                return old_cached if old_cached else []
            else:
                print(f"Error fetching news for {symbol}: {e}")
                return []
    
    def scrape_financial_news(self):
        """Scrape general financial news for market trends"""
        cache_key = "financial_news_general"
        
        # Check cache first
        cached_data = self.cache.get(cache_key, max_age_minutes=60)
        if cached_data is not None:
            return cached_data
        
        # Check rate limit
        if not self._check_rate_limit():
            print("Rate limit approaching for news API, using cached financial news")
            old_cached = self.cache.get(cache_key, max_age_minutes=720)
            return old_cached if old_cached else []
        
        try:
            # Add delay between API calls
            time.sleep(0.5)
            
            # Get top business headlines
            self.api_call_count += 1
            top_headlines = self.newsapi.get_top_headlines(
                category='business',
                language='en',
                country='us'
            )
            
            articles = top_headlines.get('articles', [])
            
            # Cache the results
            self.cache.set(cache_key, articles)
            
            return articles
            
        except Exception as e:
            error_str = str(e)
            if 'rateLimited' in error_str:
                print("Rate limit hit for financial news, using cached data")
                old_cached = self.cache.get(cache_key, max_age_minutes=720)
                return old_cached if old_cached else []
            else:
                print(f"Error scraping financial news: {e}")
                return []
