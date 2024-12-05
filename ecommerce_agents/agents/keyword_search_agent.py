"""
KeywordSearchAgent for performing DuckDuckGo searches.

This agent provides basic search functionality with:
1. Simple query parsing
2. Result enrichment
3. Data normalization

The agent maintains clean separation between:
- Query processing (simple parsing)
- Result enrichment (metadata, scoring)
- Data normalization (URLs, text, dates)

Example:
    agent = KeywordSearchAgent()
    results = await agent.search(
        query="Sneakers OR running shoes",
        user_id="user123",
        region="fr-fr",
        max_results=10,
        timelimit="m"
    )
"""
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse
import re
from phi.agent import Agent
from ecommerce_agents.tools.duckduckgo_tool import DuckDuckGoSearchTool
import logging

logger = logging.getLogger(__name__)

@dataclass
class SearchQuery:
    """
    Represents a processed search query with metadata.
    
    Attributes:
        original_query: The raw query from the user
        parsed_query: The processed query ready for search
        category: Optional industry category filter
        region: Geographic region for results
        timelimit: Time limit for result freshness
        timestamp: UTC timestamp of query creation
    """
    original_query: str
    parsed_query: str
    category: Optional[str] = None
    region: str = "wt-wt"
    timelimit: Optional[str] = None
    timestamp: str = ""

    def __post_init__(self):
        """Initialize timestamp if not provided."""
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

