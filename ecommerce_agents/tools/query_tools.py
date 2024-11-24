from typing import Dict, Any, List
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

class OutputValidator(FunctionCall):
    """Tool for validating query outputs"""
    
    def __init__(self):
        super().__init__(
            name="output_validator",
            description="Validates the expanded query output",
            fn=self.validate_output,
            fn_schema={
                "expanded_query": dict,
                "validation_rules": list
            }
        )
    
    @staticmethod
    def validate_output(
        expanded_query: Dict[str, Any],
        validation_rules: List[str]
    ) -> Dict[str, bool]:
        """Validate the expanded query output"""
        return {
            "is_valid": True,  # To be determined by the agent
            "validation_results": {
                rule: True for rule in validation_rules  # To be checked by the agent
            },
            "suggestions": []  # To be filled by the agent if improvements needed
        }

class QueryGuardrail(FunctionCall):
    """Tool for enforcing query guardrails"""
    
    def __init__(self):
        super().__init__(
            name="query_guardrail",
            description="Enforces safety and relevance guardrails on queries",
            fn=self.check_guardrails,
            fn_schema={
                "query": dict,
                "safety_rules": list,
                "relevance_rules": list
            }
        )
    
    @staticmethod
    def check_guardrails(
        query: Dict[str, Any],
        safety_rules: List[str],
        relevance_rules: List[str]
    ) -> Dict[str, Any]:
        """Check if the query passes all guardrails"""
        return {
            "passes_guardrails": True,  # To be determined by the agent
            "safety_check": {
                rule: True for rule in safety_rules  # To be checked by the agent
            },
            "relevance_check": {
                rule: True for rule in relevance_rules  # To be checked by the agent
            },
            "modifications_needed": []  # To be filled by the agent if changes needed
        }
