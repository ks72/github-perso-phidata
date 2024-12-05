from typing import Dict, List, Optional, Any
from phi.tools.tool import Tool
import requests
from bs4 import BeautifulSoup
import json
import os
import logging

logger = logging.getLogger(__name__)

class FirecrawlTool(Tool):
    """Tool for performing Firecrawl searches with configurable parameters."""
    
    # The type of tool
    type: str = "search"
    name: str = "FirecrawlTool"
    description: str = "Performs Firecrawl searches and returns structured results"
    client: Any = None  # Firecrawl client instance
    
    def __init__(self):
        super().__init__(type=self.type)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    def _run(self, urls: List[str], save_path: Optional[str] = None) -> List[Dict]:
        """
        Scrape content from provided URLs.
        
        Args:
            urls: List of URLs to scrape
            save_path: Optional path to save scraped content as JSON
            
        Returns:
            List of dictionaries containing scraped content
        """
        results = []
        
        for url in urls:
            try:
                # Fetch the webpage
                response = requests.get(url, headers=self.headers, timeout=30)
                response.raise_for_status()
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract text content
                text_content = []
                for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                    text = p.get_text(strip=True)
                    if text:  # Only add non-empty text
                        text_content.append({
                            'type': p.name,
                            'content': text
                        })
                
                # Extract images
                images = []
                for img in soup.find_all('img'):
                    src = img.get('src', '')
                    alt = img.get('alt', '')
                    if src:  # Only add images with valid src
                        images.append({
                            'src': src if src.startswith('http') else f"{url.rstrip('/')}/{src.lstrip('/')}",
                            'alt': alt
                        })
                
                # Structure the results
                result = {
                    'url': url,
                    'title': soup.title.string if soup.title else '',
                    'text_content': text_content,
                    'images': images,
                    'status': 'success'
                }
                
            except Exception as e:
                result = {
                    'url': url,
                    'error': str(e),
                    'status': 'error'
                }
            
            results.append(result)
        
        # Save results if path provided
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        
        return results
    
    async def _arun(self, urls: List[str], save_path: Optional[str] = None) -> List[Dict]:
        """Async version of the run method."""
        return self._run(urls, save_path)
