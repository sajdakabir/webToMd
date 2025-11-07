from readability import Document
import html2text
from bs4 import BeautifulSoup

class ContentExtractor:
    """Extract and convert web content to clean markdown"""
    
    def __init__(self):
        self.html2text = html2text.HTML2Text()
        self.html2text.ignore_links = False
        self.html2text.body_width = 0  # Don't wrap lines
        self.html2text.ignore_images = False
        self.html2text.ignore_emphasis = False
    
    def extract_content(self, html: str, url: str, detailed: bool = False) -> dict:
        """
        Extract main content from HTML and convert to markdown
        
        Args:
            html: Raw HTML content
            url: Source URL
            detailed: If True, include full page content
        
        Returns:
            dict with title, markdown, and metadata
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # Extract title
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else ''
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '') if meta_desc else ''
        
        if detailed:
            # Remove unwanted elements but keep structure
            for tag in soup(['script', 'style', 'nav', 'footer', 'aside', 'noscript']):
                tag.decompose()
            clean_html = str(soup)
        else:
            # Use Readability to extract main content
            doc = Document(html)
            title = doc.title() or title
            clean_html = doc.summary()
        
        # Convert to markdown
        markdown = self.html2text.handle(clean_html)
        
        # Extract links
        links = self._extract_links(soup, url)
        
        return {
            'title': title,
            'description': description,
            'markdown': markdown,
            'links': links,
            'url': url
        }
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> list:
        """Extract all internal links from the page"""
        from urllib.parse import urljoin, urlparse
        
        base_domain = urlparse(base_url).netloc
        links = []
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(base_url, href)
            
            # Only include internal links
            if urlparse(full_url).netloc == base_domain:
                links.append(full_url)
        
        return list(set(links))  # Remove duplicates
