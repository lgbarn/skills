# Remove Feature Workflow

Step-by-step workflow for safely removing features from existing bots.

---

## Overview

This workflow removes features that aren't working or are no longer needed. Common reasons to remove features:
- Feature not improving performance (e.g., volume filter hurting results)
- Over-complexity (simplify strategy)
- Deprecation (old code, replaced by better approach)
- Resource optimization (remove unused modules)

**Key Principle:** Clean removal without breaking dependencies.

---

## Quick Command

```bash
/bot:remove-feature <bot_name> <feature>
```

**Examples:**
```bash
/bot:remove-feature keltner reentry
/bot:remove-feature vwap volume_filter
/bot:remove-feature ema_cross trailing_stop
```

---

## Manual Workflow

### Step 1: Identify Feature Dependencies

**Find all references:**
```bash
cd bot_keltner

# Find all uses of feature
grep -r "reentry" .

# Find config parameters
grep "reentry" config.py

# Find in bot code
grep "reentry" bot_keltner.py
```

**Document what will be removed:**
- Config parameters
- Instance variables
- Methods/functions
- Imports
- Comments/documentation

---

### Step 2: Backup Current State

```bash
# Create git branch
git checkout -b remove-reentry-feature

# Or backup directory
cp -r bot_keltner bot_keltner_backup
```

**Capture baseline:**
```bash
python bot_keltner.py --csv data/nq_2m_2024.csv > before.log
```

---

### Step 3: Remove from Configuration

Edit `config.py`:

```python
@dataclass
class Config:
    # ... existing config ...

    # RE-ENTRY LOGIC (REMOVE THIS SECTION)
    # reentry_enabled: bool = True
    # reentry_bars_wait: int = 3
    # reentry_adx_min: float = 30.0
    # max_reentries: int = 10

    def __post_init__(self):
        # ... existing __post_init__ ...

        # Load re-entry settings (REMOVE THIS SECTION)
        # self.reentry_enabled = os.getenv("REENTRY_ENABLED", "true").lower() == "true"
        # self.reentry_bars_wait = int(os.getenv("REENTRY_BARS_WAIT", str(self.reentry_bars_wait)))
        # self.reentry_adx_min = float(os.getenv("REENTRY_ADX_MIN", str(self.reentry_adx_min)))
        # self.max_reentries = int(os.getenv("MAX_REENTRIES", str(self.max_reentries)))
```

Update `.env.example`:

```bash
# Re-entry Logic (REMOVE THIS SECTION)
# REENTRY_ENABLED=true
# REENTRY_BARS_WAIT=3
# REENTRY_ADX_MIN=30.0
# MAX_REENTRIES=10
```

---

### Step 4: Remove from Bot Code

Edit `bot_keltner.py`:

**Remove instance variables from `__init__()`:**
```python
def __init__(self, config: Config):
    # ... existing initialization ...

    # Re-entry state (REMOVE THIS SECTION)
    # self.last_exit_bar = -999
    # self.last_exit_profitable = False
    # self.last_exit_direction = 0
    # self.reentry_count = 0
```

**Remove from `_check_signal()`:**
```python
def _check_signal(self, curr: dict, prev: dict) -> tuple[bool, bool, bool]:
    long_sig = False
    short_sig = False
    is_reentry = False  # REMOVE THIS LINE (no longer used)

    # ... signal detection ...

    # Re-entry logic (REMOVE THIS ENTIRE SECTION)
    # if self.config.reentry_enabled and self.last_exit_profitable:
    #     bars_since_exit = self.current_bar_idx - self.last_exit_bar
    #     if bars_since_exit >= self.config.reentry_bars_wait:
    #         if self.reentry_count < self.config.max_reentries:
    #             if curr["adx"] > self.config.reentry_adx_min:
    #                 # Signal-specific re-entry logic
    #                 is_reentry = True
    #                 long_sig = True  # or short_sig = True

    # Reset reentry count on fresh signal (REMOVE THIS SECTION)
    # if not is_reentry and (long_sig or short_sig):
    #     self.reentry_count = 0

    return long_sig, short_sig, is_reentry  # CHANGE to: return long_sig, short_sig
```

**Update method signature:**
```python
def _check_signal(self, curr: dict, prev: dict) -> tuple[bool, bool]:  # Removed is_reentry
    # ...
    return long_sig, short_sig  # No longer return is_reentry
```

**Update `_check_entries()`:**
```python
async def _check_entries(self, curr: dict, prev: dict):
    # ...

    # Check for signals
    long_sig, short_sig = self._check_signal(curr, prev)  # Removed is_reentry

    # ADX filter (skip for re-entries) (SIMPLIFY - no more re-entry skip)
    if long_sig and not self._check_adx(curr, prev, 1):
        long_sig = False
    if short_sig and not self._check_adx(curr, prev, -1):
        short_sig = False

    # Execute entry
    if long_sig:
        await self._enter_position(1, curr["close"], sl_pts, tp_pts, contracts)  # Removed is_reentry
    elif short_sig:
        await self._enter_position(-1, curr["close"], sl_pts, tp_pts, contracts)  # Removed is_reentry
```

**Update `_enter_position()` signature:**
```python
async def _enter_position(
    self,
    direction: int,
    price: float,
    sl_pts: float,
    tp_pts: float,
    contracts: int,
    # is_reentry: bool,  # REMOVE THIS PARAMETER
):
    # ...

    # Remove re-entry counter increment
    # if is_reentry:
    #     self.reentry_count += 1

    action = "buy" if direction == 1 else "sell"
    # entry_type = "RE-ENTRY" if is_reentry else "ENTRY"  # REMOVE
    entry_type = "ENTRY"  # SIMPLIFIED

    logger.info(
        f"{entry_type}: {action.upper()} {contracts} contracts @ {entry:.2f} | "
        f"SL: {self.stop_loss:.2f} | TP: {self.take_profit:.2f}"
    )
```

