from typing import Dict, Any, List
from phi.tools import FunctionCall

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
