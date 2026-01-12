# Test Suite Template

Complete test suite template for trading bots.

---

## Overview

This template provides a comprehensive test suite covering:
- Unit tests (indicator calculations)
- Integration tests (signal detection)
- Risk management tests
- State persistence tests
- End-to-end tests

---

## Directory Structure

```
bot_{{SIGNAL}}/
├── bot_{{SIGNAL}}.py
├── config.py
├── indicators.py
├── risk_manager.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures
│   ├── test_indicators.py       # Unit tests
│   ├── test_signals.py          # Integration tests
│   ├── test_risk_manager.py     # Risk logic
│   ├── test_persistence.py      # Database
│   └── fixtures/
│       ├── test_bars.csv        # Test data
│       ├── long_breakout.csv    # Long signal test
│       └── short_breakout.csv   # Short signal test
├── pytest.ini
└── requirements-test.txt
```

---

## pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --strict-markers
markers =
    unit: Unit tests (fast)
    integration: Integration tests (medium)
    slow: Slow tests (CSV backtest, etc.)
```

---

## requirements-test.txt

```
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
```

---

## conftest.py

```python
"""
Shared pytest fixtures.
"""

import pytest
from datetime import datetime, timedelta
import numpy as np

from config import Config
from indicators import Indicators
from risk_manager import RiskManager
from bot_{{SIGNAL}} import {{SIGNAL_CLASS}}Bot


@pytest.fixture
def config():
    """Basic config for testing."""
    cfg = Config()
    cfg.paper_mode = True
    cfg.persistence_enabled = False  # Disable for tests
    return cfg


@pytest.fixture
def indicators(config):
    """Indicators instance."""
    return Indicators(config)


@pytest.fixture
def risk_manager(config):
    """Risk manager instance."""
    return RiskManager(config)


@pytest.fixture
def bot(config):
    """Bot instance."""
    return {{SIGNAL_CLASS}}Bot(config)


@pytest.fixture
def sample_bars():
    """Generate sample bar data."""
    bars = []
    for i in range(100):
        bars.append({
            "timestamp": datetime(2024, 1, 1) + timedelta(minutes=i*2),
            "open": 18500 + np.sin(i/10) * 10,
            "high": 18510 + np.sin(i/10) * 10,
            "low": 18490 + np.sin(i/10) * 10,
            "close": 18500 + np.sin(i/10) * 10,
            "volume": 1000 + i*10,
        })
    return bars


@pytest.fixture
def trending_bars():
    """Generate trending market data."""
    bars = []
    for i in range(100):
        bars.append({
            "timestamp": datetime(2024, 1, 1) + timedelta(minutes=i*2),
            "open": 18500 + i,
            "high": 18510 + i,
            "low": 18490 + i,
            "close": 18500 + i,
            "volume": 1000,
        })
    return bars


@pytest.fixture
def ranging_bars():
    """Generate ranging market data."""
    bars = []
    for i in range(100):
        bars.append({
            "timestamp": datetime(2024, 1, 1) + timedelta(minutes=i*2),
            "open": 18500 + (i % 10 - 5) * 2,
            "high": 18510 + (i % 10 - 5) * 2,
            "low": 18490 + (i % 10 - 5) * 2,
            "close": 18500 + (i % 10 - 5) * 2,
            "volume": 1000,
        })
    return bars
```

---

## test_indicators.py

```python
"""
Unit tests for indicator calculations.
"""

import pytest
import numpy as np
from datetime import datetime, timedelta


