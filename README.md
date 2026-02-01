# Web to Markdown

Convert any website into clean, LLM-ready markdown format. This project provides a full-stack solution for scraping websites and extracting content with high quality markdown output.

## Overview

Web to Markdown is a web scraping tool that converts websites into structured markdown documents. It features a modern React/Next.js frontend and a Flask-based Python backend with support for multiple scraping strategies.

## Tech Stack

Frontend:
- Next.js 14 with TypeScript
- Tailwind CSS for styling
- React Markdown for preview and rendering
- Lucide Icons for UI components

Backend:
- Flask with Python 3.11
- BeautifulSoup4 for HTML parsing
- Playwright for advanced scraping
- ZenRows API integration for javascript-heavy sites
- Redis for caching (optional)
- Flask-CORS for cross-origin requests
- Flask-Limiter for rate limiting

## Project Structure

```
webToMd/
├── frontend/                    # Next.js frontend application
│   ├── app/                    # App router pages
│   │   ├── page.tsx           # Main scraping interface
│   │   ├── layout.tsx         # Root layout
│   │   └── globals.css        # Global styles
│   ├── components/            # React components
│   │   ├── UrlInput.tsx       # URL input form
│   │   └── ResultsDisplay.tsx # Results viewer
│   ├── lib/                   # Utility functions
│   │   └── api.ts            # API client functions
│   └── package.json           # Frontend dependencies
│
├── backend/                     # Flask backend application
│   ├── app/                   # Main Flask app
│   │   ├── __init__.py        # Flask app initialization
│   │   ├── config.py          # Configuration settings
│   │   ├── api/               # API routes
│   │   │   └── routes.py      # Flask route definitions
│   │   ├── core/              # Core scraping logic
│   │   │   ├── scraper.py     # Main scraper class
│   │   │   ├── zenrows_helper.py  # ZenRows integration
│   │   │   ├── llm_cleaner.py     # LLM content cleaning
│   │   │   └── sitemap.py         # Sitemap parsing
│   │   └── utils/             # Utility modules
│   │       ├── cache.py       # Redis caching
│   │       └── validators.py  # URL validation
│   ├── Dockerfile             # Docker configuration
│   ├── requirements.txt        # Python dependencies
│   ├── run.py                 # Development server
│   ├── vercel.json            # Vercel deployment config
│   └── api/index.py           # Vercel serverless handler
│
├── docker-compose.yml          # Docker compose for development
└── README.md                   # This file
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn
- Python 3.11+
- Docker and Docker Compose (optional)
- ZenRows API key (optional, for advanced scraping)
- OpenAI API key (optional, for content cleaning)

### Local Development Setup

1. Clone the repository:

```bash
git clone https://github.com/sajdakabir/webToMd.git
cd webToMd
```

2. Set up the backend:

```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
python run.py
```

The backend will start on http://localhost:5000

3. Set up the frontend:

```bash
cd frontend
npm install
npm run dev
```

The frontend will start on http://localhost:3000

4. Access the application at http://localhost:3000

### Environment Variables

Backend (.env file):

```dotenv
# Rate Limiting
RATE_LIMIT=10 per minute

# Storage
OUTPUT_DIR=./scraped_data

# Optional: Redis for caching
REDIS_URL=redis://localhost:6379/0

# Optional: ZenRows API for advanced scraping
ZENROWS_API_KEY=your_api_key_here

