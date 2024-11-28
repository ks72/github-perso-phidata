"""
UserQueryAgent for processing and analyzing ecommerce trend queries.

This agent uses LLM capabilities to:
1. Analyze and understand user queries about market trends
2. Extract structured components (focus, objective, context and scope)
3. Enrich queries with relevant terms and metrics
4. Generate optimized search queries for market research

The agent maintains session state and uses caching to improve performance.
"""
from typing import Dict, Any, List, Optional, Tuple, ClassVar
import json
from datetime import datetime
from langdetect import detect
from phi.agent import Agent, RunResponse, AgentSession
from openai import AsyncOpenAI
from phi.storage.agent.sqlite import SqlAgentStorage
import uuid
import asyncio
import os

# Words that indicate temporal context
TEMPORAL_TERMS: ClassVar[List[str]] = [
    "recent", "current", "latest", "upcoming", "future",
    "past", "previous", "historical", "next", "last"
]

class UserQueryAgent(Agent):
    """
    An agent for processing and analyzing ecommerce trend queries.
    
    This agent leverages LLM capabilities to understand and structure user queries
    about customer trends, product analysis, and industry research. It performs:
    - Query term analysis and focus identification
    - Component extraction and structuring
    - Query enrichment with relevant terms
    - Search query generation
    
    The agent uses GPT-4 for semantic understanding and maintains session state
    for consistent analysis across multiple queries.
    
    Attributes:
        client (AsyncOpenAI): OpenAI API client for LLM interactions
        current_year (int): Current year for temporal context
        current_month (int): Current month for seasonal analysis
    """

    # Standard scope areas for market analysis
    STANDARD_SCOPE_AREAS: ClassVar[List[str]] = [
        "functionality",
        "aesthetic_appeal", 
        "sustainability",
        "technology_integration",
        "health_wellness",
        "affordability",
        "seasonality",
        "exclusivity",
        "cultural_alignment",
        "innovation"
    ]

    # Product category mappings
    PRODUCT_CATEGORIES: ClassVar[Dict[str, List[str]]] = {
        "clothing": ["shirts", "pants", "dresses", "outerwear", "underwear"],
        "footwear": ["shoes", "boots", "sandals", "sneakers", "athletic shoes"],
        "accessories": ["bags", "jewelry", "watches", "belts", "scarves"],
        "electronics": ["smartphones", "laptops", "tablets", "wearables"],
        "home": ["furniture", "decor", "kitchenware", "bedding"],
        "beauty": ["skincare", "makeup", "haircare", "fragrances"],
        "sports": ["equipment", "apparel", "accessories", "footwear"]
    }

    def __init__(self, storage=None, **kwargs):
        """
        Initialize the UserQueryAgent with OpenAI client and temporal context.
        
        Args:
            storage: Optional storage backend for the agent
            **kwargs: Additional arguments passed to parent Agent class
        """
        if storage is None:
            storage = SqlAgentStorage(table_name="user_query_agent")
            
        super().__init__(storage=storage, **kwargs)
        object.__setattr__(self, "client", AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY")))
        object.__setattr__(self, "current_year", datetime.now().year)
        object.__setattr__(self, "current_month", datetime.now().month)
        
    def get_current_season(self) -> str:
        """
        Get the current season based on the month.
        
        Returns:
            str: Current season (Winter, Spring, Summer, Fall)
        """
        month = self.current_month
        if month in [12, 1, 2]:
            return "Winter"
        elif month in [3, 4, 5]:
            return "Spring"
        elif month in [6, 7, 8]:
            return "Summer"
        else:
            return "Fall"

    def get_upcoming_season(self) -> str:
        """
        Get the upcoming season based on the current month.
        
        Returns:
            str: Next season (Winter, Spring, Summer, Fall)
        """
        current_season = self.get_current_season()
        seasons = ["Winter", "Spring", "Summer", "Fall"]
        current_idx = seasons.index(current_season)
        return seasons[(current_idx + 1) % 4]

    async def get_product_category(self, focus_term: str) -> str:
        """Determine the product category using LLM."""
        try:
            prompt = f"""Return the product category for: "{focus_term}"
            Return as JSON:
            {{"category": "broad product category name"}}
            
            Example categories: clothing, footwear, electronics, home goods, beauty, etc.
            Keep categories broad and standardized."""

            response = await self.client.chat.completions.create(
                messages=[{
                    "role": "user", 
                    "content": f"Return JSON: {prompt}"
                }],
                model="gpt-4-1106-preview",
                response_format={"type": "json_object"},
                temperature=0.3
            )

            result = json.loads(response.choices[0].message.content)
            return result.get("category", "general").lower()

        except Exception as e:
            print(f"Error getting product category: {str(e)}")
            return "general"

    async def analyze_query_terms(self, query: str) -> dict:
        """Analyze and extract key terms from the query."""
        try:
            prompt = f"""Analyze this product research query.
            Query: {query}

            Return JSON with these components:
            {{
                "focus_term": "main product/category being researched (required)",
                "objective": "research goal (e.g. trends, comparison, performance) - return null if not specified",
                "temporal_context": "time frame reference - return null if not specified",
                "geographical_context": "location or market scope - return null if not specified",
                "scope": "specific analysis areas mentioned (e.g. functionality, sustainability) - return null if not specified"
            }}
            
            Rules:
            1. focus_term must be a product or product category
            2. Only include explicitly mentioned components
            3. Return null for components not mentioned in the query"""

            response = await self.client.chat.completions.create(
                messages=[{
                    "role": "user", 
                    "content": f"Return JSON: {prompt}"
                }],
                model="gpt-4-1106-preview",
                response_format={"type": "json_object"},
                temperature=0.3
            )

            result = json.loads(response.choices[0].message.content)
            
            # Get product category
            focus_term = result.get("focus_term", "").strip()
            if not focus_term:
                return None
                
            category = await self.get_product_category(focus_term)
            
            # Handle missing parameters with None values
            objective = result.get("objective")
            temporal = result.get("temporal_context")
            geo_context = result.get("geographical_context")
            scope = result.get("scope")
            
            # Only process temporal context if it was explicitly mentioned
            temporal_context = None
            if temporal:
                if temporal in ["recent", "current", "latest"]:
                    specific_time = f"{self.get_current_season()} {self.current_year}"
                elif temporal in ["upcoming", "future", "next"]:
                    specific_time = f"{self.get_upcoming_season()} {self.current_year}"
                else:
                    specific_time = temporal
                    
                temporal_context = {
                    "main": temporal,
                    "specific": specific_time
                }
            
            return {
                "focus_term": focus_term,
                "category": category,
                "objective": objective.strip() if objective else None,
                "temporal_context": temporal_context,
                "geographical_context": geo_context.strip() if geo_context else None,
                "scope": scope.strip() if scope else None
            }

        except Exception as e:
            print(f"Error analyzing query terms: {str(e)}")
            return None

    async def enrich_scope(self, scope: str, category: str, focus_term: str) -> dict:
        """Enrich scope terms with synonyms and related aspects."""
        try:
            prompt = f"""For the scope/aspect "{scope}" in the context of {focus_term} ({category}), provide enriched terms.
            Return JSON:
            {{
                "scope_synonyms": ["2-3 synonymous terms for {scope}"],
                "related_aspects": ["3-4 specific aspects or characteristics related to {scope} for {focus_term}"]
            }}
            
            Example:
            For scope "design" of "running shoes":
            {{
                "scope_synonyms": ["aesthetics", "styling"],
                "related_aspects": ["color scheme", "texture", "silhouette", "material finish"]
            }}"""

            response = await self.client.chat.completions.create(
                messages=[{
                    "role": "user", 
                    "content": f"Return JSON: {prompt}"
                }],
                model="gpt-4-1106-preview",
                response_format={"type": "json_object"},
                temperature=0.3
            )

            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error enriching scope: {str(e)}")
            return {"scope_synonyms": [], "related_aspects": []}

    def is_seasonal_category(self, category: str) -> bool:
        """Check if the product category is seasonal."""
        seasonal_categories = {
            "clothing", "footwear", "accessories", "sports equipment",
            "outdoor gear", "swimwear", "beachwear"
        }
        return category.lower() in seasonal_categories

    async def enrich_location(self, location: str) -> List[str]:
        """Enrich location with appropriate granular levels."""
        try:
            prompt = f"""For the location '{location}', provide the most relevant market regions.
            Return JSON:
            {{
                "regions": [
                    "2 most important market areas",
                    "combine major regions with key cities"
                ]
            }}
            
            Examples:
            - For 'global': ["North America (US)", "Asia Pacific (China)"]
            - For 'Europe': ["Western Europe (Paris)", "Central Europe (Berlin)"]
            - For 'US': ["East Coast (New York)", "West Coast (Los Angeles)"]"""

            response = await self.client.chat.completions.create(
                messages=[{
                    "role": "user", 
                    "content": f"Return JSON: {prompt}"
                }],
                model="gpt-4-1106-preview",
                response_format={"type": "json_object"},
                temperature=0.3
            )

            result = json.loads(response.choices[0].message.content)
            return result.get("regions", [])[:2]  # Ensure we only return 2 regions max

        except Exception as e:
            print(f"Error enriching location: {str(e)}")
            return []

    async def enrich_query(self, query_components: dict) -> dict:
        """Enrich the query with relevant research terms."""
        try:
            focus = query_components.get("focus_term", "")
            category = query_components.get("category", "")
            objective = query_components.get("objective") or "trends"
            temporal = query_components.get("temporal_context")
            location = query_components.get("geographical_context") or "global"
            scope = query_components.get("scope")
            
            # Get objective synonyms
            objective_prompt = f"""For the research objective "{objective}", provide synonyms.
            Return JSON:
            {{
                "synonyms": ["5-6 synonymous terms or phrases"]
            }}"""

            obj_response = await self.client.chat.completions.create(
                messages=[{
                    "role": "user", 
                    "content": f"Return JSON: {objective_prompt}"
                }],
                model="gpt-4-1106-preview",
                response_format={"type": "json_object"},
                temperature=0.3
            )

            obj_enrichment = json.loads(obj_response.choices[0].message.content)
            
            # Get product and market enrichment
            prompt = f"""For market research about "{focus}" (category: {category}), provide enrichment:
            Return JSON:
            {{
                "focus_synonyms": ["3-4 similar product terms"],
                "objective_terms": ["3-4 terms related to {objective} - focus on consumer behavior"],
                "temporal_terms": ["2-3 specific time references"],
                "location_terms": ["2 key market regions"]
            }}"""

            response = await self.client.chat.completions.create(
                messages=[{
                    "role": "user", 
                    "content": f"Return JSON: {prompt}"
                }],
                model="gpt-4-1106-preview",
                response_format={"type": "json_object"},
                temperature=0.3
            )

            enriched = json.loads(response.choices[0].message.content)
            
            # Get temporal enrichment considering seasonality
            temporal_enrichment = []
            is_seasonal = self.is_seasonal_category(category)
            
            if temporal:
                temporal_main = temporal.get("main", "")
                temporal_specific = temporal.get("specific", "")
                
                if temporal_main in ["recent", "current", "latest"]:
                    current_season = self.get_current_season()
                    if is_seasonal:
                        temporal_enrichment = [
                            f"{current_season} {self.current_year}",
                            f"{self.get_upcoming_season()} {self.current_year}",
                            f"Q{(self.current_month-1)//3 + 1} {self.current_year}"
                        ]
                    else:
                        temporal_enrichment = [
                            f"{self.current_month}/1/{self.current_year}",
                            f"Q{(self.current_month-1)//3 + 1} {self.current_year}",
                            str(self.current_year)
                        ]
                elif temporal_main in ["upcoming", "future", "next"]:
                    next_year = self.current_year + 1
                    if is_seasonal:
                        next_season = self.get_upcoming_season()
                        following_season = self.get_upcoming_season()  # Call twice for season after next
                        temporal_enrichment = [
                            f"{next_season} {next_year}",  # Next season
                            f"{following_season} {next_year}",  # Following season
                            f"{next_year}-{next_year + 1}"  # Year range
                        ]
                    else:
                        temporal_enrichment = [
                            f"{next_year}",  # Next year
                            f"{next_year}-{next_year + 1}",  # Short term
                            f"{next_year + 1}-{next_year + 2}"  # Medium term
                        ]
                else:
                    temporal_enrichment = [temporal_specific] if temporal_specific else []
            else:
                # Default temporal enrichment
                if is_seasonal:
                    temporal_enrichment = [
                        f"{self.get_current_season()} {self.current_year}",
                        f"{self.get_upcoming_season()} {self.current_year}"
                    ]
                else:
                    temporal_enrichment = [
                        f"{self.current_month}/1/{self.current_year}",
                        f"Q{(self.current_month-1)//3 + 1} {self.current_year}"
                    ]

            # Get location enrichment
            location_terms = await self.enrich_location(location)
            
            # Get scope enrichment if provided
            scope_enrichment = None
            if scope:
                scope_enrichment = await self.enrich_scope(scope, category, focus)
            
            enriched_data = {
                "focus_synonyms": [term.strip() for term in enriched.get("focus_synonyms", []) if term.strip()],
                "objective_terms": [term.strip() for term in enriched.get("objective_terms", []) if term.strip()],
                "temporal_terms": temporal_enrichment,
                "location_terms": location_terms,
                "objective_enrichment": {
                    "synonyms": obj_enrichment.get("synonyms", [])
                }
            }
            
            # Add scope enrichment if available
            if scope_enrichment:
                enriched_data["scope_enrichment"] = scope_enrichment
            
            return {
                "original": query_components,
                "enriched": enriched_data
            }

        except Exception as e:
            print(f"Error enriching query: {str(e)}")
            return None

    async def generate_search_queries(self, query_components: dict, enriched_data: dict) -> dict:
        """Generate optimized search queries using LLM."""
        try:
            focus = query_components.get("focus_term", "")
            category = query_components.get("category", "")
            objective = query_components.get("objective", "trends")
            temporal = query_components.get("temporal_context", {})
            location = query_components.get("geographical_context", "global")
            
            # Get enriched terms
            enriched = enriched_data.get("enriched", {})
            synonyms = enriched.get("focus_synonyms", [])
            obj_terms = enriched.get("objective_terms", [])
            temporal_terms = enriched.get("temporal_terms", [])
            location_terms = enriched.get("location_terms", [])
            
            prompt = f"""Generate optimized search queries for market research.
            
            Context:
            - Product: {focus} ({category})
            - Objective: {objective}
            - Time Frame: {temporal.get('specific', 'recent') if isinstance(temporal, dict) else temporal}
            - Location: {location}
            
            Enrichment:
            - Similar Products: {', '.join(synonyms)}
            - Related Terms: {', '.join(obj_terms)}
            - Time References: {', '.join(temporal_terms)}
            - Market Regions: {', '.join(location_terms)}
            
            Return JSON:
            {{
                "keyword_queries": [
                    "3-4 optimized keyword-based queries using boolean operators (AND, OR)"
                ],
                "semantic_queries": [
                    "3-4 natural language queries for semantic search"
                ]
            }}
            
            Rules:
            1. Keyword queries should use boolean operators and be optimized for traditional search
            2. Semantic queries should be natural language questions focused on market insights"""
            response = await self.client.chat.completions.create(
                messages=[{
                    "role": "user", 
                    "content": f"Return JSON: {prompt}"
                }],
                model="gpt-4-1106-preview",
                response_format={"type": "json_object"},
                temperature=0.7
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            print(f"Error generating search queries: {str(e)}")
            return None

    async def extract_structured_components(self, query: str, use_cache: bool = True) -> Dict[str, Any]:
        """Extract structured components from the query."""
        try:
            # Use the analysis result directly
            result = await self.analyze_query_terms(query)
            if not result:
                return None
            
            # Get temporal context
            temporal_context = result.get("temporal_context", {})
            specific_time = temporal_context.get("specific", "")
            
            # Return the same structure as the analysis
            return {
                "enriched_data": {
                    "original": {
                        "focus": result.get("focus_term", ""),
                        "objective": result.get("objective", ""),
                        "geography": result.get("geographical_context", ""),
                        "context": {
                            "temporal": {
                                "main": temporal_context.get("main", ""),
                                "specific": specific_time
                            }
                        }
                    }
                }
            }

        except Exception as e:
            print(f"Error extracting components: {e}")
            return None

    def get_scope_terms(self) -> dict:
        """Return predefined scope terms for different categories."""
        return {
            "functionality": ["practical features", "usability", "performance", "reliability", "durability"],
            "aesthetic_appeal": ["design", "style", "appearance", "visual appeal", "aesthetics"],
            "sustainability": ["eco-friendly", "sustainable", "environmental impact", "green products"],
            "technology_integration": ["smart features", "connectivity", "digital integration", "tech-enabled"],
            "health_wellness": ["health benefits", "wellness features", "safety", "comfort"],
            "affordability": ["price point", "value for money", "cost-effectiveness", "budget-friendly"],
            "seasonality": ["seasonal relevance", "seasonal trends", "time-specific features"],
            "exclusivity": ["premium features", "luxury aspects", "unique selling points"],
            "cultural_alignment": ["cultural relevance", "local preferences", "cultural adaptation"],
            "innovation": ["innovative features", "new technology", "cutting-edge solutions"]
        }