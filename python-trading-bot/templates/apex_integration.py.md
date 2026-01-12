# Apex Integration Template

Template for integrating Apex Trader Funding account logic into the risk manager.

---

## Overview

This template shows how to integrate the Apex account simulation from `Python/apex_account.py` into the bot's risk manager. Supports both eval and PA modes with proper drawdown tracking, position sizing, and state persistence.

---

## apex_account.py (Integrated into RiskManager)

```python
"""
Apex Account Integration
Author: Luther Barnum

Integrates Apex Trader Funding account logic into bot risk manager.
Supports eval mode (profit targets, trailing DD) and PA mode (risk-based sizing, static DD).

Based on Python/apex_account.py with modifications for live trading.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal


# Apex account presets (from apex_account.py)
APEX_ACCOUNTS = {
    "25K": {
        "balance": 25000,
        "profit_target": 1500,
        "trailing_dd": 1500,
        "max_contracts": 4,
        "initial_contracts": 2,
    },
    "50K": {
        "balance": 50000,
        "profit_target": 3000,
        "trailing_dd": 2500,
        "max_contracts": 10,
        "initial_contracts": 5,
    },
    "75K": {
        "balance": 75000,
        "profit_target": 4000,
        "trailing_dd": 2750,
        "max_contracts": 12,
        "initial_contracts": 6,
    },
    "100K": {
        "balance": 100000,
        "profit_target": 6000,
        "trailing_dd": 3000,
        "max_contracts": 14,
        "initial_contracts": 7,
    },
    "150K": {
        "balance": 150000,
        "profit_target": 8000,
        "trailing_dd": 5000,
        "max_contracts": 17,
        "initial_contracts": 8,
    },
    "250K": {
        "balance": 250000,
        "profit_target": 12500,
        "trailing_dd": 6500,
        "max_contracts": 27,
        "initial_contracts": 13,
    },
    "300K": {
        "balance": 300000,
        "profit_target": 15000,
        "trailing_dd": 7500,
        "max_contracts": 35,
        "initial_contracts": 17,
    },
}


@dataclass
class ApexAccountState:
    """
    Apex Trader Funding account state.

    Tracks equity, drawdown, and enforces eval/PA rules.
    """

    # Configuration
    mode: Literal["eval", "pa"]
    account_size: str
    balance: float
    profit_target: float  # 0 for PA mode
    trailing_dd: float  # Static DD for PA mode
    max_contracts: int
    initial_contracts: int

    # Dynamic state
    equity: float = 0.0  # Current equity (P&L from starting balance)
    high_water_mark: float = 0.0  # Highest equity reached
    dd_threshold: float = 0.0  # Current drawdown threshold
    dd_locked: bool = False  # Whether DD has stopped trailing (eval only)
    profit_target_hit: bool = False  # Whether profit target reached (eval only)

    # PA-specific
    risk_pct: float = 0.02  # Risk % per trade (PA mode only)

    def __post_init__(self):
        """Initialize DD threshold."""
        if self.mode == "eval":
            # Trailing DD starts at negative balance
            self.dd_threshold = -self.trailing_dd
        else:  # PA mode
            # Static DD
            self.dd_threshold = -self.trailing_dd

    @classmethod
    def from_config(cls, config):
        """
        Create ApexAccountState from bot config.

        Args:
            config: Bot Config object with account_mode, account_size, risk_pct

        Returns:
            ApexAccountState instance
        """
        preset = APEX_ACCOUNTS.get(config.account_size)
        if not preset:
            raise ValueError(f"Unknown account size: {config.account_size}")

        return cls(
            mode=config.account_mode,
            account_size=config.account_size,
            balance=preset["balance"],
            profit_target=preset["profit_target"] if config.account_mode == "eval" else 0,
            trailing_dd=preset["trailing_dd"],
            max_contracts=preset["max_contracts"],
            initial_contracts=preset["initial_contracts"],
            risk_pct=getattr(config, "risk_pct", 0.02),
        )

    def update_equity(self, pnl: float):
        """
        Update equity after trade.

        Args:
            pnl: P&L from trade (can be negative)
        """
        self.equity += pnl

        # Update high water mark
        if self.equity > self.high_water_mark:
            self.high_water_mark = self.equity

        # Update DD threshold based on mode
        if self.mode == "eval":
            self._update_eval_dd()
        else:
            # PA mode: static DD, no updates
            pass

    def _update_eval_dd(self):
        """Update trailing drawdown for eval mode."""
        if self.dd_locked:
            return  # DD already locked

        # Check if we should lock DD
        if self.equity >= self.profit_target:
            # Lock DD at starting balance (0 equity)
            self.dd_threshold = 0.0
            self.dd_locked = True
            return

        # Trail the DD threshold
        new_threshold = self.high_water_mark - self.trailing_dd
        self.dd_threshold = max(self.dd_threshold, new_threshold)

    def check_profit_target(self) -> bool:
        """
        Check if profit target hit (eval mode only).

        Returns:
            True if target reached
        """
        if self.mode != "eval":
            return False

        if self.equity >= self.profit_target:
            self.profit_target_hit = True
            return True

        return False

    def check_drawdown_breach(self) -> bool:
        """
        Check if drawdown breached.

        Returns:
            True if equity below DD threshold
        """
        return self.equity < self.dd_threshold

    def is_stopped(self) -> bool:
        """
        Check if trading should stop.

        Returns:
            True if profit target hit or DD breached
        """
        return self.profit_target_hit or self.check_drawdown_breach()

    def get_position_size(self, atr: float, sl_atr_mult: float, point_value: float) -> int:
        """
        Calculate position size based on mode.

        Args:
            atr: Current ATR value
            sl_atr_mult: Stop loss ATR multiplier
            point_value: Point value (e.g., $20 for NQ)

        Returns:
            Number of contracts to trade
        """
        if self.mode == "eval":
            # Fixed contracts in eval mode
            return self.initial_contracts

        # PA mode: risk-based sizing
        current_balance = self.balance + self.equity
        risk_per_trade = current_balance * self.risk_pct
        sl_distance = atr * sl_atr_mult

        contracts = int(risk_per_trade / (sl_distance * point_value))

        # Cap at max for account size
        contracts = min(contracts, self.max_contracts)

        # Floor at 1
        contracts = max(1, contracts)

        return contracts

    def get_stats(self) -> dict:
        """Get current account statistics."""
        return {
            "mode": self.mode,
            "account_size": self.account_size,
            "balance": self.balance,
            "equity": self.equity,
            "current_balance": self.balance + self.equity,
            "high_water_mark": self.high_water_mark,
            "dd_threshold": self.dd_threshold,
            "dd_locked": self.dd_locked,
            "profit_target": self.profit_target,
            "profit_target_hit": self.profit_target_hit,
            "drawdown_room": self.equity - self.dd_threshold,
            "profit_to_target": self.profit_target - self.equity if self.mode == "eval" else None,
        }
```

