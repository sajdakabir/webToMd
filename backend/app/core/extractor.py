from bs4 import BeautifulSoup
import re

class ContentExtractor:
    """Extract and convert web content to clean markdown"""
    
    def __init__(self):
        pass
    
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
        
        # Remove scripts, styles, and other non-content elements
        for tag in soup(['script', 'style', 'noscript', 'svg', 'path']):
            tag.decompose()
        
        # Get body content
        body = soup.find('body')
        if not body:
            body = soup
        
        # Extract text content with structure
        markdown = self._html_to_markdown(body)
        
        print(f"Final markdown length: {len(markdown)} characters")
        # Convert to markdown
        markdown = self.html2text.handle(clean_html)
        
        print(f"Markdown after html2text: {len(markdown)} characters")
        print(f"First 500 chars of markdown: {markdown[:500]}")
        
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
