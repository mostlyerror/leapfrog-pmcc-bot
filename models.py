"""
Database models for PMCC Bot
"""
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Database:
    """Database connection and operations"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS leaps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    strike REAL NOT NULL,
                    expiration TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    quantity INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    closed_at TEXT,
                    status TEXT DEFAULT 'active',
                    notes TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS short_calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    leaps_id INTEGER NOT NULL,
                    symbol TEXT NOT NULL,
                    strike REAL NOT NULL,
                    expiration TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    quantity INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    closed_at TEXT,
                    exit_price REAL,
                    profit REAL,
                    status TEXT DEFAULT 'active',
                    notes TEXT,
                    FOREIGN KEY (leaps_id) REFERENCES leaps (id)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    short_call_id INTEGER NOT NULL,
                    alert_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    triggered_at TEXT NOT NULL,
                    acknowledged INTEGER DEFAULT 0,
                    FOREIGN KEY (short_call_id) REFERENCES short_calls (id)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS cost_basis_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    leaps_id INTEGER NOT NULL,
                    short_call_id INTEGER NOT NULL,
                    adjustment_amount REAL NOT NULL,
                    adjusted_cost REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (leaps_id) REFERENCES leaps (id),
                    FOREIGN KEY (short_call_id) REFERENCES short_calls (id)
                )
            """)

            conn.commit()

        logger.info(f"Database initialized at {self.db_path}")

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn


class LeapsPosition:
    """LEAPS position model"""

    def __init__(self, db: Database):
        self.db = db

    def add(self, symbol: str, strike: float, expiration: str,
            entry_price: float, quantity: int, notes: str = "") -> int:
        """Add a new LEAPS position"""
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO leaps (symbol, strike, expiration, entry_price,
                                   quantity, created_at, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (symbol, strike, expiration, entry_price, quantity,
                  datetime.now().isoformat(), notes))
            conn.commit()
            logger.info(f"Added LEAPS: {symbol} {strike}C {expiration}")
            return cursor.lastrowid

    def get_active(self) -> List[Dict[str, Any]]:
        """Get all active LEAPS positions"""
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM leaps WHERE status = 'active'
                ORDER BY expiration DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def get_by_id(self, leaps_id: int) -> Optional[Dict[str, Any]]:
        """Get LEAPS by ID"""
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM leaps WHERE id = ?
            """, (leaps_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_status(self, leaps_id: int, status: str):
        """Update LEAPS status"""
        with self.db.get_connection() as conn:
            conn.execute("""
                UPDATE leaps SET status = ?, closed_at = ?
                WHERE id = ?
            """, (status, datetime.now().isoformat() if status == 'closed' else None, leaps_id))
            conn.commit()
            logger.info(f"Updated LEAPS {leaps_id} status to {status}")

    def get_adjusted_cost_basis(self, leaps_id: int) -> float:
        """Get adjusted cost basis after premium credits"""
        leaps = self.get_by_id(leaps_id)
        if not leaps:
            return 0.0

        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                SELECT COALESCE(SUM(adjustment_amount), 0) as total_adjustments
                FROM cost_basis_history
                WHERE leaps_id = ?
            """, (leaps_id,))
            row = cursor.fetchone()
            total_adjustments = row['total_adjustments'] if row else 0.0

        adjusted_cost = (leaps['entry_price'] * leaps['quantity']) - total_adjustments
        return adjusted_cost / leaps['quantity']  # Per-contract adjusted basis


class ShortCall:
    """Short call position model"""

    def __init__(self, db: Database):
        self.db = db

    def add(self, leaps_id: int, symbol: str, strike: float,
            expiration: str, entry_price: float, quantity: int,
            notes: str = "") -> int:
        """Add a new short call position"""
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO short_calls (leaps_id, symbol, strike, expiration,
                                         entry_price, quantity, created_at, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (leaps_id, symbol, strike, expiration, entry_price,
                  quantity, datetime.now().isoformat(), notes))
            conn.commit()
            logger.info(f"Added short call: {symbol} {strike}C {expiration}")
            return cursor.lastrowid

    def get_active(self) -> List[Dict[str, Any]]:
        """Get all active short call positions"""
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                SELECT sc.*, l.symbol as leaps_symbol, l.strike as leaps_strike,
                       l.expiration as leaps_expiration
                FROM short_calls sc
                JOIN leaps l ON sc.leaps_id = l.id
                WHERE sc.status = 'active'
                ORDER BY sc.expiration ASC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def get_by_id(self, short_call_id: int) -> Optional[Dict[str, Any]]:
        """Get short call by ID"""
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                SELECT sc.*, l.symbol as leaps_symbol, l.strike as leaps_strike,
                       l.expiration as leaps_expiration
                FROM short_calls sc
                JOIN leaps l ON sc.leaps_id = l.id
                WHERE sc.id = ?
            """, (short_call_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def close(self, short_call_id: int, exit_price: float) -> float:
        """Close a short call and calculate profit"""
        short_call = self.get_by_id(short_call_id)
        if not short_call:
            raise ValueError(f"Short call {short_call_id} not found")

        profit = (short_call['entry_price'] - exit_price) * short_call['quantity'] * 100

        with self.db.get_connection() as conn:
            conn.execute("""
                UPDATE short_calls
                SET status = 'closed', closed_at = ?, exit_price = ?, profit = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), exit_price, profit, short_call_id))

            # Update cost basis
            leaps = LeapsPosition(self.db).get_by_id(short_call['leaps_id'])
            adjusted_cost = (leaps['entry_price'] * leaps['quantity']) - (profit / 100)

            conn.execute("""
                INSERT INTO cost_basis_history
                (leaps_id, short_call_id, adjustment_amount, adjusted_cost, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (short_call['leaps_id'], short_call_id, profit / 100,
                  adjusted_cost / leaps['quantity'], datetime.now().isoformat()))

            conn.commit()

        logger.info(f"Closed short call {short_call_id}, profit: ${profit:.2f}")
        return profit


class Alert:
    """Alert model"""

    def __init__(self, db: Database):
        self.db = db

    def add(self, short_call_id: int, alert_type: str, message: str) -> int:
        """Add a new alert"""
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO alerts (short_call_id, alert_type, message, triggered_at)
                VALUES (?, ?, ?, ?)
            """, (short_call_id, alert_type, message, datetime.now().isoformat()))
            conn.commit()
            return cursor.lastrowid

    def get_unacknowledged(self) -> List[Dict[str, Any]]:
        """Get unacknowledged alerts"""
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM alerts
                WHERE acknowledged = 0
                ORDER BY triggered_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def acknowledge(self, alert_id: int):
        """Acknowledge an alert"""
        with self.db.get_connection() as conn:
            conn.execute("""
                UPDATE alerts SET acknowledged = 1 WHERE id = ?
            """, (alert_id,))
            conn.commit()
