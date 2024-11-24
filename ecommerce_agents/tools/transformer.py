from typing import Dict, Any
from phi.tools import FunctionCall

class QueryTransformer(FunctionCall):
    """Tool for transforming queries into research-oriented formats"""
    
    def __init__(self):
        super().__init__(
            name="query_transformer",
            description="Transforms queries into research-oriented formats",
            fn=self.transform_query,
            fn_schema={
                "preprocessed_query": dict,
                "format_type": str
            }
        )
    
    @staticmethod
    def transform_query(preprocessed_query: Dict[str, Any], format_type: str = "trend_research") -> Dict[str, Any]:
        """Transform the preprocessed query into specified format"""
        return {
            "original_query": preprocessed_query["original_query"],
            "research_format": {
                "main_topic": preprocessed_query["components"]["main_topic"],
                "industry_context": preprocessed_query["components"]["industry"],
                "time_frame": preprocessed_query["components"]["time_frame"],
                "geographical_focus": preprocessed_query["components"]["geo_focus"],
                "format_type": format_type
            }
        }
