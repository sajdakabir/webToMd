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
        
        # Call ZenRows with parameters
        params = {
            'js_render': 'true',
            'premium_proxy': 'true'
        }
        
        response = client.get(url, params=params)
        
        if response.status_code >= 400:
            raise Exception(f"HTTP {response.status_code}")
        
        html = response.text
        
        # Parse HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'noscript']):
            tag.decompose()
        
        # Extract title
        title_elem = soup.find('title')
        title = title_elem.get_text().strip() if title_elem else ''
        
        # Get main content
        main_content = soup.find('body') or soup
        
        # Extract text with spacing
        text = main_content.get_text(separator=' ', strip=True)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
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
