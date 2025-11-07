'use client';

import { useState } from 'react';
import { Loader2, Download } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export default function Home() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [markdown, setMarkdown] = useState<string>('');

  const handleScrape = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;

    setLoading(true);
    setError(null);
    setMarkdown('');

    try {
      const response = await fetch('http://localhost:5000/api/scrape', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        throw new Error('Failed to scrape URL');
      }

      const data = await response.json();
      
      if (data.results && data.results[0]) {
        if (data.results[0].status === 'success') {
          setMarkdown(data.results[0].markdown);
        } else {
          setError(data.results[0].error || 'Failed to extract content');
        }
      }
    } catch (err: any) {
      setError(err.message || 'Failed to scrape URL');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    const blob = new Blob([markdown], { type: 'text/markdown' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'content.md';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-5xl font-bold text-gray-900 mb-4">
              Web to Markdown ⚡
            </h1>
            <p className="text-xl text-gray-600">
              Convert any website into clean, LLM-ready markdown
            </p>
          </div>

          {/* Input Form */}
          <div className="bg-white rounded-xl shadow-lg p-8 mb-6">
            <form onSubmit={handleScrape} className="space-y-4">
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

              <button
                type="submit"
                disabled={loading || !url}
                className="w-full bg-gray-900 hover:bg-black disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition-colors flex items-center justify-center space-x-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Converting...</span>
                  </>
                ) : (
                  <span>Convert to Markdown</span>
                )}
              </button>
            </form>
          </div>

          {/* Error Display */}
          {error && (
            <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-yellow-800">{error}</p>
            </div>
          )}

          {/* Preview and Download */}
          {markdown && (
            <div className="space-y-4">
              {/* Download Button */}
              <div className="flex justify-end">
                <button
                  onClick={handleDownload}
                  className="flex items-center space-x-2 px-6 py-3 bg-gray-700 hover:bg-gray-800 text-white font-semibold rounded-lg transition-colors"
                >
                  <Download className="w-5 h-5" />
                  <span>Download Markdown</span>
                </button>
              </div>

              {/* Preview */}
              <div className="bg-white rounded-lg shadow-sm p-8">
                <h2 className="text-2xl font-bold mb-4 text-gray-900">Preview</h2>
                <div className="prose max-w-none">
                  <ReactMarkdown>{markdown}</ReactMarkdown>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
