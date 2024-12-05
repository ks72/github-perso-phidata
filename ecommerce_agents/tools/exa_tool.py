from typing import Dict, List, Optional, Any
from phi.tools.tool import Tool
import requests
import os
import logging

logger = logging.getLogger(__name__)

class ExaSearchTool(Tool):
    """Tool for performing Exa.ai searches with configurable parameters."""
    
    # The type of tool
    type: str = "search"
    name: str = "ExaSearchTool"
    description: str = "Performs Exa.ai searches and returns structured results"
    client: Any = None  # Exa client instance
    
    def __init__(self):
        super().__init__(type=self.type)
        self.api_key = os.getenv("EXA_API_KEY")
        if not self.api_key:
            raise ValueError("EXA_API_KEY environment variable not set")
        self.base_url = "https://api.exa.ai/search"
    
    def _run(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Run Exa search and return structured results.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return (default: 10)
            
        Returns:
            List of dictionaries containing search results with score, title, date, etc.
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            params = {
                "query": query,
                "num_results": max_results
            }
            
            response = requests.post(self.base_url, headers=headers, json=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Structure the results according to requirements
            structured_results = []
            for result in data.get("results", []):
                structured_result = {
                    "score": result.get("score", 0.0),
                    "title": result.get("title", ""),
                    "date": result.get("published_date", ""),
                    "id": result.get("id", ""),
                    "url": result.get("url", ""),
                    "highlight": result.get("highlight", ""),
                    "highlight_score": result.get("highlight_score", 0.0)
                }
                structured_results.append(structured_result)
            
            return structured_results
            
        except Exception as e:
            print(f"Error performing Exa search: {str(e)}")
            return []
    
    async def _arun(self, query: str, max_results: int = 10) -> List[Dict]:
        """Async version of the run method."""
        return self._run(query, max_results)