---

## Integration into RiskManager

Modify `risk_manager.py` to include Apex account tracking:

```python
"""
Risk Manager with Apex Account Integration
Author: Luther Barnum
"""

import logging
from datetime import date
from apex_account import ApexAccountState  # Import from above

logger = logging.getLogger(__name__)


class RiskManager:
    """Risk manager with Apex account tracking."""

    def __init__(self, config):
        self.config = config

        # Apex account state
        self.apex_account = ApexAccountState.from_config(config)

        # Daily tracking
        self.current_date = None
        self.daily_pnl = 0.0
        self.daily_stopped = False

        # State persistence (covered in PERSISTENCE.md)
        self.db = StateDB(config.db_path) if config.persistence_enabled else None

        # Load saved state if exists
        if self.db:
            self._load_state()

    def check_new_day(self, bar_date: date):
        """Reset daily stats on new trading day."""
        if bar_date != self.current_date:
            logger.info(f"New trading day: {bar_date}")
            self.current_date = bar_date
            self.daily_pnl = 0.0
            self.daily_stopped = False

    def record_trade(self, pnl: float, contracts: int):
        """
        Record trade and update account state.

        Args:
            pnl: Trade P&L
            contracts: Contracts traded
        """
        # Update daily P&L
        self.daily_pnl += pnl

        # Update Apex account equity
        self.apex_account.update_equity(pnl)

        # Check daily max loss
        if self.daily_pnl <= -self.config.daily_max_loss:
            self.daily_stopped = True
            logger.warning(f"Daily max loss hit: ${self.daily_pnl:.2f}")

        # Check profit target (eval mode)
        if self.apex_account.check_profit_target():
            logger.info("🎉 PROFIT TARGET REACHED! Account eligible for PA conversion.")

        # Check drawdown breach
        if self.apex_account.check_drawdown_breach():
            logger.error("⚠️ DRAWDOWN BREACHED! Stop trading immediately.")

        # Save state
        if self.db:
            self._save_state()

        # Log summary
        stats = self.apex_account.get_stats()
        logger.info(
            f"Trade: ${pnl:.2f} | "
            f"Daily: ${self.daily_pnl:.2f} | "
            f"Equity: ${stats['current_balance']:.2f} | "
            f"DD Room: ${stats['drawdown_room']:.2f}"
        )

    def is_stopped(self) -> bool:
        """Check if trading should stop."""
        # Daily max loss
        if self.daily_stopped:
            return True

        # Apex account rules (profit target or DD breach)
        if self.apex_account.is_stopped():
            return True

        return False

    def get_position_size(self, atr: float) -> int:
        """
        Calculate position size based on account mode.

        Args:
            atr: Current ATR value

        Returns:
            Number of contracts
        """
        return self.apex_account.get_position_size(
            atr=atr,
            sl_atr_mult=self.config.sl_atr_mult,
            point_value=self.config.point_value,
        )

    def get_stats(self) -> dict:
        """Get comprehensive risk statistics."""
        apex_stats = self.apex_account.get_stats()

        return {
            **apex_stats,
            "daily_pnl": self.daily_pnl,
            "daily_max_loss": self.config.daily_max_loss,
            "daily_stopped": self.daily_stopped,
        }

    def _save_state(self):
        """Save state to database."""
        if not self.db:
            return

        self.db.save_account_state(self.apex_account)
        self.db.save_daily_pnl(self.current_date, self.daily_pnl, self.daily_stopped)

    def _load_state(self):
        """Load state from database."""
        if not self.db:
            return

        account_state = self.db.load_account_state()
        if account_state:
            self.apex_account.equity = account_state["equity"]
            self.apex_account.high_water_mark = account_state["high_water_mark"]
            self.apex_account.dd_threshold = account_state["dd_threshold"]
            self.apex_account.dd_locked = account_state["dd_locked"]
            self.apex_account.profit_target_hit = account_state["profit_target_hit"]
            logger.info("Loaded saved account state from database")
```

