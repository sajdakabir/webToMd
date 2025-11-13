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
    // Extract domain from URL for filename
    let filename = 'content.md';
    try {
      const urlObj = new URL(url);
      let domain = urlObj.hostname.replace('www.', '');
      // Remove TLD (.com, .ai, .io, etc.)
      domain = domain.split('.')[0];
      filename = `${domain}.md`;
    } catch (e) {
      console.error('Failed to extract domain:', e);
    }

    const blob = new Blob([markdown], { type: 'text/markdown' });
    const downloadUrl = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = downloadUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(downloadUrl);
    document.body.removeChild(a);
  };

  return (
    <main className="min-h-screen bg-white">
      <div className="container mx-auto px-6 py-20">
        <div className="max-w-3xl mx-auto">
          {/* Header */}
          <div className="mb-16 text-center">
            <h1 className="text-xl  text-black mb-2 tracking-tight">
              Web to Markdown 
            </h1>
            <p className="text-md text-gray-500 font-light">
              Convert any website into clean, LLM-ready markdown
            </p>
          </div>

          {/* Input Form */}
          <div className="bg-gray-50 rounded-2xl p-8 mb-6">
            <form onSubmit={handleScrape}>
              <div className="flex items-center gap-4">
                {/* Icon */}
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center shadow-sm">
                    <svg className="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                </div>

                {/* Input */}
                <input
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="Enter website URL..."
                  className="flex-1 px-4 py-3 bg-transparent border-none focus:outline-none text-gray-900 placeholder-gray-400"
                  required
                  disabled={loading}
                />

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={loading || !url}
                  className="flex-shrink-0 w-12 h-12 bg-gray-700 hover:bg-gray-800 disabled:bg-gray-300 rounded-full flex items-center justify-center transition-colors"
                >
                  {loading ? (
                    <Loader2 className="w-5 h-5 text-white animate-spin" />
                  ) : (
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                    </svg>
                  )}
                </button>
              </div>

            </form>
            
          </div>

              <p className="text-sm text-gray-400 mt-4 text-center">
                Press Enter or use the arrow to send
              </p>
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
