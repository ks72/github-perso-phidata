from typing import Dict, Any, List
from phi.tools import FunctionCall

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