---

## Usage in Bot

```python
# In bot_*.py

class TradingBot:
    def __init__(self, config):
        self.config = config
        self.risk_manager = RiskManager(config)
        # ...

    async def _check_entries(self, curr, prev):
        """Check for entry signals."""

        # Check if stopped
        if self.risk_manager.is_stopped():
            logger.debug("Trading stopped (DD breach or target hit)")
            return

        # ... session filter, volume filter, etc ...

        # Get position size (dynamic for PA, fixed for eval)
        atr = curr["atr"]
        contracts = self.risk_manager.get_position_size(atr)

        # Calculate exit levels
        sl_pts = atr * self.config.sl_atr_mult
        tp_pts = atr * self.config.tp_atr_mult

        # ... check signal ...

        if long_sig:
            await self._enter_position(1, curr["close"], sl_pts, tp_pts, contracts)

    async def _enter_position(self, direction, price, sl_pts, tp_pts, contracts):
        """Enter position with calculated contracts."""
        # ... slippage, entry logic ...

        logger.info(
            f"ENTRY: {direction_str} {contracts} contracts @ {entry:.2f} | "
            f"SL: {self.stop_loss:.2f} | TP: {self.take_profit:.2f}"
        )

        # ... send order via TradersPost ...

    async def _exit_position(self, reason, exit_price=None):
        """Exit position and update risk manager."""
        # ... exit logic ...

        # Calculate P&L
        pnl = (exit_price - self.entry_price) * self.position
        pnl *= self.config.point_value * self.contracts
        pnl -= self.config.commission_rt * self.contracts

        # Update risk manager (updates Apex account)
        self.risk_manager.record_trade(pnl, self.contracts)

        # ... reset position state ...
```

