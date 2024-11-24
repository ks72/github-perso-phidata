from typing import Dict, Any
from phi.tools import FunctionCall

class QueryExpander(FunctionCall):
    """Tool for expanding queries with synonyms and context"""
    
    def __init__(self):
        super().__init__(
            name="query_expander",
            description="Expands queries with synonyms and contextual details",
            fn=self.expand_query,
            fn_schema={
                "transformed_query": dict,
                "include_synonyms": bool,
                "include_context": bool
            }
        )
    
    @staticmethod
    def expand_query(
        transformed_query: Dict[str, Any],
        include_synonyms: bool = True,
        include_context: bool = True
    ) -> Dict[str, Any]:
        """Expand the query with synonyms and context"""
        return {
            "original_query": transformed_query["original_query"],
            "research_format": transformed_query["research_format"],
            "expansions": {
                "synonyms": [],  # To be filled by the agent
                "context": [],   # To be filled by the agent
                "related_terms": []  # To be filled by the agent
            }
        }
