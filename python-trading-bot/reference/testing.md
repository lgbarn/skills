# Testing Guide

Comprehensive guide for testing trading bots before live deployment.

---

## Overview

Testing is critical for trading bots. A bug can cost real money. This guide covers all testing levels from unit tests to live paper trading.

**Testing Pyramid:**
```
         Live Paper Trading (days)
            ↑
       CSV Backtest (minutes)
            ↑
    Integration Tests (seconds)
            ↑
      Unit Tests (milliseconds)
```

---

## Test Levels

### 1. Unit Tests

**What:** Test individual functions in isolation

**Example:** Indicator calculations
```python
def test_ema_calculation():
    """Test EMA calculation accuracy."""
    prices = [10, 11, 12, 11, 10, 11, 12, 13]
    period = 3

    ema = calculate_ema(prices, period)

    # Verify against known values
    assert abs(ema[-1] - 11.75) < 0.01
```

**When to run:**
- After writing new indicator
- After modifying calculations
- Before committing code changes
- As part of CI/CD

---

### 2. Integration Tests

**What:** Test multiple components working together

**Example:** Signal detection logic
```python
def test_keltner_breakout_signal():
    """Test Keltner breakout detection."""
    # Setup
    bars = load_test_bars()
    indicators = Indicators(config)
    indicators.update(bars)

    # Get bar where breakout occurs
    curr = indicators.get_bar(100)
    prev = indicators.get_bar(99)

    # Verify signal
    assert curr["close"] > curr["upper_band"]  # Above upper band
    assert prev["close"] <= prev["upper_band"]  # Crossover
    assert curr["adx"] > 35  # ADX filter passed
```

**When to run:**
- After changing signal logic
- After adding/removing filters
- Before major refactoring
- Weekly regression

---

### 3. CSV Backtest

**What:** Run bot on historical data

**Example:**
```bash
python bot_keltner.py --csv data/nq_2m_2024.csv > backtest.log
```

**What to verify:**
- Trade count reasonable
- Win rate matches expectations
- Profit factor > 1.0
- Max drawdown acceptable
- No errors in logs

**When to run:**
- Before deploying new bot
- After any code change
- Before switching paper → live
- Monthly validation

---

### 4. State Persistence Tests

**What:** Verify bot can survive restart

**Example:**
```python
def test_position_resume():
    """Test bot resumes position after restart."""
    # Start bot, enter position
    bot = KeltnerBot(config)
    await bot._enter_position(1, 18500, 30, 60, 2)

    # Save state
    bot.risk_manager.db.save_position(bot.position, bot.entry_price, ...)

    # Simulate restart
    bot2 = KeltnerBot(config)  # New instance

    # Verify state restored
    assert bot2.position == 1
    assert bot2.entry_price == 18500
```

**When to run:**
- After implementing persistence
- After database schema changes
- Before deploying with persistence
- Monthly validation

---

### 5. Live Paper Trading

**What:** Run bot in paper mode against live market

**Duration:** Minimum 3-5 days

**What to verify:**
- Bot starts without errors
- Connects to data feed
- Processes bars correctly
- Enters/exits positions
- Risk management works
- Alerts send successfully

**When to run:**
- Before first live deployment
- After major refactoring
- After adding production features
- When migrating eval → PA

---

## Test Organization

### Directory Structure

```
bot_keltner/
├── bot_keltner.py
├── config.py
├── indicators.py
├── risk_manager.py
├── tests/
│   ├── __init__.py
│   ├── test_indicators.py      # Unit tests
│   ├── test_signals.py         # Integration tests
│   ├── test_risk_manager.py    # Risk logic tests
│   ├── test_persistence.py     # Database tests
│   └── fixtures/
│       └── test_bars.csv       # Test data
└── pytest.ini
```

---

## Unit Testing

### Test Indicators

