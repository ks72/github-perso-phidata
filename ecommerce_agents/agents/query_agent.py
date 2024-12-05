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
import re

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

    # Pattern matching constants
    TEMPORAL_PATTERNS: ClassVar[Dict[str, str]] = {
        'year': r'\b(20\d{2})\b',
        'season': r'\b(spring|summer|fall|winter|q[1-4])\b',
        'relative': r'\b(current|upcoming|next|future|past|previous|recent|latest)(?:\s+season)?\b',
        'month': r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b',
        'period': r'\b(daily|weekly|monthly|quarterly|yearly|annual)\b'
    }
    
    LOCATION_PATTERNS: ClassVar[Dict[str, str]] = {
        'global': r'\b(global|worldwide|international)\b',
        'continent': r'\b(europe|asia|africa|north america|south america|australia)\b'
    }
    
    OBJECTIVE_TERMS: ClassVar[Dict[str, List[str]]] = {
        'trends': ['pattern', 'movement', 'direction', 'shift', 'evolution'],
        'demand': ['consumption', 'need', 'requirement', 'market interest', 'uptake'],
        'performance': ['results', 'achievement', 'outcome', 'track record', 'effectiveness'],
        'comparison': ['analysis', 'evaluation', 'assessment', 'benchmark', 'contrast']
    }
    
    SCOPE_PATTERNS: ClassVar[Dict[str, str]] = {
        'functionality': r'\b(feature|function|capability|performance|efficiency)\b',
        'aesthetic': r'\b(design|style|appearance|aesthetic|visual)\b',
        'sustainability': r'\b(sustainable|eco-friendly|green|environmental)\b',
        'technology': r'\b(tech|digital|smart|connected|innovative)\b',
        'health': r'\b(health|wellness|safety|comfort)\b',
        'price': r'\b(price|cost|affordable|premium|luxury)\b',
        'culture': r'\b(cultural|social|lifestyle|demographic)\b'
    }

    def __init__(self, storage=None, **kwargs):
        """
        Initialize the UserQueryAgent with OpenAI client.
        
        Args:
            storage: Optional storage backend for the agent
            **kwargs: Additional arguments passed to parent Agent class
        """
        if storage is None:
            storage = SqlAgentStorage(table_name="user_query_agent")
            
        super().__init__(storage=storage, **kwargs)
        object.__setattr__(self, "client", AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY")))
        
    @property
    def current_year(self) -> int:
        """Get the current year."""
        return datetime.now().year
        
    @property
    def current_month(self) -> int:
        """Get the current month."""
        return datetime.now().month

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

    async def analyze_query_terms(self, query: str, attempt: int = 1, previous_focus: str = None) -> dict:
        """Analyze query terms to detect components and validate them."""
        try:
            # If we have a previous focus and no clear focus in the current query,
            # prepend it to the query
            if previous_focus and not any(term in query.lower() for term in ["shoes", "clothing", "apparel"]):
                query = f"{previous_focus} {query}"

            # Step 1: Get initial analysis from LLM
            prompt = f"""Analyze this market research query: "{query}"
            Return a JSON object with these components:
            {{
                "focus_term": "product term (can be compound like 'running shoes' or 'winter boots')",
                "objective": "single research objective (trends/demand/performance/comparison)",
                "scope": "single analysis area (functionality/sustainability/technology/etc)",
                "temporal_context": "single time reference",
                "geographical_context": "single location reference",
                "unmatched_terms": ["terms that don't fit any category"],
                "original_keywords": {json.dumps(query.split())}
            }}
            
            Important:
            - Focus can be a compound term (e.g., 'running shoes', 'dress boots') but should not include scope modifiers
            - Scope modifiers like 'sustainable', 'smart', 'eco-friendly' should be part of scope, not focus
            - Objective must be one of: trends, demand, performance, comparison
            - Scope must be one of: functionality, sustainability, technology, health, price, culture
            - Only include terms that are explicitly mentioned in the query"""

            response = await self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="gpt-4-1106-preview",
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            analysis = json.loads(response.choices[0].message.content)
            components = {}
            
            # Step 2: Extract and validate components
            if focus := analysis.get("focus_term"):
                components["focus_term"] = focus.lower()
            
            if objective := analysis.get("objective"):
                if await self.validate_objective(objective):
                    components["objective"] = objective.lower()
            
            # Extract temporal context using patterns
            temporal_matches = []
            for pattern_type, pattern in self.TEMPORAL_PATTERNS.items():
                matches = re.finditer(pattern, query.lower(), re.IGNORECASE)
                for match in matches:
                    temporal_matches.append({
                        'type': pattern_type,
                        'value': match.group()
                    })
            
            # Sort matches by length to prioritize longer matches like "next season"
            temporal_matches.sort(key=lambda x: len(x['value']), reverse=True)

            if temporal_matches:
                components["temporal_context"] = temporal_matches[0]['value']
            
            # Extract location context using patterns
            location_matches = []
            for pattern_type, pattern in self.LOCATION_PATTERNS.items():
                matches = re.finditer(pattern, query.lower(), re.IGNORECASE)
                for match in matches:
                    location_matches.append({
                        'type': pattern_type,
                        'value': match.group()
                    })
            
            if location_matches:
                components["geographical_context"] = location_matches[0]['value']
            
            if scope := analysis.get("scope"):
                if await self.validate_scope(scope):
                    components["scope"] = scope.lower()
            
            # Step 3: Check for missing components on first attempt
            if attempt == 1:
                missing = []
                if "focus_term" not in components:
                    missing.append("product or topic")
                if "objective" not in components:
                    missing.append("research objective (trends/demand/performance/comparison)")
                if "scope" not in components:
                    scope_suggestions = ", ".join(self.STANDARD_SCOPE_AREAS[:5])  # Show first 5 standard scopes
                    missing.append(f"analysis areas (suggested: {scope_suggestions})")
                if "temporal_context" not in components:
                    missing.append("time reference (e.g., current, next season)")
                if "geographical_context" not in components:
                    missing.append("location reference (e.g., global, Europe)")
                
                if missing or analysis.get("unmatched_terms"):
                    components["validation"] = {
                        "unmatched_terms": analysis.get("unmatched_terms", []),
                        "missing_components": missing,
                        "attempt": attempt
                    }
                    return components
            
            # Step 4: Add defaults only after second attempt
            if attempt > 1:
                if "objective" not in components:
                    components["objective"] = "trends"
                if "geographical_context" not in components:
                    components["geographical_context"] = "global"
                if "temporal_context" not in components:
                    components["temporal_context"] = "current"
                # Removed default scope assignment

            return components

        except Exception as e:
            print(f"Error analyzing query terms: {str(e)}")
            return {}

    async def enrich_query_data(self, query_components: dict) -> dict:
        """Enrich query data with additional relevant terms."""
        if not query_components or not query_components.get("focus_term"):
            return None

        try:
            focus = query_components["focus_term"]
            objective = query_components.get("objective", "trends")
            temporal = query_components.get("temporal_context", {})
            location = query_components.get("geographical_context", "global")
            scope = query_components.get("scope")

            # Get product category for better enrichment
            category = await self.get_product_category(focus)
            
            # Prepare location metadata based on context
            location_terms = []
            if location.lower() == "global":
                location_terms = ["Europe", "North America", "Asia"]
            elif location.lower() in ["europe", "asia", "africa", "north america", "south america", "australia"]:
                location_terms = [location]
            
            # Prepare temporal context
            temporal_terms = []
            temporal_metadata = {}
            
            if isinstance(temporal, str):
                current_year = str(self.current_year)
                
                if 'next season' in temporal.lower():
                    next_season = self.get_upcoming_season()
                    next_season_month = {
                        "Spring": "March",
                        "Summer": "June",
                        "Fall": "September",
                        "Winter": "December"
                    }[next_season]
                    
                    next_year = str(self.current_year + 1)
                    temporal_terms = [
                        f"{next_season} {next_year}",
                        f"{next_season_month} {next_year}"
                    ]
                    temporal_metadata["duration"] = "12 months"
                
                elif 'past season' in temporal.lower():
                    current_season = self.get_current_season()
                    past_season_map = {
                        "Spring": "Winter",
                        "Summer": "Spring",
                        "Fall": "Summer",
                        "Winter": "Fall"
                    }
                    past_season = past_season_map[current_season]
                    past_season_month = {
                        "Spring": "March",
                        "Summer": "June",
                        "Fall": "September",
                        "Winter": "December"
                    }[past_season]
                    
                    temporal_terms = [
                        f"{past_season} {current_year}",
                        f"{past_season_month} {current_year}"
                    ]
                    temporal_metadata["duration"] = "12 months"
                
                else:
                    temporal_terms = [temporal]
                    temporal_metadata["duration"] = "12 months"  # fixed duration for all cases
            
            # Add temporal metadata to the metadata dict
            metadata = {
                "location_terms": location_terms,
                "temporal_terms": temporal_terms,
                "temporal": temporal_metadata,
                "category": category
            }

            # Prepare enrichment prompt
            prompt = f"""Given a focus on {focus} with objective {objective}, provide JSON with:
            {{
                "objective": ["1 synonym for {objective}"],
                "focus": ["2-3 related terms for {focus}"],
                "scope": ["up to 5 relevant terms about {scope}" if scope else "[]"],
                "location": {json.dumps(location_terms)},
                "temporal": {json.dumps(temporal_terms)}
            }}
            Keep terms concise and directly relevant to the current context.
            For temporal terms, use only specific time references matching the original context."""

            response = await self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="gpt-4-1106-preview",
                response_format={"type": "json_object"},
                temperature=0.7
            )

            enriched = json.loads(response.choices[0].message.content)
            
            # Add objective synonyms - limit to 1
            if objective.lower() in self.OBJECTIVE_TERMS:
                enriched["objective"] = [self.OBJECTIVE_TERMS[objective.lower()][0]]
            
            return {
                "original": query_components,
                "enriched": enriched,
                "metadata": metadata
            }

        except Exception as e:
            print(f"Error enriching query: {str(e)}")
            return None

    async def generate_search_queries(self, enriched_data: dict) -> dict:
        """Generate search queries from enriched data."""
        if not enriched_data:
            return {"keyword_queries": [], "semantic_queries": []}

        queries = {"keyword_queries": [], "semantic_queries": []}
        
        try:
            # Extract components
            original = enriched_data.get("original", {})
            enriched = enriched_data.get("enriched", {})
            metadata = enriched_data.get("metadata", {})
            
            # Get components with defaults
            focus = original.get("focus_term", "")
            objective = original.get("objective", "trends")
            geo_context = original.get("geographical_context", "global")
            temporal = metadata.get("temporal", {})
            scope = original.get("scope", "")
            temporal_terms = metadata.get("temporal_terms", [])
            
            # Generate queries in order of specificity
            queries["keyword_queries"] = []
            
            # 1. Most specific query (all components)
            query_parts = []
            query_parts.append(focus)
            query_parts.append(objective)
            if geo_context and geo_context.lower() != "global":
                query_parts.append(geo_context)
            if temporal_terms and temporal_terms[0]:
                query_parts.append(temporal_terms[0])
            if scope:
                query_parts.append(scope)
            queries["keyword_queries"].append({
                "query": " ".join(query_parts).strip(),
                "metadata": {
                    "location": metadata.get("location_terms", []),
                    "category": metadata.get("category"),
                    "temporal": temporal
                }
            })
            
            # 2. General category query
            base_query = f"{focus} {objective}"
            if base_query != queries["keyword_queries"][0]["query"]:
                queries["keyword_queries"].append({
                    "query": base_query,
                    "metadata": {
                        "location": metadata.get("location_terms", []),
                        "category": metadata.get("category"),
                        "temporal": temporal
                    }
                })
            
            # 3. Location-specific query (if applicable)
            if geo_context and geo_context.lower() != "global":
                location_query = f"{focus} {objective} {geo_context}"
                queries["keyword_queries"].append({
                    "query": location_query,
                    "metadata": {
                        "location": metadata.get("location_terms", []),
                        "category": metadata.get("category"),
                        "temporal": temporal
                    }
                })
            
            # 4. Temporal-specific query
            if temporal_terms and temporal_terms[0]:
                temporal_query = f"{focus} {objective} {temporal_terms[0]}"
                queries["keyword_queries"].append({
                    "query": temporal_query,
                    "metadata": {
                        "location": metadata.get("location_terms", []),
                        "category": metadata.get("category"),
                        "temporal": temporal
                    }
                })
            
            # 5. Scope-specific query
            if scope:
                scope_query = f"{focus} {objective} {scope}"
                queries["keyword_queries"].append({
                    "query": scope_query,
                    "metadata": {
                        "location": metadata.get("location_terms", []),
                        "category": metadata.get("category"),
                        "temporal": temporal
                    }
                })
            
            # Generate natural language semantic queries
            prompt = f"""Generate 5 research questions about {original["focus_term"]}.

            Use these components:
            - Objective: {original.get("objective")} ({", ".join(enriched.get("objective", []))})
            - Time frame: {metadata.get("temporal", "current")}
            - Location: {original.get("geographical_context", "global")}
            - Scope: {", ".join(enriched.get("scope", [])) if enriched.get("scope", []) else "general"}

            Guidelines:
            1. First question should be very close to the original query
            2. Other questions should explore different perspectives
            3. Keep questions general and high-level
            4. Avoid too specific or technical details
            5. Make questions simple and direct

            Return a JSON object with an array of 5 queries in the format:
            {{
                "queries": [
                    "What are the [objective] for [product] in [location]?",
                    "How is the market evolving?",
                    "What are the main influencing factors?",
                    "What direction is this heading?",
                    "Why do people make these choices?"
                ]
            }}"""

            response = await self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="gpt-4-1106-preview",
                response_format={"type": "json_object"},
                temperature=0.7
            )

            semantic_queries = json.loads(response.choices[0].message.content)
            queries["semantic_queries"] = semantic_queries.get("queries", [])
            
            return queries
            
        except Exception as e:
            print(f"Error generating search queries: {str(e)}")
            return {"keyword_queries": [], "semantic_queries": []}

    def is_seasonal_category(self, category: str) -> bool:
        """Check if the product category is seasonal."""
        seasonal_categories = {
            "clothing", "footwear", "accessories", "sports equipment",
            "outdoor gear", "swimwear", "beachwear"
        }
        return category.lower() in seasonal_categories

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

    async def validate_objective(self, objective: str) -> tuple[bool, str]:
        """Validate if the objective is relevant for market research."""
        try:
            prompt = f"""Is this objective "{objective}" relevant for customer research?
            Valid objectives include: trends, comparison, performance, analysis, demand, preferences, etc.
            Return JSON: {{"is_valid": boolean, "suggestion": "suggested correction if invalid, empty if valid"}}"""

            response = await self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="gpt-4-1106-preview",
                response_format={"type": "json_object"},
                temperature=0.3
            )
            result = json.loads(response.choices[0].message.content)
            return result["is_valid"], result.get("suggestion", "")
        except Exception as e:
            print(f"Error validating objective: {str(e)}")
            return True, ""

    async def validate_temporal(self, temporal: str) -> tuple[bool, str]:
        """Validate temporal context."""
        if not temporal:
            return True, ""
            
        # Convert relative terms to specific seasons
        if temporal.lower() in ["next season", "upcoming season", "future"]:
            season = self.get_upcoming_season()
            year = self.current_year
            return True, f"{season} {year}"
            
        # Check if it's a valid season with year
        seasons = ["spring", "summer", "fall", "winter"]
        words = temporal.lower().split()
        
        has_season = any(season in words for season in seasons)
        has_year = any(word.isdigit() and len(word) == 4 for word in words)
        
        if has_season and has_year:
            return True, temporal
            
        if has_season:
            # Add current year if only season is provided
            return True, f"{temporal} {self.current_year}"
            
        return False, "Please provide a season (Spring, Summer, Fall, Winter) with an optional year"

    async def validate_geographical(self, geo_context: str) -> tuple[bool, str]:
        """Validate if the geographical context is valid."""
        try:
            prompt = f"""Is this geographical context "{geo_context}" valid for customer research?
            Valid formats: global, continent names, country names, regions, major cities, etc.
            Return JSON: {{"is_valid": boolean, "suggestion": "suggested correction if invalid, empty if valid"}}"""

            response = await self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="gpt-4-1106-preview",
                response_format={"type": "json_object"},
                temperature=0.3
            )
            result = json.loads(response.choices[0].message.content)
            return result["is_valid"], result.get("suggestion", "")
        except Exception as e:
            print(f"Error validating geographical context: {str(e)}")
            return True, ""

    async def validate_scope(self, scope: str) -> tuple[bool, str]:
        """Validate if the scope/analysis areas are relevant."""
        try:
            prompt = f"""Is this scope/analysis area "{scope}" relevant for customer research?
            Valid areas include: functionality, sustainability, technology, design, price, quality, etc.
            Return JSON: {{"is_valid": boolean, "suggestion": "suggested correction if invalid, empty if valid"}}"""

            response = await self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="gpt-4-1106-preview",
                response_format={"type": "json_object"},
                temperature=0.3
            )
            result = json.loads(response.choices[0].message.content)
            return result["is_valid"], result.get("suggestion", "")
        except Exception as e:
            print(f"Error validating scope: {str(e)}")
            return True, ""