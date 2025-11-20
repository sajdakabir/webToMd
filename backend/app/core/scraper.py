from app.core.extractor import ContentExtractor
from app.core.sitemap import SitemapParser
from app.core.llm_cleaner import LLMCleaner
from app.core.zenrows_helper import zenrows_scrape
from app.utils.cache import cache_get, cache_set
from app.config import Config
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
import requests
import os

class WebScraper:
    """Main scraper class combining sitemap parsing and content extraction"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.extractor = ContentExtractor()
        self.llm_cleaner = LLMCleaner(api_key=Config.OPENAI_API_KEY)
        self.zenrows_api_key = Config.ZENROWS_API_KEY
        self.use_zenrows = bool(self.zenrows_api_key)
    
    def scrape_url(self, url: str, options: dict = None) -> dict:
        """
        Scrape a single URL using ZenRows
        
        Args:
            url: URL to scrape
            options: Scraping options (detailed, llmFilter, etc.)
        
        Returns:
            dict with scraped content
        """
        options = options or {}
        detailed = options.get('enableDetailedResponse', False)
        
        # Check cache first
        cache_key = self._get_cache_key(url, options)
        cached = cache_get(cache_key)
        if cached:
            return cached
        
        # Try ZenRows first
        result = None
        if self.zenrows_api_key:
            try:
                print(f"🔍 Scraping {url} with ZenRows...")
                result = zenrows_scrape(url, self.zenrows_api_key)
                
                if result['success']:
                    print(f"✓ ZenRows: Extracted {len(result['text'])} characters")
                else:
                    print(f"⚠ ZenRows failed: {result.get('error', 'Unknown error')}")
                    result = None
            except Exception as e:
                print(f"⚠ ZenRows error: {str(e)}")
                result = None
        
        # Fallback to simple requests if ZenRows failed
        if not result or not result.get('success'):
            try:
                print(f"🔄 Falling back to simple HTTP request...")
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
                response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
                response.raise_for_status()
                
                # Ensure response content is properly decoded (handles gzip/deflate automatically)
                response.encoding = response.apparent_encoding or 'utf-8'
                html_content = response.text
                
                from bs4 import BeautifulSoup
                # Try parsers in order: lxml -> html.parser -> html5lib
                soup = None
                parser_used = None
                for parser in ['lxml', 'html.parser', 'html5lib']:
                    try:
                        soup = BeautifulSoup(html_content, parser)
                        parser_used = parser
                        print(f"✓ Using parser: {parser}")
                        break
                    except Exception as e:
                        print(f"⚠ Parser {parser} failed: {str(e)}")
                        continue
                
                if soup is None:
                    raise Exception("All HTML parsers failed")
                
                # Extract title
                title_tag = soup.find('title')
                title = title_tag.get_text().strip() if title_tag else ''
                
                # Remove unwanted elements
                for tag in soup(['script', 'style', 'noscript']):
                    tag.decompose()
                
                # Get text
                body = soup.find('body') or soup
                text = body.get_text(separator='\n\n', strip=True)
                
                # Validate text content is readable
                if text:
                    non_printable = sum(1 for char in text[:500] if ord(char) < 32 and char not in '\n\r\t')
                    if non_printable > 50:
                        raise Exception("Received garbled content - encoding issue detected")
                
                # Extract links
                base_domain = urlparse(url).netloc
                links = []
                for a in soup.find_all('a', href=True):
                    from urllib.parse import urljoin
                    full_url = urljoin(url, a['href'])
                    if urlparse(full_url).netloc == base_domain:
                        links.append(full_url)
                
                result = {
                    'title': title,
                    'text': text,
                    'links': list(set(links)),
                    'success': True
                }
                print(f"✓ Fallback: Extracted {len(text)} characters")
                
            except Exception as e:
                print(f"✗ Fallback failed: {str(e)}")
                return {
                    'url': url,
                    'status': 'error',
                    'error': f'All scraping methods failed: {str(e)}'
                }
        
        # Build response
        response_data = {
            'title': result['title'],
            'description': '',
            'markdown': result['text'],
            'links': result['links'],
            'url': url,
            'status': 'success'
        }
        
        # Clean with LLM if enabled
        use_llm = options.get('llmFilter', False)
        if use_llm and self.llm_cleaner.enabled:
            print("🤖 Cleaning with LLM...")
            response_data['markdown'] = self.llm_cleaner.clean_content(response_data['markdown'], url)
        
        # Cache the result
        cache_set(cache_key, response_data)
        
        return response_data
    
    def scrape_website(self, base_url: str, options: dict = None) -> dict:
        """
        Scrape entire website
        
        Args:
            base_url: Starting URL
            options: Scraping options
        
        Returns:
            dict with job info and results
        """
        options = options or {}
        max_pages = min(options.get('maxPages', 50), 500)
        crawl_subpages = options.get('crawlSubpages', True)
        follow_sitemap = options.get('followSitemap', True)
        
        urls_to_scrape = [base_url]
        
        # Get URLs from sitemap if enabled
        if follow_sitemap:
            try:
                parser = SitemapParser(base_url)
                sitemap_urls = parser.get_urls_from_sitemap(max_pages)
                urls_to_scrape = sitemap_urls
            except Exception as e:
                print(f"Sitemap parsing failed: {e}")
        
        # Limit to max_pages
        urls_to_scrape = urls_to_scrape[:max_pages]
        
        # Scrape all URLs concurrently
        results = []
        discovered_urls = set(urls_to_scrape)
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {
                executor.submit(self.scrape_url, url, options): url 
                for url in urls_to_scrape
            }
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    # If crawling subpages, add discovered links
                    if crawl_subpages and len(discovered_urls) < max_pages:
                        links = result.get('links', [])
                        for link in links:
                            if link not in discovered_urls and len(discovered_urls) < max_pages:
                                discovered_urls.add(link)
                                # Submit new scraping job
                                future_to_url[executor.submit(self.scrape_url, link, options)] = link
                    
                except Exception as e:
                    results.append({
                        'url': url,
                        'status': 'error',
                        'error': str(e)
                    })
        
        # Generate summary
        successful = [r for r in results if r.get('status') == 'success']
        failed = [r for r in results if r.get('status') == 'error']
        
        return {
            'baseUrl': base_url,
            'totalPages': len(results),
            'successful': len(successful),
            'failed': len(failed),
            'results': results
        }
    
    def _get_cache_key(self, url: str, options: dict) -> str:
        """Generate cache key from URL and options"""
        key_parts = [url]
        if options.get('enableDetailedResponse'):
            key_parts.append('detailed')
        if options.get('llmFilter'):
            key_parts.append('llm')
        
        key_string = '|'.join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
