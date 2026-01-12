# State Persistence Template

SQLite database template for persisting bot state across restarts.

---

## Overview

This template implements state persistence to SQLite, allowing the bot to:
- Survive restarts mid-day without losing position or P&L data
- Resume trading with exact account state knowledge
- Maintain audit trail of all trades
- Recover from crashes gracefully

---

## state_db.py

```python
"""
State Persistence with SQLite
Author: Luther Barnum

Persists bot state to SQLite database for crash recovery and audit trail.
"""

import sqlite3
from datetime import datetime, date
from pathlib import Path
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class StateDB:
    """SQLite database for bot state persistence."""

    def __init__(self, db_path: str = "bot_state.db"):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.conn: Optional[sqlite3.Connection] = None
        self._connect()
        self._create_tables()

    def _connect(self):
        """Establish database connection."""
        try:
            self.conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,  # Allow use from async context
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            )
            self.conn.row_factory = sqlite3.Row  # Access columns by name
            logger.info(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise

    def _create_tables(self):
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()

        # Account state table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS account_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                equity REAL NOT NULL,
                high_water_mark REAL NOT NULL,
                dd_threshold REAL NOT NULL,
                dd_locked BOOLEAN NOT NULL,
                profit_target_hit BOOLEAN NOT NULL,
                last_updated TIMESTAMP NOT NULL
            )
        """)

        # Positions table (single row - current position)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                direction INTEGER NOT NULL,
                entry_price REAL,
                stop_loss REAL,
                take_profit REAL,
                trail_on BOOLEAN,
                hwm REAL,
                lwm REAL,
                contracts INTEGER,
                opened_at TIMESTAMP,
                last_updated TIMESTAMP NOT NULL
            )
        """)

        # Daily P&L table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_pnl (
                date TEXT PRIMARY KEY,
                pnl REAL NOT NULL,
                trades INTEGER NOT NULL DEFAULT 0,
                stopped BOOLEAN NOT NULL DEFAULT 0,
                last_updated TIMESTAMP NOT NULL
            )
        """)

        # Trades history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP NOT NULL,
                direction INTEGER NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL NOT NULL,
                exit_reason TEXT NOT NULL,
                pnl REAL NOT NULL,
                contracts INTEGER NOT NULL,
                atr REAL,
                adx REAL
            )
        """)

        # Re-entry tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reentry_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                last_exit_bar INTEGER NOT NULL,
                last_exit_profitable BOOLEAN NOT NULL,
                last_exit_direction INTEGER NOT NULL,
                reentry_count INTEGER NOT NULL,
                last_updated TIMESTAMP NOT NULL
            )
        """)

        self.conn.commit()
        logger.info("Database tables created/verified")

    # =========================================================================
    # Account State
    # =========================================================================

    def save_account_state(self, apex_account):
        """
        Save Apex account state.

        Args:
            apex_account: ApexAccountState object
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO account_state (
                id, equity, high_water_mark, dd_threshold, dd_locked,
                profit_target_hit, last_updated
            ) VALUES (1, ?, ?, ?, ?, ?, ?)
        """, (
            apex_account.equity,
            apex_account.high_water_mark,
            apex_account.dd_threshold,
            apex_account.dd_locked,
            apex_account.profit_target_hit,
            datetime.now()
        ))

        self.conn.commit()

    def load_account_state(self) -> Optional[Dict]:
        """
        Load saved account state.

        Returns:
            Dict with account state or None if no saved state
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM account_state WHERE id = 1")
        row = cursor.fetchone()

        if row:
            return {
                "equity": row["equity"],
                "high_water_mark": row["high_water_mark"],
                "dd_threshold": row["dd_threshold"],
                "dd_locked": bool(row["dd_locked"]),
                "profit_target_hit": bool(row["profit_target_hit"]),
            }

        return None

    # =========================================================================
    # Position State
    # =========================================================================

    def save_position(self, position_state: Dict):
        """
        Save current position state.

        Args:
            position_state: Dict with position details
                - direction: 1=long, -1=short, 0=flat
                - entry_price, stop_loss, take_profit
                - trail_on, hwm, lwm
                - contracts
                - opened_at
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO positions (
                id, direction, entry_price, stop_loss, take_profit,
                trail_on, hwm, lwm, contracts, opened_at, last_updated
            ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            position_state.get("direction", 0),
            position_state.get("entry_price"),
            position_state.get("stop_loss"),
            position_state.get("take_profit"),
            position_state.get("trail_on", False),
            position_state.get("hwm"),
            position_state.get("lwm"),
            position_state.get("contracts"),
            position_state.get("opened_at"),
            datetime.now()
        ))

        self.conn.commit()

    def load_position(self) -> Optional[Dict]:
        """
        Load saved position state.

        Returns:
            Dict with position state or None
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM positions WHERE id = 1")
        row = cursor.fetchone()

        if row and row["direction"] != 0:
            return {
                "direction": row["direction"],
                "entry_price": row["entry_price"],
                "stop_loss": row["stop_loss"],
                "take_profit": row["take_profit"],
                "trail_on": bool(row["trail_on"]),
                "hwm": row["hwm"],
                "lwm": row["lwm"],
                "contracts": row["contracts"],
                "opened_at": row["opened_at"],
            }

        return None

    def clear_position(self):
        """Clear position (mark as flat)."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO positions (
                id, direction, entry_price, stop_loss, take_profit,
                trail_on, hwm, lwm, contracts, opened_at, last_updated
            ) VALUES (1, 0, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, ?)
        """, (datetime.now(),))
        self.conn.commit()

    # =========================================================================
    # Daily P&L
    # =========================================================================

    def save_daily_pnl(self, trade_date: date, pnl: float, stopped: bool, trades: int = 0):
        """
        Save daily P&L state.

        Args:
            trade_date: Trading date
            pnl: Daily P&L
            stopped: Whether daily max loss hit
            trades: Number of trades today
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO daily_pnl (
                date, pnl, trades, stopped, last_updated
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            trade_date.isoformat(),
            pnl,
            trades,
            stopped,
            datetime.now()
        ))

        self.conn.commit()

    def load_daily_pnl(self, trade_date: date) -> Optional[Dict]:
        """
        Load daily P&L for date.

        Args:
            trade_date: Trading date

        Returns:
            Dict with daily stats or None
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM daily_pnl WHERE date = ?",
            (trade_date.isoformat(),)
        )
        row = cursor.fetchone()

        if row:
            return {
                "pnl": row["pnl"],
                "trades": row["trades"],
                "stopped": bool(row["stopped"]),
            }

        return None

    # =========================================================================
    # Trade History
    # =========================================================================

    def record_trade(self, trade: Dict):
        """
        Record completed trade.

        Args:
            trade: Dict with trade details
                - timestamp, direction, entry_price, exit_price
                - exit_reason, pnl, contracts
                - atr, adx (optional)
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO trades (
                timestamp, direction, entry_price, exit_price,
                exit_reason, pnl, contracts, atr, adx
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            trade["timestamp"],
            trade["direction"],
            trade["entry_price"],
            trade["exit_price"],
            trade["exit_reason"],
            trade["pnl"],
            trade["contracts"],
            trade.get("atr"),
            trade.get("adx"),
        ))

        self.conn.commit()

    def get_trades(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict]:
        """
        Get trade history.

        Args:
            start_date: Filter trades on/after this date
            end_date: Filter trades on/before this date

        Returns:
            List of trade dicts
        """
        cursor = self.conn.cursor()

        query = "SELECT * FROM trades WHERE 1=1"
        params = []

        if start_date:
            query += " AND DATE(timestamp) >= ?"
            params.append(start_date.isoformat())

        if end_date:
            query += " AND DATE(timestamp) <= ?"
            params.append(end_date.isoformat())

        query += " ORDER BY timestamp ASC"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    # =========================================================================
    # Re-entry State
    # =========================================================================

    def save_reentry_state(self, reentry_state: Dict):
        """
        Save re-entry tracking state.

        Args:
            reentry_state: Dict with re-entry tracking
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO reentry_state (
                id, last_exit_bar, last_exit_profitable,
                last_exit_direction, reentry_count, last_updated
            ) VALUES (1, ?, ?, ?, ?, ?)
        """, (
            reentry_state["last_exit_bar"],
            reentry_state["last_exit_profitable"],
            reentry_state["last_exit_direction"],
            reentry_state["reentry_count"],
            datetime.now()
        ))

        self.conn.commit()

    def load_reentry_state(self) -> Optional[Dict]:
        """Load re-entry state."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM reentry_state WHERE id = 1")
        row = cursor.fetchone()

        if row:
            return {
                "last_exit_bar": row["last_exit_bar"],
                "last_exit_profitable": bool(row["last_exit_profitable"]),
                "last_exit_direction": row["last_exit_direction"],
                "reentry_count": row["reentry_count"],
            }

        return None

    # =========================================================================
    # Utilities
    # =========================================================================

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def backup(self, backup_path: str):
        """
        Create backup of database.

        Args:
            backup_path: Path for backup file
        """
        import shutil
        shutil.copy2(self.db_path, backup_path)
        logger.info(f"Database backed up to: {backup_path}")
```

