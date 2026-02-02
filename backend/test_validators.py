"""
Test URL validation and SQL injection protection
Run this with: python3 test_validators.py
"""
import sys
import re
from urllib.parse import urlparse, unquote
from typing import Tuple

# Inline validator functions for testing without dependencies

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

def is_valid_url_simple(url: str) -> bool:
    """Simple URL validation without validators library"""
    if not url or not isinstance(url, str):
        return False
    
    # Check length constraints
    if len(url) > 2048 or len(url) < 10:
        return False
    
    try:
        # Additional security checks
        parsed = urlparse(url)
        
        # Must have http or https scheme
        if parsed.scheme not in ['http', 'https']:
            return False
        
        # Must have a valid domain
        if not parsed.netloc or len(parsed.netloc) < 3:
            return False
        
        # Check if domain has at least one dot (e.g., example.com)
        if '.' not in parsed.netloc:
            return False
        
        # Block localhost and private IPs for security
        blocked_hosts = ['localhost', '127.0.0.1', '0.0.0.0', '::1']
        if parsed.netloc.lower() in blocked_hosts:
            return False
        
        # Block private IP ranges
        if re.match(r'^(10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.)', parsed.netloc):
            return False
        
        return True
    except Exception:
        return False

def validate_and_sanitize_url(url: str) -> Tuple[bool, str, str]:
    """Comprehensive URL validation and sanitization"""
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
    if not is_valid_url_simple(sanitized_url):
        return False, "", "Invalid URL format"
    
    return True, sanitized_url, ""

# Test functions

def test_valid_urls():
    """Test that valid URLs pass validation"""
    print("Testing valid URLs...")
    
    valid_urls = [
        "https://example.com",
        "http://example.com",
        "example.com",
        "https://subdomain.example.com",
        "https://example.com/path/to/page",
        "https://example.com:8080",
    ]
    
    for url in valid_urls:
        is_valid, sanitized, error = validate_and_sanitize_url(url)
        assert is_valid, f"Valid URL failed: {url} - Error: {error}"
        assert sanitized, f"No sanitized URL returned for: {url}"
        print(f"  ✓ {url} -> {sanitized}")
    
    print("  All valid URLs passed!\n")

def test_sql_injection():
    """Test SQL injection detection"""
    print("Testing SQL injection patterns...")
    
    malicious_inputs = [
        "'; DROP TABLE users--",
        "' OR '1'='1",
        "example.com; DELETE FROM users",
        "UNION SELECT * FROM passwords",
        "example.com/* comment */",
        "<script>alert('xss')</script>",
        "javascript:alert(1)",
    ]
    
    for malicious in malicious_inputs:
        is_valid, sanitized, error = validate_and_sanitize_url(malicious)
        assert not is_valid, f"SQL injection not detected: {malicious}"
        assert "prohibited characters" in error.lower() or "invalid" in error.lower()
        print(f"  ✓ Blocked: {malicious}")
    
    print("  All SQL injection attempts blocked!\n")

def test_blocked_hosts():
    """Test that localhost and private IPs are blocked"""
    print("Testing blocked hosts...")
    
    blocked_urls = [
        "http://localhost",
        "http://127.0.0.1",
        "http://0.0.0.0",
        "http://10.0.0.1",
        "http://192.168.1.1",
        "http://172.16.0.1",
    ]
    
    for url in blocked_urls:
        is_valid, sanitized, error = validate_and_sanitize_url(url)
        assert not is_valid, f"Blocked host not rejected: {url}"
        print(f"  ✓ Blocked: {url}")
    
    print("  All localhost/private IPs blocked!\n")

def test_invalid_formats():
    """Test invalid URL formats"""
    print("Testing invalid formats...")
    
    invalid_urls = [
        "",
        "not a url",
        "ftp://example.com",
        "file:///etc/passwd",
        "x" * 3000,  # Too long
        "abc",  # Too short
    ]
    
    for url in invalid_urls:
        is_valid, sanitized, error = validate_and_sanitize_url(url)
        assert not is_valid, f"Invalid URL not rejected: {url[:50]}"
        print(f"  ✓ Rejected: {url[:50]}...")
    
    print("  All invalid formats rejected!\n")

def test_sanitization():
    """Test input sanitization"""
    print("Testing sanitization...")
    
    test_cases = [
        ("  https://example.com  ", "https://example.com"),
        ("example.com\x00malicious", "example.commalicious"),
    ]
    
    for input_str, expected in test_cases:
        sanitized = sanitize_input(input_str)
        assert expected in sanitized or sanitized.startswith("https://"), \
            f"Sanitization failed: {input_str}"
        print(f"  ✓ Sanitized: '{input_str}' -> '{sanitized}'")
    
    print("  All sanitization tests passed!\n")

def main():
    """Run all tests"""
    print("=" * 60)
    print("URL Validation and Security Tests")
    print("=" * 60)
    print()
    
    try:
        test_valid_urls()
        test_sql_injection()
        test_blocked_hosts()
        test_invalid_formats()
        test_sanitization()
        
        print("=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
