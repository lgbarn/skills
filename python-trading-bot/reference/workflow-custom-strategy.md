# Custom Strategy Workflow

Workflow for building bots with custom trading strategies.

---

## Overview

This workflow guides you through creating a bot with a custom strategy not covered by the 5 pre-built signals (keltner, ema_cross, vwap, supertrend, alligator).

**Use custom strategy when:**
- Testing your own indicator idea
- Combining multiple indicators in unique ways
- Implementing proprietary signal logic
- Building strategy from research/backtesting

---

## Quick Command

```bash
/bot:custom
```

The skill will ask you questions to build your strategy.

---

## Interactive Workflow

### Step 1: Describe Your Strategy

**Question:** "Describe your trading strategy"

**Good Answer:**
```
"Enter long when price crosses above 21 EMA and RSI is above 50,
exit when price crosses below 21 EMA or RSI drops below 40.
Use ADX > 30 filter to avoid ranging markets."
```

**Bad Answer:**
```
"Buy low, sell high"  # Too vague
```

**Template:**
```
Entry: [Condition] AND [Condition]
Exit: [Condition] OR [Condition]
Filters: [Condition]
```

---

### Step 2: Specify Indicators Needed

**Question:** "What indicators does your strategy need?"

**Answer format:**
```
- EMA(21)
- RSI(14)
- ADX(14)
```

**Supported indicators:**
- Moving averages: EMA, SMA, WMA
- Volatility: ATR, Bollinger Bands, Keltner Channels
- Momentum: RSI, Stochastic, MACD
- Trend: ADX, Supertrend, Parabolic SAR
- Volume: Volume MA, OBV, VWAP
- Custom: Describe calculation

---

### Step 3: Define Entry Logic

**Question:** "What conditions trigger a long entry?"

**Answer:**
```python
# Long entry when:
# 1. Price crosses above EMA(21)
# 2. RSI > 50
# 3. ADX > 30

long_sig = (
    curr["close"] > curr["ema_21"] and
    prev["close"] <= prev["ema_21"] and  # Crossover
    curr["rsi"] > 50 and
    curr["adx"] > 30
)
```

**Question:** "What conditions trigger a short entry?"

**Answer:**
```python
# Short entry when:
# 1. Price crosses below EMA(21)
# 2. RSI < 50
# 3. ADX > 30

short_sig = (
    curr["close"] < curr["ema_21"] and
    prev["close"] >= prev["ema_21"] and  # Crossover
    curr["rsi"] < 50 and
    curr["adx"] > 30
)
```

---

### Step 4: Define Exit Logic

**Question:** "How do you exit positions?"

**Options:**
1. **Fixed TP/SL** (ATR-based)
2. **Indicator-based** (opposite signal, indicator condition)
3. **Trailing stop** (ATR-based trailing)
4. **Combination** (TP or indicator exit)

**Example (Indicator-based):**
```python
# Exit long when:
# - Price crosses below EMA, OR
# - RSI drops below 40

if position == 1:  # Long
    if (curr["close"] < curr["ema_21"] and prev["close"] >= prev["ema_21"]) or curr["rsi"] < 40:
        await _exit_position("SignalExit")
```

---

### Step 5: Specify Parameters

**Question:** "What parameters need to be configurable?"

**Answer:**
```python
# Configurable parameters:
ema_period: int = 21
rsi_period: int = 14
rsi_entry_threshold: float = 50.0
rsi_exit_threshold: float = 40.0
adx_period: int = 14
adx_threshold: float = 30.0
```

---

## Manual Workflow

### Step 1: Plan Your Strategy

**Document:**
- Entry conditions (long + short)
- Exit conditions
- Filters
- Indicators needed
- Parameters

