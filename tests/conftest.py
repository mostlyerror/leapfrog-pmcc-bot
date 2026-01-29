"""
Pytest configuration and fixtures
"""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock
from models import Database, LeapsPosition, ShortCall, Alert
from tradier import TradierAPI
from bot import PMCCBot


@pytest.fixture
def temp_db_path():
    """Create a temporary database file path"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        yield Path(tmp.name)
        # Cleanup
        Path(tmp.name).unlink(missing_ok=True)


@pytest.fixture
def sqlite_db(temp_db_path):
    """Create a SQLite database instance for testing"""
    db = Database(temp_db_path)
    yield db


@pytest.fixture
def mock_postgres_db(monkeypatch):
    """Create a mock PostgreSQL database for testing"""
    # Mock psycopg2 connection
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

    def mock_connect(*args, **kwargs):
        return mock_conn

    import models
    if models.POSTGRES_AVAILABLE:
        monkeypatch.setattr('models.psycopg2.connect', mock_connect)

    db = Database('postgresql://test:test@localhost/test')
    db._mock_conn = mock_conn
    db._mock_cursor = mock_cursor
    yield db


@pytest.fixture
def leaps_model(sqlite_db):
    """Create a LeapsPosition model instance"""
    return LeapsPosition(sqlite_db)


@pytest.fixture
def short_call_model(sqlite_db):
    """Create a ShortCall model instance"""
    return ShortCall(sqlite_db)


@pytest.fixture
def alert_model(sqlite_db):
    """Create an Alert model instance"""
    return Alert(sqlite_db)


@pytest.fixture
def mock_tradier_api():
    """Create a mock TradierAPI instance"""
    api = MagicMock(spec=TradierAPI)
    api.get_quote.return_value = {
        'symbol': 'SPY',
        'last': 500.0,
        'bid': 499.50,
        'ask': 500.50
    }
    api.get_options_chain.return_value = {
        'options': []
    }
    return api


@pytest.fixture
def mock_telegram_update():
    """Create a mock Telegram Update object"""
    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.chat_id = 123456789
    return update


@pytest.fixture
def mock_telegram_context():
    """Create a mock Telegram Context object"""
    context = MagicMock()
    context.args = []
    return context


@pytest.fixture
def mock_bot(sqlite_db, mock_tradier_api, monkeypatch):
    """Create a mock PMCCBot instance"""
    # Mock Telegram Application
    mock_app = MagicMock()
    mock_app.bot = MagicMock()
    mock_app.bot.send_message = AsyncMock()

    def mock_builder():
        builder = MagicMock()
        builder.token.return_value = builder
        builder.build.return_value = mock_app
        return builder

    monkeypatch.setattr('telegram.ext.Application.builder', mock_builder)

    bot = PMCCBot(sqlite_db, mock_tradier_api)
    bot._mock_app = mock_app
    return bot
