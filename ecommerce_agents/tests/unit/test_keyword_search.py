"""
Test script for the KeywordSearchAgent.
Tests various query types and search parameters.

Usage:
    1. Regular search:
       python test_keyword_search.py
    
    2. Test relevance scoring:
       python test_keyword_search.py --test-relevance
       
    3. Test relevance for specific query:
       python test_keyword_search.py --test-relevance --query "your search query"
"""
import asyncio
from datetime import datetime
from typing import Dict, Any
import os
import sys
import argparse

# Add the parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))  # This should point to the root directory
sys.path.insert(0, parent_dir)

# Now we can import our modules
from ecommerce_agents.agents.keyword_search_agent import KeywordSearchAgent
from ecommerce_agents.admin.api import AdminAPI

async def test_user_search(query: str, category: str = None, region: str = "wt-wt", max_results: int = 5):
    """
    Perform a search with user-provided parameters.
    
    Args:
        query: Search query string
        category: Optional category (no longer used for filtering)
        region: Region code (default: wt-wt)
        max_results: Maximum number of results to return
    """
    agent = KeywordSearchAgent()
    
    print(f"\nPerforming search with:")
    print(f"Query: '{query}'")
    print(f"Region: {region}")
    print(f"Max Results: {max_results}")
    print("\nSearching...")
    
    try:
        results = await agent.search(
            query=query,
            category=category,
            region=region,
            max_results=max_results
        )
        
        print(f"\nFound {len(results)} results:")
        for i, result in enumerate(results, 1):
            # Calculate and show relevance information
            relevance = analyze_relevance(query, result.title, result.description)
            
            print(f"\n{i}. Result Analysis:")
            print(f"   Search Terms: {', '.join(relevance['search_terms'])}")
            print(f"   Title: {result.title}")
            print(f"   Relevance Breakdown:")
            print(f"   - Title Score: {relevance['title_score']:.2f}")
            print(f"     Matches found: {', '.join(relevance['title_matches']) if relevance['title_matches'] else 'none'}")
            print(f"   - Description Score: {relevance['desc_score']:.2f}")
            print(f"     Matches found: {', '.join(relevance['desc_matches']) if relevance['desc_matches'] else 'none'}")
            print(f"   - Total Score: {relevance['total_score']:.2f}")
            print(f"\n   URL: {result.url}")
            print(f"   Description: {result.description[:150]}...")
            if result.date:
                print(f"   Date: {result.date}")
            print("-" * 50)
            
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        raise  # Show full traceback for debugging

def analyze_relevance(query: str, title: str, description: str) -> Dict[str, Any]:
    """
    Analyze how relevance score is calculated for a result.
    """
    search_terms = query.lower().split()
    title = title.lower()
    description = description.lower()
    
    title_matches = []
    desc_matches = []
    title_score = 0.0
    desc_score = 0.0
    
    # Check title matches
    for term in search_terms:
        if term in title:
            title_matches.append(term)
            title_score += 0.5  # Each title match adds 0.5
            
    # Check description matches
    for term in search_terms:
        if term in description:
            desc_matches.append(term)
            desc_score += 0.3  # Each description match adds 0.3
    
    total_score = min(title_score + desc_score, 1.0)  # Cap at 1.0
    
    return {
        "search_terms": search_terms,
        "title_matches": title_matches,
        "desc_matches": desc_matches,
        "title_score": title_score,
        "desc_score": desc_score,
        "total_score": total_score
    }

async def test_relevance_scoring(query: str, max_results: int = 5):
    """
    Test the relevance scoring functionality of the search agent.
    """
    agent = KeywordSearchAgent()
    
    print(f"\nTesting relevance scoring for query: '{query}'")
    print(f"Search terms: {query.lower().split()}")
    print("=" * 60)
    
    try:
        results = await agent.search(query=query, max_results=max_results)
        
        if not results:
            print("No results found.")
            return
            
        print(f"\nFound {len(results)} results, sorted by relevance:")
        for i, result in enumerate(results, 1):
            relevance = analyze_relevance(query, result.title, result.description)
            
            print(f"\n{i}. Result Analysis:")
            print(f"   Search Terms: {', '.join(relevance['search_terms'])}")
            print(f"   Title: {result.title}")
            print(f"   Relevance Breakdown:")
            print(f"   - Title Score: {relevance['title_score']:.2f}")
            print(f"     Matches found: {', '.join(relevance['title_matches']) if relevance['title_matches'] else 'none'}")
            print(f"   - Description Score: {relevance['desc_score']:.2f}")
            print(f"     Matches found: {', '.join(relevance['desc_matches']) if relevance['desc_matches'] else 'none'}")
            print(f"   - Total Score: {relevance['total_score']:.2f}")
            print(f"\n   URL: {result.url}")
            print(f"   Description: {result.description[:150]}...")
            if result.date:
                print(f"   Date: {result.date}")
            print("-" * 50)
            
    except Exception as e:
        print(f"Error during relevance testing: {str(e)}")
        raise  # Re-raise to see full traceback

def get_user_input():
    """Get search parameters from user input."""
    print("\nEnter search parameters:")
    query = input("Search query: ").strip()
    
    # Get max results
    while True:
        try:
            max_results = input("Maximum number of results (default: 5): ").strip()
            if not max_results:
                max_results = 5
            else:
                max_results = int(max_results)
            break
        except ValueError:
            print("Please enter a valid number")
    
    # Get region
    region = input("Region code (default: wt-wt): ").strip()
    if not region:
        region = "wt-wt"
    
    return query, None, region, max_results

