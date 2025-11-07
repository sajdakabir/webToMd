# WebToMarkdown 🚀

Convert any website into clean, LLM-ready markdown. Built with Python Flask backend and Next.js frontend.

## Features ✨

- ✅ Smart content extraction (removes ads, nav, footer)
- ✅ Full sitemap crawling (robots.txt + sitemap.xml)
- ✅ Unlimited pages (configurable)
- ✅ Redis caching (1-hour TTL)
- ✅ Rate limiting (10 req/min)
- ✅ Multiple export formats (MD, JSON, ZIP)
- ✅ Modern Next.js UI
- ✅ Playwright for JavaScript rendering
- ✅ Concurrent processing

## Tech Stack 🛠️

**Backend:**
- Python 3.11
- Flask (REST API)
- Playwright (browser automation)
- Readability + html2text (content extraction)
- Redis (caching)
- Celery (async tasks - optional)

**Frontend:**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- React Markdown

## Quick Start 🚀

### Option 1: Docker (Recommended)

```bash
# Clone the repo
git clone <your-repo>
cd web-scraper-pro

# Start all services
docker-compose up

# Access the app
# Frontend: http://localhost:3000
# Backend API: http://localhost:5000
```

### Option 2: Manual Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Set up environment
cp .env.example .env
# Edit .env with your settings

# Start Redis (required)
redis-server

# Run the backend
python run.py
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Set up environment
echo "NEXT_PUBLIC_API_URL=http://localhost:5000/api" > .env.local

# Run the frontend
npm run dev
```

## API Documentation 📚

### POST /api/scrape

Scrape a URL or entire website.

**Request:**
```json
{
  "url": "https://example.com",
  "options": {
    "maxPages": 50,
    "crawlSubpages": true,
    "enableDetailedResponse": false,
    "followSitemap": true
  }
}
```

**Response:**
```json
{
  "baseUrl": "https://example.com",
  "totalPages": 45,
  "successful": 43,
  "failed": 2,
  "results": [
    {
      "url": "https://example.com",
      "title": "Example Domain",
      "markdown": "# Example Domain\n\nThis domain is...",
      "status": "success"
    }
  ]
}
```

### POST /api/scrape/preview

Quick preview of a single page (no caching).

### POST /api/export

Export results in different formats.

**Request:**
```json
{
  "results": [...],
  "format": "markdown" | "json" | "zip"
}
```

## Configuration ⚙️

### Backend (.env)

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
REDIS_URL=redis://localhost:6379/0
RATE_LIMIT=10 per minute
OUTPUT_DIR=./scraped_data
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:5000/api
```

## Usage Examples 💡

### Single Page Scraping

```bash
curl -X POST http://localhost:5000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "options": {
      "crawlSubpages": false
    }
  }'
```

### Full Website Crawling

```bash
curl -X POST http://localhost:5000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "options": {
      "maxPages": 100,
      "crawlSubpages": true,
      "followSitemap": true
    }
  }'
```

## Deployment 🚢

### Railway / Render

1. Push code to GitHub
2. Connect to Railway/Render
3. Add Redis addon
4. Set environment variables
5. Deploy!

### VPS (DigitalOcean, Linode, etc.)

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Clone and run
git clone <your-repo>
cd web-scraper-pro
docker-compose up -d
```

## Performance 📊

- **Single page:** ~2-5 seconds
- **10 pages:** ~10-20 seconds (concurrent)
- **100 pages:** ~1-3 minutes (with sitemap)
- **Cache hit:** <100ms

## License 📄

MIT License
