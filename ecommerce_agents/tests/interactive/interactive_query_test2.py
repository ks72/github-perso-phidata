"""
Interactive test module for the UserQueryAgent class.

This module provides an interactive testing interface for:
1. Query term analysis (focus term detection)
2. User refinement of other components
3. Query enrichment and search generation
"""
import asyncio
import os
import sys
import json
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typing import Dict

# Load environment variables from .env file
load_dotenv()

# Add the project root to Python path for absolute imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from agents.query_agent import UserQueryAgent
from phi.agent import Agent, RunResponse  # Import for Agent and RunResponse

# Initialize Rich console
console = Console()

def get_input(prompt: str, optional: bool = False) -> str:
    """Get input from user with proper prompt handling."""
    user_input = input(prompt).strip()
    if user_input.lower() in ['quit', 'exit']:
        console.print("\n[cyan]Exiting interactive query test...[/cyan]")
        sys.exit(0)
    if not user_input and not optional:
        console.print("[red]Input is required. Please provide a valid value.[/red]")
        return get_input(prompt, optional)  # Re-prompt user if input is required
    return user_input

async def get_missing_components(agent: UserQueryAgent, detected: Dict) -> Dict:
    """Prompt user for any missing components."""
    console.print("\n[bold cyan]Query Component Input[/bold cyan]")

    # Mandatory: focus_term
    if not detected.get("focus_term"):
        focus_input = get_input("[yellow]Enter what you want to research: [/yellow]")
        detected["focus_term"] = focus_input.strip()

    # Mandatory: objective
    if not detected.get("objective"):
        objective_input = get_input(
            "[green]Enter research objective[/green] (e.g., trends, comparison, performance): "
        )
        detected["objective"] = objective_input.strip()

    # Mandatory: temporal_context
    if not detected.get("temporal_context"):
        temporal_input = get_input(
            "[green]Enter time frame[/green] (e.g., next season, current, upcoming, Q1 2024): "
        )
        detected["temporal_context"] = temporal_input.strip()

    # Mandatory: geographical_context
    if not detected.get("geographical_context"):
        geo_input = get_input(
            "[green]Enter location/market scope[/green] (e.g., global, US, Europe) or press Enter for 'global': ", optional=True
        )
        if not geo_input:
            detected["geographical_context"] = "global"
            console.print("[green]Using default location:[/green] global")
        else:
            detected["geographical_context"] = geo_input.strip()

    # Optional: scope
    if not detected.get("scope"):
        # Get first 5 standard scopes from agent
        scope_suggestions = ", ".join(agent.STANDARD_SCOPE_AREAS[:5])
        scope_input = get_input(
            f"[green]Enter analysis areas (optional)[/green] (suggested: {scope_suggestions}): ", optional=True
        )
        if scope_input:
            scope_valid, scope_suggestion = await agent.validate_scope(scope_input.strip())
            if scope_valid:
                detected["scope"] = scope_input.strip()
            else:
                console.print(f"[yellow]Invalid scope. Suggestion: {scope_suggestion}[/yellow]")

    # Display temporal context interpretation
    if detected.get("temporal_context"):
        console.print(f"[green]Temporal context:[/green] {detected['temporal_context']}")

    return detected

async def analyze_user_query(agent: UserQueryAgent, query: str) -> Dict:
    """Analyze user query and get missing components."""
    components = await agent.analyze_query_terms(query)
    if not components:
        components = {}

    # Check for missing components and prompt user
    required_components = ["focus_term", "objective", "temporal_context", "geographical_context"]
    missing_components = [comp for comp in required_components if not components.get(comp)]

    if missing_components:
        console.print(f"\n[yellow]Missing components detected: {', '.join(missing_components)}[/yellow]")
        components = await get_missing_components(agent, components)

    return components