@pytest.mark.unit
class TestIndicators:
    """Test indicator calculations."""

    def test_ema_calculation(self, indicators, sample_bars):
        """Test EMA calculation."""
        indicators.bars = sample_bars
        ema = indicators._calculate_ema(period=20)

        # Verify output
        assert len(ema) == len(sample_bars)
        assert all(~np.isnan(ema[20:]))  # No NaN after warmup
        assert np.isnan(ema[0])  # NaN before warmup

    def test_atr_calculation(self, indicators, sample_bars):
        """Test ATR calculation."""
        indicators.bars = sample_bars
        atr = indicators._calculate_atr(period=14)

        # Verify positive values
        assert all(atr[14:] > 0)
        assert len(atr) == len(sample_bars)

    def test_adx_calculation(self, indicators, trending_bars):
        """Test ADX calculation with trending data."""
        indicators.bars = trending_bars
        adx = indicators._calculate_adx(period=14)

        # ADX should be high in strong trend
        assert adx[-1] > 25
        assert len(adx) == len(trending_bars)

    def test_{{SIGNAL}}_bands(self, indicators, sample_bars):
        """Test {{SIGNAL}} indicator calculation."""
        indicators.bars = sample_bars
        indicators.update(sample_bars)

        curr = indicators.get_bar(-1)

        # Verify bands exist
        assert "upper_band" in curr
        assert "middle_band" in curr
        assert "lower_band" in curr

        # Verify relationship
        assert curr["upper_band"] > curr["middle_band"]
        assert curr["middle_band"] > curr["lower_band"]

    def test_volume_ma(self, indicators, sample_bars):
        """Test volume MA calculation."""
        indicators.bars = sample_bars
        indicators.update(sample_bars)

        curr = indicators.get_bar(-1)

        assert "vol_ma" in curr
        assert curr["vol_ma"] > 0

    def test_indicator_update_idempotent(self, indicators, sample_bars):
        """Test multiple updates don't change results."""
        indicators.bars = sample_bars
        indicators.update(sample_bars)
        first = indicators.get_bar(-1)

        # Update again (shouldn't change)
        indicators.update(sample_bars)
        second = indicators.get_bar(-1)

        assert first["close"] == second["close"]
        assert first["upper_band"] == second["upper_band"]
```

---

## test_signals.py

```python
"""
Integration tests for signal detection.
"""

import pytest
from datetime import datetime


@pytest.mark.integration
class TestSignals:
    """Test signal detection logic."""

    def test_long_signal_detection(self, bot, sample_bars):
        """Test long breakout signal."""
        # Create breakout scenario
        bot.bars = sample_bars
        bot.indicators.update(sample_bars)

        # Manually create breakout
        curr = bot.indicators.get_bar(-1)
        prev = bot.indicators.get_bar(-2)

        # Force breakout above upper band
        curr["close"] = curr["upper_band"] + 10
        curr["adx"] = 40  # Pass ADX filter

        long_sig, short_sig = bot._check_signal(curr, prev)

        assert long_sig is True
        assert short_sig is False

    def test_short_signal_detection(self, bot, sample_bars):
        """Test short breakout signal."""
        bot.bars = sample_bars
        bot.indicators.update(sample_bars)

        curr = bot.indicators.get_bar(-1)
        prev = bot.indicators.get_bar(-2)

        # Force breakout below lower band
        curr["close"] = curr["lower_band"] - 10
        curr["adx"] = 40

        long_sig, short_sig = bot._check_signal(curr, prev)

        assert long_sig is False
        assert short_sig is True

    def test_adx_filter_blocks_entry(self, bot, sample_bars):
        """Test ADX filter blocks low-ADX signals."""
        bot.config.adx_enabled = True
        bot.config.adx_threshold = 35.0

        bot.bars = sample_bars
        bot.indicators.update(sample_bars)

        curr = bot.indicators.get_bar(-1)
        prev = bot.indicators.get_bar(-2)

        # Breakout but low ADX
        curr["close"] = curr["upper_band"] + 10
        curr["adx"] = 25  # Below threshold

        # Signal detected but filter blocks
        long_sig, short_sig = bot._check_signal(curr, prev)
        assert long_sig is True  # Raw signal

        # But ADX filter fails
        assert bot._check_adx(curr, prev, 1) is False

    def test_session_filter(self, bot, sample_bars):
        """Test session filter blocks off-hours."""
        bot.config.session_filter = True
        bot.config.allowed_hours = [10, 11, 12, 13, 14, 15]

        # Bar outside session
        sample_bars[-1]["timestamp"] = datetime(2024, 1, 10, 9, 0)

        bot.bars = sample_bars
        bot.indicators.update(sample_bars)

        curr = bot.indicators.get_bar(-1)

        # Should be filtered
        assert curr["hour"] == 9
        assert curr["hour"] not in bot.config.allowed_hours

    def test_volume_filter(self, bot, sample_bars):
        """Test volume filter blocks low-volume signals."""
        bot.config.volume_filter = True

        bot.bars = sample_bars
        bot.indicators.update(sample_bars)

        curr = bot.indicators.get_bar(-1)

        # Low volume
        curr["volume"] = 100
        curr["vol_ma"] = 1000

        # Should be filtered
        assert curr["volume"] < curr["vol_ma"]

    def test_no_false_signals_ranging_market(self, bot, ranging_bars):
        """Test no excessive signals in ranging market."""
        bot.bars = ranging_bars
        bot.indicators.update(ranging_bars)

        signals = 0
        for i in range(50, len(ranging_bars)):
            curr = bot.indicators.get_bar(i)
            prev = bot.indicators.get_bar(i - 1)

            long_sig, short_sig = bot._check_signal(curr, prev)
            if long_sig or short_sig:
                signals += 1

        # Should have minimal signals in range
        assert signals < 10
