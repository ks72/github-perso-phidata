"""
Agent definitions for the eCommerce trend analysis system.
"""
from typing import List, Dict, Optional
from phi.agent import Agent
from phi.llm.openai import OpenAIChat
from phi.tools.streamlit import StreamlitTools
from phi.tools.duckduckgo import DuckDuckGoTools

class UserQueryAgent(Agent):
    def __init__(
        self,
        name: str = "User Query Agent",
        description: str = "Transform user input into structured, trend research-oriented queries",
        llm: Optional[OpenAIChat] = None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            description=description,
            llm=llm or OpenAIChat(model="gpt-4"),
            **kwargs,
        )
        
        # Add tools
        self.add_tool(StreamlitTools())
        
        # Set the system message
        self.system_message = """You are a specialized agent focused on transforming user queries about eCommerce trends into structured, research-oriented queries.

Follow these steps for each query:
1. Set the current date and detect input language
2. Enforce research scope guardrails
3. Parse query into components (focus, context, objective, scope)
4. Restructure into trend research template
5. Enrich with synonyms and related terms

Example:
User: "Furniture trends in France"
Processed: {
    "language": "en",
    "date": "2024-01-20",
    "components": {
        "focus": "furniture",
        "context": "France",
        "objective": "trends",
        "scope": "market_analysis"
    },
    "enriched_terms": ["home furnishings", "interior design", "home decor", "furniture market"],
    "structured_query": "What are the recent trends in the furniture and home furnishings market in France?"
}"""

class WebSearchAgent(Agent):
    def __init__(
        self,
        name: str = "Web Search Agent",
        description: str = "Perform searches across pre-defined websites based on structured queries",
        llm: Optional[OpenAIChat] = None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            description=description,
            llm=llm or OpenAIChat(model="gpt-4"),
            **kwargs,
        )
        
        # Add tools
        self.add_tool(DuckDuckGoTools())
        
        # Set the system message
        self.system_message = """You are a specialized web search agent that performs targeted searches based on structured eCommerce trend queries.

Your responsibilities:
1. Interpret structured queries
2. Perform searches across relevant websites
3. Filter and rank results
4. Return the most relevant information

Focus on reliable sources such as:
- Industry reports
- Market analysis websites
- Trusted news sources
- eCommerce platforms
- Social media trends"""

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

Evaluation criteria:
1. Relevance to the query
2. Source credibility
3. Content freshness
4. Information depth
5. Market impact

For each result, provide:
- Relevance score (0-100)
- Credibility score (0-100)
- Key insights summary
- Recommendation for further analysis"""
