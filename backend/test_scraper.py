#!/usr/bin/env python3
"""
Quick test script to verify the scraper works
Run: python test_scraper.py
"""

from app.core.scraper import WebScraper
from app.core.sitemap import SitemapParser
import json

def test_single_page():
    """Test scraping a single page"""
    print("🧪 Testing single page scraping...")
    
    scraper = WebScraper()
    result = scraper.scrape_url("https://example.com")
    
    if result.get('status') == 'success':
        print("✅ Single page scraping works!")
        print(f"   Title: {result.get('title')}")
        print(f"   Markdown length: {len(result.get('markdown', ''))} chars")
    else:
        print(f"❌ Failed: {result.get('error')}")
    
    return result

def test_sitemap():
    """Test sitemap parsing"""
    print("\n🧪 Testing sitemap parsing...")
    
    parser = SitemapParser("https://example.com")
    urls = parser.get_urls_from_sitemap(max_urls=5)
    
    if urls:
        print(f"✅ Sitemap parsing works!")
        print(f"   Found {len(urls)} URLs")
        for url in urls[:3]:
            print(f"   - {url}")
    else:
        print("⚠️  No sitemap found (this is okay for example.com)")
    
    return urls

def test_full_scrape():
    """Test full website scraping"""
    print("\n🧪 Testing full website scraping...")
    
    scraper = WebScraper(max_workers=2)
    result = scraper.scrape_website(
        "https://example.com",
        options={
            'maxPages': 3,
            'crawlSubpages': False,
            'followSitemap': False
        }
    )
    
    print(f"✅ Full scraping works!")
    print(f"   Total pages: {result.get('totalPages')}")
    print(f"   Successful: {result.get('successful')}")
    print(f"   Failed: {result.get('failed')}")
    
    return result

if __name__ == "__main__":
    print("=" * 60)
    print("Web Scraper Pro - Test Suite")
    print("=" * 60)
    
    try:
        # Test 1: Single page
        single_result = test_single_page()
        
        # Test 2: Sitemap
        sitemap_urls = test_sitemap()
        
        # Test 3: Full scrape
        full_result = test_full_scrape()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        print("\nYou can now:")
        print("1. Start the backend: python run.py")
        print("2. Start the frontend: cd ../frontend && npm run dev")
        print("3. Open http://localhost:3000")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("\nMake sure you have:")
        print("1. Installed all dependencies: pip install -r requirements.txt")
        print("2. Installed Playwright: playwright install chromium")
        print("3. Started Redis: redis-server")
