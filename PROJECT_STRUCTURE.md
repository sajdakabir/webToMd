# WebToMarkdown - Project Structure

## 📁 Complete Project Structure

```
WebToMarkdown/
├── README.md                      # Main documentation
├── QUICKSTART.md                  # 5-minute setup guide
├── docker-compose.yml             # Docker orchestration
│
├── backend/                       # Python Flask API
│   ├── app/
│   │   ├── __init__.py           # Flask app setup
│   │   ├── config.py             # Configuration
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py         # API endpoints
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── scraper.py        # Main scraper
│   │   │   ├── extractor.py      # Content extraction
│   │   │   └── sitemap.py        # Sitemap parser
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── cache.py          # Redis helpers
│   │       └── validators.py     # URL validation
│   ├── requirements.txt           # Python dependencies
│   ├── Dockerfile                 # Backend container
│   ├── .env.example              # Environment template
│   ├── .gitignore
│   ├── run.py                    # Start server
│   └── test_scraper.py           # Test script
│
└── frontend/                      # Next.js UI
    ├── app/
    │   ├── page.tsx              # Home page
    │   ├── layout.tsx            # Root layout
    │   └── globals.css           # Global styles
    ├── components/
    │   ├── UrlInput.tsx          # Input form
    │   └── ResultsDisplay.tsx    # Results view
    ├── lib/
    │   └── api.ts                # API client
    ├── package.json              # Node dependencies
    ├── Dockerfile                # Frontend container
    ├── next.config.js
    ├── tailwind.config.ts
    ├── tsconfig.json
    ├── postcss.config.js
    └── .gitignore
```

## 🚀 Quick Start

```bash
cd WebToMarkdown
docker-compose up
```

Open http://localhost:3000

## 📝 Key Files

### Backend
- **scraper.py** - Main scraping logic with Playwright
- **extractor.py** - Content extraction using Readability
- **sitemap.py** - Parse robots.txt and sitemap.xml
- **routes.py** - API endpoints (/scrape, /export, /preview)
- **cache.py** - Redis caching layer

### Frontend
- **page.tsx** - Main page with state management
- **UrlInput.tsx** - Form with URL input and options
- **ResultsDisplay.tsx** - Display results and export
- **api.ts** - API client for backend calls

## 🛠️ Tech Stack

**Backend:** Python 3.11, Flask, Playwright, Readability, html2text, Redis  
**Frontend:** Next.js 14, TypeScript, Tailwind CSS, React Markdown  
**Infrastructure:** Docker, Docker Compose

## 📊 File Count

- Python files: 10
- TypeScript/TSX files: 7
- Config files: 8
- Documentation: 3

Total: ~30 files (excluding node_modules, venv, etc.)