---

## Integration into Bot

```python
# In bot_*.py

class TradingBot:
    def __init__(self, config):
        self.config = config

        # Initialize state database
        self.db = StateDB(config.db_path) if config.persistence_enabled else None

        # Load saved state on startup
        if self.db:
            self._load_saved_state()

    def _load_saved_state(self):
        """Load saved state from database on startup."""
        # Load position
        position = self.db.load_position()
        if position:
            self.position = position["direction"]
            self.entry_price = position["entry_price"]
            self.stop_loss = position["stop_loss"]
            self.take_profit = position["take_profit"]
            self.trail_on = position["trail_on"]
            self.hwm = position["hwm"]
            self.lwm = position["lwm"]
            self.contracts = position["contracts"]

            logger.warning(
                f"⚠️ RESUMING FROM SAVED STATE: "
                f"{'LONG' if self.position == 1 else 'SHORT'} {self.contracts} @ {self.entry_price}"
            )

        # Load re-entry state
        reentry = self.db.load_reentry_state()
        if reentry:
            self.last_exit_bar = reentry["last_exit_bar"]
            self.last_exit_profitable = reentry["last_exit_profitable"]
            self.last_exit_direction = reentry["last_exit_direction"]
            self.reentry_count = reentry["reentry_count"]

    async def _enter_position(self, direction, price, sl_pts, tp_pts, contracts):
        """Enter position and save state."""
        # ... entry logic ...

        # Save position to database
        if self.db:
            self.db.save_position({
                "direction": self.position,
                "entry_price": self.entry_price,
                "stop_loss": self.stop_loss,
                "take_profit": self.take_profit,
                "trail_on": False,
                "hwm": self.hwm,
                "lwm": self.lwm,
                "contracts": self.contracts,
                "opened_at": datetime.now(),
            })

    async def _exit_position(self, reason, exit_price=None):
        """Exit position, record trade, and update database."""
        # ... exit logic and P&L calculation ...

        # Record trade in database
        if self.db:
            self.db.record_trade({
                "timestamp": datetime.now(),
                "direction": self.position,
                "entry_price": self.entry_price,
                "exit_price": exit_price,
                "exit_reason": reason,
                "pnl": pnl,
                "contracts": self.contracts,
                "atr": curr.get("atr"),
                "adx": curr.get("adx"),
            })

            # Clear position in database
            self.db.clear_position()

            # Save re-entry state
            self.db.save_reentry_state({
                "last_exit_bar": self.current_bar_idx,
                "last_exit_profitable": pnl > 0,
                "last_exit_direction": self.position,
                "reentry_count": self.reentry_count,
            })

        # ... reset position state ...

    async def stop(self):
        """Graceful shutdown."""
        # Close database connection
        if self.db:
            self.db.close()
```

