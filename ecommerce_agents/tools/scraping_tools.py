"""Tools for web scraping and content extraction."""
from typing import Dict, Any, Optional, List
import os
from firecrawl import FireCrawl

class FirecrawlTool:
    """Tool for scraping web content using Firecrawl."""
    
    def __init__(self):
        """Initialize the Firecrawl client."""
        self.client = FireCrawl(api_key=os.getenv('FIRECRAWL_API_KEY'))
        
    def scrape_url(self, url: str, elements: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Scrape content from a URL.
        
        Args:
            url: The URL to scrape
            elements: Optional list of specific HTML elements to target
            
        Returns:
            Dictionary containing scraped content including text, images, and metadata
        """
        try:
            # Configure scraping options
            options = {
                'wait_for': elements if elements else ['body'],
                'extract_text': True,
                'extract_images': True,
                'extract_metadata': True
            }
            
            # Perform the scrape
            result = self.client.scrape(url, options)
            
            # Process and format the result
            content = {
                'url': url,
                'text': result.get('text', ''),
                'images': result.get('images', []),
                'metadata': {
                    'title': result.get('metadata', {}).get('title', ''),
                    'description': result.get('metadata', {}).get('description', ''),
                    'author': result.get('metadata', {}).get('author', ''),
                    'published_date': result.get('metadata', {}).get('published_date', ''),
                    'modified_date': result.get('metadata', {}).get('modified_date', '')
                }
            }
            
            return content
        except Exception as e:
            print(f"Error scraping URL {url}: {str(e)}")
            return {
                'url': url,
                'error': str(e)
            }
            
    def extract_article(self, url: str) -> Dict[str, Any]:
        """
        Extract article content from a URL using article extraction mode.
        
        Args:
            url: The URL of the article to extract
            
        Returns:
            Dictionary containing the extracted article content
        """
        try:
            # Configure article extraction options
            options = {
                'mode': 'article',
                'extract_text': True,
                'extract_images': True,
                'extract_metadata': True
            }
            
            # Perform the extraction
            result = self.client.scrape(url, options)
            
            # Process and format the article
            article = {
                'url': url,
                'title': result.get('title', ''),
                'content': result.get('content', ''),
                'author': result.get('author', ''),
                'published_date': result.get('published_date', ''),
                'images': result.get('images', []),
                'summary': result.get('summary', '')
            }
            
            return article
        except Exception as e:
            print(f"Error extracting article from {url}: {str(e)}")
            return {
                'url': url,
                'error': str(e)
            }
