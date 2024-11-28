import asyncio
import os
import json
from datetime import datetime
from phi.agent import Agent, RunResponse
from agents.query_agent import UserQueryAgent

def print_result(result):
    """Print the query analysis result in a formatted way."""
    if not result:
        print("\n❌ No results to display")
        return

    print("\n=== Query Analysis Results ===\n")
    
    # Handle both direct analysis and enriched results uniformly
    original = result.get("original", result)  # Use result directly if no "original" key
    
    if original:
        print("Query Components:")
        if focus := original.get("focus_term"):
            print(f"  • Focus Term: {focus}")
        if category := original.get("category"):
            print(f"  • Category: {category}")
        if objective := original.get("objective"):
            print(f"  • Objective: {objective}")
        if geo := original.get("geographical_context"):
            print(f"  • Geography: {geo}")
        if scope := original.get("scope"):
            print(f"  • Analysis Areas: {scope}")
        
        # Handle temporal context with new structure
        if temporal := original.get("temporal_context"):
            if isinstance(temporal, dict):
                main = temporal.get("main", "")
                specific = temporal.get("specific", "")
                time_str = f"{specific}"
                if main and main != specific:
                    time_str = f"{main} ({specific})"
                print(f"  • Time Frame: {time_str}")
            else:
                print(f"  • Time Frame: {temporal}")
    
    # Print Enriched Terms if available
    if enriched := result.get("enriched"):
        print("\nEnriched Terms:")
        if synonyms := enriched.get("focus_synonyms"):
            print(f"  • Similar Products: {', '.join(synonyms)}")
        if obj_terms := enriched.get("objective_terms"):
            print(f"  • Related Terms: {', '.join(obj_terms)}")
        if temporal := enriched.get("temporal_terms"):
            print(f"  • Time References: {', '.join(temporal)}")
        if location := enriched.get("location_terms"):
            print(f"  • Market Regions: {', '.join(location)}")
        
        # Print scope enrichment if available
        if scope_enrichment := enriched.get("scope_enrichment"):
            if scope_synonyms := scope_enrichment.get("scope_synonyms"):
                print(f"\nScope Synonyms:")
                for term in scope_synonyms:
                    print(f"  • {term}")
            if related_aspects := scope_enrichment.get("related_aspects"):
                print(f"\nRelated Aspects:")
                for aspect in related_aspects:
                    print(f"  • {aspect}")
    
    print("\n" + "="*50)

def print_search_queries(queries):
    """Print generated search queries in a formatted way."""
    if not queries:
        return
        
    print("\n=== Generated Search Queries ===\n")
    
    if keyword := queries.get("keyword_queries"):
        print("Keyword-Based Queries:")
        for query in keyword:
            print(f"  • {query}")
            
    if semantic := queries.get("semantic_queries"):
        print("\nSemantic Search Queries:")
        for query in semantic:
            print(f"  • {query}")
    
    print("\n" + "="*50)

