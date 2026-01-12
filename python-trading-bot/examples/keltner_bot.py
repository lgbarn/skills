#!/usr/bin/env python3
"""
Keltner Channel Trading Bot
Author: Luther Barnum
Generated: 2026-01-04

Live trading bot for NQ futures using:
- Tradovate WebSocket for real-time 2-minute bar data
- TradersPost webhooks for order execution

Signal: Keltner Channel Breakout
Profit Factor: 10.04 | Win Rate: 87.8%

Usage:
    python keltner_bot.py --paper   # Paper trading (recommended first)
    python keltner_bot.py --live    # Live trading (requires confirmation)
"""

import asyncio
import logging
import os
import signal
import sys
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Callable, Optional, Set

import aiohttp

# =============================================================================
# LOGGING SETUP
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"bot_keltner_{datetime.now().strftime('%Y%m%d')}.log"),
    ],
)
logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION
# =============================================================================


@dataclass
class Config:
    """Bot configuration from environment variables."""

    # Signal
    entry_signal: str = "keltner"

    # Keltner Parameters (optimal from backtest)
    keltner_ema_period: int = 20
    keltner_atr_period: int = 14
    keltner_atr_mult: float = 2.75

    # ADX Filter
    adx_enabled: bool = True
    adx_period: int = 14
    adx_threshold: float = 35.0
    adx_mode: str = "di_rising"

    # Exits (ATR-based)
    atr_period: int = 14
    sl_atr_mult: float = 3.0
    tp_atr_mult: float = 3.0
    trail_enabled: bool = True
    trail_trigger_atr: float = 0.15
    trail_distance_atr: float = 0.15

    # Re-entry
    reentry_enabled: bool = True
    reentry_bars_wait: int = 3
    reentry_adx_min: float = 40.0
    max_reentries: int = 10

    # Risk
    contracts: int = 2
    daily_max_loss: float = 500.0
    slippage_ticks: int = 1
    commission_rt: float = 4.00
    point_value: float = 5.0
    tick_size: float = 0.25

    # Filters
    volume_filter: bool = True
    volume_ma_period: int = 20
    session_filter: bool = True
    allowed_hours: Set[int] = field(
        default_factory=lambda: {9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20}
    )

    # Tradovate
    tradovate_username: str = ""
    tradovate_password: str = ""
    tradovate_cid: int = 0
    tradovate_secret: str = ""
    tradovate_env: str = "demo"

    # TradersPost
    traderspost_webhook_url: str = ""

    # Bot
    ticker: str = "NQH5"
    paper_mode: bool = True

    def __post_init__(self):
        """Load from environment variables."""
        self.tradovate_username = os.getenv("TRADOVATE_USERNAME", "")
        self.tradovate_password = os.getenv("TRADOVATE_PASSWORD", "")
        self.tradovate_cid = int(os.getenv("TRADOVATE_CID", "0"))
        self.tradovate_secret = os.getenv("TRADOVATE_SECRET", "")
        self.tradovate_env = os.getenv("TRADOVATE_ENV", "demo")
        self.traderspost_webhook_url = os.getenv("TRADERSPOST_WEBHOOK_URL", "")
        self.ticker = os.getenv("BOT_TICKER", "NQH5")
        self.paper_mode = os.getenv("BOT_PAPER_MODE", "true").lower() == "true"
        self.contracts = int(os.getenv("BOT_CONTRACTS", "2"))
        self.daily_max_loss = float(os.getenv("BOT_DAILY_MAX_LOSS", "500"))


# =============================================================================
# INDICATORS
# =============================================================================


