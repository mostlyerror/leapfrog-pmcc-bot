-- PMCC Bot Database Schema

-- LEAPS positions table
CREATE TABLE IF NOT EXISTS leaps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    strike REAL NOT NULL,
    expiration TEXT NOT NULL,  -- Format: YYYY-MM-DD
    entry_price REAL NOT NULL,
    quantity INTEGER NOT NULL,
    created_at TEXT NOT NULL,  -- ISO format timestamp
    closed_at TEXT,            -- ISO format timestamp, NULL if active
    status TEXT DEFAULT 'active',  -- 'active' or 'closed'
    notes TEXT
);

-- Short call positions table
CREATE TABLE IF NOT EXISTS short_calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    leaps_id INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    strike REAL NOT NULL,
    expiration TEXT NOT NULL,  -- Format: YYYY-MM-DD
    entry_price REAL NOT NULL,
    quantity INTEGER NOT NULL,
    created_at TEXT NOT NULL,  -- ISO format timestamp
    closed_at TEXT,            -- ISO format timestamp, NULL if active
    exit_price REAL,           -- Price at which position was closed
    profit REAL,               -- Realized profit in dollars
    status TEXT DEFAULT 'active',  -- 'active' or 'closed'
    notes TEXT,
    FOREIGN KEY (leaps_id) REFERENCES leaps (id)
);

-- Alerts table for triggered alerts
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    short_call_id INTEGER NOT NULL,
    alert_type TEXT NOT NULL,  -- 'profit_50', 'profit_80', 'strike_threatened', 'expiration_approaching'
    message TEXT NOT NULL,
    triggered_at TEXT NOT NULL,  -- ISO format timestamp
    acknowledged INTEGER DEFAULT 0,  -- 0 = not acknowledged, 1 = acknowledged
    FOREIGN KEY (short_call_id) REFERENCES short_calls (id)
);

-- Cost basis history table
CREATE TABLE IF NOT EXISTS cost_basis_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    leaps_id INTEGER NOT NULL,
    short_call_id INTEGER NOT NULL,
    adjustment_amount REAL NOT NULL,  -- Premium collected (in dollars, not cents)
    adjusted_cost REAL NOT NULL,      -- New adjusted cost basis per contract
    created_at TEXT NOT NULL,         -- ISO format timestamp
    FOREIGN KEY (leaps_id) REFERENCES leaps (id),
    FOREIGN KEY (short_call_id) REFERENCES short_calls (id)
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_leaps_status ON leaps(status);
CREATE INDEX IF NOT EXISTS idx_leaps_expiration ON leaps(expiration);
CREATE INDEX IF NOT EXISTS idx_short_calls_status ON short_calls(status);
CREATE INDEX IF NOT EXISTS idx_short_calls_leaps_id ON short_calls(leaps_id);
CREATE INDEX IF NOT EXISTS idx_short_calls_expiration ON short_calls(expiration);
CREATE INDEX IF NOT EXISTS idx_alerts_acknowledged ON alerts(acknowledged);
CREATE INDEX IF NOT EXISTS idx_cost_basis_leaps_id ON cost_basis_history(leaps_id);