async def process_query_with_details(agent: UserQueryAgent, query: str):
    """Process a query and show all intermediate steps."""
    print("\n" + "="*50)
    print(" Market Analysis Query Processor ".center(50, "="))
    print("="*50)

    if not query.strip():
        print("\n❌ Error: Empty query provided")
        return None

    print(f"\n📝 Query: '{query}'")

    try:
        # Step 1: Analyze Query Terms
        print("\n[1] Analyzing query components...")
        analysis_result = await agent.analyze_query_terms(query)
        
        if not analysis_result:
            print("❌ Query analysis failed - please try rephrasing your query")
            return None
            
        # Check for required focus term
        if not analysis_result.get("focus_term"):
            print("\n❗ Unable to identify main product/topic")
            new_query = input("Please provide a more specific query with a clear product or topic: ")
            if new_query:
                return await process_query_with_details(agent, new_query)
            return None
        
        # Check for missing optional parameters and combine refinement prompts
        missing_components = []
        if not analysis_result.get("objective"):
            missing_components.append("objective")
        if not analysis_result.get("temporal_context"):
            missing_components.append("time frame")
        if not analysis_result.get("geographical_context"):
            missing_components.append("geographical scope")
        if not analysis_result.get("scope"):
            missing_components.append("analysis areas")
            
        if missing_components:
            print("\n📌 Some query components were not specified. You can refine your query with additional details:")
            print("\nMissing components:", ", ".join(missing_components))
            print("\nExamples:")
            print("  • Objective: trends, comparison, performance, demand, innovation")
            print("  • Time Frame: recent, current, upcoming, Q1 2024")
            print("  • Geography: global, US, Europe, Asia")
            print("  • Analysis Areas: functionality, sustainability, technology, design")
            
            print("\nEnter additional details in the format:")
            print("objective: value | time: value | geography: value | areas: value")
            print("(Press Enter to use defaults)")
            
            refinements = input("\nRefinements: ").strip()
            
            if refinements:
                # Parse refinements
                for refinement in refinements.split("|"):
                    if ":" not in refinement:
                        continue
                    key, value = [part.strip() for part in refinement.split(":", 1)]
                    
                    if not value:
                        continue
                        
                    if key.lower() in ["objective", "obj"]:
                        analysis_result["objective"] = value
                    elif key.lower() in ["time", "temporal", "timeframe"]:
                        analysis_result["temporal_context"] = {
                            "main": value,
                            "specific": value
                        }
                    elif key.lower() in ["geo", "geography", "location"]:
                        analysis_result["geographical_context"] = value
                    elif key.lower() in ["areas", "scope", "analysis"]:
                        analysis_result["scope"] = value
            
        print_result(analysis_result)
        
        # Step 2: Query Enrichment
        print("\n[2] Enriching with market intelligence...")
        enriched = await agent.enrich_query(analysis_result)
        
        if not enriched:
            print("❌ Enrichment failed - using basic analysis only")
            return {"analysis": analysis_result}
            
        print_result(enriched)
        
        # Step 3: Display Objective Enrichment
        if obj_enrichment := enriched.get("enriched", {}).get("objective_enrichment"):
            objective = analysis_result.get("objective", "trends")
            print(f"\nObjective Enrichment for '{objective}':")
            
            if synonyms := obj_enrichment.get("synonyms"):
                print("\nSynonyms:")
                for term in synonyms:
                    print(f"  • {term}")
                    
        # Step 4: Generate Search Queries
        print("\n[3] Generating optimized search queries...")
        search_queries = await agent.generate_search_queries(analysis_result, enriched)
        
        if search_queries:
            print_search_queries(search_queries)
        else:
            print("❌ Failed to generate search queries")
        
        return {
            "analysis": analysis_result,
            "enriched": enriched,
            "search_queries": search_queries
        }
    
    except Exception as e:
        print(f"\n❌ Processing error: {str(e)}")
        print("Please try again with a simpler query")

async def test_interactive():
    """Interactive testing function for the UserQueryAgent."""
    if not os.getenv("OPENAI_API_KEY"):
        print("\n❌ Error: OPENAI_API_KEY environment variable is not set")
        return
        
    agent = UserQueryAgent()
    
    print("\n=== Ecommerce Trend Research Assistant ===")
    print("\nThis tool helps analyze market trends by:")
    print("1. Analyzing query terms and objectives")
    print("2. Enriching with related terms")
    print("\nExample queries:")
    print("- recent trends in running shoes")
    print("- market analysis of gaming laptops")
    print("- consumer preferences in smart home devices")
    print("- sustainability trends in fashion retail")
    
    while True:
        try:
            print("\nEnter your query (or 'quit' to exit): ", end='', flush=True)
            query = input()
            if not query:
                continue
            if query.lower() in ['quit', 'exit', 'q']:
                print("\nExiting...")
                break
                
            print("\nProcessing your query...\n")
            await process_query_with_details(agent, query)
            
        except EOFError:
            print("\nExiting due to EOF...")
            break
        except KeyboardInterrupt:
            print("\nExiting due to keyboard interrupt...")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Try checking your internet connection and OpenAI API key.")
            continue

if __name__ == "__main__":
    try:
        asyncio.run(test_interactive())
    except Exception as e:
        print(f"\nError: {str(e)}")
