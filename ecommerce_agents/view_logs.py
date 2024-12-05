import sqlite3
import json
from datetime import datetime
from typing import Dict, Any

def format_timestamp(timestamp: int) -> str:
    """Convert Unix timestamp to readable format."""
    if timestamp is None or timestamp == 0:
        return "N/A"
    try:
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    except (TypeError, ValueError):
        return "Invalid timestamp"

def print_dict(d: Dict[str, Any], indent: int = 0) -> None:
    """Pretty print a dictionary with proper indentation."""
    for key, value in d.items():
        prefix = "  " * indent
        if isinstance(value, dict):
            print(f"{prefix}{key}:")
            print_dict(value, indent + 1)
        elif isinstance(value, list):
            print(f"{prefix}{key}:")
            for item in value:
                if isinstance(item, dict):
                    print_dict(item, indent + 1)
                else:
                    print(f"{prefix}  - {item}")
        else:
            print(f"{prefix}{key}: {value}")

def view_agent_sessions():
    """View detailed agent session information from the database."""
    db_path = "tmp/agents.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get table schema
        cursor.execute("PRAGMA table_info(query_agent)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"\nDatabase columns: {', '.join(columns)}\n")
        
        # Get the last 5 sessions with all columns
        cursor.execute("""
            SELECT *
            FROM query_agent 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        sessions = cursor.fetchall()
        
        print("\n=== Last 5 Agent Sessions ===\n")
        for session in sessions:
            # Convert row to dictionary using column names
            session_dict = dict(zip(columns, session))
            
            print("="*80)
            print(f"Session ID: {session_dict.get('session_id', 'N/A')}")
            created_at = session_dict.get('created_at')
            updated_at = session_dict.get('updated_at')
            print(f"Created At: {format_timestamp(created_at)}")
            print(f"Updated At: {format_timestamp(updated_at)}")
            
            # Parse and display agent_data
            try:
                agent_data = json.loads(session_dict.get('agent_data', '{}'))
                print("\nAgent Data:")
                print("-" * 40)
                
                # Display operation info
                print(f"Operation: {agent_data.get('operation', 'N/A')}")
                print(f"Status: {agent_data.get('status', 'N/A')}")
                print(f"Timestamp: {agent_data.get('timestamp', 'N/A')}")
                
                # Display query and processing details
                print(f"\nQuery: {agent_data.get('query', 'N/A')}")
                
                # Display result if available
                if 'result' in agent_data:
                    print("\nResult Details:")
                    print("-" * 40)
                    result = agent_data['result']
                    print(f"Query ID: {result.get('query_id', 'N/A')}")
                    print(f"Language: {result.get('language', 'N/A')}")
                    print(f"Date: {result.get('date', 'N/A')}")
                    
                    # Display components if available
                    if 'components' in result:
                        print("\nQuery Components:")
                        print_dict(result['components'], indent=1)
                    
                    # Display search queries if available
                    if 'search_queries' in result:
                        print("\nSearch Queries:")
                        search_queries = result['search_queries']
                        if isinstance(search_queries, dict):
                            print_dict(search_queries, indent=1)
                        else:
                            print(f"  {search_queries}")
                    
                    # Display enriched terms if available
                    if 'enriched_terms' in result:
                        print("\nEnriched Terms:")
                        print_dict(result['enriched_terms'], indent=1)
                
                # Display any errors
                if 'error' in agent_data:
                    print("\nError Information:")
                    print("-" * 40)
                    print(f"Error: {agent_data['error']}")
                
            except json.JSONDecodeError as e:
                print(f"\nError parsing agent_data: {e}")
            
            print("\n" + "="*80 + "\n")
        
        # Display session count
        cursor.execute("SELECT COUNT(*) FROM query_agent")
        total_sessions = cursor.fetchone()[0]
        print(f"\nTotal number of sessions in database: {total_sessions}")
        
    finally:
        conn.close()

if __name__ == "__main__":
    view_agent_sessions()