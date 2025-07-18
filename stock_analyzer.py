import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from transformers import pipeline
import warnings
warnings.filterwarnings('ignore')

class StockAnalyzer:
    def __init__(self):
        # Initialize sentiment analysis pipeline
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="ProsusAI/finbert",  # Financial sentiment analysis model
            device=-1  # Use CPU, set to 0 for GPU
        )
        
    def analyze_trend(self, symbol):
        """Analyze stock trend based on technical indicators"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get historical data
            hist = ticker.history(period="3mo")
            
            if hist.empty:
                return 0.5
            
            # Calculate moving averages
            hist['MA_20'] = hist['Close'].rolling(window=20).mean()
            hist['MA_50'] = hist['Close'].rolling(window=50).mean()
            
            # Calculate RSI
            rsi = self.calculate_rsi(hist['Close'])
            
            # Calculate trend score
            trend_score = 0.0
            
            # Price above moving averages (bullish)
            current_price = hist['Close'].iloc[-1]
            if current_price > hist['MA_20'].iloc[-1]:
                trend_score += 0.3
            if current_price > hist['MA_50'].iloc[-1]:
                trend_score += 0.2
                
            # Moving average crossover
            if hist['MA_20'].iloc[-1] > hist['MA_50'].iloc[-1]:
                trend_score += 0.2
                
            # RSI analysis
            if 40 < rsi < 70:  # Not oversold or overbought
                trend_score += 0.2
            elif rsi < 30:  # Oversold (potential bounce)
                trend_score += 0.1
                
            # Volume trend
            recent_volume = hist['Volume'].iloc[-5:].mean()
            avg_volume = hist['Volume'].mean()
            if recent_volume > avg_volume * 1.2:
                trend_score += 0.1
                
            return min(trend_score, 1.0)
            
        except Exception as e:
            print(f"Error analyzing trend for {symbol}: {e}")
            return 0.5
    
    def calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1]
    
    def get_company_summary(self, symbol):
        """Get a comprehensive summary of the company"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get company description
            description = info.get('longBusinessSummary', '')
            
            if not description:
                return f"{info.get('longName', symbol)} operates in the {info.get('sector', 'market')} sector."
            
            # Create summary with full description first
            summary_parts = []
            
            # Add the complete description first
            summary_parts.append(description)
            
            # Add a separator before metrics
            summary_parts.append("\n\n")
            
            # Then add key metrics section
            metrics_parts = []
            
            # Market cap
            market_cap = info.get('marketCap', 0)
            if market_cap > 0:
                if market_cap > 1e12:
                    market_cap_str = f"${market_cap/1e12:.2f}T"
                elif market_cap > 1e9:
                    market_cap_str = f"${market_cap/1e9:.2f}B"
                else:
                    market_cap_str = f"${market_cap/1e6:.2f}M"
                metrics_parts.append(f"Market Cap: {market_cap_str}")
            
            # Employees
            employees = info.get('fullTimeEmployees', 0)
            if employees > 0:
                metrics_parts.append(f"Employees: {employees:,}")
            
            # P/E Ratio
            pe_ratio = info.get('trailingPE', 0)
            if pe_ratio > 0:
                metrics_parts.append(f"P/E Ratio: {pe_ratio:.2f}")
            
            # Revenue
            revenue = info.get('totalRevenue', 0)
            if revenue > 0:
                if revenue > 1e9:
                    revenue_str = f"${revenue/1e9:.2f}B"
                else:
                    revenue_str = f"${revenue/1e6:.2f}M"
                metrics_parts.append(f"Revenue: {revenue_str}")
            
            # Add metrics if available
            if metrics_parts:
                summary_parts.append("Key Metrics: " + " | ".join(metrics_parts))
            
            return " ".join(summary_parts)
            
        except Exception as e:
            return f"Unable to retrieve detailed information for {symbol}."
    
    def analyze_news_sentiment(self, news_texts):
        """Analyze sentiment of news articles using FinBERT"""
        if not news_texts:
            return 0.5
        
        try:
            # Analyze each text
            sentiments = []
            for text in news_texts[:5]:  # Limit to 5 articles for performance
                if text:
                    result = self.sentiment_analyzer(text[:512])[0]  # Limit text length
                    
                    # Convert to score
                    if result['label'] == 'positive':
                        sentiments.append(result['score'])
                    elif result['label'] == 'negative':
                        sentiments.append(1 - result['score'])
                    else:  # neutral
                        sentiments.append(0.5)
            
            return np.mean(sentiments) if sentiments else 0.5
            
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return 0.5
