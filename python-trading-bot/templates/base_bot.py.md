# Base Bot Template

Main entry point for the trading bot with production features. Replace `{{PLACEHOLDER}}` values during generation.

---

## bot_{{SIGNAL}}.py

```python
#!/usr/bin/env python3
"""
{{SIGNAL_NAME}} Trading Bot
Author: Luther Barnum
Generated: {{GENERATED_DATE}}

Live trading bot for NQ futures using:
- Databento API for real-time 2-minute bar data
- TradersPost webhooks for order execution
- Apex Trader Funding account simulation (eval/PA modes)
- State persistence (SQLite) for mid-day restarts
- News calendar integration for blackout periods
- Email/SMS alerting for critical events

Signal: {{SIGNAL}} ({{SIGNAL_DESCRIPTION}})
Profit Factor: {{PROFIT_FACTOR}} | Win Rate: {{WIN_RATE}}
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime, time
from typing import Optional

from config import Config
from indicators import Indicators
from risk_manager import RiskManager
from news_calendar import NewsCalendar
from alert_manager import AlertManager
from traderspost_client import TradersPostClient
from databento_provider import DatabentoProvider

# =============================================================================
# LOGGING SETUP
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"bot_{{SIGNAL}}_{datetime.now().strftime('%Y%m%d')}.log"),
    ],
)
logger = logging.getLogger(__name__)


# =============================================================================
# BOT CLASS
# =============================================================================


class {{SIGNAL_CLASS}}Bot:
    """{{SIGNAL_NAME}} trading bot with full position management and production features."""

    def __init__(self, config: Config):
        self.config = config
        self.indicators = Indicators(config)
        self.risk_manager = RiskManager(config)
        self.news_calendar = NewsCalendar(config) if config.news_filter_enabled else None
        self.alert_manager = AlertManager(config) if (config.alert_email_enabled or config.alert_pushover_enabled) else None
        self.traderspost = TradersPostClient(config.traderspost_webhook_url)
        self.data_provider: Optional[DatabentoProvider] = None

        # Position state
        self.position = 0  # 0=flat, 1=long, -1=short
        self.contracts = 0  # Number of contracts in position
        self.entry_price = 0.0
        self.stop_loss = 0.0
        self.take_profit = 0.0
        self.trail_on = False
        self.hwm = 0.0  # High water mark (for longs)
        self.lwm = 0.0  # Low water mark (for shorts)

        # Re-entry state
        self.last_exit_bar = -999
        self.last_exit_profitable = False
        self.last_exit_direction = 0
        self.reentry_count = 0

        # Bar data
        self.bars: list[dict] = []
        self.current_bar_idx = 0

        # Tracking
        self.current_losing_streak = 0
        self.losing_streak_pnl = 0.0

        # Shutdown flag
        self.running = True

    async def start(self):
        """Start the bot and connect to data feed."""
        logger.info(f"Starting {{SIGNAL_NAME}} Bot")
        logger.info(f"Ticker: {self.config.ticker}")
        logger.info(f"Paper Mode: {self.config.paper_mode}")
        logger.info(f"Account Mode: {self.config.account_mode.upper()}")
        logger.info(f"Account Size: {self.config.account_size}")

        # Get account stats
        stats = self.risk_manager.get_stats()
        logger.info(f"Starting Balance: ${stats['balance']:.2f}")
        logger.info(f"Current Equity: ${stats['current_balance']:.2f}")
        logger.info(f"DD Room: ${stats['drawdown_room']:.2f}")

        if self.config.account_mode == "eval":
            logger.info(f"Profit Target: ${stats['profit_target']:.2f}")
            logger.info(f"Initial Contracts: {stats['initial_contracts']}")
        else:
            logger.info(f"Risk Per Trade: {self.config.risk_pct * 100:.1f}%")
            logger.info(f"Max Contracts: {stats['max_contracts']}")

        logger.info(f"Daily Max Loss: ${self.config.daily_max_loss}")
        logger.info(f"News Filter: {self.config.news_filter_enabled}")
        logger.info(f"Alerting: Email={self.config.alert_email_enabled}, SMS={self.config.alert_pushover_enabled}")

        # Connect to news calendar
        if self.news_calendar:
            await self.news_calendar.connect()
            await self.news_calendar.fetch_today_events()

        # Connect to alert manager
        if self.alert_manager:
            await self.alert_manager.connect()
            await self.alert_manager.alert_bot_started()

        # Connect to data provider
        self.data_provider = DatabentoProvider(self.config)
        await self.data_provider.connect()

        # Subscribe to market data
        await self.data_provider.subscribe_bars(
            symbol=self.config.ticker,
            bar_size=2,  # 2-minute bars
            callback=self.on_bar,
        )

        # Keep running until shutdown
        while self.running:
            await asyncio.sleep(1)

    async def stop(self):
        """Graceful shutdown."""
        logger.info("Shutting down bot...")
        self.running = False

        # Exit any open position
        if self.position != 0:
            logger.info("Exiting open position on shutdown")
            await self._exit_position("Shutdown")

        # Close connections
        if self.data_provider:
            await self.data_provider.disconnect()

        # Close risk manager (saves state to database)
        self.risk_manager.close()

        # Send shutdown alert
        if self.alert_manager:
            await self.alert_manager.alert_bot_stopped("Manual shutdown")
            await self.alert_manager.disconnect()

        # Close news calendar
        if self.news_calendar:
            await self.news_calendar.disconnect()

        logger.info("Bot stopped")

    async def on_bar(self, bar: dict):
        """
        Called when a new bar completes.

        Args:
            bar: Dict with open, high, low, close, volume, timestamp
        """
        self.bars.append(bar)
        self.current_bar_idx = len(self.bars) - 1

        # Need enough bars for indicators
        warmup = max({{WARMUP_BARS}}, self.config.adx_period + 10)
        if len(self.bars) < warmup:
            logger.debug(f"Warmup: {len(self.bars)}/{warmup} bars")
            return

        # Calculate indicators
        self.indicators.update(self.bars)

        # Get current and previous bar with indicators
        curr = self.indicators.get_bar(self.current_bar_idx)
        prev = self.indicators.get_bar(self.current_bar_idx - 1)

        # Check for new trading day
        bar_date = bar["timestamp"].date()
        self.risk_manager.check_new_day(bar_date)

        # Fetch news events at start of day
        if self.news_calendar and bar["timestamp"].hour == 9 and bar["timestamp"].minute == 30:
            await self.news_calendar.fetch_today_events()

            # Log today's events
            events = self.news_calendar.events
            if events:
                logger.warning(f"⚠️ {len(events)} high-impact events today:")
                for event in events:
                    logger.warning(f"   {event}")

        # Check news blackout period
        if self.news_calendar and self.news_calendar.is_blackout_period(bar["timestamp"]):
            # Exit position if configured
            if self.position != 0 and self.config.news_exit_on_blackout:
                logger.warning("Exiting position: news blackout starting")
                await self._exit_position("NewsBlackout", curr["close"])
            else:
                logger.debug("Skipping bar (news blackout)")
            return

        # Skip if stopped (daily max loss, profit target, or DD breach)
        if self.risk_manager.is_stopped():
            logger.debug("Trading stopped")
            return

        # Alert on drawdown warning
        if self.alert_manager:
            stats = self.risk_manager.get_stats()
            equity = stats["equity"]
            dd_threshold = stats["dd_threshold"]
            dd_room = stats["drawdown_room"]

            if dd_room > 0:
                dd_pct_used = 1.0 - (dd_room / abs(dd_threshold))
                if dd_pct_used >= self.config.alert_drawdown_pct:
                    await self.alert_manager.alert_drawdown_warning(equity, dd_threshold)

        # Alert on daily loss warning
        if self.alert_manager:
            daily_pnl = self.risk_manager.daily_pnl
            max_loss = self.config.daily_max_loss

            if daily_pnl < 0:
                loss_pct = abs(daily_pnl) / max_loss
                if loss_pct >= self.config.alert_daily_loss_pct:
                    await self.alert_manager.alert_daily_loss_warning(daily_pnl, max_loss)

        # Process position
        if self.position != 0:
            await self._check_exits(curr, prev)
        else:
            await self._check_entries(curr, prev)

    async def _check_entries(self, curr: dict, prev: dict):
        """Check for entry signals."""
        # Session filter
        if self.config.session_filter:
            if curr["hour"] not in self.config.allowed_hours:
                return

        # Volume filter
        if self.config.volume_filter:
            if curr["volume"] < curr["vol_ma"]:
                return

        # Get position size (dynamic for PA, fixed for eval)
        atr = curr["atr"]
        contracts = self.risk_manager.get_position_size(atr)

        # Calculate ATR-based levels
        sl_pts = atr * self.config.sl_atr_mult
        tp_pts = atr * self.config.tp_atr_mult

        # Check for signals
        long_sig, short_sig, is_reentry = self._check_signal(curr, prev)

        # ADX filter (skip for re-entries)
        if not is_reentry:
            if long_sig and not self._check_adx(curr, prev, 1):
                long_sig = False
            if short_sig and not self._check_adx(curr, prev, -1):
                short_sig = False

        # Execute entry
        if long_sig:
            await self._enter_position(1, curr["close"], sl_pts, tp_pts, contracts, is_reentry)
        elif short_sig:
            await self._enter_position(-1, curr["close"], sl_pts, tp_pts, contracts, is_reentry)

    def _check_signal(self, curr: dict, prev: dict) -> tuple[bool, bool, bool]:
        """
        Check for entry signal.

        Returns:
            (long_signal, short_signal, is_reentry)
        """
        long_sig = False
        short_sig = False
        is_reentry = False

        {{SIGNAL_DETECTION_CODE}}

        # Re-entry logic
        if self.config.reentry_enabled and self.last_exit_profitable:
            bars_since_exit = self.current_bar_idx - self.last_exit_bar
            if bars_since_exit >= self.config.reentry_bars_wait:
                if self.reentry_count < self.config.max_reentries:
                    if curr["adx"] > self.config.reentry_adx_min:
                        {{REENTRY_LOGIC_CODE}}

        # Reset reentry count on fresh signal
        if not is_reentry and (long_sig or short_sig):
            self.reentry_count = 0

        return long_sig, short_sig, is_reentry

    def _check_adx(self, curr: dict, prev: dict, direction: int) -> bool:
        """Check ADX condition for entry."""
        if not self.config.adx_enabled:
            return True

        if curr["adx"] <= self.config.adx_threshold:
            return False

        mode = self.config.adx_mode

        if mode == "traditional":
            return True

        elif mode == "di_aligned":
            if direction == 1:
                return curr["plus_di"] > curr["minus_di"]
            else:
                return curr["minus_di"] > curr["plus_di"]

        elif mode == "di_rising":
            if direction == 1:
                return curr["plus_di"] > prev["plus_di"]
            else:
                return curr["minus_di"] > prev["minus_di"]

        elif mode == "adx_rising":
            return curr["adx"] > prev["adx"]

        elif mode == "combined":
            adx_rising = curr["adx"] > prev["adx"]
            if direction == 1:
                di_aligned = curr["plus_di"] > curr["minus_di"]
            else:
                di_aligned = curr["minus_di"] > curr["plus_di"]
            return di_aligned and adx_rising

        return True

    async def _enter_position(
        self,
        direction: int,
        price: float,
        sl_pts: float,
        tp_pts: float,
        contracts: int,
        is_reentry: bool,
    ):
        """Enter a position."""
        # Apply slippage
        slippage = self.config.slippage_ticks * self.config.tick_size
        if direction == 1:
            entry = price + slippage
            self.stop_loss = entry - sl_pts
            self.take_profit = entry + tp_pts
        else:
            entry = price - slippage
            self.stop_loss = entry + sl_pts
            self.take_profit = entry - tp_pts

        self.position = direction
        self.contracts = contracts
        self.entry_price = entry
        self.hwm = entry
        self.lwm = entry
        self.trail_on = False

        if is_reentry:
            self.reentry_count += 1

        action = "buy" if direction == 1 else "sell"
        entry_type = "RE-ENTRY" if is_reentry else "ENTRY"

        logger.info(
            f"{entry_type}: {action.upper()} {contracts} contracts @ {entry:.2f} | "
            f"SL: {self.stop_loss:.2f} | TP: {self.take_profit:.2f}"
        )

        # Log position size calculation for PA mode
        if self.config.account_mode == "pa":
            stats = self.risk_manager.get_stats()
            equity = stats["current_balance"]
            risk_per_trade = equity * self.config.risk_pct
            logger.info(f"Position size: {contracts} contracts (risk-based: ${risk_per_trade:.0f} / ${sl_pts * self.config.point_value:.0f} = {risk_per_trade / (sl_pts * self.config.point_value):.2f} → {contracts})")

        # Send order via TradersPost
        if not self.config.paper_mode:
            await self.traderspost.send_signal(
                ticker=self.config.ticker,
                action=action,
                quantity=contracts,
                stop_loss=self.stop_loss,
                take_profit=self.take_profit,
            )

    async def _check_exits(self, curr: dict, prev: dict):
        """Check exit conditions for open position."""
        high = curr["high"]
        low = curr["low"]
        close = curr["close"]

        # Update HWM/LWM
        if self.position == 1:
            self.hwm = max(self.hwm, high)
        else:
            self.lwm = min(self.lwm, low)

        # Check trailing stop activation
        atr = curr["atr"]
        trail_trigger = atr * self.config.trail_trigger_atr
        trail_distance = atr * self.config.trail_distance_atr

        if self.config.trail_enabled and not self.trail_on:
            if self.position == 1:
                profit = high - self.entry_price
                if profit >= trail_trigger:
                    self.trail_on = True
                    self.stop_loss = self.hwm - trail_distance
                    logger.info(f"Trailing stop activated @ {self.stop_loss:.2f}")
            else:
                profit = self.entry_price - low
                if profit >= trail_trigger:
                    self.trail_on = True
                    self.stop_loss = self.lwm + trail_distance
                    logger.info(f"Trailing stop activated @ {self.stop_loss:.2f}")

        # Update trailing stop
        if self.trail_on:
            if self.position == 1:
                new_stop = self.hwm - trail_distance
                if new_stop > self.stop_loss:
                    self.stop_loss = new_stop
            else:
                new_stop = self.lwm + trail_distance
                if new_stop < self.stop_loss:
                    self.stop_loss = new_stop

        # Check exit conditions (priority order: Trail, SL, TP)
        exit_price = None
        exit_reason = None

        if self.position == 1:  # Long
            if self.trail_on and low <= self.stop_loss:
                exit_price = self.stop_loss
                exit_reason = "TrailingStop"
            elif low <= self.stop_loss:
                exit_price = self.stop_loss
                exit_reason = "StopLoss"
            elif high >= self.take_profit:
                exit_price = self.take_profit
                exit_reason = "TakeProfit"
        else:  # Short
            if self.trail_on and high >= self.stop_loss:
                exit_price = self.stop_loss
                exit_reason = "TrailingStop"
            elif high >= self.stop_loss:
                exit_price = self.stop_loss
                exit_reason = "StopLoss"
            elif low <= self.take_profit:
                exit_price = self.take_profit
                exit_reason = "TakeProfit"

        if exit_price is not None:
            await self._exit_position(exit_reason, exit_price)

    async def _exit_position(self, reason: str, exit_price: float = None):
        """Exit the current position."""
        if exit_price is None:
            exit_price = self.bars[-1]["close"]

        # Apply slippage
        slippage = self.config.slippage_ticks * self.config.tick_size
        if self.position == 1:
            exit_price -= slippage
        else:
            exit_price += slippage

        # Calculate P&L
        pnl = (exit_price - self.entry_price) * self.position
        pnl *= self.config.point_value * self.contracts
        pnl -= self.config.commission_rt * self.contracts

        # Track for re-entry
        self.last_exit_bar = self.current_bar_idx
        self.last_exit_profitable = pnl > 0
        self.last_exit_direction = self.position

        # Track losing streaks
        if pnl < 0:
            self.current_losing_streak += 1
            self.losing_streak_pnl += pnl

            # Alert on losing streak
            if self.alert_manager and self.current_losing_streak >= self.config.alert_losing_streak:
                await self.alert_manager.alert_losing_streak(
                    self.current_losing_streak,
                    self.losing_streak_pnl
                )
        else:
            # Reset on winning trade
            self.current_losing_streak = 0
            self.losing_streak_pnl = 0.0

        direction_str = "LONG" if self.position == 1 else "SHORT"
        logger.info(
            f"EXIT {direction_str}: {reason} @ {exit_price:.2f} | "
            f"P&L: ${pnl:.2f} | Daily: ${self.risk_manager.daily_pnl:.2f}"
        )

        # Update risk manager (updates Apex account, checks limits, persists state)
        curr = self.indicators.get_bar(self.current_bar_idx)
        self.risk_manager.record_trade(
            pnl=pnl,
            contracts=self.contracts,
            atr=curr.get("atr"),
            adx=curr.get("adx")
        )

        # Check if daily max loss hit
        if self.risk_manager.daily_stopped:
            if self.alert_manager:
                await self.alert_manager.alert_daily_loss_hit(
                    self.risk_manager.daily_pnl,
                    self.config.daily_max_loss
                )

        # Check if profit target reached
        if self.risk_manager.apex_account.profit_target_hit:
            if self.alert_manager:
                await self.alert_manager.alert_profit_target_reached(
                    self.risk_manager.apex_account.equity,
                    self.risk_manager.apex_account.profit_target
                )

        # Check if drawdown breached
        if self.risk_manager.apex_account.check_drawdown_breach():
            if self.alert_manager:
                await self.alert_manager.alert_drawdown_breach(
                    self.risk_manager.apex_account.equity,
                    self.risk_manager.apex_account.dd_threshold
                )

        # Send exit order via TradersPost
        if not self.config.paper_mode:
            await self.traderspost.send_signal(
                ticker=self.config.ticker,
                action="exit",
            )

        # Reset position state
        self.position = 0
        self.contracts = 0
        self.entry_price = 0
        self.stop_loss = 0
        self.take_profit = 0
        self.trail_on = False
        self.hwm = 0
        self.lwm = 0


# =============================================================================
# MAIN
# =============================================================================


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="{{SIGNAL_NAME}} Trading Bot")
    parser.add_argument("--paper", action="store_true", help="Paper trading mode")
    parser.add_argument("--live", action="store_true", help="Live trading mode")
    args = parser.parse_args()

    # Load config
    config = Config()

    # Override paper mode from command line
    if args.paper:
        config.paper_mode = True
    elif args.live:
        config.paper_mode = False

    # Safety check for live mode
    if not config.paper_mode:
        logger.warning("=" * 60)
        logger.warning("LIVE TRADING MODE - REAL MONEY AT RISK")
        logger.warning("=" * 60)
        confirm = input("Type 'CONFIRM' to proceed with live trading: ")
        if confirm != "CONFIRM":
            logger.info("Cancelled. Use --paper for paper trading.")
            return

    # Create bot
    bot = {{SIGNAL_CLASS}}Bot(config)

    # Setup signal handlers for graceful shutdown
    loop = asyncio.get_event_loop()

    def shutdown_handler():
        logger.info("Received shutdown signal")
        asyncio.create_task(bot.stop())

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown_handler)

    # Run bot
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        await bot.stop()
    except Exception as e:
        logger.error(f"Bot error: {e}")

        # Send alert on crash
        if bot.alert_manager:
            await bot.alert_manager.send_alert(
                title="Bot Crashed",
                message=f"Error: {str(e)}\nBot will attempt to restart.",
                priority="critical",
                force=True
            )

        await bot.stop()
        raise


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Placeholder Reference

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{SIGNAL}}` | Signal name (lowercase) | `keltner` |
| `{{SIGNAL_NAME}}` | Signal display name | `Keltner Channel` |
| `{{SIGNAL_CLASS}}` | Signal class name | `Keltner` |
| `{{SIGNAL_DESCRIPTION}}` | Brief description | `Channel breakout` |
| `{{PROFIT_FACTOR}}` | Backtest profit factor | `10.04` |
| `{{WIN_RATE}}` | Backtest win rate | `87.8%` |
| `{{GENERATED_DATE}}` | Generation timestamp | `2026-01-04` |
| `{{WARMUP_BARS}}` | Minimum bars for indicators | `720` |
| `{{SIGNAL_DETECTION_CODE}}` | Signal-specific entry logic | See signals/*.md |
| `{{REENTRY_LOGIC_CODE}}` | Signal-specific re-entry logic | See signals/*.md |

---

## Key Features Integrated

### 1. Data Provider Abstraction
- Uses `DatabentoProvider` instead of hardcoded Tradovate
- Easy to swap providers (see [DATA_PROVIDER_GUIDE.md](../docs/DATA_PROVIDER_GUIDE.md))

### 2. Apex Account Integration
- Dynamic position sizing (PA mode) via `risk_manager.get_position_size(atr)`
- Fixed contracts (eval mode)
- Automatic profit target and drawdown tracking
- See [APEX_INTEGRATION.md](APEX_INTEGRATION.md)

### 3. State Persistence
- RiskManager saves state after every trade
- Survives mid-day restarts
- Resume from database on startup
- See [PERSISTENCE.md](PERSISTENCE.md)

### 4. News Calendar Integration
- Fetches events at start of day
- Checks blackout periods before trading
- Optional position exit on blackout start
- See [NEWS_FILTER.md](NEWS_FILTER.md)

### 5. Alerting System
- Email + SMS notifications
- Daily loss warnings (80% of max)
- Drawdown warnings (80% of threshold)
- Losing streak alerts
- Critical events (target hit, DD breach)
- See [ALERTING.md](ALERTING.md)

### 6. Production Ready
- Graceful shutdown with state save
- Signal handlers (SIGINT, SIGTERM)
- Error handling with crash alerts
- Logging to file and console

---

## New Dependencies

Add to bot directory:

```python
# databento_provider.py
# Implements DataProviderBase for Databento API
# See DATA_PROVIDER_GUIDE.md for template

# news_calendar.py
# See NEWS_FILTER.md for template

# alert_manager.py
# See ALERTING.md for template

# Updated files:
# - risk_manager.py (Apex integration, persistence)
# - config.py (account_mode, news, alerting params)
```

---

## Configuration Changes

The bot now requires additional environment variables:

```bash
# Apex Account
ACCOUNT_MODE=eval  # or pa
ACCOUNT_SIZE=50K
RISK_PCT=0.02  # PA mode only

# State Persistence
PERSISTENCE_ENABLED=true
DB_PATH=bot_state.db

# News Calendar
NEWS_FILTER_ENABLED=true
NEWS_API=fmp
NEWS_API_KEY=your_fmp_api_key
NEWS_BLACKOUT_MINUTES=30
NEWS_EXIT_ON_BLACKOUT=false

# Email Alerts
ALERT_EMAIL_ENABLED=true
ALERT_EMAIL_FROM=your_bot@gmail.com
ALERT_EMAIL_TO=your_email@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_bot@gmail.com
SMTP_PASSWORD=your_app_password

# Pushover Alerts
ALERT_PUSHOVER_ENABLED=true
ALERT_PUSHOVER_TOKEN=your_app_token
ALERT_PUSHOVER_USER=your_user_key

# Alert Triggers
ALERT_DAILY_LOSS_PCT=0.8
ALERT_DRAWDOWN_PCT=0.8
ALERT_LOSING_STREAK=5
```

See [CONFIG.md](../CONFIG.md) for full reference.

---

## Migration from Old Bots

To upgrade an existing bot to this template:

1. **Replace bot_*.py** with new template
2. **Update config.py** to add new parameters
3. **Add .env variables** for account_mode, news, alerting
4. **Create/update modules**:
   - `databento_provider.py` (replace tradovate_client.py)
   - `news_calendar.py` (new)
   - `alert_manager.py` (new)
   - `risk_manager.py` (update with Apex integration)
5. **Test in CSV backtest mode** first
6. **Verify state persistence** works (start/stop/resume)
7. **Test alerts** (send test notifications)

See [REFACTOR.md](../REFACTOR.md) for detailed migration guide.

---

## See Also

- [APEX_INTEGRATION.md](APEX_INTEGRATION.md) - Apex account integration
- [PERSISTENCE.md](PERSISTENCE.md) - State persistence template
- [NEWS_FILTER.md](NEWS_FILTER.md) - News calendar template
- [ALERTING.md](ALERTING.md) - Alerting system template
- [DATA_PROVIDER_GUIDE.md](../docs/DATA_PROVIDER_GUIDE.md) - Data provider abstraction
- [RISK_MANAGER.md](RISK_MANAGER.md) - Risk manager template
- [CONFIG.md](../CONFIG.md) - Configuration reference
- [EVAL_VS_PA.md](../docs/EVAL_VS_PA.md) - Eval vs PA mode guide
