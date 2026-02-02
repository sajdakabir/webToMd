import validators
import re
from urllib.parse import urlparse, unquote
from typing import Tuple

# SQL injection patterns to detect
SQL_INJECTION_PATTERNS = [
    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE|UNION|DECLARE)\b)",
    r"(--|;|/\*|\*/|xp_|sp_)",
    r"(\bOR\b.*=.*|\bAND\b.*=.*)",
    r"('|(\-\-)|(;)|(\|\|)|(\*))",
    r"(\bSCRIPT\b|<script|javascript:)",
]

def sanitize_input(input_string: str) -> str:
    """Remove or escape potentially dangerous characters"""
    if not input_string:
        return ""
    
    # Remove null bytes
    sanitized = input_string.replace('\x00', '')
    
    # Decode URL encoding
    sanitized = unquote(sanitized)
    
    # Remove control characters
    sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\t\n\r')
    
    return sanitized.strip()

def contains_sql_injection(input_string: str) -> bool:
    """Check if input contains SQL injection patterns"""
    if not input_string:
        return False
    
    # Check against known SQL injection patterns
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, input_string, re.IGNORECASE):
            return True
    
    return False

def is_valid_url(url: str) -> bool:
    """Validate URL format with security checks"""
    if not url or not isinstance(url, str):
        return False
    
    # Check length constraints
    if len(url) > 2048:  # Maximum URL length
        return False
    
    if len(url) < 10:  # Minimum reasonable URL length
        return False
    
    # Basic URL validation using validators library
    if not validators.url(url):
        return False
    
    # Additional security checks
    parsed = urlparse(url)
    
    # Must have http or https scheme
    if parsed.scheme not in ['http', 'https']:
        return False
    
    # Must have a valid domain
    if not parsed.netloc or len(parsed.netloc) < 3:
        return False
    
    # Block localhost and private IPs for security
    blocked_hosts = ['localhost', '127.0.0.1', '0.0.0.0', '::1']
    if parsed.netloc.lower() in blocked_hosts:
        return False
    
    # Block private IP ranges
    if re.match(r'^(10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.)', parsed.netloc):
        return False
    
    return True

def validate_and_sanitize_url(url: str) -> Tuple[bool, str, str]:
    """Comprehensive URL validation and sanitization
    
    Returns:
        Tuple[bool, str, str]: (is_valid, sanitized_url, error_message)
    """
    if not url:
        return False, "", "URL is required"
    
    if not isinstance(url, str):
        return False, "", "URL must be a string"
    
    # Sanitize the input first
    sanitized_url = sanitize_input(url)
    
    # Check for SQL injection attempts
    if contains_sql_injection(sanitized_url):
        return False, "", "Invalid URL: contains prohibited characters or patterns"
    
    # Normalize URL (add scheme if missing)
    if not sanitized_url.startswith(('http://', 'https://')):
        sanitized_url = 'https://' + sanitized_url
    
    # Validate the URL
    if not is_valid_url(sanitized_url):
        return False, "", "Invalid URL format"
    
    return True, sanitized_url, ""

def normalize_url(url: str) -> str:
    """Normalize URL (add scheme if missing, etc.)"""
    if not url:
        return ""
    
    # Sanitize first
    url = sanitize_input(url)
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url

def get_domain(url: str) -> str:
    """Extract domain from URL"""
    parsed = urlparse(url)
    return parsed.netloc
