"""
My Learning Agent with UI

This is a learning project that demonstrates various capabilities of phidata:
1. Web search capabilities
2. Beautiful UI interface
3. Custom tools and functions
"""

from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.duckduckgo import DuckDuckGo
from rich.prompt import Prompt

# Initialize the agent with various capabilities
learning_agent = Agent(
    name="Learning Assistant",
    description="I am a helpful AI assistant focused on learning and research.",
    model=OpenAIChat(
        model="gpt-4",
        temperature=0.7,
    ),
    # Add useful tools
    tools=[
        DuckDuckGo(),  # For web search
    ],
    # Add helpful instructions
    instructions=[
        "I am a helpful AI assistant focused on learning and research",
        "I can search the web to provide up-to-date information",
        "I format my responses in markdown for better readability",
    ],
    # Enable markdown formatting
    markdown=True,
    # Show when tools are being used
    show_tool_calls=True,
)

# Run the agent UI
if __name__ == "__main__":
    print("\nWelcome to the Learning Assistant! Type 'exit' or 'quit' to end the conversation.\n")
    
    while True:
        # Get user input
        user_input = Prompt.ask("[bold]You[/bold]")
        
        # Check for exit command
        if user_input.lower() in ['exit', 'quit']:
            print("\nGoodbye! Have a great day!")
            break
            
        # Get agent response
        learning_agent.print_response(user_input, stream=True)
