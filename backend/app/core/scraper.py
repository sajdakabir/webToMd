from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from app.core.extractor import ContentExtractor
from app.core.sitemap import SitemapParser
from app.utils.cache import cache_get, cache_set
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

class WebScraper:
    """Main scraper class combining sitemap parsing and content extraction"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.extractor = ContentExtractor()
    
    def scrape_url(self, url: str, options: dict = None) -> dict:
        """
        Scrape a single URL
        
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
        
        # Scrape the page
        browser = None
        context = None
        page = None
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=['--disable-blink-features=AutomationControlled']
                )
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080}
                )
                page = context.new_page()
                
                # Navigate to URL
                page.goto(url, wait_until='domcontentloaded', timeout=30000)
                page.wait_for_timeout(2000)  # Wait 2 seconds for JS to load
                
                # Get HTML content
                html = page.content()
                
                # Properly close everything
                page.close()
                context.close()
                browser.close()
            
            # Extract and convert to markdown
            result = self.extractor.extract_content(html, url, detailed)
            result['status'] = 'success'
            
            # Cache the result
            cache_set(cache_key, result)
            
            return result
            
        except PlaywrightTimeout:
            return {
                'url': url,
                'status': 'error',
                'error': 'Page load timeout'
            }
        except Exception as e:
            return {
                'url': url,
                'status': 'error',
                'error': str(e)
            }
        finally:
            # Ensure cleanup even if error occurs
            try:
                if page:
                    page.close()
                if context:
                    context.close()
                if browser:
                    browser.close()
            except:
                pass
    
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
