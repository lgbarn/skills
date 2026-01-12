# Add Feature Workflow

Step-by-step workflow for adding features to existing bots.

---

## Overview

This workflow adds new functionality to an existing bot without breaking current behavior. Features can be:
- Production features (news filter, alerting, persistence)
- Indicators (RSI, MACD, Stochastic)
- Filters (volume, session, time-based)
- Risk management (trailing stops, dynamic sizing)

---

## Quick Command

```bash
/bot:add-feature <bot_name> <feature>
```

**Examples:**
```bash
/bot:add-feature keltner news_filter
/bot:add-feature vwap alerting
/bot:add-feature ema_cross persistence
/bot:add-feature supertrend rsi_filter
```

---

## Manual Workflow

### Step 1: Identify Feature Requirements

**Questions to answer:**
- What files need to change?
- Does it need a new module?
- What config parameters are needed?
- How does it integrate with existing code?

**Example (News Filter):**
- New module: `news_calendar.py`
- Config: `news_filter_enabled`, `news_api_key`, `news_blackout_minutes`
- Integration: Check blackout in `on_bar()` before trading

---

### Step 2: Read Current Bot State

```bash
# Read all bot files
ls bot_keltner/

# Understand current config
cat bot_keltner/config.py

# Check what's already integrated
grep "import" bot_keltner/bot_keltner.py
```

---

### Step 3: Add Configuration

Edit `config.py`:

```python
@dataclass
class Config:
    # ... existing config ...

    # News Filter (new)
    news_filter_enabled: bool = False
    news_api: str = "fmp"
    news_api_key: str = ""
    news_blackout_minutes: int = 30

    def __post_init__(self):
        # ... existing __post_init__ ...

        # Load news filter settings
        self.news_filter_enabled = os.getenv("NEWS_FILTER_ENABLED", "false").lower() == "true"
        self.news_api = os.getenv("NEWS_API", self.news_api)
        self.news_api_key = os.getenv("NEWS_API_KEY", "")
        self.news_blackout_minutes = int(os.getenv("NEWS_BLACKOUT_MINUTES", str(self.news_blackout_minutes)))
```

Update `.env.example`:

```bash
# News Calendar Filter
NEWS_FILTER_ENABLED=false
NEWS_API=fmp
NEWS_API_KEY=your_fmp_api_key_here
NEWS_BLACKOUT_MINUTES=30
```

---

### Step 4: Create New Module (if needed)

If feature requires new module, copy from template:

```bash
# For news filter
cp /path/to/templates/NEWS_FILTER.md bot_keltner/news_calendar.py
# Extract code from markdown, remove markdown formatting
```

Or create from scratch following template pattern.

---

### Step 5: Update Bot Code

Edit `bot_keltner.py`:

**Add import:**
```python
from news_calendar import NewsCalendar
```

**Add to `__init__()`:**
```python
def __init__(self, config: Config):
    # ... existing initialization ...
    self.news_calendar = NewsCalendar(config) if config.news_filter_enabled else None
```

**Add to `start()`:**
```python
async def start(self):
    # ... existing startup ...

    # Connect to news calendar
    if self.news_calendar:
        await self.news_calendar.connect()
        await self.news_calendar.fetch_today_events()
```

**Add to `on_bar()`:**
```python
async def on_bar(self, bar: dict):
    # ... existing bar processing ...

    # Check news blackout period
    if self.news_calendar and self.news_calendar.is_blackout_period(bar["timestamp"]):
        logger.debug("Skipping bar (news blackout)")
        return

    # ... rest of on_bar() ...
```

**Add to `stop()`:**
```python
async def stop(self):
    # ... existing shutdown ...

    # Close news calendar
    if self.news_calendar:
        await self.news_calendar.disconnect()
```

---

### Step 6: Test with CSV Backtest

```bash
# Run backtest
python bot_keltner.py --csv data/nq_2m_2024.csv > after.log

# Check for errors
grep "ERROR" after.log

# Verify feature working
grep "blackout" after.log
# Should see: "Skipping bar (news blackout)" during events

# Verify no breakage
grep "ENTRY:" before.log | wc -l  # e.g., 45
grep "ENTRY:" after.log | wc -l  # Should be similar (unless blackout blocked trades)
```

---

### Step 7: Update Tests (if exist)

If bot has `test_bot_keltner.py`:

```python
def test_news_filter():
    """Test news filter integration."""
    config = Config()
    config.news_filter_enabled = True

    bot = KeltnerBot(config)

    # Mock blackout event
    bot.news_calendar.events = [
        EconomicEvent(
            name="Test Event",
            date=datetime(2024, 1, 10, 10, 0),
            impact="High",
            country="US"
        )
    ]

    # Bar during blackout
    bar = {"timestamp": datetime(2024, 1, 10, 10, 0), "close": 18500}

    # Should skip
    await bot.on_bar(bar)
    assert bot.position == 0  # No entry
```

---

