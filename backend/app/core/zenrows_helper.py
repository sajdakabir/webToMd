from zenrows import ZenRowsClient
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

def zenrows_scrape(url: str, api_key: str) -> dict:
    """
    Scrape URL using ZenRows client and extract clean content
    
    Returns:
        dict with title, text, and links
    """
    try:
        # Initialize ZenRows client
        client = ZenRowsClient(api_key)
        
        # Call ZenRows with enhanced parameters for better JavaScript handling
        params = {
            'js_render': 'true',
            'premium_proxy': 'true',
            'antibot': 'true',
            'wait': 2000,  # Wait 2 seconds for dynamic content to load
        }
        
        response = client.get(url, params=params)
        
        if response.status_code >= 400:
            raise Exception(f"HTTP {response.status_code}")
        
        # Ensure proper text decoding (handles gzip/deflate/br automatically via requests)
        response.encoding = response.apparent_encoding or 'utf-8'
        html = response.text
        
        # Validate we got actual HTML/text content
        if not html or len(html) < 50:
            raise Exception("Received empty or invalid response")
        
        # Parse HTML with fallback parsers
        soup = None
        for parser in ['lxml', 'html.parser', 'html5lib']:
            try:
                soup = BeautifulSoup(html, parser)
                break
            except Exception:
                continue
        
        if soup is None:
            soup = BeautifulSoup(html, 'html.parser')  # Last resort
        
        # Remove unwanted elements
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'noscript', 'iframe']):
            tag.decompose()
        
        # Extract title
        title_elem = soup.find('title')
        title = title_elem.get_text().strip() if title_elem else ''
        
        # Try to find main content area first (common patterns)
        main_content = None
        for selector in ['main', 'article', '[role="main"]', '.main-content', '#main-content', '.content']:
            if isinstance(selector, str) and selector.startswith(('.', '#', '[')):
                # CSS selector
                continue
            main_content = soup.find(selector)
            if main_content:
                break
        
        # Fallback to body
        if not main_content:
            main_content = soup.find('body') or soup
        
        # Extract text with better spacing (paragraph breaks)
        text = main_content.get_text(separator='\n\n', strip=True)
        
        # Check if we got garbled/binary data (common with encoding issues)
        # Count non-printable characters
        non_printable = sum(1 for char in text[:500] if ord(char) < 32 and char not in '\n\r\t')
        if non_printable > 50:  # Too many non-printable chars
            raise Exception("Received garbled/binary content - possible encoding issue")
        
        # Clean up excessive whitespace but preserve paragraph structure
        text = re.sub(r' +', ' ', text)  # Multiple spaces to single
        text = re.sub(r'\n\n\n+', '\n\n', text)  # Max 2 newlines
        text = text.strip()
        
        # Extract all links
        links = soup.find_all('a')
        links = [link.get('href') for link in links if link.get('href')]
        
        return {
            'title': title,
            'text': text,
            'links': links,
            'success': True
        }
        
    except Exception as e:
        return {
            'title': '',
            'text': f"Error: {str(e)}",
            'links': [],
            'success': False,
            'error': str(e)
        }