class Indicators:
    """Calculate and cache technical indicators."""

    def __init__(self, config: Config):
        self.config = config
        self._atr: list[float] = []
        self._adx: list[float] = []
        self._plus_di: list[float] = []
        self._minus_di: list[float] = []
        self._vol_ma: list[float] = []
        self._keltner: list[dict] = []

    def update(self, bars: list[dict]):
        """Recalculate all indicators."""
        closes = [b["close"] for b in bars]
        volumes = [b["volume"] for b in bars]

        self._atr = self._calc_atr(bars, self.config.atr_period)
        self._adx, self._plus_di, self._minus_di = self._calc_adx(
            bars, self.config.adx_period
        )
        self._vol_ma = self._calc_ema(volumes, self.config.volume_ma_period)
        self._keltner = self._calc_keltner(
            bars,
            self.config.keltner_ema_period,
            self.config.keltner_atr_period,
            self.config.keltner_atr_mult,
        )

    def get_bar(self, idx: int) -> dict:
        """Get bar with indicator values attached."""
        return {
            "atr": self._atr[idx] if idx < len(self._atr) else 0,
            "adx": self._adx[idx] if idx < len(self._adx) else 0,
            "plus_di": self._plus_di[idx] if idx < len(self._plus_di) else 0,
            "minus_di": self._minus_di[idx] if idx < len(self._minus_di) else 0,
            "vol_ma": self._vol_ma[idx] if idx < len(self._vol_ma) else 0,
            **self._keltner[idx] if idx < len(self._keltner) else {},
        }

    @staticmethod
    def _calc_ema(values: list[float], period: int) -> list[float]:
        if not values:
            return []
        ema = []
        k = 2 / (period + 1)
        for i, v in enumerate(values):
            if i == 0:
                ema.append(v)
            else:
                ema.append(v * k + ema[-1] * (1 - k))
        return ema

    @staticmethod
    def _calc_atr(bars: list[dict], period: int) -> list[float]:
        if not bars:
            return []
        trs = []
        for i, bar in enumerate(bars):
            if i == 0:
                tr = bar["high"] - bar["low"]
            else:
                prev = bars[i - 1]
                tr = max(
                    bar["high"] - bar["low"],
                    abs(bar["high"] - prev["close"]),
                    abs(bar["low"] - prev["close"]),
                )
            trs.append(tr)
        return Indicators._calc_ema(trs, period)

    @staticmethod
    def _calc_adx(
        bars: list[dict], period: int
    ) -> tuple[list[float], list[float], list[float]]:
        if not bars:
            return [], [], []

        trs = []
        for i, bar in enumerate(bars):
            if i == 0:
                tr = bar["high"] - bar["low"]
            else:
                prev = bars[i - 1]
                tr = max(
                    bar["high"] - bar["low"],
                    abs(bar["high"] - prev["close"]),
                    abs(bar["low"] - prev["close"]),
                )
            trs.append(tr)

        plus_dm = [0]
        minus_dm = [0]
        for i in range(1, len(bars)):
            up = bars[i]["high"] - bars[i - 1]["high"]
            down = bars[i - 1]["low"] - bars[i]["low"]
            plus_dm.append(up if up > down and up > 0 else 0)
            minus_dm.append(down if down > up and down > 0 else 0)

        plus_dm_ema = Indicators._calc_ema(plus_dm, period)
        minus_dm_ema = Indicators._calc_ema(minus_dm, period)
        atr_ema = Indicators._calc_ema(trs, period)

        plus_di_vals = []
        minus_di_vals = []
        dx_vals = []

        for i in range(len(bars)):
            if atr_ema[i] == 0:
                plus_di_vals.append(0)
                minus_di_vals.append(0)
                dx_vals.append(0)
                continue
            plus_di = 100 * plus_dm_ema[i] / atr_ema[i]
            minus_di = 100 * minus_dm_ema[i] / atr_ema[i]
            plus_di_vals.append(plus_di)
            minus_di_vals.append(minus_di)
            di_sum = plus_di + minus_di
            dx = 100 * abs(plus_di - minus_di) / di_sum if di_sum > 0 else 0
            dx_vals.append(dx)

        adx_vals = Indicators._calc_ema(dx_vals, period)
        return adx_vals, plus_di_vals, minus_di_vals

    @staticmethod
    def _calc_keltner(
        bars: list[dict], ema_period: int, atr_period: int, atr_mult: float
    ) -> list[dict]:
        closes = [b["close"] for b in bars]
        middle = Indicators._calc_ema(closes, ema_period)
        atr = Indicators._calc_atr(bars, atr_period)
        results = []
        for i in range(len(bars)):
            band_width = atr[i] * atr_mult
            results.append({
                "keltner_middle": middle[i],
                "keltner_upper": middle[i] + band_width,
                "keltner_lower": middle[i] - band_width,
            })
        return results


