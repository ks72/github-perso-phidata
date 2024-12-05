"""
Interactive test module for the UserQueryAgent class.

This module provides an interactive testing interface for:
1. Query term analysis (focus term detection)
2. User refinement of other components
3. Query enrichment and search generation
"""
import asyncio
import os
import json
import sys
from datetime import datetime
from phi.agent import Agent, RunResponse
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from typing import Tuple, Dict

# Load environment variables from .env file
load_dotenv()

# Add the project root to Python path for absolute imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from agents.query_agent import UserQueryAgent

# Initialize Rich console
console = Console()

def get_input(prompt: str, default: str = "") -> str:
    """Get input from user with proper prompt handling."""
    user_input = input(prompt).strip()
    if user_input.lower() in ['quit', 'exit']:
        console.print("\n[cyan]Exiting interactive query test...[/cyan]")
        sys.exit(0)
    return user_input if user_input else default

async def analyze_user_query(agent: UserQueryAgent, query: str, attempt: int = 1) -> Tuple[Dict, Dict]:
    """Analyze user query and get missing components."""
    try:
        # First analyze the query to detect components
        components = await agent.analyze_query_terms(query, attempt)
        if not components:
            components = {}
            
        # Show validation results on first attempt
        if attempt == 1 and components.get("validation"):
            validation = components["validation"]
            if validation.get("unmatched_terms"):
                console.print("\n[yellow]Some terms in your query were not recognized:[/yellow]")
                for term in validation["unmatched_terms"]:
                    console.print(f"  • {term}")
            
            if validation.get("missing_components"):
                # First handle required components
                required = []
                seen = set()
                for comp in validation["missing_components"]:
                    if comp != "temporal_context" and comp not in seen:
                        required.append(comp)
                        seen.add(comp)
                if required:
                    console.print("\n[yellow]Required components missing from your query:[/yellow]")
                    for component in required:
                        if component == "objective":
                            console.print("  • research objective (e.g., trends, demand, performance, comparison)")
                        elif component == "scope":
                            console.print("  • analysis areas (e.g., functionality, sustainability)")
                        else:
                            console.print(f"  • {component}")
                    
                    # Get additional input from user for required components
                    additional_input = get_input("\n[yellow]Please provide these details (or press Enter to use defaults):[/yellow] ")
                    if additional_input:
                        # Combine original query with additional input
                        full_query = f"{query} {additional_input}"
                        return await analyze_user_query(agent, full_query, attempt=2)
                    
                    # If no input provided, proceed with second attempt
                    return await analyze_user_query(agent, query, attempt=2)
        
        # Enrich the query data
        enriched = await agent.enrich_query_data(components)
        return components, enriched
        
    except Exception as e:
        console.print(f"[red]Error analyzing query terms: {str(e)}[/red]")
        return None, None

