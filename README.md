# TrendStock AI - Smart Stock Analysis Platform

A dark-mode stock analysis website powered by AI that scrapes news articles, analyzes sentiment, and identifies trending stocks with upward momentum.

## Features

- 🌙 Beautiful dark mode interface with modern design
- 🤖 AI-powered sentiment analysis using Hugging Face Transformers
- 📈 Real-time stock data and interactive charts
- 📰 News scraping and analysis for market insights
- 🔥 Automatic detection of trending stocks
- 📊 Technical analysis with moving averages and RSI
- 🔄 Auto-refresh every 5 minutes

## Setup Instructions

### 1. Install Dependencies

```bash
# Using uv (recommended)
uv pip install -r requirements.txt

# Or using pip
pip install -r requirements.txt
```

### 2. API Keys Setup

#### News API Key (Required)
1. Go to [https://newsapi.org/](https://newsapi.org/)
2. Sign up for a free account
3. Get your API key
4. Add it to the `.env` file

#### Hugging Face (Optional - for cloud inference)
1. Go to [https://huggingface.co/](https://huggingface.co/)
2. Create an account
3. Go to Settings > Access Tokens
4. Create a new token with `read` permissions
5. Add it to the `.env` file (optional - the app works without it)

### 3. Update Environment Variables

Edit the `.env` file:
```
NEWS_API_KEY=your_actual_news_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_token_here  # Optional
```

### 4. Run the Application

```bash
python app.py
```

Open your browser and go to `http://localhost:5000`

## How It Works

1. **Stock Analysis**: The system analyzes 20 popular stocks using technical indicators
2. **News Sentiment**: AI analyzes recent news articles for each stock using FinBERT
3. **Trend Detection**: Combines technical analysis (60%) and sentiment (40%) to score stocks
4. **Display**: Shows the top 10 trending stocks with scores above 0.6

## AI Integration

The project uses Hugging Face Transformers with the **FinBERT** model, specifically trained for financial sentiment analysis. This provides more accurate sentiment detection for stock-related news.

### Why AI is Important:
- **Sentiment Analysis**: AI can understand context and nuance in financial news
- **Pattern Recognition**: Identifies positive/negative trends from text
- **Scalability**: Can analyze hundreds of articles quickly
- **Accuracy**: Financial-specific models understand market terminology

## Hugging Face Permissions

For the Hugging Face API token, you only need:
- **Read access** to public models
- No special permissions required
- The token is optional (the app downloads models locally by default)

## Dark Mode Design

The website features a sophisticated dark color scheme:
- **Background**: Deep black (#0a0b0d) for reduced eye strain
- **Cards**: Dark gray (#1a1b23) with subtle borders
- **Accents**: Blue (#3b82f6) and green (#10b981) for positive trends
- **Text**: High contrast white (#e4e4e7) for readability
- **Charts**: Color-coded (green for gains, red for losses)

## Future Enhancements

- Add more technical indicators
- Include options flow analysis
- Add portfolio tracking
- Implement alerts for significant changes
- Add more AI models for comparison

## Troubleshooting

If you encounter issues:
1. Make sure all dependencies are installed
2. Check that your NEWS_API_KEY is valid
3. Ensure you have internet connection for API calls
4. Check console for error messages

## Note

This is for educational purposes only. Always do your own research before making investment decisions.