async def print_result(result: Dict):
    """Print the query analysis result in a formatted way."""
    if not result:
        console.print("[red]No results to display[/red]")
        return
        
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Component", style="cyan", width=30)
    table.add_column("Value", style="green", width=50)
    
    def format_value(value):
        if isinstance(value, (list, tuple)):
            return "\n".join([f"- {item}" for item in value])
        elif isinstance(value, dict):
            return "\n".join([f"{k}: {format_value(v)}" for k, v in value.items()])
        return str(value)
    
    # Add detected components
    for key, value in result.items():
        formatted_value = format_value(value)
        table.add_row(key.replace("_", " ").title(), formatted_value)
    
    console.print(table)

async def process_query_with_details(agent: UserQueryAgent, query: str):
    """Process a query and show all intermediate steps."""
    try:
        console.print("\n[cyan]Processing query:[/cyan]", query)
        
        # Analyze the query and get components
        components = await analyze_user_query(agent, query)
        console.print("\n[yellow]Debug - Components Structure:[/yellow]")
        console.print(json.dumps(components, indent=2))

        # Display the analyzed components
        console.print("\n[cyan]Query Components:[/cyan]")
        await print_result(components)

        # Enrich the query data
        console.print("\n[cyan]Enriching query with relevant terms...[/cyan]")
        enriched = await agent.enrich_query_data(components)
        
        if enriched:
            # Debug: Print the raw enriched data structure
            console.print("\n[yellow]Debug - Raw Enriched Data Structure:[/yellow]")
            console.print(json.dumps(enriched, indent=2))
            
            try:
                # Create simplified version based on the actual structure
                original = enriched.get("original", {})
                enriched_data = enriched.get("enriched", {})
                metadata = enriched.get("metadata", {})
                
                display_enriched = {
                    "Original Query": {
                        "Focus": original.get("focus_term", ""),
                        "Objective": original.get("objective", ""),
                        "Temporal": original.get("temporal_context", ""),
                        "Geography": original.get("geographical_context", "")
                    },
                    "Enriched Terms": {
                        "Focus Items": enriched_data.get("focus", []),
                        "Related Objectives": enriched_data.get("objective", []),
                        "Target Locations": enriched_data.get("location", []),
                        "Time Frame": enriched_data.get("temporal", [])
                    },
                    "Additional Info": {
                        "Category": metadata.get("category", ""),
                        "Duration": metadata.get("temporal", {}).get("duration", "")
                    }
                }
                console.print("\n[bold cyan]Enriched Query Data:[/bold cyan]")
                await print_result(display_enriched)
            except Exception as e:
                console.print(f"[red]Error processing enriched data: {str(e)}[/red]")
                console.print(f"[yellow]Error occurred at:[/yellow]")
                import traceback
                console.print(traceback.format_exc())
        else:
            console.print("[red]Error: Failed to enrich query data[/red]")

        # Generate search queries
        console.print("\n[cyan]Generating search queries...[/cyan]")
        search_queries = await agent.generate_search_queries(enriched)
        if search_queries:
            console.print("\n[bold cyan]Generated Search Queries:[/bold cyan]")
            for query_type, queries in search_queries.items():
                console.print(f"\n[magenta]{query_type}:[/magenta]")
                for q in queries:
                    console.print(f"- {q}")
    except Exception as e:
        console.print(f"[red]Error in process_query_with_details: {str(e)}[/red]")
        console.print(f"[yellow]Full traceback:[/yellow]")
        import traceback
        console.print(traceback.format_exc())

async def test_interactive():
    """Interactive testing function for the UserQueryAgent."""
    agent = UserQueryAgent()
    
    console.print(Panel.fit(
        "[bold blue]Interactive Query Agent Test[/bold blue]\n"
        "Enter your queries for analysis. Type 'exit' to quit."
    ))
    
    while True:
        try:
            query = get_input("\n[bold green]Enter your query:[/bold green]")
            if not query or query.lower() == 'exit':
                break

            # Process the query
            await process_query_with_details(agent, query)
                
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