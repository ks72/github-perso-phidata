"""
My Learning Agent with UI

This is a learning project that demonstrates various capabilities of phidata:
1. Web search capabilities
2. Memory to remember conversation context
3. Beautiful UI interface
4. Custom tools and functions
"""

from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.wikipedia import Wikipedia
from phi.knowledge.pdf import PDFKnowledge
from phi.storage.conversation import ConversationStorage

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
        Wikipedia(),    # For Wikipedia lookups
    ],
    # Add conversation memory
    conversation_storage=ConversationStorage(
        storage_path="./storage/conversations"
    ),
    # Add helpful instructions
    instructions=[
        "I am a helpful AI assistant focused on learning and research",
        "I can search the web and Wikipedia to provide up-to-date information",
        "I maintain context of our conversation to provide better assistance",
        "I format my responses in markdown for better readability",
    ],
    # Enable markdown formatting
    markdown=True,
    # Show when tools are being used
    show_tool_calls=True,
)

# Run the agent UI
if __name__ == "__main__":
    learning_agent.run_ui(
        title="My Learning Assistant",
        description="A helpful AI assistant for learning and research",
        # Run on port 8501
        port=8501,
        # Allow file uploads (PDFs, etc.)
        share_files=True,
    )
