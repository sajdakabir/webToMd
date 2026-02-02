/**
 * URL validation and security utilities
 */

// SQL injection patterns to detect
const SQL_INJECTION_PATTERNS = [
  /(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE|UNION|DECLARE)\b)/i,
  /(--|;|\/\*|\*\/|xp_|sp_)/,
  /(\bOR\b.*=.*|\bAND\b.*=.*)/i,
  /('|(\-\-)|(;)|(\|\|)|(\*))/,
  /(\bSCRIPT\b|<script|javascript:)/i,
];

export interface ValidationResult {
  valid: boolean;
  error: string;
  sanitizedUrl?: string;
}

/**
 * Sanitize input string by removing dangerous characters
 */
export function sanitizeInput(input: string): string {
  if (!input) return '';
  
  // Remove null bytes and control characters
  let sanitized = input.replace(/\x00/g, '');
  sanitized = sanitized.replace(/[\x00-\x1F\x7F]/g, '');
  
  return sanitized.trim();
}

/**
 * Check if input contains SQL injection patterns
 */
export function containsSqlInjection(input: string): boolean {
  if (!input) return false;
  
  for (const pattern of SQL_INJECTION_PATTERNS) {
    if (pattern.test(input)) {
      return true;
    }
  }
  
  return false;
}

/**
 * Comprehensive URL validation with security checks
 */
export function validateUrl(url: string): ValidationResult {
  // Check if URL is empty
  if (!url || url.trim().length === 0) {
    return { valid: false, error: 'URL is required' };
  }

  // Sanitize the input
  const sanitized = sanitizeInput(url);

  // Check length constraints
  if (sanitized.length > 2048) {
    return { valid: false, error: 'URL is too long (max 2048 characters)' };
  }

  if (sanitized.length < 10) {
    return { valid: false, error: 'URL is too short' };
  }

  // Check for SQL injection patterns
  if (containsSqlInjection(sanitized)) {
    return { valid: false, error: 'Invalid URL: contains prohibited characters' };
  }

  // Add protocol if missing
  let testUrl = sanitized;
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

    // Block private IP ranges (10.x.x.x, 172.16-31.x.x, 192.168.x.x)
    if (/^(10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.)/.test(urlObj.hostname)) {
      return { valid: false, error: 'Cannot scrape private IP addresses' };
    }

    return { valid: true, error: '', sanitizedUrl: testUrl };
  } catch (e) {
    return { valid: false, error: 'Invalid URL format' };
  }
}

/**
 * Normalize URL by adding protocol if missing
 */
export function normalizeUrl(url: string): string {
  if (!url) return '';
  
  const sanitized = sanitizeInput(url);
  
  if (!sanitized.startsWith('http://') && !sanitized.startsWith('https://')) {
    return 'https://' + sanitized;
  }
  
  return sanitized;
}
