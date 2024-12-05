"""
Playground for testing and interacting with eCommerce trend analysis agents with built-in monitoring.
"""
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from phi.playground import Playground, serve_playground_app
from phi.model.openai import OpenAIChat
from phi.storage.agent.sqlite import SqlAgentStorage
from phi.agent import Agent
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.exa import ExaTools

# Create agents directory if it doesn't exist
os.makedirs("agents", exist_ok=True)

# Set up storage with monitoring table
agent_storage_file: str = "tmp/agents.db"

# Initialize the query agent with monitoring capabilities
query_agent = UserQueryAgent(
    model=OpenAIChat(
        id="gpt-4",
        model_kwargs={"response_format": {"type": "text"}}  # Ensure text response format
    ),
    storage=SqlAgentStorage(
        table_name="query_agent",
        db_file=agent_storage_file
    ),
    role="Process and structure eCommerce trend queries with automated monitoring",
    debug=True,  # Enable debugging
    show_tool_calls=True,  # Show tool usage
    show_function_calls=True  # Show function calls
)

# Create the playground app with monitored agent
app = Playground(
    agents=[query_agent]
).get_app()

if __name__ == "__main__":
    serve_playground_app("ecommerce_agents.playground:app", reload=True)