async def main():
    """Main entry point for the test script."""
    parser = argparse.ArgumentParser(
        description="Test the KeywordSearchAgent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--query", type=str, help="Search query")
    parser.add_argument("--test-relevance", action="store_true", help="Run relevance scoring test")
    parser.add_argument("--max-results", type=int, default=5, help="Maximum number of results")
    args = parser.parse_args()
    
    try:
        if args.test_relevance:
            if args.query:
                await test_relevance_scoring(args.query, args.max_results)
            else:
                # Run a series of relevance test cases
                test_queries = [
                    "python programming tutorial",
                    "best running shoes 2024",
                    "machine learning tensorflow pytorch comparison",
                    "AI technology trends 2024",
                    "cryptocurrency"
                ]
                for query in test_queries:
                    await test_relevance_scoring(query, args.max_results)
        else:
            query, category, region, max_results = get_user_input()
            await test_user_search(query, category, region, max_results)
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        raise  # Show full traceback for debugging

if __name__ == "__main__":
    asyncio.run(main())

import pytest
from datetime import datetime
from agents.query_agent import UserQueryAgent

@pytest.fixture
def query_agent():
    return UserQueryAgent()

@pytest.mark.asyncio
async def test_temporal_metadata_processing():
    agent = UserQueryAgent()
    
    # Test recent/current time
    result = agent._process_temporal_metadata({"specific": "recent"}, ["current", "nowadays"])
    assert result["time_limit"] == "6 months"
    
    # Test last quarter
    result = agent._process_temporal_metadata({"specific": "last quarter"}, [])
    assert result["time_limit"] == "3 months"
    
    # Test last year
    result = agent._process_temporal_metadata({"specific": "last year"}, [])
    assert result["time_limit"] == "1 year"
    
    # Test future date
    future_year = str(datetime.now().year + 1)
    result = agent._process_temporal_metadata({"specific": f"trends for {future_year}"}, [])
    assert result["time_limit"] is None

@pytest.mark.asyncio
async def test_location_metadata_processing():
    agent = UserQueryAgent()
    
    # Test global location
    result = agent._process_location_metadata("global", ["worldwide", "international"])
    assert len(result["locations"]) == 0
    
    # Test specific locations
    result = agent._process_location_metadata("Europe", ["France", "Germany", "UK"])
    assert "France" in result["locations"]
    assert "Germany" in result["locations"]
    assert "UK" in result["locations"]
    
    # Test invalid location terms
    result = agent._process_location_metadata("Europe", ["EU", "A", "France"])
    assert len(result["locations"]) == 1
    assert "France" in result["locations"]

@pytest.mark.asyncio
async def test_generate_search_queries():
    agent = UserQueryAgent()
    
    # Test case 1: Basic query with recent timeframe
    query_components = {
        "focus_term": "running shoes",
        "category": "footwear",
        "objective": "trends",
        "temporal_context": {"specific": "recent"},
        "geographical_context": "Europe"
    }
    
    enriched_data = {
        "enriched": {
            "focus_synonyms": ["sneakers"],
            "objective_terms": ["design", "style"],
            "temporal_terms": ["current"],
            "location_terms": ["France", "Germany", "UK"]
        }
    }
    
    result = await agent.generate_search_queries(query_components, enriched_data)
    
    # Verify keyword queries structure
    assert "keyword_queries" in result
    assert isinstance(result["keyword_queries"], list)
    assert len(result["keyword_queries"]) > 0
    
    # Check first keyword query
    first_query = result["keyword_queries"][0]
    assert "query" in first_query
    assert "metadata" in first_query
    assert "time_limit" in first_query["metadata"]
    assert "locations" in first_query["metadata"]
    
    # Verify query components
    assert "running shoes" in first_query["query"]
    assert first_query["metadata"]["time_limit"] == "6 months"
    assert len(first_query["metadata"]["locations"]) > 0
    
    # Test case 2: Future trends query
    query_components["temporal_context"] = {"specific": f"trends for {datetime.now().year + 1}"}
    result = await agent.generate_search_queries(query_components, enriched_data)
    
    # Verify no time limit for future trends
    assert result["keyword_queries"][0]["metadata"]["time_limit"] is None
    
    # Test case 3: Global market query
    query_components["geographical_context"] = "global"
    result = await agent.generate_search_queries(query_components, enriched_data)
    
    # Verify no location filters for global search
    assert len(result["keyword_queries"][0]["metadata"]["locations"]) == 0

@pytest.mark.asyncio
async def test_query_combinations():
    agent = UserQueryAgent()
    
    # Test query combinations with multiple terms
    query_components = {
        "focus_term": "smartphone",
        "category": "electronics",
        "objective": "trends",
        "temporal_context": {"specific": "recent"},
        "geographical_context": "Asia"
    }
    
    enriched_data = {
        "enriched": {
            "focus_synonyms": ["mobile phone", "cell phone"],
            "objective_terms": ["innovation", "features"],
            "temporal_terms": ["current"],
            "location_terms": ["Japan", "South Korea", "China"]
        }
    }
    
    result = await agent.generate_search_queries(query_components, enriched_data)
    
    # Verify all combinations are generated
    expected_combinations = (
        len(["smartphone", "mobile phone", "cell phone"]) *  # focus terms
        len(["trends", "innovation", "features"])  # objective terms
    )
    
    assert len(result["keyword_queries"]) == expected_combinations
    
    # Verify query formatting
    for query in result["keyword_queries"]:
        # Check parentheses around focus terms
        assert query["query"].startswith("(")
        closing_paren_index = query["query"].find(")")
        assert closing_paren_index > 0
        
        # Verify metadata
        assert query["metadata"]["time_limit"] == "6 months"
        assert len(query["metadata"]["locations"]) == 3  # Japan, South Korea, China