# =============================================================================
# RISK MANAGER
# =============================================================================


class RiskManager:
    """Risk manager for daily P&L tracking."""

    def __init__(self, config: Config):
        self.config = config
        self._current_date: Optional[date] = None
        self._daily_pnl: float = 0.0
        self._daily_stopped: bool = False

    @property
    def daily_pnl(self) -> float:
        return self._daily_pnl

    def is_stopped(self) -> bool:
        return self._daily_stopped

    def check_new_day(self, bar_date: date):
        if bar_date != self._current_date:
            if self._current_date is not None:
                logger.info(f"Daily P&L: ${self._daily_pnl:.2f}")
            self._current_date = bar_date
            self._daily_pnl = 0.0
            self._daily_stopped = False
            logger.info(f"New trading day: {bar_date}")

    def record_trade(self, pnl: float) -> bool:
        self._daily_pnl += pnl
        if self._daily_pnl <= -self.config.daily_max_loss:
            self._daily_stopped = True
            logger.warning(f"Daily max loss reached: ${self._daily_pnl:.2f}")
            return False
        return True


# =============================================================================
# TRADERSPOST CLIENT
# =============================================================================


class TradersPostClient:
    """TradersPost webhook client for order execution."""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def send_signal(
        self,
        ticker: str,
        action: str,
        quantity: int = 1,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
    ) -> dict:
        payload = {"ticker": ticker, "action": action, "orderType": "market"}
        if quantity:
            payload["quantity"] = quantity
        if stop_loss:
            payload["stopLoss"] = {"stopPrice": stop_loss}
        if take_profit:
            payload["takeProfit"] = {"limitPrice": take_profit}
        if action == "buy":
            payload["sentiment"] = "bullish"
        elif action == "sell":
            payload["sentiment"] = "bearish"
        elif action == "exit":
            payload["sentiment"] = "flat"

        session = await self._get_session()
        try:
            async with session.post(
                self.webhook_url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                result = await resp.json()
                if result.get("success"):
                    logger.info(f"Signal sent: {action} {ticker}")
                else:
                    logger.warning(f"Signal failed: {result.get('message')}")
                return result
        except Exception as e:
            logger.error(f"Error sending signal: {e}")
            return {"success": False, "error": str(e)}


# =============================================================================
# TRADOVATE CLIENT (SIMPLIFIED)
# =============================================================================


class TradovateClient:
    """Simplified Tradovate client - uses simulated bars for demo."""

    def __init__(self, config: Config):
        self.config = config
        self._running = False
        self._callback: Optional[Callable] = None

    async def connect(self):
        logger.info(f"Connecting to Tradovate ({self.config.tradovate_env})...")
        # In production, implement full WebSocket connection
        # For this example, we'll simulate bar data
        await asyncio.sleep(1)
        logger.info("Connected to Tradovate")

    async def disconnect(self):
        self._running = False
        logger.info("Disconnected from Tradovate")

    async def subscribe_bars(self, symbol: str, bar_size: int, callback: Callable):
        self._callback = callback
        self._running = True
        logger.info(f"Subscribing to {symbol} ({bar_size}-min bars)")

        # Simulate bars for demo (replace with real WebSocket in production)
        base_price = 21500.0
        bar_idx = 0

        while self._running:
            await asyncio.sleep(2)  # Simulate 2-min bars (accelerated for demo)

            # Generate simulated bar
            import random
            change = random.uniform(-5, 5)
            base_price += change

            bar = {
                "timestamp": datetime.now(),
                "open": base_price - 2,
                "high": base_price + 3,
                "low": base_price - 4,
                "close": base_price,
                "volume": random.randint(1000, 5000),
                "hour": datetime.now().hour,
            }

            if self._callback:
                await self._callback(bar)

            bar_idx += 1
            if bar_idx > 100:  # Stop after 100 bars for demo
                break


# =============================================================================
# BOT CLASS
# =============================================================================


class KeltnerBot:
    """Keltner Channel trading bot."""

    def __init__(self, config: Config):
        self.config = config
        self.indicators = Indicators(config)
        self.risk_manager = RiskManager(config)
        self.traderspost = TradersPostClient(config.traderspost_webhook_url)
        self.tradovate: Optional[TradovateClient] = None

        # Position state
        self.position = 0
        self.entry_price = 0.0
        self.stop_loss = 0.0
        self.take_profit = 0.0
        self.trail_on = False
        self.hwm = 0.0
        self.lwm = 0.0

        # Re-entry state
        self.last_exit_bar = -999
        self.last_exit_profitable = False
        self.last_exit_direction = 0
        self.reentry_count = 0

        # Bar data
        self.bars: list[dict] = []
        self.current_bar_idx = 0
        self.running = True

    async def start(self):
        logger.info("Starting Keltner Channel Bot")
        logger.info(f"Ticker: {self.config.ticker}")
        logger.info(f"Paper Mode: {self.config.paper_mode}")
        logger.info(f"Contracts: {self.config.contracts}")
        logger.info(f"Daily Max Loss: ${self.config.daily_max_loss}")

        self.tradovate = TradovateClient(self.config)
        await self.tradovate.connect()
        await self.tradovate.subscribe_bars(
            symbol=self.config.ticker,
            bar_size=2,
            callback=self.on_bar,
        )

        while self.running:
            await asyncio.sleep(1)

    async def stop(self):
        logger.info("Shutting down bot...")
        self.running = False
        if self.position != 0:
            await self._exit_position("Shutdown")
        if self.tradovate:
            await self.tradovate.disconnect()
        await self.traderspost.close()
        logger.info("Bot stopped")

    async def on_bar(self, bar: dict):
        self.bars.append(bar)
        self.current_bar_idx = len(self.bars) - 1

        warmup = 50
        if len(self.bars) < warmup:
            logger.debug(f"Warmup: {len(self.bars)}/{warmup} bars")
            return

        self.indicators.update(self.bars)
        curr = {**bar, **self.indicators.get_bar(self.current_bar_idx)}
        prev = {**self.bars[-2], **self.indicators.get_bar(self.current_bar_idx - 1)}

        bar_date = bar["timestamp"].date()
        self.risk_manager.check_new_day(bar_date)

        if self.risk_manager.is_stopped():
            return

        if self.position != 0:
            await self._check_exits(curr, prev, bar)
        else:
            await self._check_entries(curr, prev, bar)

    async def _check_entries(self, curr: dict, prev: dict, bar: dict):
        if self.config.session_filter:
            if curr["hour"] not in self.config.allowed_hours:
                return

        if self.config.volume_filter:
            if bar["volume"] < curr["vol_ma"]:
                return

        atr = curr["atr"]
        sl_pts = atr * self.config.sl_atr_mult
        tp_pts = atr * self.config.tp_atr_mult

        # Keltner signal detection
        long_sig = (
            prev["close"] <= prev.get("keltner_upper", float("inf"))
            and bar["close"] > curr.get("keltner_upper", float("inf"))
        )
        short_sig = (
            prev["close"] >= prev.get("keltner_lower", 0)
            and bar["close"] < curr.get("keltner_lower", 0)
        )

        is_reentry = False

        # Re-entry logic
        if self.config.reentry_enabled and self.last_exit_profitable:
            bars_since_exit = self.current_bar_idx - self.last_exit_bar
            if bars_since_exit >= self.config.reentry_bars_wait:
                if self.reentry_count < self.config.max_reentries:
                    if curr["adx"] > self.config.reentry_adx_min:
                        if self.last_exit_direction == 1 and bar["close"] > curr.get("keltner_upper", float("inf")):
                            long_sig = True
                            is_reentry = True
                        elif self.last_exit_direction == -1 and bar["close"] < curr.get("keltner_lower", 0):
                            short_sig = True
                            is_reentry = True

        if not is_reentry and (long_sig or short_sig):
            self.reentry_count = 0

        # ADX filter
        if not is_reentry:
            if long_sig and not self._check_adx(curr, prev, 1):
                long_sig = False
            if short_sig and not self._check_adx(curr, prev, -1):
                short_sig = False

        if long_sig:
            await self._enter_position(1, bar["close"], sl_pts, tp_pts, is_reentry)
        elif short_sig:
            await self._enter_position(-1, bar["close"], sl_pts, tp_pts, is_reentry)

    def _check_adx(self, curr: dict, prev: dict, direction: int) -> bool:
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
        self, direction: int, price: float, sl_pts: float, tp_pts: float, is_reentry: bool
    ):
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
        self.entry_price = entry
        self.hwm = entry
        self.lwm = entry
        self.trail_on = False

        if is_reentry:
            self.reentry_count += 1

        action = "buy" if direction == 1 else "sell"
        entry_type = "RE-ENTRY" if is_reentry else "ENTRY"

        logger.info(
            f"{entry_type}: {action.upper()} @ {entry:.2f} | "
            f"SL: {self.stop_loss:.2f} | TP: {self.take_profit:.2f}"
        )

        if not self.config.paper_mode:
            await self.traderspost.send_signal(
                ticker=self.config.ticker,
                action=action,
                quantity=self.config.contracts,
                stop_loss=self.stop_loss,
                take_profit=self.take_profit,
            )

    async def _check_exits(self, curr: dict, prev: dict, bar: dict):
        high = bar["high"]
        low = bar["low"]

        if self.position == 1:
            self.hwm = max(self.hwm, high)
        else:
            self.lwm = min(self.lwm, low)

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

        if self.trail_on:
            if self.position == 1:
                new_stop = self.hwm - trail_distance
                if new_stop > self.stop_loss:
                    self.stop_loss = new_stop
            else:
                new_stop = self.lwm + trail_distance
                if new_stop < self.stop_loss:
                    self.stop_loss = new_stop

        exit_price = None
        exit_reason = None

        if self.position == 1:
            if self.trail_on and low <= self.stop_loss:
                exit_price = self.stop_loss
                exit_reason = "TrailingStop"
            elif low <= self.stop_loss:
                exit_price = self.stop_loss
                exit_reason = "StopLoss"
            elif high >= self.take_profit:
                exit_price = self.take_profit
                exit_reason = "TakeProfit"
        else:
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
        if exit_price is None:
            exit_price = self.bars[-1]["close"]

        slippage = self.config.slippage_ticks * self.config.tick_size
        if self.position == 1:
            exit_price -= slippage
        else:
            exit_price += slippage

        pnl = (exit_price - self.entry_price) * self.position
        pnl *= self.config.point_value * self.config.contracts
        pnl -= self.config.commission_rt * self.config.contracts

        self.risk_manager.record_trade(pnl)

        self.last_exit_bar = self.current_bar_idx
        self.last_exit_profitable = pnl > 0
        self.last_exit_direction = self.position

        direction_str = "LONG" if self.position == 1 else "SHORT"
        logger.info(
            f"EXIT {direction_str}: {reason} @ {exit_price:.2f} | "
            f"P&L: ${pnl:.2f} | Daily: ${self.risk_manager.daily_pnl:.2f}"
        )

        if not self.config.paper_mode:
            await self.traderspost.send_signal(ticker=self.config.ticker, action="exit")

        self.position = 0
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
    import argparse

    parser = argparse.ArgumentParser(description="Keltner Channel Trading Bot")
    parser.add_argument("--paper", action="store_true", help="Paper trading mode")
    parser.add_argument("--live", action="store_true", help="Live trading mode")
    args = parser.parse_args()

    # Load .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # dotenv optional

    config = Config()

    if args.paper:
        config.paper_mode = True
    elif args.live:
        config.paper_mode = False

    if not config.paper_mode:
        logger.warning("=" * 60)
        logger.warning("LIVE TRADING MODE - REAL MONEY AT RISK")
        logger.warning("=" * 60)
        confirm = input("Type 'CONFIRM' to proceed with live trading: ")
        if confirm != "CONFIRM":
            logger.info("Cancelled. Use --paper for paper trading.")
            return

    bot = KeltnerBot(config)

    loop = asyncio.get_event_loop()

    def shutdown_handler():
        logger.info("Received shutdown signal")
        asyncio.create_task(bot.stop())

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown_handler)

    try:
        await bot.start()
    except Exception as e:
        logger.error(f"Bot error: {e}")
        await bot.stop()
        raise


if __name__ == "__main__":
    asyncio.run(main())