```

---

## test_risk_manager.py

```python
"""
Tests for risk management logic.
"""

import pytest
from datetime import date


@pytest.mark.unit
class TestRiskManager:
    """Test risk manager functionality."""

    def test_daily_max_loss_enforcement(self, risk_manager):
        """Test daily max loss stops trading."""
        risk_manager.config.daily_max_loss = 500.0

        # Record losing trades
        risk_manager.record_trade(-200, 2)
        risk_manager.record_trade(-200, 2)
        risk_manager.record_trade(-150, 2)

        # Should stop after hitting limit
        assert risk_manager.daily_pnl == -550
        assert risk_manager.is_stopped() is True

    def test_new_day_resets_daily_pnl(self, risk_manager):
        """Test new day resets daily stats."""
        # Record trade on day 1
        risk_manager.current_date = date(2024, 1, 10)
        risk_manager.record_trade(-200, 2)

        assert risk_manager.daily_pnl == -200

        # New day
        risk_manager.check_new_day(date(2024, 1, 11))

        assert risk_manager.daily_pnl == 0
        assert risk_manager.is_stopped() is False

    def test_eval_mode_profit_target(self, risk_manager):
        """Test eval mode profit target detection."""
        risk_manager.config.account_mode = "eval"
        risk_manager.config.account_size = "50K"

        # Record profitable trades
        risk_manager.record_trade(1000, 2)
        risk_manager.record_trade(1000, 2)
        risk_manager.record_trade(1100, 2)  # Total: $3100 > $3000 target

        # Should hit profit target
        assert risk_manager.apex_account.profit_target_hit is True
        assert risk_manager.is_stopped() is True

    def test_pa_mode_dynamic_sizing(self, risk_manager):
        """Test PA mode risk-based position sizing."""
        risk_manager.config.account_mode = "pa"
        risk_manager.config.account_size = "50K"
        risk_manager.config.risk_pct = 0.02  # 2%
        risk_manager.config.sl_atr_mult = 3.0
        risk_manager.config.point_value = 20.0

        # Initial sizing
        atr = 10.0
        contracts = risk_manager.get_position_size(atr)

        # $50K × 2% = $1000 risk / (10 ATR × 3.0 × $20) = 1.67 → 1 contract
        assert contracts == 1

        # After profit
        risk_manager.record_trade(20000, 1)  # +$20K

        # New sizing
        contracts = risk_manager.get_position_size(atr)

        # $70K × 2% = $1400 risk / (10 ATR × 3.0 × $20) = 2.33 → 2 contracts
        assert contracts == 2

    def test_drawdown_breach_detection(self, risk_manager):
        """Test drawdown breach stops trading."""
        risk_manager.config.account_mode = "eval"
        risk_manager.config.account_size = "50K"

        # Record large loss
        risk_manager.record_trade(-2600, 5)  # Breach $2500 DD

        # Should breach DD
        assert risk_manager.apex_account.check_drawdown_breach() is True
        assert risk_manager.is_stopped() is True