---

## Configuration Example

```python
# config.py

@dataclass
class Config:
    # Apex Account
    account_mode: str = "eval"  # or "pa"
    account_size: str = "50K"
    risk_pct: float = 0.02  # PA mode only

    # ... rest of config ...

    def __post_init__(self):
        # Load from .env
        self.account_mode = os.getenv("ACCOUNT_MODE", self.account_mode)
        self.account_size = os.getenv("ACCOUNT_SIZE", self.account_size)
        self.risk_pct = float(os.getenv("RISK_PCT", str(self.risk_pct)))
```

```bash
# .env

# Apex Account Configuration
ACCOUNT_MODE=eval
ACCOUNT_SIZE=50K

# PA mode only
RISK_PCT=0.02
```

---

## Testing

```python
def test_eval_mode():
    """Test eval mode behavior."""
    config = Config()
    config.account_mode = "eval"
    config.account_size = "50K"

    risk_mgr = RiskManager(config)

    # Should start with fixed contracts
    contracts = risk_mgr.get_position_size(atr=10.0)
    assert contracts == 5  # initial_contracts for 50K

    # Record profitable trades
    risk_mgr.record_trade(500, contracts)
    risk_mgr.record_trade(800, contracts)
    risk_mgr.record_trade(1200, contracts)  # Total: $2500

    # Not at target yet
    assert not risk_mgr.apex_account.profit_target_hit

    # Hit profit target
    risk_mgr.record_trade(600, contracts)  # Total: $3100 > $3000 target

    # Should be stopped
    assert risk_mgr.apex_account.profit_target_hit
    assert risk_mgr.is_stopped()


def test_pa_mode():
    """Test PA mode behavior."""
    config = Config()
    config.account_mode = "pa"
    config.account_size = "50K"
    config.risk_pct = 0.02
    config.sl_atr_mult = 3.0
    config.point_value = 20.0

    risk_mgr = RiskManager(config)

    # Dynamic sizing based on equity
    atr = 10.0
    contracts = risk_mgr.get_position_size(atr)

    # Initial: $50K * 2% = $1000 risk / (10 ATR * 3.0 * $20) = 1.67 → 1 contract
    assert contracts == 1

    # After profit
    risk_mgr.record_trade(5000, 1)  # +$5K profit

    # New: $55K * 2% = $1100 risk / (10 ATR * 3.0 * $20) = 1.83 → 1 contract
    contracts = risk_mgr.get_position_size(atr)
    assert contracts == 1  # Still 1, need more equity for 2

    # More profit
    risk_mgr.record_trade(10000, 1)  # +$10K more (total +$15K)

    # New: $65K * 2% = $1300 risk / (10 ATR * 3.0 * $20) = 2.17 → 2 contracts
    contracts = risk_mgr.get_position_size(atr)
    assert contracts == 2
```

---

## See Also

- [EVAL_VS_PA.md](../docs/EVAL_VS_PA.md) - Eval vs PA mode guide
- [PERSISTENCE.md](PERSISTENCE.md) - State persistence template
- [CONFIG.md](../CONFIG.md) - Configuration reference
