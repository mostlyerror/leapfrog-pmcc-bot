"""
Tests for database models
"""
import pytest
from datetime import datetime
from models import Database, LeapsPosition, ShortCall, Alert


class TestDatabase:
    """Test Database class"""

    def test_sqlite_initialization(self, temp_db_path):
        """Test SQLite database initialization"""
        db = Database(temp_db_path)
        assert db.db_type == "sqlite"
        assert db.db_path == temp_db_path
        assert db.db_url is None

    def test_postgresql_type_detection(self):
        """Test PostgreSQL URL detection"""
        from unittest.mock import patch, MagicMock

        with patch('models.psycopg2.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
            mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
            mock_connect.return_value = mock_conn

            db = Database('postgresql://user:pass@localhost/testdb')
            assert db.db_type == "postgresql"
            assert db.db_url == 'postgresql://user:pass@localhost/testdb'
            assert db.db_path is None

    def test_sqlite_connection(self, sqlite_db):
        """Test SQLite connection works"""
        with sqlite_db.get_connection() as conn:
            assert conn is not None


class TestLeapsPosition:
    """Test LeapsPosition model"""

    def test_add_leaps(self, leaps_model):
        """Test adding a LEAPS position"""
        leaps_id = leaps_model.add(
            symbol="SPY",
            strike=620.0,
            expiration="2027-01-17",
            entry_price=109.00,
            quantity=2,
            notes="Test LEAPS"
        )
        assert leaps_id > 0

    def test_get_active_leaps(self, leaps_model):
        """Test retrieving active LEAPS positions"""
        # Add a LEAPS
        leaps_model.add("SPY", 620.0, "2027-01-17", 109.00, 2)

        # Get active positions
        active = leaps_model.get_active()
        assert len(active) == 1
        assert active[0]['symbol'] == "SPY"
        assert active[0]['status'] == "active"

    def test_get_by_id(self, leaps_model):
        """Test retrieving LEAPS by ID"""
        leaps_id = leaps_model.add("SPY", 620.0, "2027-01-17", 109.00, 2)
        leaps = leaps_model.get_by_id(leaps_id)

        assert leaps is not None
        assert leaps['id'] == leaps_id
        assert leaps['symbol'] == "SPY"

    def test_update_status(self, leaps_model):
        """Test updating LEAPS status"""
        leaps_id = leaps_model.add("SPY", 620.0, "2027-01-17", 109.00, 2)
        leaps_model.update_status(leaps_id, "closed")

        leaps = leaps_model.get_by_id(leaps_id)
        assert leaps['status'] == "closed"
        assert leaps['closed_at'] is not None


class TestShortCall:
    """Test ShortCall model"""

    def test_add_short_call(self, leaps_model, short_call_model):
        """Test adding a short call position"""
        leaps_id = leaps_model.add("SPY", 620.0, "2027-01-17", 109.00, 2)

        short_id = short_call_model.add(
            leaps_id=leaps_id,
            symbol="SPY",
            strike=730.0,
            expiration="2026-03-21",
            entry_price=6.50,
            quantity=2,
            notes="Test short call"
        )
        assert short_id > 0

    def test_get_active_short_calls(self, leaps_model, short_call_model):
        """Test retrieving active short calls"""
        leaps_id = leaps_model.add("SPY", 620.0, "2027-01-17", 109.00, 2)
        short_call_model.add(leaps_id, "SPY", 730.0, "2026-03-21", 6.50, 2)

        active = short_call_model.get_active()
        assert len(active) == 1
        assert active[0]['symbol'] == "SPY"

    def test_close_short_call(self, leaps_model, short_call_model):
        """Test closing a short call and calculating profit"""
        leaps_id = leaps_model.add("SPY", 620.0, "2027-01-17", 109.00, 2)
        short_id = short_call_model.add(leaps_id, "SPY", 730.0, "2026-03-21", 6.50, 2)

        # Close at $3.25 (entry was $6.50)
        profit = short_call_model.close(short_id, 3.25)

        # Profit = (6.50 - 3.25) * 2 contracts * 100 = $650
        assert profit == 650.0

        # Check position is closed
        short = short_call_model.get_by_id(short_id)
        assert short['status'] == "closed"
        assert short['exit_price'] == 3.25


class TestAlert:
    """Test Alert model"""

    def test_add_alert(self, leaps_model, short_call_model, alert_model):
        """Test adding an alert"""
        leaps_id = leaps_model.add("SPY", 620.0, "2027-01-17", 109.00, 2)
        short_id = short_call_model.add(leaps_id, "SPY", 730.0, "2026-03-21", 6.50, 2)

        alert_id = alert_model.add(
            short_call_id=short_id,
            alert_type="profit_target",
            message="50% profit target reached"
        )
        assert alert_id > 0

    def test_get_unacknowledged_alerts(self, leaps_model, short_call_model, alert_model):
        """Test retrieving unacknowledged alerts"""
        leaps_id = leaps_model.add("SPY", 620.0, "2027-01-17", 109.00, 2)
        short_id = short_call_model.add(leaps_id, "SPY", 730.0, "2026-03-21", 6.50, 2)
        alert_model.add(short_id, "profit_target", "Test alert")

        alerts = alert_model.get_unacknowledged()
        assert len(alerts) == 1
        assert alerts[0]['acknowledged'] == 0

    def test_acknowledge_alert(self, leaps_model, short_call_model, alert_model):
        """Test acknowledging an alert"""
        leaps_id = leaps_model.add("SPY", 620.0, "2027-01-17", 109.00, 2)
        short_id = short_call_model.add(leaps_id, "SPY", 730.0, "2026-03-21", 6.50, 2)
        alert_id = alert_model.add(short_id, "profit_target", "Test alert")

        alert_model.acknowledge(alert_id)

        alerts = alert_model.get_unacknowledged()
        assert len(alerts) == 0


class TestCostBasisTracking:
    """Test cost basis adjustment tracking"""

    def test_cost_basis_adjustment(self, leaps_model, short_call_model):
        """Test that closing short calls adjusts LEAPS cost basis"""
        # Add LEAPS at $109.00
        leaps_id = leaps_model.add("SPY", 620.0, "2027-01-17", 109.00, 2)

        # Initial cost basis should be entry price
        initial_basis = leaps_model.get_adjusted_cost_basis(leaps_id)
        assert initial_basis == 109.00

        # Add and close short call for $6.50 profit per contract
        short_id = short_call_model.add(leaps_id, "SPY", 730.0, "2026-03-21", 6.50, 2)
        short_call_model.close(short_id, 0.00)  # Close at $0 = full profit

        # Cost basis should be reduced by profit
        # $6.50 profit per contract reduces basis by $6.50
        adjusted_basis = leaps_model.get_adjusted_cost_basis(leaps_id)
        assert adjusted_basis == 102.50  # 109.00 - 6.50