async def get_missing_components(agent: UserQueryAgent, detected: Dict) -> Dict:
    """Get any missing components from user input."""
    console.print("\n[bold cyan]Query Component Input[/bold cyan]")
    
    # Always need a focus term if not detected
    if not detected.get("focus_term"):
        focus_input = get_input("[yellow]Enter what you want to research: [/yellow]")
        if not focus_input:
            console.print("[red]No focus term provided. Cannot proceed.[/red]")
            return None
        detected["focus_term"] = focus_input.strip()
    
    # Get objective if not detected
    if not detected.get("objective"):
        objective_input = get_input(
            "[green]Enter research objective[/green] (e.g., trends, comparison, performance) or press Enter for default 'trends': "
        )
        if not objective_input:
            detected["objective"] = "trends"
            console.print("[green]Using default objective:[/green] trends")
        else:
            is_valid, _ = await agent.validate_objective(objective_input)
            if is_valid:
                detected["objective"] = objective_input
            else:
                detected["objective"] = "trends"
                console.print("[yellow]Invalid objective. Using default:[/yellow] trends")
    
    # Get temporal context if not detected
    if not detected.get("temporal_context"):
        temporal_input = get_input(
            "[green]Enter time frame[/green] (e.g., current, upcoming, Q1 2024) or press Enter for current season: "
        )
        if not temporal_input:
            current_season = agent.get_current_season()
            current_year = agent.current_year
            detected["temporal_context"] = {
                "main": "current",
                "specific": f"{current_season} {current_year}"
            }
            console.print(f"[green]Using current time frame:[/green] {current_season} {current_year}")
        else:
            is_valid, suggestion = await agent.validate_temporal(temporal_input)
            if is_valid:
                detected["temporal_context"] = {
                    "main": temporal_input,
                    "specific": suggestion if suggestion else temporal_input
                }
            else:
                current_season = agent.get_current_season()
                current_year = agent.current_year
                detected["temporal_context"] = {
                    "main": "current",
                    "specific": f"{current_season} {current_year}"
                }
                console.print(f"[yellow]Invalid time frame. Using current:[/yellow] {current_season} {current_year}")
    
    # Get geographical context if not detected
    if not detected.get("geographical_context"):
        geo_input = get_input(
            "[green]Enter location/market scope[/green] (e.g., global, US, Europe) or press Enter for 'global': "
        )
        if not geo_input:
            detected["geographical_context"] = "global"
            console.print("[green]Using default location:[/green] global")
        else:
            is_valid, _ = await agent.validate_geographical(geo_input)
            if is_valid:
                detected["geographical_context"] = geo_input
            else:
                detected["geographical_context"] = "global"
                console.print("[yellow]Invalid location. Using default:[/yellow] global")
    
    # Get scope if not detected (optional)
    if not detected.get("scope"):
        scope_input = get_input(
            "[green]Enter analysis areas[/green] (e.g., functionality, sustainability) or press Enter to skip: "
        )
        if scope_input:
            is_valid, _ = await agent.validate_scope(scope_input)
            if is_valid:
                detected["scope"] = scope_input
            else:
                console.print("[yellow]Invalid scope. Skipping.[/yellow]")
    
    return detected

async def print_result(result: Dict):
    """Print the query analysis result in a formatted way."""
    if not result:
        console.print("[red]No results to display[/red]")
        return
        
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Component", style="cyan")
    table.add_column("Value", style="green")
    
    # Add detected components - checking both top level and nested structure
    if "focus_term" in result:
        table.add_row("Focus", str(result["focus_term"]))
    if "objective" in result:
        table.add_row("Objective", str(result["objective"]))
    if "temporal_context" in result:
        table.add_row("Temporal", str(result["temporal_context"]))
    if "geographical_context" in result:
        table.add_row("Location", str(result["geographical_context"]))
    if "scope" in result:
        table.add_row("Scope", str(result["scope"]))
    
    # Also check in detected if present
    if "detected" in result:
        detected = result["detected"]
        if "focus_term" in detected and "focus_term" not in result:
            table.add_row("Focus", str(detected["focus_term"]))
        if "objective" in detected and "objective" not in result:
            table.add_row("Objective", str(detected["objective"]))
        if "temporal_context" in detected and "temporal_context" not in result:
            table.add_row("Temporal", str(detected["temporal_context"]))
        if "geographical_context" in detected and "geographical_context" not in result:
            table.add_row("Location", str(detected["geographical_context"]))
        if "scope" in detected and "scope" not in result:
            table.add_row("Scope", str(detected["scope"]))
    
    console.print(table)

