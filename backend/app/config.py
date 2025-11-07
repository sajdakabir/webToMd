import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')
    RATE_LIMIT = os.getenv('RATE_LIMIT', '10 per minute')
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', './scraped_data')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # Scraper settings
    MAX_PAGES_DEFAULT = 50
    MAX_PAGES_LIMIT = 500
    CACHE_TTL = 3600  # 1 hour
    REQUEST_TIMEOUT = 30
    MAX_WORKERS = 4