# Optional: OpenAI API for content cleaning
OPENAI_API_KEY=your_api_key_here
```

Frontend (.env.local file):

```dotenv
NEXT_PUBLIC_API_URL=http://localhost:5000/api
```

### Using Docker

To run the entire application using Docker Compose:

```bash
docker-compose up
```

This will start:
- Frontend on http://localhost:3000
- Backend on http://localhost:5000
- Redis cache (optional)

## API Documentation

### Endpoints

#### GET /api

Health check endpoint. Returns connection status.

Request:
```
GET /api
```

Response:
```json
{
  "message": "Hi from webtomd",
  "status": "connected"
}
```

#### POST /api/scrape

Scrape a single URL or entire website.

Request:
```json
{
  "url": "https://example.com",
  "options": {
    "crawlSubpages": false,
    "maxPages": 50,
    "enableDetailedResponse": false
  }
}
```

Response:
```json
{
  "baseUrl": "https://example.com",
  "totalPages": 1,
  "successful": 1,
  "failed": 0,
  "results": [
    {
      "url": "https://example.com",
      "title": "Example Domain",
      "markdown": "# Example Domain\n\nThis domain is for use in examples...",
      "status": "success"
    }
  ]
}
```

#### POST /api/scrape/preview

Quick preview of a single page without caching.

Request:
```json
{
  "url": "https://example.com"
}
```

Response:
```json
{
  "url": "https://example.com",
  "title": "Example Domain",
  "markdown": "# Example Domain\n\n...",
  "status": "success"
}
```

#### POST /api/export

Export scraping results in specified format.

Request:
```json
{
  "results": [...],
  "format": "markdown"
}
```

Formats supported: `markdown`, `json`, `zip`

## Contributing

We welcome contributions from the community. Here's how to contribute:

### Development Workflow

1. Create a feature branch:

```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and commit:

```bash
git add .
git commit -m "feat: description of your changes"
```

3. Push to your fork and create a pull request:

```bash
git push origin feature/your-feature-name
```

### Code Style Guidelines

Backend (Python):
- Follow PEP 8 style guide
- Use meaningful variable names
- Add docstrings to functions and classes
- No emoji in code or comments

Frontend (TypeScript/React):
- Use TypeScript for type safety
- Use functional components with hooks
- Keep components modular and reusable
- No emoji in code or comments

### Testing

Before submitting a pull request:

1. Test the backend:

```bash
cd backend
python -m pytest
```

2. Test the frontend:

```bash
cd frontend
npm run test
```

3. Run linting checks:

```bash
# Backend
python -m pylint app/

# Frontend
npm run lint
```

### Reporting Issues

If you find a bug, please open an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, Node version, etc.)

### Feature Requests

Feature requests are welcome. Please include:
- Clear description of the feature
- Why you think it would be useful
- Example use cases

## Deployment

### Railway Deployment

1. Connect your GitHub repository to Railway
2. Set the root directory to `backend/` for the backend service
3. Add environment variables in Railway dashboard
4. Deploy

### Vercel Deployment

1. The backend is configured with serverless functions
2. Push changes to GitHub
3. Vercel will automatically deploy from the repository
4. Update frontend environment variables with Vercel URL

### Docker Deployment

Build and run Docker containers:

```bash
docker build -t webtomd-backend ./backend
docker run -p 5000:5000 webtomd-backend
```

## Performance Optimization

- Content is cached using Redis (when available)
- Rate limiting prevents abuse (10 requests per minute for scrape, 20 for preview)
- Markdown conversion happens on the backend for better performance
- Frontend uses code splitting and lazy loading

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari 14+, Chrome Mobile)

## Security Considerations

- Input validation on all endpoints
- Rate limiting to prevent DoS attacks
- CORS properly configured for allowed origins
- No sensitive data in frontend bundles
- API keys stored securely in environment variables

## Troubleshooting

### Issue: CORS Errors

**Solution:** Ensure backend CORS is configured correctly:
- Check that NEXT_PUBLIC_API_URL in frontend .env matches backend URL
- Verify backend is running and accessible
- Clear browser cache

### Issue: Playwright Browser Not Found

**Solution:** Ensure Playwright browsers are installed:

```bash
playwright install chromium
```

### Issue: ZenRows API Errors

**Solution:** Verify your API key is valid and has available credits in your ZenRows account.

### Issue: Redis Connection Failed

**Solution:** Redis is optional. The application will work without it, but caching will be disabled.

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Contact and Support

For questions or support, please:
- Open an issue on GitHub
- Contact the maintainers

## Changelog

### Version 1.0.0

Initial release with core scraping functionality, markdown export, and web UI.

## Roadmap

Future features in development:
- AI-powered content summarization
- Multi-language support
- Advanced filtering options
- Batch URL processing
- API webhook integration

