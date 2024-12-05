import asyncio
import sys
from dotenv import load_dotenv
import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint
from ecommerce_agents.agents.query_agent import UserQueryAgent

# Load environment variables from .env file
load_dotenv()

console = Console()

def get_input(prompt: str) -> str:
    """Get input from user with proper prompt handling."""
    console.print(prompt)
    try:
        return input()
    except EOFError:
        return "exit"

async def main():
    agent = UserQueryAgent()
    
    console.print(Panel.fit(
        "[bold blue]Welcome to the Interactive Query Agent![/bold blue]\n"
        "This agent helps analyze and enrich your product research queries.\n"
        "Type 'exit' to quit."
    ))
    
    while True:
        try:
            # Get user input
            query = get_input("\n[bold green]Enter your query:[/bold green]")
            
            if not query or query.lower() == 'exit':
                console.print("[yellow]Goodbye![/yellow]")
                break
                
            # Analyze query terms
            console.print("\n[bold]Analyzing query...[/bold]")
            terms = await agent.analyze_query_terms(query)
            
            if not terms:
                console.print("[red]Could not analyze query. Please try again.[/red]")
                continue
                
            # Display analyzed components
            component_table = Table(title="Query Components")
            component_table.add_column("Component", style="cyan")
            component_table.add_column("Value", style="green")
            
            for key, value in terms.items():
                if isinstance(value, dict):
                    value_str = json.dumps(value, indent=2)
                else:
                    value_str = str(value)
                component_table.add_row(key, value_str)
            
            console.print(component_table)
            
            # Enrich query
            console.print("\n[bold]Enriching query...[/bold]")
            enriched = await agent.enrich_query(terms)
            
            if not enriched:
                console.print("[red]Could not enrich query. Please try again.[/red]")
                continue
            
            # Display enriched data
            enriched_table = Table(title="Enriched Query Data")
            enriched_table.add_column("Category", style="cyan")
            enriched_table.add_column("Terms", style="green")
            
            for key, value in enriched["enriched"].items():
                if isinstance(value, list):
                    value_str = "\n".join(value)
                elif isinstance(value, dict):
                    value_str = json.dumps(value, indent=2)
                else:
                    value_str = str(value)
                enriched_table.add_row(key, value_str)
            
            console.print(enriched_table)
            
            # Generate search queries
            console.print("\n[bold]Generating search queries...[/bold]")
            try:
                queries = await agent.generate_search_queries(terms, enriched)
                
                # Display keyword queries
                keyword_table = Table(title="Keyword Queries")
                keyword_table.add_column("Query", style="cyan")
                keyword_table.add_column("Metadata", style="green")
                
                for query in queries["keyword_queries"]:
                    keyword_table.add_row(
                        query["query"],
                        json.dumps(query["metadata"], indent=2)
                    )
                
                console.print(keyword_table)
                
                # Display semantic queries
                semantic_table = Table(title="Semantic Queries")
                semantic_table.add_column("Query", style="cyan")
                
                for query in queries["semantic_queries"]:
                    semantic_table.add_row(query)
                
                console.print(semantic_table)
            except Exception as e:
                console.print(f"[red]Error processing search queries: {str(e)}[/red]")
                continue
            
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            continue
        
        console.print("\n[bold]Ready for next query![/bold]")

def run():
    """Run the interactive query agent."""
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")
    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]")

if __name__ == "__main__":
    run()
