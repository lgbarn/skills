# Change Indicator Workflow

Step-by-step workflow for replacing indicators in existing bots.

---

## Overview

This workflow replaces an indicator while preserving the overall strategy logic. Common scenarios:
- Keltner Channels → Bollinger Bands
- EMA → SMA
- VWAP → TWAP
- ADX → ATR
- Custom indicator replacement

**Key Principle:** Change calculation method, keep entry/exit logic similar.

---

## Quick Command

```bash
/bot:refactor <bot_name>
# Then tell Claude: "Replace <old_indicator> with <new_indicator>"
```

**Examples:**
```
"Replace Keltner Channels with Bollinger Bands"
"Replace EMA with SMA"
"Replace VWAP with standard TWAP"
```

---

## Manual Workflow

### Step 1: Understand Current Indicator

**Document how it's used:**
```bash
cd bot_keltner

# Find indicator calculations
grep -n "keltner" indicators.py

# Find signal usage
grep -n "upper_band\|lower_band" bot_keltner.py

# Find config parameters
grep -n "keltner" config.py
```

**Map usage:**
- Calculation: `upper_band = ema + (atr * keltner_mult)`
- Entry signal: `close > upper_band` → long
- Exit: Fixed TP/SL (independent of bands)
- Filters: ADX, session, volume

---

### Step 2: Research New Indicator

**Understand formula:**
```python
# Bollinger Bands formula:
# middle_band = SMA(close, period)
# upper_band = middle_band + (stddev * multiplier)
# lower_band = middle_band - (stddev * multiplier)
```

**Determine parameters:**
- `bb_period`: int (default 20)
- `bb_mult`: float (default 2.0)
- Output: `upper_band`, `middle_band`, `lower_band`

---

### Step 3: Update Configuration

Edit `config.py`:

```python
@dataclass
class Config:
    # ... existing config ...

    # CHANGE: Keltner → Bollinger Bands
    # keltner_period: int = 20  # OLD
    # keltner_mult: float = 2.5  # OLD
    bb_period: int = 20  # NEW
    bb_mult: float = 2.0  # NEW

    def __post_init__(self):
        # ... existing __post_init__ ...

        # CHANGE: Load Bollinger params
        # self.keltner_period = int(os.getenv("KELTNER_PERIOD", str(self.keltner_period)))  # OLD
        # self.keltner_mult = float(os.getenv("KELTNER_MULT", str(self.keltner_mult)))  # OLD
        self.bb_period = int(os.getenv("BB_PERIOD", str(self.bb_period)))  # NEW
        self.bb_mult = float(os.getenv("BB_MULT", str(self.bb_mult)))  # NEW
```

Update `.env.example`:

```bash
# CHANGE: Bollinger Bands (was Keltner Channels)
# KELTNER_PERIOD=20  # OLD
# KELTNER_MULT=2.5  # OLD
BB_PERIOD=20  # NEW
BB_MULT=2.0  # NEW
```

---

### Step 4: Update Indicator Calculations

Edit `indicators.py`:

**Replace calculation method:**
```python
def update(self, bars: list[dict]):
    """Calculate all indicators."""
    # ... existing calculations (EMA, ATR, ADX) ...

    # REMOVE: Keltner Channels
    # ema = self._calculate_ema(self.config.keltner_period)
    # atr = self._calculate_atr(self.config.atr_period)
    # upper_band = ema + (atr * self.config.keltner_mult)
    # lower_band = ema - (atr * self.config.keltner_mult)
    # middle_band = ema

    # ADD: Bollinger Bands
    middle_band = self._calculate_sma(self.config.bb_period)
    stddev = self._calculate_stddev(self.config.bb_period)
    upper_band = middle_band + (stddev * self.config.bb_mult)
    lower_band = middle_band - (stddev * self.config.bb_mult)

    # Add to bars
    for i, bar in enumerate(self.bars):
        bar["upper_band"] = upper_band[i]
        bar["middle_band"] = middle_band[i]
        bar["lower_band"] = lower_band[i]

def _calculate_sma(self, period: int) -> np.ndarray:
    """Calculate Simple Moving Average."""
    closes = np.array([b["close"] for b in self.bars])
    sma = np.convolve(closes, np.ones(period) / period, mode='valid')
    return np.pad(sma, (period - 1, 0), constant_values=np.nan)

def _calculate_stddev(self, period: int) -> np.ndarray:
    """Calculate rolling standard deviation."""
    closes = np.array([b["close"] for b in self.bars])
    std = np.array([
        np.std(closes[max(0, i - period + 1):i + 1])
        for i in range(len(closes))
    ])
    return std
```

---

### Step 5: Update Signal Logic (if needed)

**If entry logic is identical, no change needed:**
```python
# Signal detection unchanged
long_sig = curr["close"] > curr["upper_band"]  # Same for Bollinger
short_sig = curr["close"] < curr["lower_band"]  # Same for Bollinger
```

**If entry logic differs slightly:**
```python
# Example: Add middle band crossover
long_sig = (
    curr["close"] > curr["upper_band"] and
    prev["close"] <= prev["middle_band"]  # NEW: must cross middle first
)
```

---

### Step 6: Update Bot Filename (optional)

```bash
# Option 1: Keep same name (strategy name, not indicator name)
# bot_keltner.py → bot_keltner.py (keep)

# Option 2: Rename to reflect new indicator
mv bot_keltner.py bot_bollinger.py
# Update class name: KeltnerBot → BollingerBot
# Update __main__ description
```