@dataclass
class SearchResult:
    """
    Represents an enriched search result with metadata.
    
    Attributes:
        title: Page title (cleaned)
        url: Original URL
        description: Page description/snippet (cleaned)
        date: Publication date (if available)
        source: Source domain (if available)
        query: Reference to the SearchQuery
        timestamp: UTC timestamp of result processing
        relevance_score: Calculated relevance to query
        domain: Extracted domain from URL
        normalized_url: Cleaned and normalized URL
    """
    title: str
    url: str
    description: str
    date: Optional[str]
    source: Optional[str]
    query: SearchQuery
    timestamp: str
    relevance_score: float = 0.0
    domain: str = ""
    normalized_url: str = ""
    
    def __post_init__(self):
        """Post-initialization processing of fields."""
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        
        # Parse and normalize URL
        parsed_url = urlparse(self.url)
        self.domain = parsed_url.netloc.lower()
        self.normalized_url = f"{parsed_url.scheme}://{parsed_url.netloc.lower()}{parsed_url.path}"
        
        # Clean text fields
        self.title = self._clean_text(self.title)
        self.description = self._clean_text(self.description)
        
        # Normalize date if present
        if self.date:
            self.date = self._normalize_date(self.date)
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean and normalize text content."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        # Remove non-printable characters
        text = ''.join(char for char in text if char.isprintable())
        return text
    
    @staticmethod
    def _normalize_date(date_str: str) -> str:
        """Normalize date string to ISO format."""
        try:
            # Add your date parsing logic here
            # Common formats: "2024-01-15", "Jan 15, 2024", etc.
            # For now, just return as is if can't parse
            return date_str
        except Exception:
            return date_str
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert to database-friendly dictionary."""
        return {
            "title": self.title,
            "url": self.normalized_url,
            "domain": self.domain,
            "description": self.description,
            "date": self.date,
            "source": self.source,
            "original_query": self.query.original_query,
            "parsed_query": self.query.parsed_query,
            "category": self.query.category,
            "region": self.query.region,
            "timelimit": self.query.timelimit,
            "query_timestamp": self.query.timestamp,
            "result_timestamp": self.timestamp,
            "relevance_score": self.relevance_score
        }

class KeywordSearchAgent(Agent):
    """
    An agent for performing keyword-based searches using DuckDuckGo.
    
    The agent handles:
    1. Basic search functionality
    2. Result enrichment
    3. Data normalization
    """
    
    type: str = "KeywordSearchAgent"
    search_tool: Optional[DuckDuckGoSearchTool] = None

    def __init__(self, **kwargs):
        """Initialize the agent."""
        super().__init__(**kwargs)
        self.search_tool = DuckDuckGoSearchTool()

    def _calculate_relevance(self, result: Dict[str, Any], query: SearchQuery) -> float:
        """Calculate relevance score for a result based on query match."""
        # Simple relevance calculation based on exact query matches
        relevance = 0.0
        search_terms = query.original_query.lower().split()
        
        # Check title
        title = result.get("title", "").lower()
        for term in search_terms:
            if term in title:
                relevance += 0.5
                
        # Check description
        description = result.get("description", "").lower()
        for term in search_terms:
            if term in description:
                relevance += 0.3
                
        return min(relevance, 1.0)

    async def search(self,
                    query: str,
                    user_id: str = None,
                    category: str = None,
                    region: str = "wt-wt",
                    max_results: int = 10,
                    timelimit: Optional[str] = None
                    ) -> List[SearchResult]:
        """
        Perform a simple keyword search using DuckDuckGo.
        
        Args:
            query: Search query
            user_id: User ID (no longer used for filtering)
            category: Industry category (no longer used for filtering)
            region: Region for search results
            max_results: Maximum number of results to return
            timelimit: Time limit for results ('d' for day, 'w' for week, 'm' for month)
        """
        # Create a search query object
        search_query = SearchQuery(
            original_query=query,
            parsed_query=query,
            category=category,
            region=region,
            timelimit=timelimit
        )
        
        try:
            # Perform the search using the async method
            raw_results = await self.search_tool._arun(
                query=query,
                max_results=max_results,
                region=region,
                timelimit=timelimit
            )
            
            logger.info(f"Got {len(raw_results)} raw results")
            
            # Process results
            results = []
            current_time = datetime.now(timezone.utc).isoformat()
            
            for result in raw_results:
                if len(results) >= max_results:
                    break
                
                try:
                    # Debug print the raw result
                    print("\nProcessing result:")
                    print(f"Raw result keys: {result.keys()}")
                    
                    url = result.get("link", "")  # This will now contain the URL from 'href' field mapped in DuckDuckGoSearchTool
                    print(f"URL from result: {url}")
                    
                    # Create SearchResult object with safe field access
                    search_result = SearchResult(
                        title=result.get("title", "Untitled"),
                        url=url,
                        description=result.get("body", "No description available"),
                        date=result.get("published"),
                        source=result.get("source"),
                        query=search_query,
                        timestamp=current_time
                    )
                    
                    # Debug print the URL
                    logger.debug(f"URL from result: {search_result.url}")
                    
                    # Skip results with empty URLs
                    if not search_result.url:
                        logger.warning("Skipping result with empty URL")
                        continue
                    
                    # Calculate relevance
                    search_result.relevance_score = self._calculate_relevance(result, search_query)
                    results.append(search_result)
                    logger.info(f"Added result: {search_result.title}")
                    
                except Exception as e:
                    logger.warning(f"Error processing search result: {str(e)}")
                    continue
            
            logger.info(f"Returning {len(results)} processed results")
            return results
            
        except Exception as e:
            logger.error(f"Error in search: {str(e)}")
            logger.exception("Full traceback:")
            return []

    async def run(self, user_id: str, query: str, **kwargs) -> Dict[str, Any]:
        """
        Run the agent with the given query.
        
        Args:
            user_id: User identifier (no longer used for filtering)
            query: Search query string
            **kwargs: Optional parameters:
                - category: Industry category (no longer used for filtering)
                - region: Geographic region
                - max_results: Result limit
                - timelimit: Time window
        """
        try:
            results = await self.search(
                query=query,
                user_id=user_id,
                **kwargs
            )
            
            return {
                "query": query,
                "results": [r.to_dict() for r in results],
                "total_results": len(results),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error running agent: {str(e)}")
            return {
                "query": query,
                "results": [],
                "total_results": 0,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": str(e)
            }
