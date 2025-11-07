'use client';

import { useState } from 'react';
import { Loader2 } from 'lucide-react';

interface UrlInputProps {
  onScrape: (url: string, options: any) => void;
  loading: boolean;
}

export default function UrlInput({ onScrape, loading }: UrlInputProps) {
  const [url, setUrl] = useState('');
  const [maxPages, setMaxPages] = useState(10);
  const [crawlSubpages, setCrawlSubpages] = useState(false);
  const [followSitemap, setFollowSitemap] = useState(true);
  const [detailedResponse, setDetailedResponse] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;

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
            type="url"
            id="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-transparent"
            required
            disabled={loading}
          />
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