```python
# tests/test_indicators.py

import pytest
import numpy as np
from indicators import Indicators
from config import Config

@pytest.fixture
def config():
    return Config()

@pytest.fixture
def indicators(config):
    return Indicators(config)

def test_ema_calculation(indicators):
    """Test EMA calculation."""
    # Simple test case
    bars = [
        {"close": 10, "timestamp": datetime(2024, 1, 1)},
        {"close": 11, "timestamp": datetime(2024, 1, 2)},
        {"close": 12, "timestamp": datetime(2024, 1, 3)},
    ]

    ema = indicators._calculate_ema(period=2)

    # Verify reasonable values
    assert len(ema) == len(bars)
    assert ema[-1] > ema[-2]  # Trending up

def test_atr_calculation(indicators):
    """Test ATR calculation."""
    bars = [
        {"high": 100, "low": 95, "close": 98, "timestamp": datetime(2024, 1, 1)},
        {"high": 102, "low": 97, "close": 100, "timestamp": datetime(2024, 1, 2)},
        {"high": 105, "low": 99, "close": 103, "timestamp": datetime(2024, 1, 3)},
    ]

    indicators.bars = bars
    atr = indicators._calculate_atr(period=2)

    # ATR should be positive
    assert all(atr > 0)

    # ATR should reflect volatility
    assert atr[-1] > 0

def test_adx_calculation(indicators):
    """Test ADX calculation."""
    # Generate trending data
    bars = []
    for i in range(50):
        bars.append({
            "high": 100 + i,
            "low": 95 + i,
            "close": 98 + i,
            "timestamp": datetime(2024, 1, 1) + timedelta(minutes=i*2)
        })

    indicators.bars = bars
    adx = indicators._calculate_adx(period=14)

    # ADX should increase in strong trend
    assert adx[-1] > 25  # Strong trend

def test_keltner_bands(indicators):
    """Test Keltner channel calculation."""
    # Generate bars
    bars = []
    for i in range(100):
        bars.append({
            "open": 100 + np.sin(i/10),
            "high": 102 + np.sin(i/10),
            "low": 98 + np.sin(i/10),
            "close": 100 + np.sin(i/10),
            "volume": 1000,
            "timestamp": datetime(2024, 1, 1) + timedelta(minutes=i*2)
        })

    indicators.bars = bars
    indicators.update(bars)

    curr = indicators.get_bar(-1)

    # Verify bands calculated
    assert "upper_band" in curr
    assert "middle_band" in curr
    assert "lower_band" in curr

    # Upper > middle > lower
    assert curr["upper_band"] > curr["middle_band"]
    assert curr["middle_band"] > curr["lower_band"]

def test_volume_ma(indicators):
    """Test volume moving average."""
    bars = []
    for i in range(50):
        bars.append({
            "close": 100,
            "volume": 1000 + i*10,  # Increasing volume
            "timestamp": datetime(2024, 1, 1) + timedelta(minutes=i*2)
        })

    indicators.bars = bars
    indicators.update(bars)

    curr = indicators.get_bar(-1)
    prev = indicators.get_bar(-2)

    # Volume MA should increase
    assert curr["vol_ma"] > prev["vol_ma"]
```

---

## Integration Testing

### Test Signal Detection

```python
# tests/test_signals.py

import pytest
from bot_keltner import KeltnerBot
from config import Config

@pytest.fixture
def config():
    cfg = Config()
    cfg.adx_threshold = 35.0
    return cfg

@pytest.fixture
def bot(config):
    return KeltnerBot(config)

def test_long_signal_detection(bot):
    """Test long signal detection."""
    # Load bars with known breakout
    bars = load_fixture("long_breakout.csv")
    bot.bars = bars
    bot.indicators.update(bars)

    curr = bot.indicators.get_bar(-1)
    prev = bot.indicators.get_bar(-2)

    long_sig, short_sig = bot._check_signal(curr, prev)

    assert long_sig is True
    assert short_sig is False

def test_short_signal_detection(bot):
    """Test short signal detection."""
    bars = load_fixture("short_breakout.csv")
    bot.bars = bars
    bot.indicators.update(bars)

    curr = bot.indicators.get_bar(-1)
    prev = bot.indicators.get_bar(-2)

    long_sig, short_sig = bot._check_signal(curr, prev)

    assert long_sig is False
    assert short_sig is True

def test_adx_filter_blocks_entry(bot):
    """Test ADX filter blocking low-ADX entries."""
    # Breakout but low ADX
    bars = load_fixture("breakout_low_adx.csv")
    bot.bars = bars
    bot.indicators.update(bars)

    curr = bot.indicators.get_bar(-1)
    prev = bot.indicators.get_bar(-2)

    # Signal detected but ADX filter fails
    assert curr["close"] > curr["upper_band"]  # Breakout
    assert curr["adx"] < 35.0  # Low ADX
    assert bot._check_adx(curr, prev, 1) is False  # Filter blocks

def test_session_filter(bot):
    """Test session filter blocks off-hours trading."""
    bot.config.session_filter = True
    bot.config.allowed_hours = [10, 11, 12, 13, 14, 15]

    # Bar at 9:00 (before session)
    bars = []
    bars.append({
        "timestamp": datetime(2024, 1, 10, 9, 0),
        "close": 18500,
        # ... other OHLCV
    })

    bot.bars = bars
    bot.indicators.update(bars)

    curr = bot.indicators.get_bar(-1)

    # Should be filtered
    assert curr["hour"] == 9
    assert curr["hour"] not in bot.config.allowed_hours
```

---

## CSV Backtesting

### Running Backtest

```bash
# Basic backtest
python bot_keltner.py --csv data/nq_2m_2024.csv

# Save to log
python bot_keltner.py --csv data/nq_2m_2024.csv > backtest_20260110.log

# Compare before/after changes
python bot_keltner.py --csv data/nq_2m_2024.csv > before.log
# Make changes
python bot_keltner.py --csv data/nq_2m_2024.csv > after.log
diff before.log after.log
```

### Validating Backtest Results

**Check for errors:**
```bash
grep "ERROR" backtest.log
grep "Exception" backtest.log
grep "undefined" backtest.log
```