**Example strategy doc:**
```markdown
# RSI-EMA Crossover Strategy

## Indicators
- EMA(21)
- RSI(14)
- ADX(14)

## Entry (Long)
1. Price crosses above EMA(21)
2. RSI > 50
3. ADX > 30

## Entry (Short)
1. Price crosses below EMA(21)
2. RSI < 50
3. ADX > 30

## Exit
- Opposite signal (EMA crossover)
- OR RSI threshold (40 for longs, 60 for shorts)

## Parameters
- ema_period: 21
- rsi_period: 14
- rsi_entry: 50
- rsi_exit_long: 40
- rsi_exit_short: 60
- adx_threshold: 30
```

---

### Step 2: Create Bot Structure

```bash
mkdir bot_custom_rsi_ema
cd bot_custom_rsi_ema

# Create files
touch bot_custom_rsi_ema.py
touch indicators.py
touch config.py
touch .env
```

---

### Step 3: Implement Indicators

**indicators.py:**
```python
"""
Custom Indicators for RSI-EMA Strategy
"""

import numpy as np
from typing import List
from datetime import datetime


class Indicators:
    def __init__(self, config):
        self.config = config
        self.bars: List[dict] = []

    def update(self, bars: List[dict]):
        """Calculate all indicators."""
        self.bars = bars

        # Calculate indicators
        ema = self._calculate_ema(self.config.ema_period)
        rsi = self._calculate_rsi(self.config.rsi_period)
        adx = self._calculate_adx(self.config.adx_period)

        # Add to bars
        for i, bar in enumerate(self.bars):
            bar["ema_21"] = ema[i]
            bar["rsi"] = rsi[i]
            bar["adx"] = adx[i]
            bar["hour"] = bar["timestamp"].hour

    def get_bar(self, idx: int) -> dict:
        """Get bar with indicators."""
        return self.bars[idx]

    def _calculate_ema(self, period: int) -> np.ndarray:
        """Calculate EMA."""
        closes = np.array([b["close"] for b in self.bars])
        ema = np.zeros_like(closes)

        # Initialize with SMA
        ema[period - 1] = np.mean(closes[:period])

        # Calculate EMA
        multiplier = 2 / (period + 1)
        for i in range(period, len(closes)):
            ema[i] = (closes[i] * multiplier) + (ema[i - 1] * (1 - multiplier))

        # Pad beginning with NaN
        ema[:period - 1] = np.nan

        return ema

    def _calculate_rsi(self, period: int = 14) -> np.ndarray:
        """Calculate RSI."""
        closes = np.array([b["close"] for b in self.bars])
        delta = np.diff(closes, prepend=closes[0])

        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)

        avg_gain = np.zeros(len(closes))
        avg_loss = np.zeros(len(closes))

        # Initial averages
        avg_gain[period] = np.mean(gain[:period + 1])
        avg_loss[period] = np.mean(loss[:period + 1])

        # Smoothed averages
        for i in range(period + 1, len(closes)):
            avg_gain[i] = (avg_gain[i - 1] * (period - 1) + gain[i]) / period
            avg_loss[i] = (avg_loss[i - 1] * (period - 1) + loss[i]) / period

        # Calculate RSI
        rs = avg_gain / (avg_loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))

        # Pad beginning
        rsi[:period] = 50  # Neutral

        return rsi

    def _calculate_adx(self, period: int = 14) -> np.ndarray:
        """Calculate ADX."""
        highs = np.array([b["high"] for b in self.bars])
        lows = np.array([b["low"] for b in self.bars])
        closes = np.array([b["close"] for b in self.bars])

        # True Range
        high_low = highs - lows
        high_close = np.abs(highs - np.roll(closes, 1))
        low_close = np.abs(lows - np.roll(closes, 1))
        tr = np.maximum(high_low, np.maximum(high_close, low_close))

        # +DM and -DM
        up_move = highs - np.roll(highs, 1)
        down_move = np.roll(lows, 1) - lows

        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)

        # Smoothed values
        atr = np.zeros_like(tr)
        plus_di = np.zeros_like(tr)
        minus_di = np.zeros_like(tr)

        atr[period] = np.mean(tr[:period + 1])

        for i in range(period + 1, len(tr)):
            atr[i] = (atr[i - 1] * (period - 1) + tr[i]) / period

        # Calculate DI
        plus_di = 100 * (plus_dm / (atr + 1e-10))
        minus_di = 100 * (minus_dm / (atr + 1e-10))

        # Calculate DX
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di + 1e-10)

        # Calculate ADX
        adx = np.zeros_like(dx)
        adx[period * 2] = np.mean(dx[period:period * 2 + 1])

        for i in range(period * 2 + 1, len(dx)):
            adx[i] = (adx[i - 1] * (period - 1) + dx[i]) / period

        # Pad beginning
        adx[:period * 2] = 0

        return adx
```

