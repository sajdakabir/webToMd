'use client';

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Download, FileText, Archive } from 'lucide-react';
import { exportResults } from '@/lib/api';

interface ResultsDisplayProps {
  results: any;
}

export default function ResultsDisplay({ results }: ResultsDisplayProps) {
  const [selectedPage, setSelectedPage] = useState(0);
  const [exporting, setExporting] = useState(false);

  const successfulResults = results.results?.filter((r: any) => r.status === 'success') || [];
  const currentResult = successfulResults[selectedPage];

  const handleExport = async (format: 'markdown' | 'json' | 'zip') => {
    setExporting(true);
    try {
      await exportResults(results.results, format);
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setExporting(false);
    }
  };

  if (!successfulResults.length) {
    return (
      <div className="mt-6 p-6 bg-yellow-50 border border-yellow-200 rounded-lg">
        <p className="text-yellow-800">No content could be extracted from the provided URL(s).</p>
      </div>
    );
  }

  return (
    <div className="mt-8 space-y-6">
      {/* Summary */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-2xl font-bold mb-4">Results</h2>
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-3xl font-bold text-blue-600">{results.totalPages}</div>
            <div className="text-sm text-gray-600">Total Pages</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-green-600">{results.successful}</div>
            <div className="text-sm text-gray-600">Successful</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-red-600">{results.failed}</div>
            <div className="text-sm text-gray-600">Failed</div>
          </div>
        </div>
      </div>

      {/* Export Buttons */}
      <div className="flex gap-3">
        <button
          onClick={() => handleExport('markdown')}
          disabled={exporting}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:bg-gray-400"
        >
          <FileText className="w-4 h-4" />
          <span>Export MD</span>
        </button>
        <button
          onClick={() => handleExport('zip')}
          disabled={exporting}
          className="flex items-center space-x-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors disabled:bg-gray-400"
        >
          <Archive className="w-4 h-4" />
          <span>Export ZIP</span>
        </button>
        <button
          onClick={() => handleExport('json')}
          disabled={exporting}
          className="flex items-center space-x-2 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors disabled:bg-gray-400"
        >
          <Download className="w-4 h-4" />
          <span>Export JSON</span>
        </button>
      </div>

      {/* Page Selector */}
      {successfulResults.length > 1 && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Page ({successfulResults.length} total)
          </label>
          <select
            value={selectedPage}
            onChange={(e) => setSelectedPage(parseInt(e.target.value))}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            {successfulResults.map((result: any, index: number) => (
              <option key={index} value={index}>
                {result.title || result.url}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Markdown Preview */}
      {currentResult && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="mb-4">
            <h3 className="text-xl font-bold">{currentResult.title}</h3>
            <a
              href={currentResult.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-blue-600 hover:underline"
            >
              {currentResult.url}
            </a>
          </div>

          <div className="prose max-w-none">
            <ReactMarkdown>{currentResult.markdown}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
}
