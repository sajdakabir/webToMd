import os
import json
import requests
from typing import Optional

class LLMCleaner:
    """Clean and improve scraped content using LLM"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.enabled = bool(self.api_key)
        self.api_url = "https://api.openai.com/v1/chat/completions"
    
    def clean_content(self, markdown: str, url: str) -> str:
        """
        Clean markdown content using LLM to remove noise
        
        Args:
            markdown: Raw markdown content
            url: Source URL for context
            
        Returns:
            Cleaned markdown content
        """
        if not self.enabled:
            print("⚠️  LLM cleaning disabled (no API key)")
            return markdown
        
        if not markdown or len(markdown) < 100:
            print("⚠️  Content too short for LLM cleaning")
            return markdown
        
        try:
            # Truncate very long content to stay within token limits
            max_chars = 12000  # ~3000 tokens
            content_to_clean = markdown[:max_chars]
            was_truncated = len(markdown) > max_chars
            
            prompt = f"""You are an expert content curator. Clean and optimize the following markdown content scraped from {url}.

**Your mission:**
1. **Remove UI noise**: Navigation menus, footers, headers, cookie notices, "Subscribe" prompts, social media links
2. **Keep valuable content**: Main text, headings, lists, key information, product details, pricing, features
3. **Improve structure**: Ensure proper heading hierarchy (# for main title, ## for sections, etc.)
4. **Remove duplicates**: Eliminate repeated sections or redundant content
5. **Fix formatting**: Clean up broken markdown, excessive line breaks, weird spacing
6. **Preserve links**: Keep important internal/external links
7. **Be concise**: Remove filler words while keeping essential information

**Original content:**
{content_to_clean}

Return ONLY the cleaned, well-structured markdown. No explanations or meta-commentary."""

            print(f"🤖 Cleaning content with OpenAI (length: {len(content_to_clean)} chars)...")
            
            # Use requests instead of openai library to avoid pydantic
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are a content cleaning expert who removes noise from scraped web content while preserving valuable information. Output clean markdown only."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,
                "max_tokens": 4000
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"❌ OpenAI API error: {response.status_code} - {response.text}")
                return markdown
            
            result = response.json()
            cleaned = result['choices'][0]['message']['content'].strip()
            
            # Remove markdown code fences if LLM added them
            if cleaned.startswith("```markdown"):
                cleaned = cleaned[11:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            # If truncated, append notice
            if was_truncated:
                cleaned += f"\n\n*[Note: Content was truncated due to length. Original length: {len(markdown)} characters]*"
            
            print(f"✅ LLM cleaning complete (reduced from {len(markdown)} to {len(cleaned)} chars)")
            return cleaned if cleaned else markdown
            
        except Exception as e:
            print(f"❌ LLM cleaning failed: {e}")
            return markdown
    
    def clean_batch(self, contents: list[dict]) -> list[dict]:
        """
        Clean multiple content items
        
        Args:
            contents: List of dicts with 'markdown' and 'url' keys
            
        Returns:
            List of dicts with cleaned markdown
        """
        if not self.enabled:
            return contents
        
        cleaned_contents = []
        for item in contents:
            cleaned_item = item.copy()
            cleaned_item['markdown'] = self.clean_content(
                item.get('markdown', ''),
                item.get('url', '')
            )
            cleaned_contents.append(cleaned_item)
        
        return cleaned_contents