---

### Step 4: Implement Signal Logic

**bot_custom_rsi_ema.py:**
```python
def _check_signal(self, curr: dict, prev: dict) -> tuple[bool, bool]:
    """
    RSI-EMA Crossover signal detection.

    Returns:
        (long_signal, short_signal)
    """
    long_sig = False
    short_sig = False

    # Long entry
    if (
        curr["close"] > curr["ema_21"] and  # Above EMA
        prev["close"] <= prev["ema_21"] and  # Crossover
        curr["rsi"] > self.config.rsi_entry_threshold and  # RSI bullish
        curr["adx"] > self.config.adx_threshold  # Trending
    ):
        long_sig = True

    # Short entry
    if (
        curr["close"] < curr["ema_21"] and  # Below EMA
        prev["close"] >= prev["ema_21"] and  # Crossover
        curr["rsi"] < (100 - self.config.rsi_entry_threshold) and  # RSI bearish
        curr["adx"] > self.config.adx_threshold  # Trending
    ):
        short_sig = True

    return long_sig, short_sig


async def _check_exits(self, curr: dict, prev: dict):
    """Check custom exit conditions."""
    # Standard TP/SL checks first
    await super()._check_exits(curr, prev)

    # Custom indicator-based exits
    if self.position == 1:  # Long
        # Exit on EMA crossover OR RSI threshold
        if (
            (curr["close"] < curr["ema_21"] and prev["close"] >= prev["ema_21"]) or
            curr["rsi"] < self.config.rsi_exit_threshold
        ):
            await self._exit_position("SignalExit", curr["close"])

    elif self.position == -1:  # Short
        # Exit on EMA crossover OR RSI threshold
        if (
            (curr["close"] > curr["ema_21"] and prev["close"] <= prev["ema_21"]) or
            curr["rsi"] > (100 - self.config.rsi_exit_threshold)
        ):
            await self._exit_position("SignalExit", curr["close"])
```

---

### Step 5: Add Configuration

**config.py:**
```python
@dataclass
class Config:
    # ... existing config ...

    # Custom Strategy Parameters
    ema_period: int = 21
    rsi_period: int = 14
    rsi_entry_threshold: float = 50.0
    rsi_exit_threshold: float = 40.0
    adx_threshold: float = 30.0

    def __post_init__(self):
        # ... existing __post_init__ ...

        # Load custom params
        self.ema_period = int(os.getenv("EMA_PERIOD", str(self.ema_period)))
        self.rsi_period = int(os.getenv("RSI_PERIOD", str(self.rsi_period)))
        self.rsi_entry_threshold = float(os.getenv("RSI_ENTRY_THRESHOLD", str(self.rsi_entry_threshold)))
        self.rsi_exit_threshold = float(os.getenv("RSI_EXIT_THRESHOLD", str(self.rsi_exit_threshold)))
        self.adx_threshold = float(os.getenv("ADX_THRESHOLD", str(self.adx_threshold)))
```

**.env:**
```bash
# Custom Strategy Parameters
EMA_PERIOD=21
RSI_PERIOD=14
RSI_ENTRY_THRESHOLD=50.0
RSI_EXIT_THRESHOLD=40.0
ADX_THRESHOLD=30.0
```

---

### Step 6: CSV Backtest

