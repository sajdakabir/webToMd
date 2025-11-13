from app.core.extractor import ContentExtractor
from app.core.sitemap import SitemapParser
from app.core.llm_cleaner import LLMCleaner
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
        self.llm_cleaner = LLMCleaner()
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
        
        # Scrape with ZenRows
        try:
            params = {
                'url': url,
                'apikey': self.zenrows_api_key,
                'js_render': 'true',
                'premium_proxy': 'true',
                'wait': '2000'
            }
            response = requests.get('https://api.zenrows.com/v1/', params=params, timeout=60)
            response.raise_for_status()
            html = response.text
        except Exception as e:
            return {
                'url': url,
                'status': 'error',
                'error': f'ZenRows scraping failed: {str(e)}'
            }
        
        # Extract and convert to markdown
        try:
            result = self.extractor.extract_content(html, url, detailed)
            result['status'] = 'success'
            
            # Clean with LLM if enabled
            use_llm = options.get('llmFilter', False)
            if use_llm and self.llm_cleaner.enabled:
                result['markdown'] = self.llm_cleaner.clean_content(result['markdown'], url)
            
            # Cache the result
            cache_set(cache_key, result)
            
            return result
        except Exception as e:
            return {
                'url': url,
                'status': 'error',
                'error': f'Content extraction failed: {str(e)}'
            }
    
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
