import validators
from urllib.parse import urlparse

def is_valid_url(url: str) -> bool:
    """Validate URL format"""
    return validators.url(url) is True

def normalize_url(url: str) -> str:
    """Normalize URL (add scheme if missing, etc.)"""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url

def get_domain(url: str) -> str:
    """Extract domain from URL"""
    parsed = urlparse(url)
    return parsed.netloc
