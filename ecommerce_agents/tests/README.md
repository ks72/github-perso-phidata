# Tests Directory Structure

This directory contains all test files for the ecommerce_agents project, organized by test type:

## Directory Structure

```
tests/
├── interactive/          # Interactive testing scripts
│   └── interactive_query_test.py
├── unit/                # Unit tests
│   ├── test_admin.py
│   ├── test_keyword_search.py
│   └── test_query_agent.py
├── integration/         # Integration tests
│   └── test_admin_ui.py
├── conftest.py         # Shared pytest fixtures
└── README.md           # This file
```

## Test Types

### Interactive Tests
- Located in `interactive/`
- Manual testing scripts with rich console output
- Used for testing user interactions and visual feedback

### Unit Tests
- Located in `unit/`
- Automated tests for individual components
- Uses pytest for testing
- Mocks external dependencies

### Integration Tests
- Located in `integration/`
- Tests multiple components working together
- Tests UI interactions and complex workflows

## Running Tests

### Interactive Tests
```bash
# Run interactive query test
python -m ecommerce_agents.tests.interactive.interactive_query_test
```

### Unit Tests
```bash
# Run all unit tests
pytest ecommerce_agents/tests/unit/

# Run specific test file
pytest ecommerce_agents/tests/unit/test_query_agent.py
```

### Integration Tests
```bash
# Run all integration tests
pytest ecommerce_agents/tests/integration/

# Run specific test file
pytest ecommerce_agents/tests/integration/test_admin_ui.py
```

## Adding New Tests

1. Place new test files in the appropriate directory based on test type
2. Use shared fixtures from `conftest.py` when possible
3. Follow existing naming conventions:
   - Unit tests: `test_*.py`
   - Interactive tests: `*_test.py`
   - Integration tests: `test_*_integration.py`
