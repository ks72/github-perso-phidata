"""
Pre-Ranking Agent for evaluating and ranking search results.
"""
from typing import Dict, List, Optional
from datetime import datetime
import json
from phi.agent import Agent
from phi.llm.openai import OpenAIChat


class PreRankingAgent(Agent):
    def __init__(
        self,
        name: str = "Pre-Ranking Agent",
        description: str = "Retrieve and rank search results based on relevance and credibility",
        llm: Optional[OpenAIChat] = None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            description=description,
            llm=llm or OpenAIChat(model="gpt-4"),
            **kwargs,
        )
        
        # Set the system message
        self.system_message = """You are a specialized ranking agent that evaluates and ranks search results based on multiple criteria.

Your responsibilities:
1. Remove duplicate URLs from combined search results
2. Prioritize freshness (recent content)
3. Score results based on:
   - For keyword searches: boost exact keyword matches in snippets
   - For semantic searches: boost highlight scores
4. Select top 7 most relevant URLs

Example output format:
{
    "ranked_results": [
        {
            "url": "example.com/article",
            "title": "2024 Market Trends",
            "score": 95,
            "freshness_boost": 10,
            "keyword_matches": ["trend", "market"],
            "highlight_score": 0.85
        }
    ],
    "metadata": {
        "total_processed": 25,
        "duplicates_removed": 3,
        "timestamp": "2024-01-20T10:30:00Z"
    }
}"""

    def rank_results(self, search_results: Dict) -> Dict:
        """Rank and filter search results."""
        try:
            # Combine results from different sources
            all_results = (
                search_results.get("search_results", {}).get("duckduckgo", []) +
                search_results.get("search_results", {}).get("exa", [])
            )
            
            # Remove duplicates
            seen_urls = set()
            unique_results = []
            duplicates = 0
            
            for result in all_results:
                url = result.get("url")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_results.append(result)
                else:
                    duplicates += 1
            
            # Score and rank results
            ranked_results = []
            for result in unique_results:
                score = self._calculate_score(result)
                ranked_results.append({
                    **result,
                    "score": score
                })
            
            # Sort by score and take top 7
            ranked_results.sort(key=lambda x: x["score"], reverse=True)
            top_results = ranked_results[:7]
            
            return {
                "ranked_results": top_results,
                "metadata": {
                    "total_processed": len(all_results),
                    "duplicates_removed": duplicates,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "results": search_results
            }
    
    def _calculate_score(self, result: Dict) -> float:
        """Calculate a score for a single result."""
        base_score = 0.0
        
        # Base score from Exa (if available)
        if "score" in result:
            base_score += result["score"] * 0.4
        
        # Highlight score (if available)
        if "highlight_score" in result:
            base_score += result["highlight_score"] * 0.3
        
        # Freshness boost
        if "date" in result and result["date"]:
            try:
                date = datetime.fromisoformat(result["date"].replace("Z", "+00:00"))
                days_old = (datetime.now() - date).days
                freshness_score = max(0, 1 - (days_old / 365))  # Decay over a year
                base_score += freshness_score * 0.3
            except (ValueError, TypeError):
                pass
        
        # Ensure score is between 0 and 100
        return min(100, max(0, base_score * 100))