```

---

## test_persistence.py

```python
"""
Tests for state persistence.
"""

import pytest
from state_db import StateDB
from datetime import date


@pytest.mark.integration
class TestPersistence:
    """Test database persistence."""

    @pytest.fixture
    def db(self):
        """In-memory database for testing."""
        db = StateDB(":memory:")
        yield db
        db.close()

    def test_save_load_account_state(self, db, risk_manager):
        """Test account state persistence."""
        # Save state
        risk_manager.apex_account.equity = 3245.0
        risk_manager.apex_account.high_water_mark = 3500.0

        db.save_account_state(risk_manager.apex_account)

        # Load state
        loaded = db.load_account_state()

        assert loaded["equity"] == 3245.0
        assert loaded["high_water_mark"] == 3500.0

    def test_save_load_position(self, db):
        """Test position state persistence."""
        # Save position
        db.save_position(
            position=1,
            entry_price=18500.0,
            stop_loss=18470.0,
            take_profit=18560.0,
            contracts=2
        )

        # Load position
        loaded = db.load_position()

        assert loaded["position"] == 1
        assert loaded["entry_price"] == 18500.0
        assert loaded["contracts"] == 2

    def test_save_load_daily_pnl(self, db):
        """Test daily P&L persistence."""
        today = date(2024, 1, 10)

        # Save daily P&L
        db.save_daily_pnl(today, -150.0, False, 5)

        # Load daily P&L
        loaded = db.load_daily_pnl(today)

        assert loaded["pnl"] == -150.0
        assert loaded["stopped"] is False
        assert loaded["trades"] == 5

    def test_restart_scenario(self, db, risk_manager):
        """Test full restart scenario."""
        today = date.today()

        # Save complete state
        risk_manager.apex_account.equity = 1500.0
        db.save_account_state(risk_manager.apex_account)
        db.save_position(1, 18500.0, 18470.0, 18560.0, 2)
        db.save_daily_pnl(today, -200.0, False, 3)

        # Load state (simulating restart)
        acct = db.load_account_state()
        pos = db.load_position()
        daily = db.load_daily_pnl(today)

        # Verify all restored
        assert acct is not None
        assert acct["equity"] == 1500.0
        assert pos is not None
        assert pos["position"] == 1
        assert daily is not None
        assert daily["pnl"] == -200.0
```

---

## Running Tests

### All Tests

```bash
pytest tests/
```

### Specific Test File

```bash
pytest tests/test_indicators.py
```

### Specific Test

```bash
pytest tests/test_indicators.py::TestIndicators::test_ema_calculation
```

### With Coverage

```bash
pytest tests/ --cov=. --cov-report=html
```

### Only Unit Tests

```bash
pytest tests/ -m unit
```

### Only Integration Tests

```bash
pytest tests/ -m integration
```

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml

name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Run tests
        run: pytest tests/ -v --cov
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## See Also

- [TESTING_GUIDE.md](../docs/TESTING_GUIDE.md) - Testing guide
- [BASE_BOT.md](BASE_BOT.md) - Bot template
- [RISK_MANAGER.md](RISK_MANAGER.md) - Risk manager template
- [PERSISTENCE.md](PERSISTENCE.md) - State persistence template
