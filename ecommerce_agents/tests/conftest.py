"""
Shared pytest fixtures for all test modules.
"""
import os
import sys
import pytest
from unittest.mock import AsyncMock, patch
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to Python path for absolute imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from agents.query_agent import UserQueryAgent
from agents.keyword_search_agent import KeywordSearchAgent
from tools.duckduckgo_tool import DuckDuckGoTool

@pytest.fixture
def query_agent():
    """Create a UserQueryAgent instance for testing."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not found in .env file")
    return UserQueryAgent()

@pytest.fixture
def keyword_search_agent():
    """Create a KeywordSearchAgent instance for testing."""
    return KeywordSearchAgent()

@pytest.fixture(scope="function")
def mock_openai():
    """Mock the OpenAI client"""
    with patch('openai.AsyncOpenAI', autospec=True) as mock:
        mock_instance = AsyncMock()
        mock_instance.chat.completions.create = AsyncMock()
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture(scope="function")
def mock_duckduckgo():
    """Mock the DuckDuckGo search tool"""
    with patch('tools.duckduckgo_tool.DuckDuckGoTool.search') as mock:
        mock.return_value = AsyncMock()
        yield mock
