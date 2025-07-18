# Deploy Without Credit Card - GitHub Pages + Vercel

## Option 1: GitHub Pages + Vercel (Recommended)

### Step 1: Separate Your App
We'll split your app into:
- **Frontend**: HTML/CSS/JS on GitHub Pages (free forever)
- **Backend API**: Python Flask on Vercel (free, no card needed)

### Step 2: Create API-only version for Vercel

Create `api/index.py`:
```python
from flask import Flask, jsonify
import yfinance as yf

app = Flask(__name__)

@app.route('/api/trending-stocks')
def trending_stocks():
    # Your trending stocks logic
    return jsonify({"stocks": []})

@app.route('/api/stock/<symbol>')
def stock_details(symbol):
    # Your stock details logic
    return jsonify({"symbol": symbol})

# Vercel requires this
def handler(request):
    return app(request)
```

Create `vercel.json`:
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/api/index" }
  ]
}
```

### Step 3: Deploy to Vercel
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub (no credit card)
3. Import your repository
4. Deploy!

### Step 4: Update Frontend for GitHub Pages
Update your `index.html` to call Vercel API:
```javascript
// Change API calls from relative to absolute
fetch('https://your-app.vercel.app/api/trending-stocks')
```

## Option 2: Replit (All-in-One, No Card)

1. Go to [replit.com](https://replit.com)
2. Sign up (free, no card)
3. Create new Repl → Python → Flask
4. Import your code
5. Click "Run"
6. Get free URL like: `https://stro.username.repl.co`

**Pros**: Easy, all-in-one
**Cons**: Limited resources, may be slow

## Option 3: Railway with GitHub Student Pack

If you're a student:
1. Get [GitHub Student Pack](https://education.github.com/pack) (free)
2. Includes Railway credits
3. Deploy without credit card

## Option 4: Glitch.com (Simple & Free)

1. Go to [glitch.com](https://glitch.com)
2. "New Project" → "Import from GitHub"
3. Automatic deployment
4. Free subdomain

**Note**: Apps sleep after 5 mins, wake on request

## Option 5: Deta Space (Newer Platform)

1. Go to [deta.space](https://deta.space)
2. Sign up (no card)
3. Install Space CLI
4. Deploy Python apps free

## Option 6: Local + Ngrok (Temporary)

Run locally and expose to internet:
```bash
# Download ngrok (no signup needed for basic)
# Run your app
python app.py

# In another terminal
ngrok http 5000
# Get temporary public URL
```

## Option 7: PythonAnywhere (Limited Free)

1. Go to [pythonanywhere.com](https://pythonanywhere.com)
2. Sign up (no card)
3. Upload your files
4. Limited to 1 web app, 512MB disk

## Best Approach for Your App:

Since your app uses:
- Heavy libraries (PyTorch)
- Background jobs
- External APIs

**I recommend**: 
1. **Simplify first** - Remove PyTorch/AI features for free hosting
2. Use **Vercel** for API + **GitHub Pages** for frontend
3. Or use **Replit** if you want everything in one place

## Quick Vercel Setup (No Credit Card):

```bash
# Install Vercel CLI
npm i -g vercel

# In your project directory
vercel

# Follow prompts (login with GitHub)
# Deploy instantly!
```