### Step 8: Validate and Commit

**Validation checklist:**
- [ ] Bot starts without errors
- [ ] New feature works as expected
- [ ] Old features still work
- [ ] CSV backtest passes
- [ ] Config parameters load correctly
- [ ] No import errors

**Commit:**
```bash
git add .
git commit -m "feat(keltner): add news calendar integration

- Added news_calendar.py module
- Updated config.py with news filter parameters
- Integrated blackout checks in on_bar()
- Added tests for news filter
- Tested with CSV backtest: 0 trades during blackout periods"
```

---

## Common Features to Add

### News Calendar Filter

**Files to modify:**
- `config.py` - add news params
- `bot_*.py` - add news_calendar, check blackout
- `.env` - add NEWS_API_KEY

**Template:** [NEWS_FILTER.md](../templates/news_filter.py.md)

---

### Email/SMS Alerting

**Files to modify:**
- `config.py` - add alert params (email, Pushover)
- `bot_*.py` - add alert_manager, send alerts
- `.env` - add SMTP and Pushover credentials

**Template:** [ALERTING.md](../templates/alerting.py.md)

---

### State Persistence

**Files to modify:**
- `risk_manager.py` - add StateDB integration
- `config.py` - add persistence params
- `.env` - add DB_PATH

**Template:** [PERSISTENCE.md](../templates/persistence.py.md)

---

### Additional Indicator (RSI)

**Files to modify:**
- `indicators.py` - add RSI calculation
- `config.py` - add rsi_period, rsi_overbought, rsi_oversold
- `bot_*.py` - add RSI filter to signal logic

**Example:**
```python
# In indicators.py
def _calculate_rsi(self, period: int = 14) -> np.ndarray:
    """Calculate RSI."""
    closes = np.array([b["close"] for b in self.bars])
    delta = np.diff(closes)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = np.convolve(gain, np.ones(period), 'valid') / period
    avg_loss = np.convolve(loss, np.ones(period), 'valid') / period

    rs = avg_gain / (avg_loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))

    return np.pad(rsi, (period, 0), constant_values=50)

# In bot_*.py signal logic
if long_sig:
    # Add RSI filter
    if curr["rsi"] > self.config.rsi_overbought:
        long_sig = False  # Overbought, skip
```

---

### Volume Filter

**Files to modify:**
- `indicators.py` - ensure volume MA calculated
- `config.py` - add volume_filter, vol_ma_period
- `bot_*.py` - check volume filter in `_check_entries()`

**Example:**
```python
# In _check_entries()
if self.config.volume_filter:
    if curr["volume"] < curr["vol_ma"]:
        return  # Low volume, skip
```

---

## Troubleshooting

### Issue: Import Error After Adding Module

```
ImportError: cannot import name 'NewsCalendar'
```

**Fix:**
```bash
# Check file exists
ls bot_keltner/news_calendar.py

# Check class name matches
grep "class NewsCalendar" bot_keltner/news_calendar.py

# Check import statement
grep "from news_calendar import" bot_keltner/bot_keltner.py
```

---

### Issue: Config Not Loading

```
AttributeError: 'Config' object has no attribute 'news_filter_enabled'
```

**Fix:**
```python
# Check config.py has the attribute
grep "news_filter_enabled" bot_keltner/config.py

# Check __post_init__() loads it
grep "NEWS_FILTER_ENABLED" bot_keltner/config.py

# Check .env has the variable
grep "NEWS_FILTER_ENABLED" bot_keltner/.env
```

---

### Issue: Feature Not Working

**Example:** News filter enabled but bot still trades during blackout

**Debug:**
```python
# Add debug logging in on_bar()
if self.news_calendar:
    logger.info(f"News filter enabled: {self.config.news_filter_enabled}")
    logger.info(f"Events today: {len(self.news_calendar.events)}")
    logger.info(f"Is blackout: {self.news_calendar.is_blackout_period(bar['timestamp'])}")
```

Check:
- Config parameter set correctly
- Events fetched successfully
- Blackout logic correct
- Return statement actually skipping

---

## Best Practices

1. **One feature at a time** - Don't add news filter + alerting + persistence simultaneously
2. **Test immediately** - CSV backtest after each change
3. **Keep it optional** - Use feature flags (`news_filter_enabled`) so feature can be disabled
4. **Follow templates** - Use existing template code instead of writing from scratch
5. **Update .env.example** - Document new environment variables
6. **Commit incrementally** - One commit per feature
7. **Paper trade** - Test in paper mode before live

---

## See Also

- [REFACTOR.md](workflow-refactor.md) - Main refactoring guide
- [REMOVE_FEATURE.md](workflow-remove-feature.md) - Removing features
- [NEWS_FILTER.md](../templates/news_filter.py.md) - News filter template
- [ALERTING.md](../templates/alerting.py.md) - Alerting template
- [PERSISTENCE.md](../templates/persistence.py.md) - Persistence template
