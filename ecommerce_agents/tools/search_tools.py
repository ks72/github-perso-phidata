"""Tools for performing web searches using various search engines."""
from typing import List, Dict, Any
import os
import json
from duckduckgo_search import ddg
from exa_py import Exa

class DuckDuckGoSearchTool:
    """Tool for performing web searches using DuckDuckGo."""
    
    def search(self, query: str, max_results: int = 10) -> List[Dict[str, str]]:
        """
        Perform a web search using DuckDuckGo.
        
        Args:
            query: The search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of dictionaries containing search results with 'title', 'link', and 'snippet' keys
        """
        try:
            results = ddg(query, max_results=max_results)
            formatted_results = []
            
            for result in results:
                formatted_results.append({
                    'title': result['title'],
                    'link': result['link'],
                    'snippet': result['body']
                })
                
            return formatted_results
        except Exception as e:
            print(f"Error performing DuckDuckGo search: {str(e)}")
            return []

class ExaSearchTool:
    """Tool for performing web searches using Exa."""
    
    def __init__(self):
        """Initialize the Exa search client."""
        self.client = Exa(api_key=os.getenv('EXA_API_KEY'))
        
    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Perform a web search using Exa.
        
        Args:
            query: The search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of dictionaries containing search results with metadata
        """
        try:
            results = self.client.search(query, num_results=max_results)
            return results.results
        except Exception as e:
            print(f"Error performing Exa search: {str(e)}")
            return []
