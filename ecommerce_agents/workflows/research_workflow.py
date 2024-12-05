"""
Research workflow that combines query processing, keyword search, and semantic search.

This workflow:
1. Processes user queries through the UserQueryAgent
2. Performs parallel searches using KeywordSearchAgent and SemanticSearchAgent
3. Combines and ranks results
"""
from typing import Dict, Any, List
from phi.workflow import Workflow
from ..agents.query_agent import UserQueryAgent
from ..agents.keyword_search_agent import KeywordSearchAgent
from ..agents.semantic_search_agent import SemanticSearchAgent
from ..utils.logging import workflow_logger as logger
from ..utils.exceptions import WorkflowError, QueryProcessingError, SearchError
import asyncio
import time
from functools import wraps

def log_execution_time(func):
    """Decorator to log function execution time."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(
                f"{func.__name__} completed successfully in {execution_time:.2f} seconds"
            )
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"{func.__name__} failed after {execution_time:.2f} seconds: {str(e)}"
            )
            raise
    return wrapper

class ResearchWorkflow(Workflow):
    """
    Workflow for processing user queries and performing comprehensive searches.
    """

    def __init__(self, user_id: str, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        logger.info(f"Initializing ResearchWorkflow for user: {user_id}")
        
        # Initialize agents
        try:
            self.query_agent = UserQueryAgent()
            self.keyword_agent = KeywordSearchAgent()
            self.semantic_agent = SemanticSearchAgent()
            logger.info("All agents initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize agents: {str(e)}")
            raise WorkflowError("Agent initialization failed") from e

    @log_execution_time
    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process a user query through the entire workflow."""
        logger.info(f"Processing query: {query}")
        
        try:
            # Step 1: Process query through UserQueryAgent
            logger.debug("Starting query processing")
            query_result = await self.query_agent.run(query)
            structured_query = query_result.get('structured_query', {})
            logger.info("Query processing completed successfully")
            
            # Step 2: Perform parallel searches
            logger.debug("Starting parallel searches")
            search_tasks = [
                self._execute_search(
                    self.keyword_agent.run,
                    "keyword",
                    user_id=self.user_id,
                    query=query,
                    structured_query=structured_query,
                    category=query_result.get('category')
                ),
                self._execute_search(
                    self.semantic_agent.run,
                    "semantic",
                    user_id=self.user_id,
                    query=query,
                    structured_query=structured_query
                )
            ]
            
            # Wait for both searches to complete
            keyword_results, semantic_results = await asyncio.gather(
                *search_tasks, return_exceptions=True
            )
            
            # Handle any exceptions from the searches
            for result in [keyword_results, semantic_results]:
                if isinstance(result, Exception):
                    logger.error(f"Search failed: {str(result)}")
                    raise result
            
            logger.info("All searches completed successfully")
            
            # Step 3: Combine results
            combined_results = self._combine_results(
                keyword_results.get('results', []),
                semantic_results.get('results', [])
            )
            
            result = {
                'original_query': query,
                'structured_query': structured_query,
                'keyword_results': keyword_results,
                'semantic_results': semantic_results,
                'combined_results': combined_results,
                'timestamp': query_result.get('timestamp')
            }
            
            logger.info(
                f"Query processing complete. Found {len(combined_results)} unique results"
            )
            return result
            
        except Exception as e:
            logger.error(f"Error in process_query: {str(e)}")
            raise WorkflowError(f"Query processing failed: {str(e)}") from e

    async def _execute_search(self, search_func, search_type: str, **kwargs) -> Dict[str, Any]:
        """Execute a search with error handling and retries."""
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                logger.debug(f"Executing {search_type} search (attempt {attempt + 1}/{max_retries})")
                return await search_func(**kwargs)
            except Exception as e:
                logger.warning(
                    f"{search_type} search failed (attempt {attempt + 1}/{max_retries}): {str(e)}"
                )
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (attempt + 1))
                else:
                    raise SearchError(
                        f"{search_type}_search",
                        f"Search failed after {max_retries} attempts: {str(e)}"
                    )

    def _combine_results(self, 
                        keyword_results: List[Dict[str, Any]], 
                        semantic_results: List[Dict[str, Any]]
                        ) -> List[Dict[str, Any]]:
        """
        Combine and deduplicate results from both search types.
        
        Strategy:
        1. Prefer semantic results when URLs overlap
        2. Sort by score/relevance
        3. Remove duplicates
        """
        logger.debug(
            f"Combining results: {len(keyword_results)} keyword, "
            f"{len(semantic_results)} semantic"
        )
        
        # Create a URL-based lookup for quick duplicate checking
        seen_urls = {}
        
        # Process semantic results first (they have priority)
        for result in semantic_results:
            url = result['url']
            seen_urls[url] = result
        
        # Add keyword results if URL not already seen
        for result in keyword_results:
            url = result['url']
            if url not in seen_urls:
                seen_urls[url] = result
        
        # Convert back to list and sort by score
        combined = list(seen_urls.values())
        combined.sort(key=lambda x: float(x.get('score', 0)), reverse=True)
        
        logger.debug(f"Combined {len(combined)} unique results")
        return combined

    @log_execution_time
    async def run(self, **kwargs) -> Dict[str, Any]:
        """Run the workflow with the given inputs."""
        query = kwargs.get('query')
        if not query:
            logger.error("No query provided")
            raise ValueError("Query is required")
            
        return await self.process_query(query)
