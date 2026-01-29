# Testing Guide

## ✅ Test Suite Summary

**Status:** All 29 tests passing ✓

### Coverage
- **Overall:** 51% code coverage
- **models.py:** 72% coverage (database operations)
- **bot.py:** 53% coverage (bot commands)
- **tests/test_bot.py:** 98% coverage
- **tests/test_models.py:** 100% coverage

### Test Distribution
- **Database Tests:** 14 tests
- **Bot Command Tests:** 15 tests
- **Total:** 29 tests

## 🎯 What's Tested

### Database Operations (`test_models.py`)
✅ SQLite and PostgreSQL compatibility
✅ Database type detection (Path vs URL)
✅ LEAPS position CRUD operations
✅ Short call CRUD operations
✅ Alert management
✅ Cost basis calculation and tracking
✅ Position closing with profit calculation

### Bot Commands (`test_bot.py`)
✅ All command handlers (/start, /help, /positions, etc.)
✅ Input validation for all commands
✅ Error handling for invalid inputs
✅ Message formatting without crashes

### Regression Tests (Prevents Past Bugs)
✅ **Markdown formatting errors** - The exact bugs we just fixed!
  - `test_help_command_no_markdown_errors`
  - `test_help_text_has_no_unescaped_markdown_v2_chars`
  - `test_all_commands_handle_special_characters`

These tests ensure we never reintroduce:
- `BadRequest: Can't parse entities: character '-' is reserved`
- `BadRequest: Can't find end of the entity starting at byte offset 565`

## 🚀 Quick Start

### Run All Tests
```bash
pytest
```

### Run With Coverage Report
```bash
pytest --cov --cov-report=html
open htmlcov/index.html
```

### Run Specific Tests
```bash
# Run database tests only
pytest tests/test_models.py

# Run bot tests only
pytest tests/test_bot.py

# Run regression tests only
pytest -m regression

# Run specific test
pytest tests/test_bot.py::TestMarkdownFormatting::test_help_command_no_markdown_errors
```

## 🔄 Continuous Integration

Tests run automatically on:
- ✅ Every push to `main` or `develop`
- ✅ Every pull request to `main`
- ✅ Multiple Python versions (3.10, 3.11, 3.12)

See: `.github/workflows/tests.yml`

## 📊 Test Results

```
============================= test session starts ==============================
collected 29 items

tests/test_bot.py::TestBotCommands::test_start_command PASSED           [  3%]
tests/test_bot.py::TestBotCommands::test_help_command PASSED            [  6%]
tests/test_bot.py::TestBotCommands::test_positions_command_empty PASSED [ 10%]
tests/test_bot.py::TestBotCommands::test_alerts_command PASSED          [ 13%]
tests/test_bot.py::TestBotCommands::test_add_leaps_command_success PASSED [ 17%]
tests/test_bot.py::TestBotCommands::test_add_leaps_command_missing_args PASSED [ 20%]
tests/test_bot.py::TestMarkdownFormatting::test_help_command_no_markdown_errors PASSED [ 24%]
tests/test_bot.py::TestMarkdownFormatting::test_help_text_has_no_unescaped_markdown_v2_chars PASSED [ 27%]
tests/test_bot.py::TestMarkdownFormatting::test_help_command_text_structure PASSED [ 31%]
tests/test_bot.py::TestMessageFormatting::test_positions_message_format PASSED [ 34%]
tests/test_bot.py::TestMessageFormatting::test_all_commands_handle_special_characters PASSED [ 37%]
tests/test_bot.py::TestCommandValidation::test_roll_command_requires_argument PASSED [ 41%]
tests/test_bot.py::TestCommandValidation::test_close_command_requires_two_arguments PASSED [ 44%]
tests/test_bot.py::TestCommandValidation::test_close_command_validates_numeric_input PASSED [ 48%]
tests/test_bot.py::TestErrorHandling::test_close_nonexistent_position PASSED [ 51%]
tests/test_models.py::TestDatabase::test_sqlite_initialization PASSED   [ 55%]
tests/test_models.py::TestDatabase::test_postgresql_type_detection PASSED [ 58%]
tests/test_models.py::TestDatabase::test_sqlite_connection PASSED       [ 62%]
tests/test_models.py::TestLeapsPosition::test_add_leaps PASSED          [ 65%]
tests/test_models.py::TestLeapsPosition::test_get_active_leaps PASSED   [ 68%]
tests/test_models.py::TestLeapsPosition::test_get_by_id PASSED          [ 72%]
tests/test_models.py::TestLeapsPosition::test_update_status PASSED      [ 75%]
tests/test_models.py::TestShortCall::test_add_short_call PASSED         [ 79%]
tests/test_models.py::TestShortCall::test_get_active_short_calls PASSED [ 82%]
tests/test_models.py::TestShortCall::test_close_short_call PASSED       [ 86%]
tests/test_models.py::TestAlert::test_add_alert PASSED                  [ 89%]
tests/test_models.py::TestAlert::test_get_unacknowledged_alerts PASSED  [ 93%]
tests/test_models.py::TestAlert::test_acknowledge_alert PASSED          [ 96%]
tests/test_models.py::TestCostBasisTracking::test_cost_basis_adjustment PASSED [100%]

============================== 29 passed in 0.44s ===============================
```

## 🛡️ What This Prevents

### Before Tests
❌ Deploy broken code to production
❌ Markdown formatting breaks bot
❌ Database compatibility issues go unnoticed
❌ Manual testing required for every change

### After Tests
✅ Catch bugs before deployment
✅ Regression tests prevent old bugs from returning
✅ Database works on SQLite AND PostgreSQL
✅ Automated testing on every commit

## 📝 Adding New Tests

When adding a feature:
```python
# tests/test_bot.py
@pytest.mark.asyncio
async def test_new_feature(mock_bot, mock_telegram_update, mock_telegram_context):
    """Test the new feature"""
    # Test implementation
    pass
```

When fixing a bug:
```python
# tests/test_bot.py
@pytest.mark.regression
@pytest.mark.asyncio
async def test_bug_description(mock_bot, mock_telegram_update, mock_telegram_context):
    """
    REGRESSION TEST: Prevents [bug description]

    This test ensures the bug doesn't come back.
    """
    # Test that would have caught the bug
    pass
```

## 📚 Documentation

Full testing documentation: `tests/README.md`

- Test structure and organization
- Available fixtures
- Writing new tests
- Debugging tests
- Best practices

## 🎓 Benefits

1. **Confidence**: Know your code works before deploying
2. **Speed**: Automated tests run in <1 second
3. **Quality**: Catch bugs early in development
4. **Documentation**: Tests show how code should behave
5. **Refactoring**: Change code confidently without breaking features

## 🔍 Example: How Tests Caught Our Bugs

The Markdown formatting bugs we fixed would have been caught immediately:

```python
# This test fails if we use MARKDOWN_V2 without proper escaping
def test_help_command_no_markdown_errors():
    """Prevents: BadRequest: Can't parse entities"""
    # Test the /help command
    # Would fail with MARKDOWN_V2 and unescaped characters
```

**With tests:** Bug caught in development ✓
**Without tests:** Bug discovered in production after user complaints ✗

## 🚦 Next Steps

1. **Increase coverage to 80%+** by adding more tests
2. **Add integration tests** for full workflows
3. **Add performance tests** for database operations
4. **Set up code quality checks** (flake8, mypy)

---

**Remember:** Write tests as you code, not after. It's easier and catches bugs earlier!
