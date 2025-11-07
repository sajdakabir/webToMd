# Quick Start Guide 🚀

Get up and running in 5 minutes!

## Prerequisites

- Python 3.11+
- Node.js 18+
- Redis (or use Docker)

## Fastest Way: Docker

```bash
# 1. Navigate to project
cd web-scraper-pro

# 2. Start everything
docker-compose up

# 3. Open browser
# Frontend: http://localhost:3000
# Backend: http://localhost:5000/api/health
```

Done! 🎉

## Manual Setup (No Docker)

### Step 1: Start Redis

```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis

# Windows
# Download from https://redis.io/download
```

### Step 2: Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (IMPORTANT!)
python -m playwright install chromium

# Setup environment
cp .env.example .env

# Run backend
python run.py
```

Backend running at http://localhost:5000 ✅

### Step 3: Frontend

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Setup environment
echo "NEXT_PUBLIC_API_URL=http://localhost:5000/api" > .env.local

# Run frontend
npm run dev
```

Frontend running at http://localhost:3000 ✅

## Test It Out

1. Open http://localhost:3000
2. Enter a URL: `https://example.com`
3. Click "Convert to Markdown"
4. See the magic happen! ✨

## Common Issues

### "Redis connection failed"
- Make sure Redis is running: `redis-cli ping` (should return "PONG")
- Check REDIS_URL in .env

### "Playwright browser not found"
- Run: `python -m playwright install chromium`
- Make sure you're in the virtual environment

### "Port 3000 already in use"
- Change port: `npm run dev -- -p 3001`

### "CORS error"
- Make sure backend is running
- Check NEXT_PUBLIC_API_URL in .env.local

## Next Steps

- Read the full [README.md](README.md)
- Check [API Documentation](README.md#api-documentation)
- Deploy to production (Railway, Render, etc.)

## Need Help?

- Check the logs: `docker-compose logs -f`
- Open an issue on GitHub
- Read the troubleshooting guide

Happy scraping! 🎉
