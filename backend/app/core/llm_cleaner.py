import os
from typing import Optional

class LLMCleaner:
    """Clean and improve scraped content using LLM"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.enabled = bool(self.api_key)
    
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
            return markdown
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            prompt = f"""You are a content cleaning assistant. Clean and improve the following markdown content scraped from {url}.

Your task:
1. Remove navigation menus, footers, cookie notices, and other UI noise
2. Keep only the main content that would be useful for understanding the page
3. Preserve headings, paragraphs, lists, and important information
4. Remove duplicate content
5. Fix formatting issues
6. Keep the content in markdown format
7. Remove excessive whitespace but maintain readability

Original content:
{markdown}

Return ONLY the cleaned markdown content, nothing else."""

            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Fast and cheap model
                messages=[
                    {"role": "system", "content": "You are a content cleaning assistant that removes noise from scraped web content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            cleaned = response.choices[0].message.content.strip()
            return cleaned if cleaned else markdown
            
        except Exception as e:
            print(f"LLM cleaning failed: {e}")
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