**Recommendation:** Keep filename if strategy is "channel breakout", regardless of which channel indicator used.

---

### Step 7: Test Both Indicators

**Baseline (old indicator):**
```bash
# Revert to old code temporarily
git stash

python bot_keltner.py --csv data/nq_2m_2024.csv > keltner.log

grep "Total P&L" keltner.log
grep "Profit Factor" keltner.log
grep "ENTRY:" keltner.log | wc -l
```

**New indicator:**
```bash
# Restore changes
git stash pop

python bot_keltner.py --csv data/nq_2m_2024.csv > bollinger.log

grep "Total P&L" bollinger.log
grep "Profit Factor" bollinger.log
grep "ENTRY:" bollinger.log | wc -l
```

**Compare:**
| Metric | Keltner | Bollinger |
|--------|---------|-----------|
| P&L | $12,500 | $11,800 |
| Profit Factor | 10.04 | 9.52 |
| Trades | 45 | 42 |
| Win Rate | 87.8% | 85.7% |

---

### Step 8: Update Documentation

**Update bot docstring:**
```python
"""
Bollinger Bands Trading Bot  # CHANGED from Keltner
Author: Luther Barnum

Live trading bot for NQ futures using:
- Databento API for real-time 2-minute bar data
- TradersPost webhooks for order execution
- Bollinger Bands for channel breakout signals  # CHANGED

Signal: Bollinger Bands (Channel breakout)  # CHANGED
Profit Factor: 9.52 | Win Rate: 85.7%  # UPDATED
"""
```

**Update README (if exists):**
```markdown
# Bollinger Bands Bot  <!-- CHANGED -->

Channel breakout strategy using Bollinger Bands.  <!-- CHANGED -->

## Indicator

- **Bollinger Bands**: SMA ± (stddev × multiplier)  <!-- CHANGED -->
- Period: 20 bars
- Multiplier: 2.0 standard deviations
```

---

### Step 9: Commit Changes

```bash
git add .
git commit -m "refactor(keltner): replace Keltner with Bollinger Bands

Changed indicator calculation while preserving strategy logic:
- Replaced Keltner Channels with Bollinger Bands
- Updated config: keltner_period/mult → bb_period/mult
- Added stddev calculation to indicators.py
- Signal logic unchanged (breakout above/below bands)
- Updated docstrings and comments

Backtest comparison (NQ 2024):
- Keltner: $12,500 P&L, 10.04 PF, 45 trades
- Bollinger: $11,800 P&L, 9.52 PF, 42 trades

Keeping Bollinger for reduced volatility sensitivity."
```

---

## Common Indicator Changes

### Keltner → Bollinger Bands

**Similarity:** Both are volatility-based channels

**Difference:** Keltner uses ATR, Bollinger uses stddev

**Impact:** Bollinger more sensitive to recent price moves

---

### EMA → SMA

**Similarity:** Both are moving averages

**Difference:** EMA weights recent data more

**Impact:** SMA smoother, fewer whipsaws

---

### VWAP → TWAP

**Similarity:** Both are price averages

**Difference:** VWAP weighted by volume, TWAP is simple average

**Impact:** TWAP less sensitive to volume spikes

---

### ADX → RSI (as trend filter)

**Similarity:** Both measure momentum

**Difference:** ADX measures trend strength, RSI measures overbought/oversold

**Impact:** Different filtering logic needed

---

## Troubleshooting

### Issue: Calculation Error

```
ValueError: operands could not be broadcast together
```

**Fix:** Array length mismatch. Ensure padding:
```python
# Add NaN padding for warmup period
sma = np.pad(sma, (period - 1, 0), constant_values=np.nan)
```

---

### Issue: No Trades After Change

**Debug:**
```python
# Log band values
logger.info(f"Close: {curr['close']}, Upper: {curr['upper_band']}")
logger.info(f"Long signal: {curr['close'] > curr['upper_band']}")
```

Check:
- Bands calculated correctly?
- Signal condition still makes sense?
- Warmup period sufficient?

---

### Issue: Performance Degraded

**If new indicator performs worse:**
1. Try adjusting parameters (period, multiplier)
2. Compare on multiple datasets
3. Consider if indicator mismatch for this strategy
4. May need to revert to original indicator

**Example:**
- Bollinger might work better on range-bound markets
- Keltner might work better on trending markets
- Test both, keep best

---

## Best Practices

1. **Understand both indicators** - Know formulas and characteristics
2. **Keep signal logic similar** - Preserve strategy essence
3. **Test on same data** - Fair comparison
4. **Document reasoning** - Why change indicator?
5. **Compare metrics** - P&L, PF, win rate, max DD
6. **Consider market regime** - Trending vs ranging
7. **Commit separately** - One indicator change per commit

---

## Decision Framework

**Should I change the indicator?**

```
Is current indicator underperforming?
├─ No → Keep current indicator
└─ Yes
    ├─ Do I understand the new indicator well?
    │   ├─ No → Research more first
    │   └─ Yes
    │       ├─ Will it work with current strategy?
    │       │   ├─ No → Rethink approach
    │       │   └─ Yes → Proceed with change
    │       └─ Test on backtest first
```

---

## See Also

- [REFACTOR.md](workflow-refactor.md) - Main refactoring guide
- [ADD_FEATURE.md](workflow-add-feature.md) - Adding features
- [REMOVE_FEATURE.md](workflow-remove-feature.md) - Removing features
- [SIGNALS.md](signals-overview.md) - Pre-built signal reference
- [TESTING_GUIDE.md](testing.md) - Testing strategies
