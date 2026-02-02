'use client';

import { useState } from 'react';
import { Loader2, AlertCircle } from 'lucide-react';

interface UrlInputProps {
  onScrape: (url: string, options: any) => void;
  loading: boolean;
}

// SQL injection patterns to detect
const SQL_INJECTION_PATTERNS = [
  /(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE|UNION|DECLARE)\b)/i,
  /(--|;|\/\*|\*\/|xp_|sp_)/,
  /(\bOR\b.*=.*|\bAND\b.*=.*)/i,
  /('|(\-\-)|(;)|(\|\|)|(\*))/,
  /(\bSCRIPT\b|<script|javascript:)/i,
];

function validateUrl(url: string): { valid: boolean; error: string } {
  // Check if URL is empty
  if (!url || url.trim().length === 0) {
    return { valid: false, error: 'URL is required' };
  }

  // Check length constraints
  if (url.length > 2048) {
    return { valid: false, error: 'URL is too long (max 2048 characters)' };
  }

  if (url.length < 10) {
    return { valid: false, error: 'URL is too short' };
  }

  // Check for SQL injection patterns
  for (const pattern of SQL_INJECTION_PATTERNS) {
    if (pattern.test(url)) {
      return { valid: false, error: 'Invalid URL: contains prohibited characters' };
    }
  }

  // Add protocol if missing
  let testUrl = url;
  if (!testUrl.startsWith('http://') && !testUrl.startsWith('https://')) {
    testUrl = 'https://' + testUrl;
  }

  // Validate URL format
  try {
    const urlObj = new URL(testUrl);
    
    // Check protocol
    if (urlObj.protocol !== 'http:' && urlObj.protocol !== 'https:') {
      return { valid: false, error: 'URL must use HTTP or HTTPS protocol' };
    }

    // Check for valid hostname
    if (!urlObj.hostname || urlObj.hostname.length < 3) {
      return { valid: false, error: 'Invalid domain name' };
    }

    // Block localhost and private IPs
    const blockedHosts = ['localhost', '127.0.0.1', '0.0.0.0', '::1'];
    if (blockedHosts.includes(urlObj.hostname.toLowerCase())) {
      return { valid: false, error: 'Cannot scrape localhost URLs' };
    }

    // Block private IP ranges
    if (/^(10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.)/.test(urlObj.hostname)) {
      return { valid: false, error: 'Cannot scrape private IP addresses' };
    }

    return { valid: true, error: '' };
  } catch (e) {
    return { valid: false, error: 'Invalid URL format' };
  }
}

export default function UrlInput({ onScrape, loading }: UrlInputProps) {
  const [url, setUrl] = useState('');
  const [maxPages, setMaxPages] = useState(10);
  const [crawlSubpages, setCrawlSubpages] = useState(false);
  const [followSitemap, setFollowSitemap] = useState(true);
  const [detailedResponse, setDetailedResponse] = useState(false);
  const [urlError, setUrlError] = useState('');

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newUrl = e.target.value;
    setUrl(newUrl);
    
    // Clear error when user starts typing
    if (urlError) {
      setUrlError('');
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate URL before submitting
    const validation = validateUrl(url);
    if (!validation.valid) {
      setUrlError(validation.error);
      return;
    }

    setUrlError('');

    const options = {
      maxPages,
      crawlSubpages,
      followSitemap,
      enableDetailedResponse: detailedResponse,
    };

    onScrape(url, options);
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-8">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* URL Input */}
        <div>
          <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-2">
            Website URL
          </label>
          <input
            type="text"
            id="url"
            value={url}
            onChange={handleUrlChange}
            placeholder="https://example.com"
            className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:border-transparent ${
              urlError
                ? 'border-red-500 focus:ring-red-500'
                : 'border-gray-300 focus:ring-gray-500'
            }`}
            required
            disabled={loading}
          />
          {urlError && (
            <div className="mt-2 flex items-center text-sm text-red-600">
              <AlertCircle className="w-4 h-4 mr-1" />
              <span>{urlError}</span>
            </div>
          )}
        </div>

        {/* Options */}
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="maxPages" className="block text-sm font-medium text-gray-700 mb-2">
              Max Pages
            </label>
            <input
              type="number"
              id="maxPages"
              value={maxPages}
              onChange={(e) => setMaxPages(parseInt(e.target.value))}
              min="1"
              max="500"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-500"
              disabled={loading}
            />
          </div>

          <div className="space-y-3 pt-8">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={crawlSubpages}
                onChange={(e) => setCrawlSubpages(e.target.checked)}
                className="w-4 h-4 text-gray-600 rounded focus:ring-gray-500"
                disabled={loading}
              />
              <span className="text-sm text-gray-700">Crawl subpages</span>
            </label>

            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={followSitemap}
                onChange={(e) => setFollowSitemap(e.target.checked)}
                className="w-4 h-4 text-gray-600 rounded focus:ring-gray-500"
                disabled={loading}
              />
              <span className="text-sm text-gray-700">Follow sitemap</span>
            </label>

            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={detailedResponse}
                onChange={(e) => setDetailedResponse(e.target.checked)}
                className="w-4 h-4 text-gray-600 rounded focus:ring-gray-500"
                disabled={loading}
              />
              <span className="text-sm text-gray-700">Detailed response</span>
            </label>
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading || !url}
          className="w-full bg-gray-900 hover:bg-black disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition-colors flex items-center justify-center space-x-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Scraping...</span>
            </>
          ) : (
            <span>Convert to Markdown</span>
          )}
        </button>
      </form>
    </div>
  );
}
