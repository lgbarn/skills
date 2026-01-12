# Risk Manager Template (Apex Integrated)

Risk management with Apex Trader Funding account tracking (eval/PA modes).

---

## Overview

The risk manager now integrates:
- Apex account state (eval/PA modes)
- Trailing/static drawdown enforcement
- Dynamic position sizing (PA mode)
- Profit target tracking (eval mode)
- Daily max loss enforcement
- State persistence (SQLite)
- Trade logging and analytics

---

## risk_manager.py

```python
"""
Risk Manager with Apex Integration
Author: Luther Barnum

Combines daily risk limits with Apex Trader Funding account rules.
Supports eval mode (profit targets, trailing DD) and PA mode (risk-based sizing, static DD).
"""

import logging
from datetime import date, datetime
from typing import Optional

from config import Config
from apex_account import ApexAccountState
from state_db import StateDB

logger = logging.getLogger(__name__)


class RiskManager:
    """
    Risk manager with Apex account integration.

    Tracks:
    - Apex account equity and drawdown
    - Daily P&L and max loss
    - Position sizing (fixed vs risk-based)
    - State persistence
    """

    def __init__(self, config: Config):
        self.config = config

        # Apex account state
        self.apex_account = ApexAccountState.from_config(config)

        # Daily tracking
        self.current_date: Optional[date] = None
        self.daily_pnl: float = 0.0
        self.daily_stopped: bool = False
        self.daily_trades: int = 0
        self.daily_wins: int = 0
        self.daily_losses: int = 0

        # Session tracking
        self.total_pnl: float = 0.0
        self.total_trades: int = 0
        self.peak_pnl: float = 0.0
        self.max_drawdown: float = 0.0

        # State persistence
        self.db: Optional[StateDB] = None
        if config.persistence_enabled:
            self.db = StateDB(config.db_path)
            self._load_saved_state()

    def _load_saved_state(self):
        """Load saved state from database on startup."""
        if not self.db:
            return

        # Load Apex account state
        account_state = self.db.load_account_state()
        if account_state:
            self.apex_account.equity = account_state["equity"]
            self.apex_account.high_water_mark = account_state["high_water_mark"]
            self.apex_account.dd_threshold = account_state["dd_threshold"]
            self.apex_account.dd_locked = account_state["dd_locked"]
            self.apex_account.profit_target_hit = account_state["profit_target_hit"]

            stats = self.apex_account.get_stats()
            logger.info(
                f"Loaded saved state | "
                f"Equity: ${stats['current_balance']:.2f} | "
                f"DD Room: ${stats['drawdown_room']:.2f}"
            )

        # Load daily P&L for today
        today = date.today()
        daily_state = self.db.load_daily_pnl(today)
        if daily_state:
            self.daily_pnl = daily_state["pnl"]
            self.daily_trades = daily_state["trades"]
            self.daily_stopped = daily_state["stopped"]
            logger.info(f"Loaded today's P&L: ${self.daily_pnl:.2f} ({self.daily_trades} trades)")

    def check_new_day(self, bar_date: date):
        """
        Check if this is a new trading day and reset daily stats.

        Args:
            bar_date: Date of current bar
        """
        if bar_date != self.current_date:
            # Log previous day summary
            if self.current_date is not None:
                self._log_daily_summary()

            # Reset for new day
            self.current_date = bar_date
            self.daily_pnl = 0.0
            self.daily_stopped = False
            self.daily_trades = 0
            self.daily_wins = 0
            self.daily_losses = 0

            logger.info(f"=== New Trading Day: {bar_date} ===")

            # Log account status
            stats = self.apex_account.get_stats()
            logger.info(
                f"Account: {stats['mode'].upper()} {stats['account_size']} | "
                f"Equity: ${stats['current_balance']:.2f} | "
                f"DD Room: ${stats['drawdown_room']:.2f}"
            )

            if stats['mode'] == 'eval' and stats['profit_to_target'] is not None:
                logger.info(f"To Target: ${stats['profit_to_target']:.2f}")

    def record_trade(self, pnl: float, contracts: int, atr: float = None, adx: float = None):
        """
        Record a completed trade.

        Args:
            pnl: Trade P&L (after costs)
            contracts: Contracts traded
            atr: ATR at trade time (optional, for logging)
            adx: ADX at trade time (optional, for logging)

        Returns:
            None (check is_stopped() separately)
        """
        # Update daily stats
        self.daily_pnl += pnl
        self.daily_trades += 1

        if pnl > 0:
            self.daily_wins += 1
        else:
            self.daily_losses += 1

        # Update session stats
        self.total_pnl += pnl
        self.total_trades += 1

        # Update peak and drawdown
        if self.total_pnl > self.peak_pnl:
            self.peak_pnl = self.total_pnl
        current_dd = self.peak_pnl - self.total_pnl
        if current_dd > self.max_drawdown:
            self.max_drawdown = current_dd

        # Update Apex account
        self.apex_account.update_equity(pnl)

        # Check daily max loss
        if self.daily_pnl <= -self.config.daily_max_loss:
            self.daily_stopped = True
            logger.warning(f"⚠️ Daily max loss hit: ${self.daily_pnl:.2f}")

        # Check profit target (eval mode)
        if self.apex_account.check_profit_target():
            logger.info("🎉 PROFIT TARGET REACHED! Account eligible for PA conversion.")

        # Check drawdown breach
        if self.apex_account.check_drawdown_breach():
            logger.error("🚨 DRAWDOWN BREACHED! Stop trading immediately.")

        # Log trade summary
        stats = self.apex_account.get_stats()
        logger.info(
            f"Trade #{self.daily_trades}: ${pnl:+.2f} | "
            f"Daily: ${self.daily_pnl:.2f} | "
            f"Equity: ${stats['current_balance']:.2f} | "
            f"DD Room: ${stats['drawdown_room']:.2f}"
        )

        # Save state to database
        if self.db:
            self._save_state()

    def is_stopped(self) -> bool:
        """
        Check if trading should stop.

        Returns:
            True if daily max loss hit, profit target reached, or DD breached
        """
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
            Number of contracts to trade
        """
        return self.apex_account.get_position_size(
            atr=atr,
            sl_atr_mult=self.config.sl_atr_mult,
            point_value=self.config.point_value,
        )

    def get_stats(self) -> dict:
        """
        Get comprehensive risk statistics.

        Returns:
            Dict with all risk metrics
        """
        apex_stats = self.apex_account.get_stats()

        win_rate = (self.daily_wins / self.daily_trades * 100) if self.daily_trades > 0 else 0

        return {
            # Apex account
            **apex_stats,
            # Daily
            "daily_pnl": self.daily_pnl,
            "daily_max_loss": self.config.daily_max_loss,
            "daily_stopped": self.daily_stopped,
            "daily_trades": self.daily_trades,
            "daily_wins": self.daily_wins,
            "daily_losses": self.daily_losses,
            "daily_win_rate": win_rate,
            # Session
            "total_pnl": self.total_pnl,
            "total_trades": self.total_trades,
            "peak_pnl": self.peak_pnl,
            "max_drawdown": self.max_drawdown,
        }

    def _save_state(self):
        """Save state to database."""
        if not self.db:
            return

        # Save Apex account state
        self.db.save_account_state(self.apex_account)

        # Save daily P&L
        if self.current_date:
            self.db.save_daily_pnl(
                self.current_date,
                self.daily_pnl,
                self.daily_stopped,
                self.daily_trades
            )

    def _log_daily_summary(self):
        """Log end-of-day summary."""
        if self.daily_trades == 0:
            logger.info("=== End of Day: No trades ===")
            return

        win_rate = (self.daily_wins / self.daily_trades * 100)

        logger.info("=== End of Day Summary ===")
        logger.info(f"Date: {self.current_date}")
        logger.info(f"Daily P&L: ${self.daily_pnl:.2f}")
        logger.info(f"Trades: {self.daily_trades} ({self.daily_wins}W / {self.daily_losses}L)")
        logger.info(f"Win Rate: {win_rate:.1f}%")

        stats = self.apex_account.get_stats()
        logger.info(f"Account Equity: ${stats['current_balance']:.2f}")
        logger.info(f"DD Room: ${stats['drawdown_room']:.2f}")

        if stats['mode'] == 'eval' and stats['profit_to_target'] is not None:
            logger.info(f"To Target: ${stats['profit_to_target']:.2f}")

    def close(self):
        """Clean up resources."""
        if self.db:
            self.db.close()
```

