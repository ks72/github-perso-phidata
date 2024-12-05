"""
SemanticSearchAgent for performing semantic searches using Exa AI with business URL exclusions.

This agent uses Exa AI to:
1. Perform semantic searches with natural language understanding
2. Exclude business and competitor URLs from results
3. Return top 15 results with source tracking
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from phi.agent import Agent
from ..admin.api import AdminAPI
from ..tools.exa_tool import ExaSearchTool
import os
import asyncio

class SemanticSearchAgent(Agent):
    """
    An agent for performing semantic searches using Exa AI while
    respecting business URL exclusions.
    """

    def __init__(self, admin_api: AdminAPI = None, **kwargs):
        """Initialize with admin API for URL exclusions."""
        super().__init__(**kwargs)
        self.admin_api = admin_api or AdminAPI()
        self.search_tool = ExaSearchTool()

    async def get_excluded_urls(self, user_id: str) -> List[str]:
        """Get URLs to exclude from search results."""
        settings = await self.admin_api.get_settings(user_id)
        excluded = []
        # Add main business URLs
        excluded.extend(settings.main_urls)
        # Add competitor URLs
        excluded.extend(settings.competitors)
        return excluded

    async def search(self, 
                    query: str,
                    user_id: str,
                    max_results: int = 15,
                    use_highlights: bool = True
                    ) -> List[Dict[str, Any]]:
        """
        Perform a semantic search using Exa AI.
        
        Args:
            query: Search query
            user_id: User ID for getting excluded URLs
            max_results: Maximum number of results to return
            use_highlights: Whether to include relevant text highlights
        """
        # Get URLs to exclude
        excluded_urls = await self.get_excluded_urls(user_id)
        
        # Prepare exclude sites query
        exclude_query = " ".join(f"-site:{url}" for url in excluded_urls)
        
        # Combine with original query
        full_query = f"{query} {exclude_query}"

        # Use the Exa tool
        results = self.search_tool._run(full_query, max_results=max_results * 2)
        
        # Filter and enhance results
        filtered_results = []
        for r in results:
            # Skip if URL contains any excluded domain
            if any(ex_url in r['url'] for ex_url in excluded_urls):
                continue
            
            # Add additional metadata
            r.update({
                'source': 'exa_ai',
                'timestamp': datetime.now().isoformat()
            })
            
            filtered_results.append(r)
            if len(filtered_results) >= max_results:
                break

        return filtered_results[:max_results]

    async def run(self, user_id: str, query: str, **kwargs) -> Dict[str, Any]:
        """Run the agent with the given query."""
        max_results = kwargs.get('max_results', 15)
        use_highlights = kwargs.get('use_highlights', True)
        
        # Get structured query from previous agent if available
        structured_query = kwargs.get('structured_query')
        if structured_query:
            # Use the structured query components
            query = f"{structured_query.get('focus', '')} {structured_query.get('objective', '')} {structured_query.get('context', '')}"
            # Add scope if available
            if 'scope' in structured_query:
                query = f"{query} {structured_query['scope']}"
        
        results = await self.search(
            query=query,
            user_id=user_id,
            max_results=max_results,
            use_highlights=use_highlights
        )
        
        return {
            'query': query,
            'results': results,
            'total_results': len(results),
            'timestamp': datetime.now().isoformat()
        }
