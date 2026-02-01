# Web to Markdown

Convert any website into clean markdown format.

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker (optional)

### Setup

1. Clone and navigate to project:
```bash
git clone https://github.com/sajdakabir/webToMd.git
cd webToMd
```

2. Start backend:
```bash
cd backend
pip install -r requirements.txt
python run.py
```

Backend runs on http://localhost:5000

3. Start frontend:
```bash
cd frontend
npm install
npm run dev
```

Frontend runs on http://localhost:3000

### Environment Variables

Backend (.env):
```
RATE_LIMIT=
OUTPUT_DIR=./scraped_data
ZENROWS_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

Frontend (.env.local):
```
NEXT_PUBLIC_API_URL=http://localhost:5000/api
```

## Using Docker

```bash
docker-compose up
```

## Project Structure

```
webToMd/
├── frontend/          # Next.js app
├── backend/           # Flask API
└── docker-compose.yml
```

## Contributing

1. Create feature branch: `git checkout -b feature/name`
2. Make changes and commit: `git commit -m "feat: description"`
3. Push: `git push origin feature/name`
4. Open pull request

## Tech Stack

- Frontend: Next.js, TypeScript, Tailwind CSS
- Backend: Flask, BeautifulSoup, Playwright
- Optional: Redis (caching), ZenRows API

## License

MIT License