---

## Usage in Bot

```python
# In bot_*.py

from risk_manager import RiskManager

class TradingBot:
    def __init__(self, config):
        self.config = config
        self.risk_manager = RiskManager(config)
        # ... other initialization ...

    async def on_bar(self, bar: dict):
        """Process each bar."""
        # ... bar processing ...

        # Check for new trading day
        bar_date = bar["timestamp"].date()
        self.risk_manager.check_new_day(bar_date)

        # Check if stopped
        if self.risk_manager.is_stopped():
            logger.debug("Trading stopped")
            return

        # ... indicator calculations ...

        # Process position
        if self.position != 0:
            await self._check_exits(curr, prev)
        else:
            await self._check_entries(curr, prev)

    async def _check_entries(self, curr, prev):
        """Check for entry signals."""
        # ... filters ...

        # Get position size (dynamic for PA, fixed for eval)
        atr = curr["atr"]
        contracts = self.risk_manager.get_position_size(atr)

        # Calculate exit levels
        sl_pts = atr * self.config.sl_atr_mult
        tp_pts = atr * self.config.tp_atr_mult

        # ... signal detection ...

        if long_sig:
            await self._enter_position(1, curr["close"], sl_pts, tp_pts, contracts)

    async def _exit_position(self, reason, exit_price=None):
        """Exit position and update risk manager."""
        # ... exit logic ...

        # Calculate P&L
        pnl = (exit_price - self.entry_price) * self.position
        pnl *= self.config.point_value * self.contracts
        pnl -= self.config.commission_rt * self.contracts

        # Update risk manager (updates Apex account, checks limits, persists state)
        self.risk_manager.record_trade(
            pnl=pnl,
            contracts=self.contracts,
            atr=curr.get("atr"),
            adx=curr.get("adx")
        )

        # ... reset position state ...

    async def stop(self):
        """Graceful shutdown."""
        logger.info("Shutting down bot...")

        # Exit open position
        if self.position != 0:
            await self._exit_position("Shutdown")

        # Close risk manager (closes database)
        self.risk_manager.close()

        logger.info("Bot stopped")
```

