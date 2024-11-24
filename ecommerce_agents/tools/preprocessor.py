from typing import Dict, Any
from datetime import datetime
from phi.tools import FunctionCall

class QueryPreprocessor(FunctionCall):
    """Tool for preprocessing user queries"""
    
    def __init__(self):
        super().__init__(
            name="query_preprocessor",
            description="Preprocesses user queries by extracting key components",
            fn=self.process_query,
            fn_schema={
                "query": str,
                "language": str
            }
        )
    
    @staticmethod
    def process_query(query: str, language: str = "en") -> Dict[str, Any]:
        """Extract key components from the user query"""
        return {
            "original_query": query,
            "language": language,
            "timestamp": datetime.now().isoformat(),
            "components": {
                "main_topic": "",  # To be filled by the agent
                "time_frame": "",  # To be filled by the agent
                "geo_focus": "",   # To be filled by the agent
                "industry": "",    # To be filled by the agent
            }
        }