**Remove from `_exit_position()`:**
```python
async def _exit_position(self, reason: str, exit_price: float = None):
    # ...

    # Track for re-entry (REMOVE THIS SECTION)
    # self.last_exit_bar = self.current_bar_idx
    # self.last_exit_profitable = pnl > 0
    # self.last_exit_direction = self.position
```

---

### Step 5: Clean Up Imports and Comments

Check for unused imports:

```python
# If removed entire module
# from reentry_manager import ReentryManager  # REMOVE if no longer used
```

Remove related comments:

```python
# Re-entry state tracking (REMOVE COMMENT)
```

---

### Step 6: Test with CSV Backtest

```bash
# Run backtest
python bot_keltner.py --csv data/nq_2m_2024.csv > after.log

# Check for errors
grep "ERROR" after.log
grep "undefined" after.log
grep "reentry" after.log  # Should be 0 results

# Compare behavior
grep "ENTRY:" before.log | wc -l  # e.g., 45 (with re-entries)
grep "ENTRY:" after.log | wc -l  # e.g., 25 (without re-entries)
grep "RE-ENTRY:" after.log | wc -l  # Should be 0

# Check P&L impact
grep "Total P&L" before.log
grep "Total P&L" after.log
```

---

### Step 7: Update Tests

If tests reference removed feature:

```python
# REMOVE re-entry tests
# def test_reentry_logic():
#     ...

# UPDATE other tests that assumed re-entry
def test_backtest():
    trades = run_backtest()
    assert len(trades) >= 20  # Changed from 40 (no more re-entries)
```

---

### Step 8: Validate and Commit

**Validation checklist:**
- [ ] No Python errors on startup
- [ ] No references to removed feature in logs
- [ ] CSV backtest completes successfully
- [ ] Fewer trades (expected when removing re-entry)
- [ ] Strategy logic still sound
- [ ] No broken imports

**Commit:**
```bash
git add .
git commit -m "refactor(keltner): remove re-entry logic

Removed re-entry feature to simplify strategy:
- Removed reentry config parameters
- Removed reentry state tracking
- Simplified _check_signal() and _enter_position()
- Updated tests to reflect new trade count expectations

Backtest results:
- Before: 45 trades, $12,500 P&L
- After: 25 trades, $11,800 P&L
- Simpler strategy with similar performance"
```

---

## Common Features to Remove

### Re-Entry Logic

**Impact:** Fewer trades, simpler code

**Files modified:**
- `config.py` - remove reentry params
- `bot_*.py` - remove state tracking, simplify signal logic

---

### Volume Filter

**Impact:** More trades (some low-volume entries allowed)

**Files modified:**
- `config.py` - remove volume_filter, vol_ma_period
- `bot_*.py` - remove volume check in `_check_entries()`

---

### Trailing Stop

**Impact:** All exits via fixed TP/SL

**Files modified:**
- `config.py` - remove trail params
- `bot_*.py` - remove trail logic in `_check_exits()`

---

### Custom Indicator

**Impact:** Depends on indicator usage

**Example (Remove RSI filter):**
- `indicators.py` - remove `_calculate_rsi()`
- `config.py` - remove RSI params
- `bot_*.py` - remove RSI filter in signal logic

---

## Troubleshooting

### Issue: Undefined Variable After Removal

```
NameError: name 'is_reentry' is not defined
```

**Fix:** Found a reference you missed. Search for all uses:
```bash
grep -n "is_reentry" bot_keltner.py
```

Remove or update each reference.

---

### Issue: Tests Failing

```
AssertionError: Expected 40 trades, got 25
```

**Fix:** Update test expectations to match new behavior:
```python
# Old (with re-entry):
assert len(trades) >= 40

# New (without re-entry):
assert len(trades) >= 20
```

---

### Issue: Strategy Broken After Removal

**Symptoms:** No entries, or entries at wrong times

**Debug:**
```python
# Add logging to verify signal logic still works
def _check_signal(self, curr, prev):
    logger.info(f"Checking signal: close={curr['close']}, upper={curr['upper_band']}")
    long_sig = curr["close"] > curr["upper_band"]
    logger.info(f"Long signal: {long_sig}")
    return long_sig, False
```

Check if removal inadvertently changed signal conditions.

---

## Best Practices

1. **Remove one feature at a time** - Don't remove multiple features simultaneously
2. **Test immediately** - CSV backtest after each removal
3. **Document why** - Explain in commit message why feature was removed
4. **Compare performance** - Ensure removal didn't break profitability
5. **Keep backups** - Git branch or directory copy before starting
6. **Update documentation** - Remove feature from README if it exists
7. **Clean thoroughly** - Remove ALL traces (config, code, comments, tests)

---

## Decision Framework

**Should I remove this feature?**

```
Is feature hurting performance?
├─ Yes → Remove it
└─ No
    ├─ Is it adding complexity without benefit?
    │   ├─ Yes → Remove it
    │   └─ No → Keep it
    └─ Is it unused/deprecated?
        ├─ Yes → Remove it
        └─ No → Keep it
```

**Example:**
- Re-entry logic: Adds 20 trades but -$500 P&L → **Remove**
- Volume filter: Blocks 10 trades, improves win rate 5% → **Keep**
- Trailing stop: Never activates (TP hit first) → **Remove**

---

## See Also

- [REFACTOR.md](workflow-refactor.md) - Main refactoring guide
- [ADD_FEATURE.md](workflow-add-feature.md) - Adding features
- [CHANGE_INDICATOR.md](workflow-change-indicator.md) - Changing indicators
- [TESTING_GUIDE.md](testing.md) - Testing strategies
