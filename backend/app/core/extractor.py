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
        self.html2text.single_line_break = False  # Use double line breaks for paragraphs
        self.html2text.skip_internal_links = False
        self.html2text.inline_links = True
        self.html2text.protect_links = True
        self.html2text.mark_code = True
        self.html2text.default_image_alt = ''
        self.html2text.ignore_tables = False
        self.html2text.decode_errors = 'ignore'
        self.html2text.ul_item_mark = '-'
        self.html2text.bypass_tables = False
        self.html2text.ignore_mailto_links = True
    
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
        
        # Remove only scripts and styles - keep everything else
        for tag in soup(['script', 'style', 'noscript']):
            tag.decompose()
        
        # Get body content
        body = soup.find('body')
        if body:
            clean_html = str(body)
        else:
            clean_html = str(soup)
        
        # Convert to markdown
        markdown = self.html2text.handle(clean_html)
        
        # Clean up markdown
        markdown = self._clean_markdown(markdown)
        
        # Extract links
        links = self._extract_links(soup, url)
        
        return {
            'title': title,
            'description': description,
            'markdown': markdown,
            'links': links,
            'url': url
        }
    
    def _clean_markdown(self, markdown: str) -> str:
        """Clean up markdown formatting"""
        import re
        
        # Remove excessive blank lines (more than 3 consecutive)
        markdown = re.sub(r'\n{4,}', '\n\n\n', markdown)
        
        # Remove leading/trailing whitespace
        markdown = markdown.strip()
        
        return markdown
    
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