```bash
python bot_custom_rsi_ema.py --csv data/nq_2m_2024.csv > backtest.log

# Analyze results
grep "Total P&L" backtest.log
grep "Profit Factor" backtest.log
grep "Win Rate" backtest.log
grep "ENTRY:" backtest.log | wc -l
```

**Iterate:**
- Adjust parameters
- Test on multiple datasets
- Compare to pre-built signals
- Refine entry/exit logic

---

## Example Custom Strategies

### 1. Triple EMA Crossover

**Indicators:** EMA(9), EMA(21), EMA(50)

**Entry Long:**
```python
long_sig = (
    curr["ema_9"] > curr["ema_21"] > curr["ema_50"] and
    prev["ema_9"] <= prev["ema_21"]  # Recent crossover
)
```

---

### 2. RSI Divergence

**Indicators:** RSI(14), Price highs/lows

**Entry Long:**
```python
# Price makes lower low, but RSI makes higher low (bullish divergence)
price_lower_low = curr["low"] < prev_swing_low
rsi_higher_low = curr["rsi"] > prev_swing_rsi

long_sig = price_lower_low and rsi_higher_low
```

---

### 3. Bollinger + MACD

**Indicators:** Bollinger Bands, MACD

**Entry Long:**
```python
long_sig = (
    curr["close"] < curr["bb_lower"] and  # Oversold
    curr["macd"] > curr["signal"] and  # MACD bullish
    prev["macd"] <= prev["signal"]  # Recent crossover
)
```

---

### 4. Support/Resistance Breakout

**Indicators:** Pivot Points, Volume

**Entry Long:**
```python
long_sig = (
    curr["close"] > resistance_level and  # Breakout
    prev["close"] <= resistance_level and  # Crossover
    curr["volume"] > curr["vol_ma"] * 1.5  # High volume
)
```

---

## Testing Custom Strategies

### Validation Checklist

- [ ] Indicators calculate correctly (unit tests)
- [ ] Entry signals detected (integration tests)
- [ ] Exit signals work (integration tests)
- [ ] Filters functional (ADX, session, volume)
- [ ] CSV backtest positive P&L
- [ ] Profit factor > 1.5
- [ ] Win rate reasonable (50-80%)
- [ ] Trade count reasonable (20-100/year)
- [ ] Paper trade 3-5 days successfully

---

## Common Pitfalls

### 1. Over-Fitting

**Problem:** Strategy works on backtest data but fails live

**Solution:**
- Test on multiple time periods
- Test on different market conditions
- Keep strategy simple
- Use out-of-sample testing

---

### 2. Look-Ahead Bias

**Problem:** Using future data in signal

**Bad:**
```python
# Using future bar data
if bars[i+1]["high"] > bars[i]["high"]:  # Can't know future!
```

**Good:**
```python
# Using only past/current data
if curr["high"] > prev["high"]:
```

---

### 3. Too Many Conditions

**Problem:** Signal never triggers

**Bad:**
```python
long_sig = (
    cond1 and cond2 and cond3 and cond4 and cond5  # Too restrictive
)
```

**Good:**
```python
long_sig = (
    cond1 and cond2  # Essential conditions only
)
```

---

## Best Practices

1. **Start simple** - Begin with 1-2 indicators
2. **Test rigorously** - Multiple datasets, time periods
3. **Document logic** - Write down strategy rules
4. **Version control** - Git commit after each change
5. **Compare to baseline** - How does it compare to pre-built signals?
6. **Paper trade** - Always paper trade first
7. **Monitor closely** - Watch first week of live trading

---

## See Also

- [WORKFLOW.md](workflow-interactive.md) - Bot creation workflow
- [SIGNALS.md](signals-overview.md) - Pre-built signals reference
- [BASE_BOT.md](../templates/base_bot.py.md) - Bot template
- [TESTING_GUIDE.md](testing.md) - Testing strategies
- [REFACTOR.md](workflow-refactor.md) - Refactoring guide
