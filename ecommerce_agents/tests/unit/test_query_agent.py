"""
Unit test module for the UserQueryAgent class.

This module contains test cases for:
1. Query term analysis (focus, objective, temporal context)
2. Component extraction with LLM-based enrichment
3. Search query generation
"""
import os
import json
import sys
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to Python path for absolute imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from agents.query_agent import UserQueryAgent

@pytest.fixture
def query_agent():
    """Create a UserQueryAgent instance for testing."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not found in .env file")
    return UserQueryAgent()

@pytest.fixture(scope="function")
def mock_openai():
    """Mock the OpenAI client"""
    with patch('openai.AsyncOpenAI', autospec=True) as mock:
        mock_instance = AsyncMock()
        mock_instance.chat.completions.create = AsyncMock()
        mock.return_value = mock_instance
        yield mock_instance

@pytest.mark.asyncio
async def test_temporal_metadata_processing(query_agent):
    """Test temporal metadata processing for different time contexts."""
    # Test recent/current time
    result = query_agent._process_temporal_metadata(
        {"specific": "recent"}, 
        ["current", "nowadays"]
    )
    assert result["time_limit"] == "6 months"
    assert result["query_terms"] == "recent"
    
    # Test last quarter
    result = query_agent._process_temporal_metadata(
        {"specific": "last quarter"}, 
        []
    )
    assert result["time_limit"] == "3 months"
    assert result["query_terms"] == "last quarter"
    
    # Test future date
    future_year = str(datetime.now().year + 1)
    result = query_agent._process_temporal_metadata(
        {"specific": f"trends for {future_year}"}, 
        []
    )
    assert result["time_limit"] is None
    assert str(future_year) in result["query_terms"]

@pytest.mark.asyncio
async def test_location_metadata_processing(query_agent):
    """Test location metadata processing for different geographical contexts."""
    # Test global location
    result = query_agent._process_location_metadata(
        "global", 
        ["worldwide", "international"]
    )
    assert len(result["locations"]) == 0
    assert result["query_terms"] == "global"
    
    # Test specific locations
    result = query_agent._process_location_metadata(
        "Europe", 
        ["France", "Germany", "UK", "EU"]
    )
    assert "France" in result["locations"]
    assert "Germany" in result["locations"]
    assert "Europe" in result["query_terms"]

@pytest.mark.asyncio
async def test_analyze_query_terms(query_agent, mock_openai):
    """Test query term analysis."""
    mock_response = {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "focus_term": "running shoes",
                    "category": "footwear",
                    "objective": "trends",
                    "temporal_context": {"main": "current", "specific": "2024"},
                    "geographical_context": "global",
                    "scope": ["functionality", "technology"]
                })
            }
        }]
    }
    mock_openai.chat.completions.create.return_value = AsyncMock(**mock_response)
    
    result = await query_agent.analyze_query_terms(
        "What are the latest trends in running shoes?"
    )
    
    assert result["focus_term"] == "running shoes"
    assert result["category"] == "footwear"
    assert result["objective"] == "trends"
    assert isinstance(result["temporal_context"], dict)
    assert result["temporal_context"]["specific"] == "2024"

@pytest.mark.asyncio
async def test_enrich_query(query_agent, mock_openai):
    """Test query enrichment."""
    mock_response = {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "focus_synonyms": ["athletic footwear", "sneakers"],
                    "objective_terms": ["popular", "emerging", "demand"],
                    "temporal_terms": ["current", "upcoming"],
                    "location_terms": ["global", "worldwide"]
                })
            }
        }]
    }
    mock_openai.chat.completions.create.return_value = AsyncMock(**mock_response)
    
    query_components = {
        "focus_term": "running shoes",
        "category": "footwear",
        "objective": "trends"
    }
    
    result = await query_agent.enrich_query(query_components)
    
    assert "focus_synonyms" in result["enriched"]
    assert "objective_terms" in result["enriched"]
    assert "temporal_terms" in result["enriched"]
    assert "location_terms" in result["enriched"]
    assert "athletic footwear" in result["enriched"]["focus_synonyms"]
    assert "popular" in result["enriched"]["objective_terms"]

@pytest.mark.asyncio
async def test_generate_search_queries(query_agent, mock_openai):
    """Test search query generation."""
    mock_response = {
        "choices": [{
            "message": {
                "content": "\n".join([
                    "What are the current market trends in running shoes?",
                    "How have running shoe designs evolved in recent years?",
                    "What are consumers looking for in running shoes today?"
                ])
            }
        }]
    }
    mock_openai.chat.completions.create.return_value = AsyncMock(**mock_response)
    
    query_components = {
        "focus_term": "running shoes",
        "category": "footwear",
        "objective": "trends",
        "temporal_context": {"main": "current", "specific": "2024"},
        "geographical_context": "global"
    }
    
    enriched_data = {
        "enriched": {
            "focus_synonyms": ["athletic footwear", "sneakers"],
            "objective_terms": ["popular", "demand"],
            "temporal_terms": ["current", "recent"],
            "location_terms": ["global", "worldwide"]
        }
    }
    
    result = await query_agent.generate_search_queries(query_components, enriched_data)
    
    assert "keyword_queries" in result
    assert "semantic_queries" in result
    assert len(result["keyword_queries"]) > 0
    assert len(result["semantic_queries"]) == 3
    assert any("running shoes" in q["query"] for q in result["keyword_queries"])
    assert any("market trends" in q for q in result["semantic_queries"])

@pytest.mark.asyncio
async def test_error_handling(query_agent):
    """Test error handling in query processing."""
    # Test with empty query
    result = await query_agent.analyze_query_terms("")
    assert result is None
    
    # Test with invalid query components
    result = await query_agent.enrich_query({})
    assert result is None
    
    # Test with missing required fields
    result = await query_agent.generate_search_queries({}, {})
    assert result is not None  # Should return fallback queries
    assert "keyword_queries" in result
    assert "semantic_queries" in result

if __name__ == "__main__":
    pytest.main(["-v", "-s", "--asyncio-mode=auto", __file__])
