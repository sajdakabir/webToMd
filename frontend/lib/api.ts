const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';

export async function scrapeUrl(url: string, options: any) {
  const response = await fetch(`${API_BASE_URL}/scrape`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ url, options }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to scrape URL');
  }

  return response.json();
}

export async function exportResults(results: any[], format: 'markdown' | 'json' | 'zip') {
  const response = await fetch(`${API_BASE_URL}/export`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ results, format }),
  });

  if (!response.ok) {
    throw new Error('Export failed');
  }

  // Extract domain from first successful result
  let filename = `scraped_${Date.now()}.${format === 'zip' ? 'zip' : format === 'json' ? 'json' : 'md'}`;
  
  const firstSuccess = results.find(r => r.status === 'success');
  if (firstSuccess && firstSuccess.url) {
    try {
      const url = new URL(firstSuccess.url);
      let domain = url.hostname.replace('www.', '');
      // Remove TLD (.com, .ai, .io, etc.)
      domain = domain.split('.')[0];
      const extension = format === 'zip' ? 'zip' : format === 'json' ? 'json' : 'md';
      filename = `${domain}.${extension}`;
    } catch (e) {
      console.error('Failed to extract domain:', e);
    }
  }

  // Download the file
  const blob = await response.blob();
  const downloadUrl = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = downloadUrl;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(downloadUrl);
  document.body.removeChild(a);
}