---

## Example Output

### Eval Mode (50K Account)

```
2026-01-10 09:30:00 [INFO] === New Trading Day: 2026-01-10 ===
2026-01-10 09:30:00 [INFO] Account: EVAL 50K | Equity: $50,000.00 | DD Room: $2,500.00
2026-01-10 09:30:00 [INFO] To Target: $3,000.00

2026-01-10 09:45:00 [INFO] ENTRY: LONG 5 contracts @ 18500.00 | SL: 18470.00 | TP: 18530.00
2026-01-10 10:12:00 [INFO] EXIT LONG: TakeProfit @ 18530.00 | P&L: $2,960.00 | Daily: $2,960.00
2026-01-10 10:12:00 [INFO] Trade #1: +$2,960.00 | Daily: $2,960.00 | Equity: $52,960.00 | DD Room: $4,460.00

2026-01-10 11:05:00 [INFO] ENTRY: LONG 5 contracts @ 18520.00 | SL: 18490.00 | TP: 18550.00
2026-01-10 11:23:00 [INFO] EXIT LONG: TakeProfit @ 18550.00 | P&L: $2,960.00 | Daily: $5,920.00
2026-01-10 11:23:00 [INFO] Trade #2: +$2,960.00 | Daily: $5,920.00 | Equity: $55,920.00 | DD Room: $7,420.00
2026-01-10 11:23:00 [INFO] 🎉 PROFIT TARGET REACHED! Account eligible for PA conversion.

2026-01-10 16:00:00 [INFO] === End of Day Summary ===
2026-01-10 16:00:00 [INFO] Date: 2026-01-10
2026-01-10 16:00:00 [INFO] Daily P&L: $5,920.00
2026-01-10 16:00:00 [INFO] Trades: 2 (2W / 0L)
2026-01-10 16:00:00 [INFO] Win Rate: 100.0%
2026-01-10 16:00:00 [INFO] Account Equity: $55,920.00
2026-01-10 16:00:00 [INFO] DD Room: $7,420.00
2026-01-10 16:00:00 [INFO] To Target: $-2,920.00 (REACHED!)
```

### PA Mode (50K Account)

```
2026-01-10 09:30:00 [INFO] === New Trading Day: 2026-01-10 ===
2026-01-10 09:30:00 [INFO] Account: PA 50K | Equity: $55,000.00 | DD Room: $7,500.00

2026-01-10 09:45:00 [INFO] Position size: 1 contracts (risk-based: $1100 / $600 = 1.83 → 1)
2026-01-10 09:45:00 [INFO] ENTRY: LONG 1 contract @ 18500.00 | SL: 18470.00 | TP: 18530.00
2026-01-10 10:12:00 [INFO] EXIT LONG: TakeProfit @ 18530.00 | P&L: $592.00 | Daily: $592.00
2026-01-10 10:12:00 [INFO] Trade #1: +$592.00 | Daily: $592.00 | Equity: $55,592.00 | DD Room: $8,092.00

[After more trading...]

2026-01-10 16:00:00 [INFO] === End of Day Summary ===
2026-01-10 16:00:00 [INFO] Date: 2026-01-10
2026-01-10 16:00:00 [INFO] Daily P&L: $1,180.00
2026-01-10 16:00:00 [INFO] Trades: 4 (3W / 1L)
2026-01-10 16:00:00 [INFO] Win Rate: 75.0%
2026-01-10 16:00:00 [INFO] Account Equity: $56,180.00
2026-01-10 16:00:00 [INFO] DD Room: $8,680.00
```

---

## See Also

- [APEX_INTEGRATION.md](APEX_INTEGRATION.md) - Apex account integration details
- [PERSISTENCE.md](PERSISTENCE.md) - State persistence implementation
- [EVAL_VS_PA.md](../docs/EVAL_VS_PA.md) - Eval vs PA mode guide
- [CONFIG.md](../CONFIG.md) - Configuration reference
