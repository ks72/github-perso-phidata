"""Custom exceptions for the ecommerce agents."""

class WorkflowError(Exception):
    """Base exception for workflow-related errors."""
    pass

class AgentError(WorkflowError):
    """Exception raised when an agent encounters an error."""
    def __init__(self, agent_name: str, message: str):
        self.agent_name = agent_name
        self.message = message
        super().__init__(f"{agent_name}: {message}")

class QueryProcessingError(AgentError):
    """Exception raised when query processing fails."""
    pass

class SearchError(AgentError):
    """Exception raised when a search operation fails."""
    pass

class APIError(WorkflowError):
    """Exception raised when an API call fails."""
    def __init__(self, api_name: str, status_code: int, message: str):
        self.api_name = api_name
        self.status_code = status_code
        self.message = message
        super().__init__(f"{api_name} API error ({status_code}): {message}")