---

## Testing State Persistence

```python
import pytest
from state_db import StateDB
from datetime import datetime, date

def test_account_state_persistence():
    """Test saving and loading account state."""
    db = StateDB(":memory:")  # In-memory for testing

    # Create mock Apex account
    from apex_account import ApexAccountState, APEX_ACCOUNTS

    account = ApexAccountState(
        mode="eval",
        account_size="50K",
        **APEX_ACCOUNTS["50K"]
    )

    account.equity = 2500.0
    account.high_water_mark = 2800.0
    account.dd_threshold = 300.0

    # Save
    db.save_account_state(account)

    # Load
    loaded = db.load_account_state()

    assert loaded["equity"] == 2500.0
    assert loaded["high_water_mark"] == 2800.0
    assert loaded["dd_threshold"] == 300.0

def test_position_persistence():
    """Test saving and loading position."""
    db = StateDB(":memory:")

    # Save position
    db.save_position({
        "direction": 1,
        "entry_price": 18500.0,
        "stop_loss": 18470.0,
        "take_profit": 18530.0,
        "trail_on": False,
        "hwm": 18500.0,
        "lwm": 18500.0,
        "contracts": 2,
        "opened_at": datetime.now(),
    })

    # Load
    loaded = db.load_position()

    assert loaded["direction"] == 1
    assert loaded["entry_price"] == 18500.0
    assert loaded["contracts"] == 2

    # Clear position
    db.clear_position()

    # Should return None
    loaded = db.load_position()
    assert loaded is None

def test_trade_history():
    """Test trade recording and retrieval."""
    db = StateDB(":memory:")

    # Record trades
    for i in range(5):
        db.record_trade({
            "timestamp": datetime(2026, 1, 10, 9, 30 + i),
            "direction": 1 if i % 2 == 0 else -1,
            "entry_price": 18500.0 + i,
            "exit_price": 18510.0 + i,
            "exit_reason": "TakeProfit",
            "pnl": 200.0,
            "contracts": 2,
            "atr": 10.0,
            "adx": 40.0,
        })

    # Get all trades
    trades = db.get_trades()
    assert len(trades) == 5

    # Get trades for specific date
    trades_today = db.get_trades(
        start_date=date(2026, 1, 10),
        end_date=date(2026, 1, 10)
    )
    assert len(trades_today) == 5
```

---

## Maintenance

### Backup Database

```python
# Daily backup
from datetime import datetime

backup_path = f"backups/bot_state_{datetime.now().strftime('%Y%m%d')}.db"
db.backup(backup_path)
```

### Clean Old Data

```python
# Delete trades older than 90 days
cursor = db.conn.cursor()
cutoff = (datetime.now() - timedelta(days=90)).date()
cursor.execute("DELETE FROM trades WHERE DATE(timestamp) < ?", (cutoff.isoformat(),))
db.conn.commit()
```

---

## See Also

- [APEX_INTEGRATION.md](APEX_INTEGRATION.md) - Apex account integration
- [CONFIG.md](../CONFIG.md) - Configuration reference
