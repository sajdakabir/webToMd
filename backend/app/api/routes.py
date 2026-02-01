from flask import Blueprint, request, jsonify, send_file
from app.core.scraper import WebScraper
from app.utils.validators import is_valid_url, normalize_url
from app import limiter
import os
import zipfile
from datetime import datetime

api_bp = Blueprint('api', __name__)
scraper = WebScraper()

@api_bp.route('/', methods=['GET'])
def root():
    """Root API endpoint"""
    return jsonify({'message': 'Hi from webtomd', 'status': 'connected'})

@api_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'timestamp': datetime.utcnow().isoformat()})

@api_bp.route('/scrape', methods=['POST'])
@limiter.limit("10 per minute")
def scrape():
    """
    Scrape a URL or entire website
    
    Body:
    {
        "url": "https://example.com",
        "options": {
            "maxPages": 50,
            "crawlSubpages": true,
            "enableDetailedResponse": false,
            "followSitemap": true
        }
    }
    """
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400
    
    url = normalize_url(data['url'])
    
    if not is_valid_url(url):
        return jsonify({'error': 'Invalid URL format'}), 400
    
    options = data.get('options', {})
    
    # Determine if single page or full website scrape
    crawl_subpages = options.get('crawlSubpages', False)
    
    try:
        if crawl_subpages:
            # Scrape entire website
            result = scraper.scrape_website(url, options)
        else:
            # Scrape single page
            result = scraper.scrape_url(url, options)
            result = {
                'baseUrl': url,
                'totalPages': 1,
                'successful': 1 if result.get('status') == 'success' else 0,
                'failed': 0 if result.get('status') == 'success' else 1,
                'results': [result]
            }
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/scrape/preview', methods=['POST'])
@limiter.limit("20 per minute")
def preview():
    """
    Quick preview of a single page (no caching, fast response)
    """
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400
    
    url = normalize_url(data['url'])
    
    if not is_valid_url(url):
        return jsonify({'error': 'Invalid URL format'}), 400
    
    try:
        result = scraper.scrape_url(url, {'enableDetailedResponse': False})
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/export', methods=['POST'])
def export():
    """
    Export scraped results as a file
    
    Body:
    {
        "results": [...],
        "format": "markdown" | "zip" | "json"
    }
    """
    data = request.get_json()
    
    if not data or 'results' not in data:
        return jsonify({'error': 'Results are required'}), 400
    
    results = data['results']
    format_type = data.get('format', 'markdown')
    
    try:
        if format_type == 'json':
            # Return as JSON file
            import json
            from urllib.parse import urlparse
            
            # Use domain name for JSON file
            json_domain = None
            if results and results[0].get('status') == 'success':
                parsed_url = urlparse(results[0].get('url', ''))
                json_domain = parsed_url.netloc.replace('www.', '')
            
            if json_domain:
                filename = f"{json_domain}.json"
            else:
                filename = f"scraped_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            filepath = os.path.join('/tmp', filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            
            return send_file(filepath, as_attachment=True, download_name=filename)
        
        elif format_type == 'zip':
            # Extract domain name for ZIP filename
            from urllib.parse import urlparse
            zip_domain = None
            if results and results[0].get('status') == 'success':
                parsed_url = urlparse(results[0].get('url', ''))
                zip_domain = parsed_url.netloc.replace('www.', '')
            
            # Use domain name for ZIP file
            if zip_domain:
                filename = f"{zip_domain}.zip"
            else:
                filename = f"scraped_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            
            filepath = os.path.join('/tmp', filename)
            
            with zipfile.ZipFile(filepath, 'w') as zipf:
                for i, result in enumerate(results):
                    if result.get('status') == 'success':
                        # Extract domain name from URL
                        parsed_url = urlparse(result.get('url', ''))
                        domain = parsed_url.netloc.replace('www.', '')
                        
                        # Use domain as filename, fallback to page number
                        if domain:
                            md_filename = f"{domain}.md"
                        else:
                            md_filename = f"page_{i+1}.md"
                        
                        # Sanitize filename
                        md_filename = "".join(c for c in md_filename if c.isalnum() or c in ('.', '-', '_')).rstrip()
                        zipf.writestr(md_filename, result.get('markdown', ''))
            
            return send_file(filepath, as_attachment=True, download_name=filename)
        
        else:  # markdown (single file)
            # If only one result, use domain name
            if len(results) == 1 and results[0].get('status') == 'success':
                from urllib.parse import urlparse
                parsed_url = urlparse(results[0].get('url', ''))
                domain = parsed_url.netloc.replace('www.', '')
                filename = f"{domain}.md" if domain else f"scraped_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            else:
                filename = f"scraped_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            
            filepath = os.path.join('/tmp', filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                for result in results:
                    if result.get('status') == 'success':
                        f.write(f"# {result.get('title', 'Untitled')}\n\n")
                        f.write(f"**URL:** {result.get('url')}\n\n")
                        f.write("---\n\n")
                        f.write(result.get('markdown', ''))
                        f.write("\n\n")
            
            return send_file(filepath, as_attachment=True, download_name=filename)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
