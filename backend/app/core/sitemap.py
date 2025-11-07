import requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
import re

class SitemapParser:
    """Parse robots.txt and sitemap.xml to discover URLs"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; WebScraperBot/1.0)'
        })
    
    def get_urls_from_sitemap(self, max_urls: int = 100) -> list:
        """
        Get URLs from sitemap.xml
        
        Returns:
            List of URLs found in sitemap
        """
        sitemap_urls = self._find_sitemaps()
        all_urls = set([self.base_url])
        
        for sitemap_url in sitemap_urls:
            if len(all_urls) >= max_urls:
                break
            urls = self._parse_sitemap(sitemap_url, max_urls - len(all_urls))
            all_urls.update(urls)
        
        return list(all_urls)[:max_urls]
    
    def _find_sitemaps(self) -> list:
        """Find sitemap URLs from robots.txt"""
        robots_url = urljoin(self.base_url, '/robots.txt')
        sitemaps = []
        
        try:
            response = self.session.get(robots_url, timeout=10)
            if response.status_code == 200:
                # Find sitemap declarations
                pattern = r'sitemap:\s*(.+)'
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                sitemaps = [m.strip() for m in matches]
        except Exception as e:
            print(f"Error fetching robots.txt: {e}")
        
        # Try common sitemap locations if none found
        if not sitemaps:
            common_paths = [
                '/sitemap.xml',
                '/sitemap_index.xml',
                '/sitemap/sitemap.xml'
            ]
            for path in common_paths:
                url = urljoin(self.base_url, path)
                try:
                    response = self.session.head(url, timeout=5)
                    if response.status_code == 200:
                        sitemaps.append(url)
                        break
                except:
                    continue
        
        return sitemaps
    
    def _parse_sitemap(self, sitemap_url: str, max_urls: int) -> set:
        """Parse a sitemap XML file"""
        urls = set()
        
        try:
            response = self.session.get(sitemap_url, timeout=10)
            if response.status_code != 200:
                return urls
            
            root = ET.fromstring(response.content)
            
            # Handle sitemap index (nested sitemaps)
            for sitemap in root.findall('.//{*}sitemap'):
                loc = sitemap.find('{*}loc')
                if loc is not None and len(urls) < max_urls:
                    nested_urls = self._parse_sitemap(loc.text, max_urls - len(urls))
                    urls.update(nested_urls)
            
            # Handle regular sitemap (URL entries)
            for url_elem in root.findall('.//{*}url'):
                if len(urls) >= max_urls:
                    break
                loc = url_elem.find('{*}loc')
                if loc is not None:
                    url = loc.text.strip()
                    if self._is_valid_url(url):
                        urls.add(url)
        
        except Exception as e:
            print(f"Error parsing sitemap {sitemap_url}: {e}")
        
        return urls
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and belongs to the same domain"""
        try:
            parsed = urlparse(url)
            if parsed.netloc != self.domain:
                return False
            
            # Skip common non-content files
            skip_ext = ['.pdf', '.jpg', '.png', '.gif', '.zip', '.exe', 
                       '.css', '.js', '.ico', '.svg', '.mp4', '.mp3']
            if any(url.lower().endswith(ext) for ext in skip_ext):
                return False
            
            return True
        except:
            return False
