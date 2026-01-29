"""
Tests for Telegram bot commands
"""
import pytest
from telegram.constants import ParseMode
from telegram.error import BadRequest


class TestBotCommands:
    """Test bot command handlers"""

    @pytest.mark.asyncio
    async def test_start_command(self, mock_bot, mock_telegram_update, mock_telegram_context):
        """Test /start command"""
        await mock_bot.cmd_start(mock_telegram_update, mock_telegram_context)

        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "Welcome to PMCC Bot" in call_args

    @pytest.mark.asyncio
    async def test_help_command(self, mock_bot, mock_telegram_update, mock_telegram_context):
        """Test /help command"""
        await mock_bot.cmd_help(mock_telegram_update, mock_telegram_context)

        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]

        # Check all essential commands are listed
        assert "/positions" in call_args
        assert "/add_leaps" in call_args
        assert "/add_short" in call_args
        assert "/alerts" in call_args
        assert "/summary" in call_args
        assert "/roll" in call_args
        assert "/newcall" in call_args
        assert "/close" in call_args

    @pytest.mark.asyncio
    async def test_positions_command_empty(self, mock_bot, mock_telegram_update, mock_telegram_context):
        """Test /positions command with no positions"""
        await mock_bot.cmd_positions(mock_telegram_update, mock_telegram_context)

        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "No active LEAPS positions" in call_args

    @pytest.mark.asyncio
    async def test_alerts_command(self, mock_bot, mock_telegram_update, mock_telegram_context):
        """Test /alerts command"""
        await mock_bot.cmd_alerts(mock_telegram_update, mock_telegram_context)

        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "Alert Configuration" in call_args

    @pytest.mark.asyncio
    async def test_add_leaps_command_success(self, mock_bot, mock_telegram_update, mock_telegram_context):
        """Test /add_leaps command with valid arguments"""
        mock_telegram_context.args = ["SPY", "620", "2027-01-17", "109.00", "2"]

        await mock_bot.cmd_add_leaps(mock_telegram_update, mock_telegram_context)

        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "LEAPS added" in call_args
        assert "SPY" in call_args

    @pytest.mark.asyncio
    async def test_add_leaps_command_missing_args(self, mock_bot, mock_telegram_update, mock_telegram_context):
        """Test /add_leaps command with missing arguments"""
        mock_telegram_context.args = ["SPY"]  # Not enough args

        await mock_bot.cmd_add_leaps(mock_telegram_update, mock_telegram_context)

        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "Usage:" in call_args


class TestMarkdownFormatting:
    """Regression tests for Markdown formatting issues"""

    @pytest.mark.asyncio
    async def test_help_command_no_markdown_errors(self, mock_bot, mock_telegram_update, mock_telegram_context):
        """
        REGRESSION TEST: Ensure /help command doesn't use problematic Markdown

        This test prevents the bug where MARKDOWN_V2 formatting caused:
        'BadRequest: Can't parse entities: character '-' is reserved and must be escaped'
        """
        await mock_bot.cmd_help(mock_telegram_update, mock_telegram_context)

        # Get the call arguments
        call_kwargs = mock_telegram_update.message.reply_text.call_args[1]

        # Help should NOT use MARKDOWN_V2 (which requires escaping)
        assert call_kwargs.get('parse_mode') != ParseMode.MARKDOWN_V2

        # Help should either use no parse_mode or simple MARKDOWN
        # (which is more forgiving with special characters)
        parse_mode = call_kwargs.get('parse_mode')
        assert parse_mode is None or parse_mode == ParseMode.MARKDOWN

    @pytest.mark.asyncio
    async def test_help_text_has_no_unescaped_markdown_v2_chars(self, mock_bot, mock_telegram_update, mock_telegram_context):
        """
        REGRESSION TEST: Check help text doesn't have unescaped special chars

        If we ever switch back to MARKDOWN_V2, this will fail and remind us
        to properly escape special characters: -_.()[]~`>#+=|{}.!
        """
        await mock_bot.cmd_help(mock_telegram_update, mock_telegram_context)

        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        call_kwargs = mock_telegram_update.message.reply_text.call_args[1]

        # If using MARKDOWN_V2, check that special chars in commands are escaped
        if call_kwargs.get('parse_mode') == ParseMode.MARKDOWN_V2:
            # Commands with underscores should be escaped: /add\_leaps not /add_leaps
            if "/add_leaps" in call_args:
                pytest.fail(
                    "Help text contains /add_leaps with unescaped underscore. "
                    "Should be /add\\_leaps for MARKDOWN_V2"
                )

    def test_help_command_text_structure(self, mock_bot):
        """Test that help text is well-formed"""
        # This is a basic structure test - we're not sending to Telegram
        # Just checking the text content is reasonable

        # Import the help text logic
        import inspect
        source = inspect.getsource(mock_bot.cmd_help)

        # Check that help command exists and has text
        assert 'help_text' in source
        assert '/positions' in source or 'positions' in source.lower()