async def print_enriched_data(enriched: Dict):
    """Print enriched query data in a formatted way."""
    if not enriched:
        console.print("[red]No enriched data to display[/red]")
        return
        
    # Print enriched terms
    console.print("\n[bold cyan]Enriched Terms:[/bold cyan]")
    enriched_terms = enriched.get("enriched", {})
    if enriched_terms:
        table = Table(show_header=True)
        table.add_column("Category", style="cyan")
        table.add_column("Terms", style="green", no_wrap=False)
        
        # Display enriched terms by category
        categories = ["objective", "focus", "scope", "location", "temporal"]
        for category in categories:
            terms = enriched_terms.get(category, [])
            if terms:
                table.add_row(category.title(), ", ".join(terms))
        
        console.print(table)
    
    # Print metadata
    metadata = enriched.get("metadata", {})
    if metadata:
        console.print("\n[bold cyan]Metadata Terms:[/bold cyan]")
        meta_table = Table(show_header=True)
        meta_table.add_column("Category", style="cyan")
        meta_table.add_column("Terms", style="yellow", no_wrap=False)
        
        # Handle location terms
        location_terms = metadata.get("location_terms", [])
        if location_terms:
            meta_table.add_row("Location", ", ".join(location_terms) if isinstance(location_terms, list) else str(location_terms))
        
        # Handle temporal terms
        temporal_terms = metadata.get("temporal_terms", [])
        if temporal_terms:
            meta_table.add_row("Temporal Terms", ", ".join(temporal_terms) if isinstance(temporal_terms, list) else str(temporal_terms))
        
        # Handle temporal metadata
        temporal_meta = metadata.get("temporal", {})
        if temporal_meta and isinstance(temporal_meta, dict):
            if duration := temporal_meta.get("duration"):
                meta_table.add_row("Temporal Duration", str(duration))
        
        # Handle category
        if category := metadata.get("category"):
            meta_table.add_row("Product Category", str(category))
        
        console.print(meta_table)

async def print_search_queries(queries: Dict):
    """Print generated search queries in a formatted way."""
    if not queries:
        console.print("[red]No search queries to display[/red]")
        return
        
    # Print search queries
    if queries and "keyword_queries" in queries:
        console.print("\n[bold cyan]Generated Search Queries:[/bold cyan]")
        table = Table(show_header=True)
        table.add_column("Query", style="green")
        table.add_column("Location Metadata", style="yellow")
        table.add_column("Category", style="cyan")
        table.add_column("Time Metadata", style="magenta")
        
        for query_data in queries["keyword_queries"]:
            query = query_data["query"]
            metadata = query_data.get("metadata", {})
            
            # Get location info
            locations = metadata.get("location", [])
            location_str = ", ".join(locations) if isinstance(locations, list) else str(locations)
            
            # Get category
            category = metadata.get("category", "N/A")
            
            # Get temporal info
            temporal_meta = metadata.get("temporal", {})
            temporal_str = temporal_meta.get("duration", "N/A") if temporal_meta else "N/A"
            
            table.add_row(query, location_str, category, temporal_str)
        
        console.print(table)