**Verify metrics:**
```bash
# Trade count
grep "ENTRY:" backtest.log | wc -l
# Should be reasonable (20-100 trades/year)

# Profit factor
grep "Profit Factor" backtest.log
# Should be > 1.5

# Win rate
grep "Win Rate" backtest.log
# Should match expectations (70-90% for channel strategies)

# Max drawdown
grep "Max Drawdown" backtest.log
# Should be < daily_max_loss × 5
```

**Verify behavior:**
```bash
# No trades during blackout (if news filter enabled)
grep "blackout" backtest.log

# Position sizing (PA mode)
grep "Position size:" backtest.log | head -10

# Risk management working
grep "Daily max loss" backtest.log
grep "DRAWDOWN" backtest.log
```

---

## State Persistence Testing

### Test Database Save/Load

```python
# tests/test_persistence.py

import pytest
from state_db import StateDB
from apex_account import ApexAccountState
from config import Config

@pytest.fixture
def db():
    db = StateDB(":memory:")  # In-memory for tests
    yield db
    db.close()

def test_save_account_state(db):
    """Test saving account state."""
    config = Config()
    config.account_mode = "eval"
    config.account_size = "50K"

    apex = ApexAccountState.from_config(config)
    apex.equity = 3245.0
    apex.high_water_mark = 3500.0

    db.save_account_state(apex)

    # Load and verify
    loaded = db.load_account_state()
    assert loaded["equity"] == 3245.0
    assert loaded["high_water_mark"] == 3500.0

def test_save_position(db):
    """Test saving position state."""
    db.save_position(
        position=1,
        entry_price=18500.0,
        stop_loss=18470.0,
        take_profit=18560.0,
        contracts=2
    )

    loaded = db.load_position()
    assert loaded["position"] == 1
    assert loaded["entry_price"] == 18500.0
    assert loaded["contracts"] == 2

def test_restart_scenario(db):
    """Test mid-trade restart scenario."""
    # Save state mid-trade
    db.save_position(1, 18500.0, 18470.0, 18560.0, 2)
    db.save_account_state(apex_account)
    db.save_daily_pnl(date.today(), -150.0, False, 3)

    # Load state (simulating restart)
    pos = db.load_position()
    acct = db.load_account_state()
    daily = db.load_daily_pnl(date.today())

    # Verify all state restored
    assert pos is not None
    assert pos["position"] == 1
    assert acct is not None
    assert daily is not None
    assert daily["pnl"] == -150.0
```

---

## Paper Trading

### Setup

```bash
# Configure for paper mode
export PAPER_MODE=true

# Start bot
python bot_keltner.py --paper

# Monitor logs
tail -f bot_keltner_20260110.log
```

### What to Monitor

**Day 1-2: Connection and Data**
- [ ] Bot connects successfully
- [ ] Receives real-time bars
- [ ] Indicators calculate correctly
- [ ] No errors in logs

**Day 3-4: Signal Detection**
- [ ] Detects entry signals
- [ ] Filters work correctly (ADX, session, volume)
- [ ] Position sizing correct
- [ ] Exit logic works

**Day 5+: Risk Management**
- [ ] Daily max loss enforced
- [ ] Trailing stops activate
- [ ] Re-entry logic works
- [ ] News filter blocks trading
- [ ] Alerts send successfully

---

## Testing Checklist

### Before New Bot Deployment

```
Unit Tests:
├─ [ ] EMA calculation correct
├─ [ ] ATR calculation correct
├─ [ ] ADX calculation correct
└─ [ ] Indicator tests pass

Integration Tests:
├─ [ ] Long signal detection works
├─ [ ] Short signal detection works
├─ [ ] ADX filter blocks low-ADX entries
└─ [ ] Session filter blocks off-hours

CSV Backtest:
├─ [ ] No errors in logs
├─ [ ] Profit factor > 1.5
├─ [ ] Win rate reasonable
├─ [ ] Trade count appropriate
└─ [ ] Max DD acceptable

Persistence Tests:
├─ [ ] State saves correctly
├─ [ ] State loads on restart
└─ [ ] Mid-trade resume works

Paper Trading:
├─ [ ] Runs for 3-5 days without errors
├─ [ ] Entries/exits execute
├─ [ ] Risk management works
└─ [ ] Performance matches backtest
```

---

## Continuous Testing

### When to Test

**Before commits:**
```bash
# Run unit tests
pytest tests/test_indicators.py

# Run integration tests
pytest tests/test_signals.py

# Quick CSV backtest
python bot_keltner.py --csv data/nq_2m_sample.csv
```

**Weekly:**
```bash
# Full test suite
pytest tests/

# Full CSV backtest
python bot_keltner.py --csv data/nq_2m_2024.csv

# Paper trade 1 day
```

**Monthly:**
```bash
# Regression test on multiple datasets
python bot_keltner.py --csv data/nq_2m_2023.csv
python bot_keltner.py --csv data/nq_2m_2024.csv

# Verify performance hasn't degraded
```

---

## See Also

- [TEST_SUITE.md](../templates/TEST_SUITE.md) - Test template
- [REFACTOR.md](workflow-refactor.md) - Refactoring guide
- [WORKFLOW.md](workflow-interactive.md) - Bot creation workflow
- [BASE_BOT.md](../templates/base_bot.py.md) - Bot template