class TestMessageFormatting:
    """Test that all bot messages format correctly"""

    @pytest.mark.asyncio
    async def test_positions_message_format(self, mock_bot, mock_telegram_update, mock_telegram_context):
        """Test that positions message formats without Markdown errors"""
        # Add a test position
        leaps_id = mock_bot.leaps_model.add("SPY", 620.0, "2027-01-17", 109.00, 2)

        await mock_bot.cmd_positions(mock_telegram_update, mock_telegram_context)

        # Should have been called
        mock_telegram_update.message.reply_text.assert_called_once()

        # Check parse_mode is specified
        call_kwargs = mock_telegram_update.message.reply_text.call_args[1]
        assert 'parse_mode' in call_kwargs

    @pytest.mark.asyncio
    async def test_all_commands_handle_special_characters(self, mock_bot, mock_telegram_update, mock_telegram_context):
        """Test commands handle special characters in output gracefully"""
        # Add position with special characters in notes
        leaps_id = mock_bot.leaps_model.add(
            "SPY", 620.0, "2027-01-17", 109.00, 2,
            notes="Test with special chars: - _ * . ! (parentheses)"
        )

        # This should not crash
        await mock_bot.cmd_positions(mock_telegram_update, mock_telegram_context)

        mock_telegram_update.message.reply_text.assert_called()


class TestCommandValidation:
    """Test command input validation"""

    @pytest.mark.asyncio
    async def test_roll_command_requires_argument(self, mock_bot, mock_telegram_update, mock_telegram_context):
        """Test /roll command requires short_call_id"""
        mock_telegram_context.args = []

        await mock_bot.cmd_roll(mock_telegram_update, mock_telegram_context)

        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "Usage:" in call_args

    @pytest.mark.asyncio
    async def test_close_command_requires_two_arguments(self, mock_bot, mock_telegram_update, mock_telegram_context):
        """Test /close command requires both short_call_id and exit_price"""
        mock_telegram_context.args = ["1"]  # Missing exit_price

        await mock_bot.cmd_close(mock_telegram_update, mock_telegram_context)

        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "Usage:" in call_args

    @pytest.mark.asyncio
    async def test_close_command_validates_numeric_input(self, mock_bot, mock_telegram_update, mock_telegram_context):
        """Test /close command validates numeric inputs"""
        mock_telegram_context.args = ["not_a_number", "3.25"]

        await mock_bot.cmd_close(mock_telegram_update, mock_telegram_context)

        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "Invalid" in call_args


class TestErrorHandling:
    """Test bot error handling"""

    @pytest.mark.asyncio
    async def test_close_nonexistent_position(self, mock_bot, mock_telegram_update, mock_telegram_context):
        """Test closing a position that doesn't exist"""
        mock_telegram_context.args = ["999", "3.25"]  # Non-existent ID

        await mock_bot.cmd_close(mock_telegram_update, mock_telegram_context)

        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "Error" in call_args or "not found" in call_args.lower()