async def process_query_with_details(agent: UserQueryAgent, query: str, previous_focus: str = None):
    """Process a query and show all intermediate steps."""
    console.print("\n[cyan]Processing query:[/cyan]", query)
    
    # First analyze the query
    components = await agent.analyze_query_terms(query, attempt=1, previous_focus=previous_focus)
    
    # Get missing and unmatched components
    missing = []
    unmatched = []
    
    if components:
        if 'missing' in components:
            missing = components['missing']
        if 'unmatched' in components:
            unmatched = components['unmatched']
            
        console.print("\n[cyan]Query Components:[/cyan]")
        await print_result(components)
    
    if missing:
        console.print("\n[yellow]Required components missing from your query:[/yellow]")
        for item in missing:
            if "objective" in item.lower():
                console.print(f"  • {item} - Use one of: trends, demand, performance, comparison")
            elif "scope" in item.lower():
                console.print(f"  • {item} - Use one of: functionality, sustainability, technology, health, price, culture")
            elif "temporal" in item.lower():
                console.print(f"  • {item} - Use terms like: current, next season, recent")
            elif "geographical" in item.lower():
                console.print(f"  • {item} - Use terms like: global, Europe, North America")
            else:
                console.print(f"  • {item}")
            
        if unmatched:
            console.print("\n[yellow]Terms that couldn't be categorized:[/yellow]")
            for term in unmatched:
                console.print(f"  • {term}")
            
        # Build the complete query with user input
        updated_terms = []
        
        # Track which components were actually missing
        missing_components = []
        for item in missing:
            if "objective" in item.lower():
                missing_components.append("objective")
            elif "scope" in item.lower():
                missing_components.append("scope")
            elif "temporal" in item.lower():
                missing_components.append("temporal")
            elif "geographical" in item.lower():
                missing_components.append("geographical")
        
        # Only prompt for components that are actually missing
        console.print("\n[cyan]Please provide the missing components:[/cyan]")
        
        for component in missing_components:
            if component == "objective":
                console.print("\n[cyan]Available research objectives:[/cyan]")
                console.print("  • trends")
                console.print("  • demand")
                console.print("  • performance")
                console.print("  • comparison")
                while True:
                    objective = input("Enter research objective: ").lower().strip()
                    if objective in ["trends", "demand", "performance", "comparison"]:
                        updated_terms.append(objective)
                        break
                    else:
                        console.print("[red]Invalid choice. Please select from the available options.[/red]")
            
            elif component == "scope":
                console.print("\n[cyan]Available analysis areas:[/cyan]")
                console.print("  • functionality")
                console.print("  • sustainability")
                console.print("  • technology")
                console.print("  • health")
                console.print("  • price")
                console.print("  • culture")
                while True:
                    scope = input("Enter analysis area: ").lower().strip()
                    if scope in ["functionality", "sustainability", "technology", "health", "price", "culture"]:
                        updated_terms.append(scope)
                        break
                    else:
                        console.print("[red]Invalid choice. Please select from the available options.[/red]")
            
            elif component == "temporal":
                console.print("\n[cyan]Available time references:[/cyan]")
                console.print("  • current")
                console.print("  • next season")
                console.print("  • recent")
                console.print("  • next fall")
                console.print("  • next spring")
                console.print("  • next summer")
                console.print("  • next winter")
                while True:
                    temporal = input("Enter time reference: ").lower().strip()
                    if temporal in ["current", "next season", "recent"] or any(season in temporal for season in ["fall", "spring", "summer", "winter"]):
                        updated_terms.append(f"for {temporal}")
                        break
                    else:
                        console.print("[red]Invalid choice. Please select from the available options.[/red]")
            
            elif component == "geographical":
                console.print("\n[cyan]Available location references:[/cyan]")
                console.print("  • global")
                console.print("  • Europe")
                console.print("  • North America")
                console.print("  • Asia")
                while True:
                    geographical = input("Enter location reference: ").lower().strip()
                    if geographical in ["global", "europe", "north america", "asia"]:
                        updated_terms.append(f"in {geographical}")
                        break
                    else:
                        console.print("[red]Invalid choice. Please select from the available options.[/red]")
        
        # Reconstruct the query with the original terms and new components
        updated_query = f"{query} {' '.join(updated_terms)}"
        console.print(f"\n[cyan]Updated query:[/cyan] {updated_query}")
        components = await agent.analyze_query_terms(updated_query, attempt=1, previous_focus=previous_focus)
            
        # Display final components
        console.print("\n[cyan]Final Query Components:[/cyan]")
        await print_result(components)
    
    # Proceed with enrichment and search generation automatically
    console.print("\n[cyan]Enriching query with relevant terms...[/cyan]")
    try:
        enriched = await agent.enrich_query_data(components)
        if enriched:
            await print_enriched_data(enriched)
            
            console.print("\n[cyan]Generating optimized search queries...[/cyan]")
            search_queries = await agent.generate_search_queries(enriched)
            if search_queries:
                await print_search_queries(search_queries)
        else:
            console.print("[red]Error: Failed to enrich query data[/red]")
    except Exception as e:
        console.print(f"[red]Error processing query: {str(e)}[/red]")
    
    return components

async def test_interactive():
    """Interactive testing function for the UserQueryAgent."""
    agent = UserQueryAgent()
    previous_focus = None
    
    console.print(Panel.fit(
        "[bold blue]Interactive Query Agent Test[/bold blue]\n"
        "Enter your queries for analysis. Type 'exit' to quit."
    ))
    
    while True:
        try:
            query = get_input("\n[bold green]Enter your query:[/bold green]")
            if not query or query.lower() == 'exit':
                break
                
            # Process the query with previous focus term context
            await process_query_with_details(agent, query, previous_focus)
            
            # Update the previous focus term if a new one is detected
            components, _ = await analyze_user_query(agent, query)
            if components and "focus_term" in components:
                previous_focus = components["focus_term"]
                
        except Exception as e:
            console.print(f"[red]Error processing query: {str(e)}[/red]")
            continue

if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(test_interactive())
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
