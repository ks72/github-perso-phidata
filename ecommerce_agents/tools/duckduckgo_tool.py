"""
DuckDuckGo search tool for performing web searches with configurable parameters.

This tool provides a clean interface to the DuckDuckGo search API with:
1. Configurable search parameters (region, safesearch, timelimit)
2. Structured result format
3. Error handling and logging
4. Both sync and async interfaces

The tool is designed to work within the phidata workflow system:
- Results are returned in a format compatible with workflow storage
- Error handling integrates with workflow retry mechanisms
- Logging coordinates with workflow logging

Example:
    tool = DuckDuckGoSearchTool()
    results = tool._run(
        query="market trends 2024",
        region="us-en",
        max_results=10,
        timelimit="m"
    )
"""
from typing import Dict, List, Optional, Any
from phi.tools.tool import Tool
from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import RatelimitException
import logging
import time

logger = logging.getLogger(__name__)

class DuckDuckGoSearchTool(Tool):
    """Tool for performing DuckDuckGo searches with configurable parameters."""
    
    type: str = "search"
    name: str = "DuckDuckGoSearchTool"
    description: str = "Performs DuckDuckGo searches and returns structured results"
    client: Any = None  # DDGS instance
    
    def __init__(self):
        """Initialize DuckDuckGo search client."""
        super().__init__()
        self.client = DDGS()

    def _run_with_retry(self, query: str, max_results: int, region: str, 
                       safesearch: str, timelimit: Optional[str], 
                       max_retries: int = 3, initial_delay: float = 1.0) -> List[Dict]:
        """Run search with retry logic for rate limits."""
        delay = initial_delay
        attempt = 0
        
        while attempt < max_retries:
            try:
                # Get raw results from DuckDuckGo
                ddg_results = list(self.client.text(
                    query,
                    region=region,
                    safesearch=safesearch,
                    timelimit=timelimit
                ))
                
                logger.info(f"Raw DuckDuckGo results count: {len(ddg_results)}")
                
                results = []
                for r in ddg_results:
                    # Print raw result for debugging
                    print("\nRaw DuckDuckGo result:")
                    for key, value in r.items():
                        print(f"{key}: {value}")
                    
                    # Map DuckDuckGo fields to our expected format
                    result = {
                        "title": r.get("title", ""),
                        "link": r.get("href", ""),  # DuckDuckGo uses 'href' for URLs
                        "body": r.get("body", ""),  # DuckDuckGo uses 'body'
                        "published": r.get("published", ""),  # DuckDuckGo uses 'published'
                        "source": r.get("source", "")
                    }
                    results.append(result)
                    if len(results) >= max_results:
                        break
                        
                logger.info(f"Processed {len(results)} results")
                return results
                
            except RatelimitException:
                attempt += 1
                if attempt >= max_retries:
                    logger.error(f"Max retries ({max_retries}) exceeded for DuckDuckGo search")
                    raise
                
                logger.warning(f"Rate limited by DuckDuckGo. Attempt {attempt}/{max_retries}. "
                             f"Waiting {delay} seconds before retry...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            
            except Exception as e:
                logger.error(f"Error in DuckDuckGo search: {str(e)}")
                logger.exception("Full traceback:")
                return []

    def _run(self, 
             query: str, 
             max_results: int = 10,
             region: str = "wt-wt",
             safesearch: str = "moderate",
             timelimit: Optional[str] = None
             ) -> List[Dict]:
        """Run synchronous search."""
        try:
            logger.info(f"Performing DuckDuckGo search for: {query}")
            
            # Add delay before search to prevent rate limiting
            logger.info("Waiting 5 seconds before search...")
            time.sleep(5)
            
            results = []
            
            # Get raw results from DuckDuckGo
            ddg_results = list(self.client.text(
                query,
                region=region,
                safesearch=safesearch,
                timelimit=timelimit
            ))
            
            logger.info(f"Raw DuckDuckGo results count: {len(ddg_results)}")
            
            for r in ddg_results:
                # Print raw result for debugging
                print("\nRaw DuckDuckGo result:")
                for key, value in r.items():
                    print(f"{key}: {value}")
                
                # Map DuckDuckGo fields to our expected format
                result = {
                    "title": r.get("title", ""),
                    "link": r.get("href", ""),  # DuckDuckGo uses 'href' for URLs
                    "body": r.get("body", ""),  # DuckDuckGo uses 'body'
                    "published": r.get("published", ""),  # DuckDuckGo uses 'published'
                    "source": r.get("source", "")
                }
                results.append(result)
                if len(results) >= max_results:
                    break
                    
            logger.info(f"Processed {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error in DuckDuckGo search: {str(e)}")
            logger.exception("Full traceback:")
            return []

    async def _arun(self, 
                    query: str, 
                    max_results: int = 10,
                    region: str = "wt-wt",
                    safesearch: str = "moderate",
                    timelimit: Optional[str] = None
                    ) -> List[Dict]:
        """Run asynchronous search."""
        # For now, we'll use the sync version since DuckDuckGo doesn't have an async API
        return self._run(
            query=query,
            max_results=max_results,
            region=region,
            safesearch=safesearch,
            timelimit=timelimit
        )
