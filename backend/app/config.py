import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Rate limiting
    RATE_LIMIT = os.getenv('RATE_LIMIT', '10 per minute')
    
    # Output directory for exports
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', './scraped_data')
    
    # Redis for caching (optional)
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_TTL = 3600  # 1 hour
    
    # ZenRows API key (optional - for better scraping)
    ZENROWS_API_KEY = os.getenv('ZENROWS_API_KEY', '')
