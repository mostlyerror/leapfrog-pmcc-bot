# PMCC Bot Test Suite

Comprehensive test suite for the PMCC Bot with unit tests, integration tests, and regression tests.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Pytest fixtures and configuration
├── test_models.py       # Database model tests (SQLite & PostgreSQL)
├── test_bot.py          # Telegram bot command tests
└── README.md            # This file
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage report
```bash
pytest --cov --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_models.py
pytest tests/test_bot.py
```

### Run specific test
```bash
pytest tests/test_bot.py::TestMarkdownFormatting::test_help_command_no_markdown_errors
```

### Run tests matching a pattern
```bash
pytest -k "markdown"
pytest -k "database"
```

### Run only regression tests
```bash
pytest -m regression
```

## Test Categories

### Unit Tests

**Database Models (`test_models.py`)**
- SQLite and PostgreSQL compatibility
- CRUD operations for LEAPS, Short Calls, and Alerts
- Cost basis calculation and tracking
- Database type detection and connection handling

**Bot Commands (`test_bot.py`)**
- Command handlers (/start, /help, /positions, etc.)
- Input validation
- Error handling
- Message formatting

### Regression Tests

**Markdown Formatting Issues**
- `test_help_command_no_markdown_errors`: Prevents MARKDOWN_V2 escaping bugs
- `test_help_text_has_no_unescaped_markdown_v2_chars`: Validates character escaping
- Tests marked with `@pytest.mark.regression`

These tests specifically prevent the bugs we encountered:
1. **BadRequest: Can't parse entities: character '-' is reserved**
2. **BadRequest: Can't find end of the entity starting at byte offset 565**

### Integration Tests

Test the interaction between components:
- Bot commands with database operations
- Alert monitoring with API calls
- Position management workflows

## Continuous Integration

Tests run automatically on:
- Every push to `main` or `develop` branches
- Every pull request to `main`

CI pipeline runs tests on Python 3.10, 3.11, and 3.12.

See: `.github/workflows/tests.yml`

## Coverage Reports

After running tests with coverage, open the HTML report:

```bash
pytest --cov --cov-report=html
open htmlcov/index.html
```

## Writing New Tests

### Adding a Unit Test

```python
# tests/test_models.py
def test_new_feature(leaps_model):
    """Test description"""
    # Arrange
    leaps_id = leaps_model.add("SPY", 620.0, "2027-01-17", 109.00, 2)

    # Act
    result = leaps_model.some_new_method(leaps_id)

    # Assert
    assert result == expected_value
```

### Adding a Regression Test

When fixing a bug, add a test that would have caught it:

```python
# tests/test_bot.py
@pytest.mark.regression
@pytest.mark.asyncio
async def test_bug_fix_description(mock_bot, mock_telegram_update, mock_telegram_context):
    """
    REGRESSION TEST: [Bug description]

    Prevents: [Error message or behavior]
    Fixed in: [Commit hash or PR number]
    """
    # Test that reproduces the bug if the fix is removed
    pass
```

### Adding an Async Test

```python
@pytest.mark.asyncio
async def test_async_command(mock_bot, mock_telegram_update, mock_telegram_context):
    """Test async bot command"""
    await mock_bot.cmd_something(mock_telegram_update, mock_telegram_context)

    # Assert the command worked
    mock_telegram_update.message.reply_text.assert_called_once()
```

## Test Fixtures

Available fixtures (see `conftest.py`):

- `temp_db_path`: Temporary SQLite database file
- `sqlite_db`: SQLite Database instance
- `mock_postgres_db`: Mock PostgreSQL Database instance
- `leaps_model`: LeapsPosition model
- `short_call_model`: ShortCall model
- `alert_model`: Alert model
- `mock_tradier_api`: Mock TradierAPI
- `mock_telegram_update`: Mock Telegram Update object
- `mock_telegram_context`: Mock Telegram Context object
- `mock_bot`: Mock PMCCBot instance

## Debugging Tests

### Run tests with verbose output
```bash
pytest -vv
```

### Show print statements
```bash
pytest -s
```

### Drop into debugger on failure
```bash
pytest --pdb
```

### Run tests and stop on first failure
```bash
pytest -x
```

## Best Practices

1. **Test one thing per test**: Each test should verify a single behavior
2. **Use descriptive names**: Test names should describe what they test
3. **Follow AAA pattern**: Arrange, Act, Assert
4. **Mock external dependencies**: Use fixtures to mock APIs, databases, etc.
5. **Add regression tests**: When fixing bugs, add tests to prevent regression
6. **Keep tests fast**: Mock slow operations (API calls, database queries)
7. **Test edge cases**: Empty inputs, invalid data, boundary conditions

## Troubleshooting

### Import errors
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Database errors
```bash
# Tests use temporary databases that are cleaned up automatically
# If you see database lock errors, ensure no other processes are using the test database
```

### Async test failures
```bash
# Make sure pytest-asyncio is installed
pip install pytest-asyncio

# Check that asyncio_mode is set in pytest.ini
```

## Coverage Goals

Aim for:
- **80%+ overall coverage**
- **90%+ coverage for critical paths** (bot commands, database operations)
- **100% coverage for regression tests** (bugs should not regress)

Current coverage can be checked with:
```bash
pytest --cov --cov-report=term-missing
```
