# Bot Refactoring Guide

Comprehensive guide for modifying existing trading bots without starting from scratch.

---

## Contents

- [Overview](#overview)
- [When to Refactor vs Create New](#when-to-refactor-vs-create-new)
- [Refactoring Commands](#refactoring-commands)
- [Refactoring Workflows](#refactoring-workflows)
- [Refactoring Best Practices](#refactoring-best-practices)
- [Safety Protocols](#safety-protocols)
- [Common Refactoring Scenarios](#common-refactoring-scenarios)
- [Refactoring Checklist](#refactoring-checklist)

---

## Overview

The bot refactoring system allows you to modify existing bots by:
- Adding new features (indicators, filters, alerts)
- Removing features (clean removal without breaking dependencies)
- Changing indicators or signals
- Migrating between modes (eval → PA, strategy changes)
- Upgrading to new templates (add production features to old bots)

**Key Principle:** Preserve what works, change only what's needed.

---

## When to Refactor vs Create New

### Refactor Existing Bot ✅

Use refactoring when:
- Bot is profitable but needs tweaks (add filter, adjust parameters)
- Adding production features (news filter, alerting, persistence)
- Migrating from eval to PA mode after passing evaluation
- Changing one indicator while keeping strategy logic
- Removing underperforming features
- Upgrading from old template to new architecture

### Create New Bot ✅

Create new bot when:
- Testing completely different signal/strategy
- Starting fresh with different ticker/market
- Experimenting with unproven approach
- Need clean separation from existing bot

**Rule of Thumb:** If > 50% of code would change, create new bot. If < 50%, refactor.

---

## Refactoring Commands

### Interactive Refactoring

```bash
/bot:refactor <bot_name>
```

Starts interactive session where Claude will:
1. Read all bot files
2. Understand current configuration
3. Ask what you want to change
4. Suggest refactoring approach
5. Make code changes
6. Update tests
7. Recommend backtest validation

**Example:**
```
User: /bot:refactor keltner
Claude: I've read your Keltner bot files. What would you like to modify?
User: Add news calendar integration and email alerts
Claude: I'll add news_calendar.py and alert_manager.py, update config.py with new parameters, and integrate into bot_keltner.py. Proceed?
User: yes
Claude: [Makes changes] Done! Run `python bot_keltner.py --csv data/nq_2m.csv` to test.
```

### Targeted Refactoring

For specific, well-defined changes:

```bash
/bot:add-feature <bot_name> <feature>
/bot:remove-feature <bot_name> <feature>
/bot:migrate-pa <bot_name>
/bot:analyze <bot_name>
```

**Examples:**
```bash
# Add specific features
/bot:add-feature keltner news_filter
/bot:add-feature vwap persistence
/bot:add-feature ema_cross alerting

# Remove features
/bot:remove-feature keltner volume_filter
/bot:remove-feature supertrend reentry

# Migrate eval → PA
/bot:migrate-pa keltner

# Analyze code quality
/bot:analyze keltner
```

---

## Refactoring Workflows

### 1. Adding a Feature

See [workflow-add-feature.md](workflow-add-feature.md) for detailed workflow.

**Quick Summary:**
1. Identify dependencies (what files need the feature)
2. Add configuration parameters
3. Create new module (if needed)
4. Integrate into bot
5. Test with CSV backtest

**Common Features to Add:**
- News calendar filtering
- Email/SMS alerting
- State persistence
- Additional indicators (RSI, MACD, etc.)
- New filters (volume, session, ADX modes)
- Trailing stop variations

### 2. Removing a Feature

See [workflow-remove-feature.md](workflow-remove-feature.md) for detailed workflow.

**Quick Summary:**
1. Identify all uses of feature
2. Remove from config
3. Remove from bot code
4. Remove imports
5. Clean up conditional logic
6. Test to ensure nothing broke

**Common Features to Remove:**
- Re-entry logic (simplify strategy)
- Volume filter (not helping)
- Specific indicator (e.g., remove MACD, keep EMA)
- Trailing stop (use fixed TP instead)

### 3. Changing Indicators

See [workflow-change-indicator.md](workflow-change-indicator.md) for detailed workflow.

**Quick Summary:**
1. Understand current indicator calculations
2. Add new indicator to `indicators.py`
3. Update signal detection in `bot_*.py`
4. Update config parameters
5. Backtest to compare performance

**Example:** Replace Keltner with Bollinger Bands
- Keep: Entry logic (breakout), ADX filter, re-entry, risk management
- Change: Channel calculation (Keltner → Bollinger)
- Update: Config (`keltner_mult` → `bb_mult`)

### 4. Migrating Eval → PA

See [workflow-migrate-eval-pa.md](workflow-migrate-eval-pa.md) for detailed workflow.

**Quick Summary:**
1. Verify profit target reached in eval mode
2. Change `ACCOUNT_MODE=pa` in `.env`
3. Set `RISK_PCT=0.015` (start conservative)
4. Remove `contracts` config (now dynamic)
5. Backtest to verify sizing logic works
6. Monitor first week closely

---

## Refactoring Best Practices

### 1. Always Backtest First

```bash
# Before changes
python bot_keltner.py --csv data/nq_2m_2024.csv > before.log

# After changes
python bot_keltner.py --csv data/nq_2m_2024.csv > after.log

# Compare
diff before.log after.log
```

**What to check:**
- Same number of trades (if strategy unchanged)
- Similar P&L (small differences from rounding OK)
- No new errors or warnings
- New features working as expected

### 2. Version Control

```bash
# Create branch before refactoring
git checkout -b refactor-add-news-filter

# Make changes
# ...

# Commit with descriptive message
git add .
git commit -m "refactor(keltner): add news calendar integration

- Added news_calendar.py module
- Updated config.py with news filter params
- Integrated blackout checks in bot_keltner.py
- Added .env.example with FMP API key
- Tested with CSV backtest: 0 trades during blackout periods"

# Merge back when validated
git checkout main
git merge refactor-add-news-filter
```

### 3. Incremental Changes

**Good:** One feature at a time
```
1. Add news filter → test → commit
2. Add alerting → test → commit
3. Add persistence → test → commit
```

**Bad:** Everything at once
```
Add news filter + alerting + persistence + new indicator → ???
(Too many variables, can't debug)
```

### 4. Keep Old Version

```bash
# Before major refactoring
cp -r keltner keltner_backup_20260110

# Or use git tags
git tag keltner-eval-v1.0
```

If refactoring fails, you can revert.

### 5. Test Edge Cases

Don't just test happy path:
- **News filter**: Verify bot stops during blackout
- **Persistence**: Kill bot mid-trade, restart, verify resume
- **Alerting**: Trigger alert conditions (80% daily loss)
- **PA mode**: Verify contracts scale with equity changes

### 6. Update Documentation

After refactoring, update:
- `README.md` (if exists in bot dir)
- `.env.example` with new parameters
- Comments in code explaining changes
- Commit message with reasoning

---

## Safety Protocols

### Pre-Flight Checks

Before refactoring:
- [ ] Bot is not currently running live
- [ ] Recent backup exists (`git tag` or directory copy)
- [ ] CSV backtest baseline captured
- [ ] All current tests pass

### During Refactoring

- [ ] Read all relevant files first
- [ ] Understand dependencies
- [ ] Make smallest change possible
- [ ] Test immediately after each change

### Post-Refactoring Validation

- [ ] CSV backtest passes
- [ ] No new Python errors
- [ ] Configuration loads without errors
- [ ] New features work as expected
- [ ] Old features still work
- [ ] Paper trade for 1 day minimum
- [ ] Commit changes with clear message

---

## Common Refactoring Scenarios

### Scenario 1: Add News Filter to Existing Bot

**Current State:** Bot trades through all hours including news events

**Goal:** Skip trading during high-impact economic events

**Steps:**
1. Run `/bot:add-feature keltner news_filter`
2. Claude will:
   - Create `news_calendar.py`
   - Update `config.py` with news params
   - Update `.env` with `NEWS_API_KEY`
   - Add blackout checks to `bot_keltner.py`
3. Get FMP API key: https://financialmodelingprep.com/
4. Add to `.env`: `NEWS_API_KEY=your_key`
5. CSV backtest to verify blackouts work
6. Paper trade during known event (e.g., NFP Friday)

**Validation:**
```bash
# Should see blackout messages in logs
python bot_keltner.py --csv data/nq_2m_2024.csv | grep "BLACKOUT"
```

---

### Scenario 2: Remove Re-Entry Logic

**Current State:** Bot re-enters after profitable exits, sometimes over-trading

**Goal:** Simplify to single entry per signal

**Steps:**
1. Run `/bot:remove-feature keltner reentry`
2. Claude will:
   - Remove re-entry params from `config.py`
   - Remove re-entry logic from `_check_signal()`
   - Remove re-entry state tracking variables
   - Update `.env.example`
3. CSV backtest to compare:
   - Fewer trades expected
   - May reduce profit or may reduce drawdown

**Validation:**
```bash
# Count trades before/after
grep "ENTRY:" before.log | wc -l  # e.g., 45 trades
grep "ENTRY:" after.log | wc -l  # e.g., 25 trades (no re-entries)
grep "RE-ENTRY:" after.log | wc -l  # Should be 0
```

---

### Scenario 3: Change Keltner → Bollinger Bands

**Current State:** Using Keltner Channels for breakout signals

**Goal:** Test if Bollinger Bands perform better

**Steps:**
1. Run `/bot:refactor keltner`
2. Tell Claude: "Replace Keltner with Bollinger Bands"
3. Claude will:
   - Add `bb_period`, `bb_mult` to config
   - Remove `keltner_period`, `keltner_mult`
   - Update `indicators.py` to calculate Bollinger
   - Update signal logic: `close > upper_band` → long
   - Rename bot? Keep as `bot_keltner.py` or rename to `bot_bb.py`
4. Backtest both strategies side-by-side
5. Compare profit factor, win rate, max drawdown

**Validation:**
```bash
# Backtest original
python bot_keltner.py --csv data/nq_2m_2024.csv > keltner.log

# Backtest modified (now Bollinger)
python bot_keltner.py --csv data/nq_2m_2024.csv > bollinger.log

# Compare results
grep "Total P&L" keltner.log
grep "Total P&L" bollinger.log
```

---

### Scenario 4: Upgrade Old Bot to New Template

**Current State:** Bot from 6 months ago, missing new features

**Goal:** Add persistence, news filter, alerting, Apex integration

**Steps:**
1. Run `/bot:refactor supertrend`
2. Tell Claude: "Upgrade to latest template with all production features"
3. Claude will:
   - Replace `tradovate_client` with `databento_provider`
   - Add `apex_account` integration
   - Add `news_calendar.py`, `alert_manager.py`
   - Update `risk_manager.py` with persistence
   - Update `bot_supertrend.py` to new structure
   - Update `config.py` with all new params
4. Create `.env` with new settings
5. CSV backtest to verify behavior unchanged (except new features)
6. Test persistence: start bot, kill mid-trade, restart

**Validation:**
- Bot starts without errors
- Logs show: "Loaded saved state from database"
- Alerts send successfully (test)
- News filter works (check logs during event)

---

### Scenario 5: Migrate from Eval to PA Mode

**Current State:** Hit $3000 profit target on 50K eval, ready for PA

**Goal:** Convert bot to PA mode with risk-based sizing

**Steps:**
1. **CRITICAL:** Verify profit target hit in logs
2. Run `/bot:migrate-pa keltner`
3. Claude will:
   - Change `ACCOUNT_MODE=pa` in `.env`
   - Add `RISK_PCT=0.015` (1.5% to start)
   - Remove fixed `contracts` setting
   - Update position sizing to use `get_position_size()`
   - Convert trailing DD to static DD
   - Remove profit target checks
4. CSV backtest with starting equity of $53,000 (post-eval)
5. Verify contracts scale: 1-2 at start, more as equity grows

**Validation:**
```bash
# Should see dynamic contract sizing in logs
python bot_keltner.py --csv data/nq_2m_2024.csv | grep "Position size:"

# Example output:
# Position size: 1 contracts (risk-based: $795 / $600 = 1.32 → 1)
# Position size: 2 contracts (risk-based: $1150 / $600 = 1.92 → 2)
```

---

## Refactoring Checklist

Use this checklist for every refactoring:

### Pre-Refactoring
- [ ] Identified what needs to change
- [ ] Understood why (problem to solve or feature to add)
- [ ] Created git branch or backup
- [ ] Captured CSV backtest baseline
- [ ] Bot not running live

### During Refactoring
- [ ] Read all relevant files
- [ ] Made minimal necessary changes
- [ ] Updated configuration
- [ ] Updated tests (if exist)
- [ ] Tested incrementally

### Post-Refactoring
- [ ] CSV backtest passes
- [ ] No Python errors
- [ ] New features work
- [ ] Old features still work
- [ ] Committed changes with clear message
- [ ] Updated documentation
- [ ] Paper traded for 1+ days
- [ ] Reviewed results before going live

---

## Troubleshooting Refactoring

### Issue: Bot won't start after refactoring

**Symptoms:**
```
ImportError: cannot import name 'NewsCalendar' from 'news_calendar'
```

**Fix:**
```bash
# Check file exists
ls news_calendar.py

# Check Python syntax
python -m py_compile news_calendar.py

# Check import path
grep "from news_calendar import" bot_keltner.py
```

### Issue: Features not working

**Symptoms:** News filter enabled but bot still trading during blackout

**Debug:**
```python
# Add debug logging
logger.info(f"News filter enabled: {self.config.news_filter_enabled}")
logger.info(f"Events today: {len(self.news_calendar.events)}")
logger.info(f"Is blackout: {self.news_calendar.is_blackout_period(bar['timestamp'])}")
```

### Issue: Performance degraded after refactoring

**Symptoms:** Profit factor dropped from 10.0 to 5.0

**Investigate:**
```bash
# Compare trade counts
grep "ENTRY:" before.log | wc -l
grep "ENTRY:" after.log | wc -l

# Compare win rates
grep "EXIT.*P&L: \$" before.log | grep "+" | wc -l
grep "EXIT.*P&L: \$" after.log | grep "+" | wc -l

# Look for new filters blocking trades
grep "Skipping" after.log
```

### Issue: Tests failing after refactoring

**Symptoms:**
```
AssertionError: Expected 45 trades, got 25
```

**Fix:** Update test expectations if behavior intentionally changed
```python
# If removed re-entry feature, fewer trades expected
def test_backtest():
    trades = run_backtest()
    assert len(trades) >= 20  # Lowered from 40
```

---

## Advanced Refactoring

### Multi-Bot Refactoring

Apply same change to multiple bots:

```bash
# Add news filter to all bots
for bot in keltner ema_cross vwap supertrend; do
    /bot:add-feature $bot news_filter
done
```

### Custom Refactoring

For complex changes not covered by workflows:

```bash
/bot:refactor keltner
# Then describe in detail what you want
```

Example complex refactoring:
- "Add RSI divergence filter: enter only if RSI shows divergence from price in last 10 bars"
- "Change exit logic: instead of fixed TP, exit on opposite signal"
- "Add dynamic ATR multiplier based on ADX strength"

---

## Refactoring vs Optimization

**Refactoring** = Changing code structure/features
- Add/remove features
- Change architecture
- Improve code quality
- No parameter tuning

**Optimization** = Tuning parameters for better performance
- Finding best ADX threshold
- Optimal ATR multipliers
- Position sizing
- Re-entry timing

**Note:** The python-trading-bot skill focuses on **refactoring**, not parameter optimization. For optimization, use the backtesting engine in `Python/backtest.py` with grid search.

---

## Next Steps

After understanding refactoring basics:

1. Review specific workflows:
   - [ADD_FEATURE.md](workflow-add-feature.md)
   - [REMOVE_FEATURE.md](workflow-remove-feature.md)
   - [CHANGE_INDICATOR.md](workflow-change-indicator.md)
   - [MIGRATE_EVAL_TO_PA.md](workflow-migrate-eval-pa.md)

2. Practice on existing bot:
   - Start with simple refactoring (add news filter)
   - CSV backtest to validate
   - Build confidence with incremental changes

3. Read about testing:
   - [TESTING_GUIDE.md](docs/TESTING_GUIDE.md)
   - [TEST_SUITE.md](templates/TEST_SUITE.md)

4. Learn about production features:
   - [NEWS_FILTER.md](templates/NEWS_FILTER.md)
   - [ALERTING.md](templates/ALERTING.md)
   - [PERSISTENCE.md](templates/PERSISTENCE.md)
   - [APEX_INTEGRATION.md](templates/APEX_INTEGRATION.md)

---

## See Also

- [SKILL.md](SKILL.md) - Main skill overview
- [WORKFLOW.md](WORKFLOW.md) - Bot creation workflow
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System architecture
- [CONFIG.md](CONFIG.md) - Configuration reference
- [EVAL_VS_PA.md](docs/EVAL_VS_PA.md) - Eval vs PA modes
- [APEX_RULES.md](docs/APEX_RULES.md) - Apex compliance
