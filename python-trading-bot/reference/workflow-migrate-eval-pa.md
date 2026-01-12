# Migrate Eval to PA Workflow

Step-by-step workflow for converting an evaluation bot to PA (funded account) mode.

---

## Overview

After passing your Apex evaluation, you need to convert your bot from eval mode to PA mode. This changes:
- **Drawdown**: Trailing → Static
- **Position sizing**: Fixed contracts → Risk-based % of equity
- **Profit target**: Remove (trade indefinitely)
- **Risk profile**: Aggressive → Conservative

**CRITICAL:** Only migrate after confirmed profit target reached and PA account activated.

---

## Quick Command

```bash
/bot:migrate-pa <bot_name>
```

**Example:**
```bash
/bot:migrate-pa keltner
```

---

## Prerequisites Checklist

Before migrating:
- [ ] **Profit target reached** in eval mode
- [ ] **Apex confirmed PA conversion** (email/dashboard)
- [ ] **New starting balance known** (eval balance + profit)
- [ ] **Bot not currently running** live
- [ ] **Backup created** (`git tag eval-v1.0`)

---

## Manual Workflow

### Step 1: Verify Eval Completion

**Check logs for profit target:**
```bash
grep "PROFIT TARGET" bot_keltner.log
# Should see: "🎉 PROFIT TARGET REACHED! Account eligible for PA conversion."
```

**Verify final equity:**
```bash
# For 50K eval with $3000 target
grep "Account Equity" bot_keltner.log | tail -1
# Should show: $53,000+ (starting $50K + $3K target)
```

**Document eval results:**
```
Eval Mode Results (50K):
- Starting Balance: $50,000
- Final Equity: $53,245
- Profit: $3,245
- Profit Target: $3,000 ✅
- DD Breached: No ✅
- Ready for PA: Yes ✅
```

---

### Step 2: Backup Current Bot

```bash
# Tag current eval version
git tag keltner-eval-v1.0
git push origin keltner-eval-v1.0

# Create PA branch
git checkout -b keltner-pa-mode

# Or backup directory
cp -r bot_keltner bot_keltner_eval_backup
```

---

### Step 3: Update Configuration

Edit `config.py`:

```python
@dataclass
class Config:
    # ... existing config ...

    # Apex Account Configuration
    account_mode: str = "pa"  # CHANGED from "eval"
    account_size: str = "50K"  # KEEP SAME
    risk_pct: float = 0.015  # ADDED (1.5% to start conservative)

    # Position sizing (REMOVED - now dynamic)
    # contracts: int = 5  # REMOVE THIS

    def __post_init__(self):
        # ... existing __post_init__ ...

        self.account_mode = os.getenv("ACCOUNT_MODE", self.account_mode)
        self.account_size = os.getenv("ACCOUNT_SIZE", self.account_size)
        self.risk_pct = float(os.getenv("RISK_PCT", str(self.risk_pct)))

        # REMOVED: Load fixed contracts
        # self.contracts = int(os.getenv("CONTRACTS", str(self.contracts)))
```

Edit `.env`:

```bash
# Apex Account Configuration
ACCOUNT_MODE=pa  # CHANGED from eval
ACCOUNT_SIZE=50K  # KEEP SAME
RISK_PCT=0.015  # ADDED (start at 1.5%, can increase to 2% later)

# Position sizing (REMOVED)
# CONTRACTS=5  # REMOVE THIS LINE
```

---

### Step 4: Verify Bot Code

The bot should already use `risk_manager.get_position_size()` if built from recent template. Verify:

```python
# In _check_entries()
atr = curr["atr"]
contracts = self.risk_manager.get_position_size(atr)  # ✅ Dynamic sizing

# NOT this (old way):
# contracts = self.config.contracts  # ❌ Fixed sizing
```

If bot uses fixed sizing, update to dynamic:

```python
# OLD (eval mode - fixed)
async def _check_entries(self, curr: dict, prev: dict):
    # ...
    if long_sig:
        await self._enter_position(1, curr["close"], sl_pts, tp_pts, self.config.contracts)

# NEW (PA mode - dynamic)
async def _check_entries(self, curr: dict, prev: dict):
    # ... Get position size from risk manager
    atr = curr["atr"]
    contracts = self.risk_manager.get_position_size(atr)

    if long_sig:
        await self._enter_position(1, curr["close"], sl_pts, tp_pts, contracts)
```

---

### Step 5: Reset State Database (Optional)

**Option 1: Start fresh** (recommended)
```bash
# Remove old eval state
rm bot_state.db

# Will create new PA state on first run
```

**Option 2: Preserve state**
```bash
# Keep database to maintain equity from eval
# RiskManager will load saved equity and continue
```

**Recommendation:** Start fresh with PA starting balance (eval final balance becomes new starting point).

---

### Step 6: Update Starting Balance in Code

If using persistence and NOT resetting database, update the Apex account starting balance:

Edit `risk_manager.py` or run one-time script:

```python
# One-time adjustment to set PA starting balance
from state_db import StateDB

db = StateDB("bot_state.db")

# Load current state
state = db.load_account_state()

if state:
    # Reset equity to 0 (PA starts fresh from eval final balance)
    db.cursor.execute("""
        UPDATE account_state
        SET equity = 0,
            high_water_mark = 0,
            dd_threshold = -2500,  -- Static DD for 50K PA
            dd_locked = 0,
            profit_target_hit = 0
        WHERE id = 1
    """)
    db.conn.commit()
    print("Account reset for PA mode")

db.close()
```

---

### Step 7: CSV Backtest Validation

Test PA sizing logic with realistic equity:

```bash
# Create test config with PA starting balance
# Temporarily modify config.py or create test config

python bot_keltner.py --csv data/nq_2m_2024.csv > pa_test.log

# Verify dynamic sizing
grep "Position size:" pa_test.log | head -10

# Example output:
# Position size: 1 contracts (risk-based: $795 / $600 = 1.32 → 1)
# Position size: 1 contracts (risk-based: $810 / $600 = 1.35 → 1)
# Position size: 2 contracts (risk-based: $1200 / $600 = 2.0 → 2)

# Should see contracts increase as equity grows
```

---

### Step 8: Paper Trade PA Mode

**CRITICAL:** Paper trade for at least 3-5 days before going live.

```bash
# Start in paper mode
python bot_keltner.py --paper

# Monitor for issues:
# - Contracts scaling correctly?
# - Static DD enforced?
# - No profit target checks?
# - Risk % appropriate?
```

**Watch for:**
- Contracts should be 1-2 at start (lower than eval's 5)
- Contracts should increase as equity grows
- No "Profit target reached" messages (removed in PA)
- Drawdown remains static (doesn't trail)

---

### Step 9: Adjust Risk % (After Testing)

After paper trading success, consider increasing risk:

```bash
# Start conservative
RISK_PCT=0.015  # 1.5%

# After 1 week of success, increase
RISK_PCT=0.017  # 1.7%

# After 2 weeks, approach standard
RISK_PCT=0.02  # 2.0% (standard PA risk)

# Never go above
RISK_PCT=0.025  # 2.5% (absolute max)
```

---

### Step 10: Go Live with PA

**Final checklist before live PA:**
- [ ] Paper traded successfully for 3+ days
- [ ] No errors in logs
- [ ] Contracts scaling as expected
- [ ] Risk % set appropriately (1.5-2%)
- [ ] Static DD enforced
- [ ] Alerts configured and tested
- [ ] News filter working
- [ ] State persistence working

**Go live:**
```bash
python bot_keltner.py --live
# Type 'CONFIRM' when prompted
```

**Monitor closely:**
- First week: Check logs daily
- Verify position sizing correct
- Ensure DD room monitored
- Watch for any anomalies

---

### Step 11: Commit Changes

```bash
git add .
git commit -m "feat(keltner): migrate from eval to PA mode

Converted bot after passing 50K evaluation:
- Changed ACCOUNT_MODE=eval → ACCOUNT_MODE=pa
- Added RISK_PCT=0.015 for dynamic position sizing
- Removed fixed CONTRACTS parameter
- Static DD enforced ($2,500 from starting balance)
- Profit target checks removed (trade indefinitely)

Eval Results:
- Starting: $50,000
- Final: $53,245
- Target: $3,000 ✅
- Time: 14 days

PA Configuration:
- Starting balance: $53,245
- Risk per trade: 1.5%
- Static DD: $2,500 (breach at $50,745)
- Initial contracts: 1-2 (vs 5 in eval)

Tested in paper mode for 5 days successfully."

git push origin keltner-pa-mode
```

---

## Key Differences: Eval vs PA

| Feature | Eval Mode | PA Mode |
|---------|-----------|---------|
| **Goal** | Hit profit target | Consistent profitability |
| **Drawdown** | Trailing (moves up) | Static (fixed from start) |
| **DD Threshold** | Locks at balance when target hit | Never changes |
| **Position Size** | Fixed contracts | Risk-based % of equity |
| **Contracts** | Set once (e.g., 5 for 50K) | Scales with account growth |
| **Risk Profile** | Aggressive | Conservative |
| **Auto-Stop** | Yes (profit target) | No (trade indefinitely) |
| **Stop Condition** | Target hit OR DD breach | DD breach only |

---

## Position Sizing Examples

### 50K PA Account

```
Starting Balance: $53,000 (after eval)
Risk Per Trade: 1.5%
Static DD: $2,500 (breach at $50,500)

Trade 1 (Day 1):
- Equity: $53,000
- Risk: $795 (1.5% of $53,000)
- ATR: 10 points
- SL Distance: 30 points (3.0 × ATR)
- Contracts: $795 / (30 × $20) = 1.32 → 1 contract

Trade 50 (Week 4):
- Equity: $58,000 (+$5,000)
- Risk: $870 (1.5% of $58,000)
- ATR: 10 points
- SL Distance: 30 points
- Contracts: $870 / (30 × $20) = 1.45 → 1 contract

Trade 150 (Week 12):
- Equity: $70,000 (+$17,000)
- Risk: $1,050 (1.5% of $70,000)
- ATR: 10 points
- SL Distance: 30 points
- Contracts: $1,050 / (30 × $20) = 1.75 → 1 contract

Trade 200 (Week 16):
- Equity: $85,000 (+$32,000)
- Risk: $1,275 (1.5% of $85,000)
- ATR: 10 points
- SL Distance: 30 points
- Contracts: $1,275 / (30 × $20) = 2.12 → 2 contracts
```

**Notice:** Contracts grow slowly. Need significant equity increase to trade more contracts.

---

## Risk % Guidelines

### Start Conservative (Week 1-2)

```bash
RISK_PCT=0.01  # 1.0% (very conservative)
# or
RISK_PCT=0.015  # 1.5% (recommended start)
```

### Standard PA (Week 3+)

```bash
RISK_PCT=0.02  # 2.0% (standard after proven)
```

### Aggressive PA (Experienced only)

```bash
RISK_PCT=0.025  # 2.5% (max, only if consistently profitable)
```

**Never exceed 2.5%** - Risk of quick drawdown too high.

---

## Monitoring PA Mode

### Daily Checks

```bash
# Check equity and DD room
grep "Account Equity" bot_keltner.log | tail -1
grep "DD Room" bot_keltner.log | tail -1

# Verify no DD breach
grep "DRAWDOWN BREACHED" bot_keltner.log
# Should be empty

# Check position sizing
grep "Position size:" bot_keltner.log | tail -5
# Verify contracts reasonable for current equity
```

### Weekly Review

```
Metrics to track:
- Total P&L (cumulative)
- Win rate (should stay similar to eval)
- Largest drawdown (stay well above DD threshold)
- Max contracts traded (should increase over time)
- Risk-adjusted return
```

---

## Troubleshooting

### Issue: Contracts Not Scaling

**Symptoms:** Always 1 contract even after significant profit

**Debug:**
```python
# Add logging
logger.info(f"Equity: {equity}, Risk: {risk_per_trade}, SL: {sl_distance}, Contracts: {contracts}")
```

**Check:**
- Risk % set correctly in .env?
- ATR reasonable? (if very high, fewer contracts)
- SL multiplier too large? (wider stops = fewer contracts)

---

### Issue: DD Breach Alert

**Symptoms:** "DRAWDOWN BREACHED" alert

**Immediate Action:**
1. Stop bot immediately
2. Review all trades
3. Check if legitimate breach or bug
4. Contact Apex support if real breach

**Prevention:**
- Monitor DD room daily
- Alert at 80% of DD ($2,000 room left for 50K)
- Never risk more than 2% per trade
- Consider reducing risk if approaching DD

---

### Issue: Performance Degraded from Eval

**Symptoms:** Win rate dropped, fewer profits

**Possible Causes:**
1. **Fewer contracts** - Expected in PA, lower absolute profit
2. **Market change** - Different conditions than eval period
3. **Risk too conservative** - Increase RISK_PCT slightly
4. **Strategy needs adjustment** - May need parameter tuning

**Solution:**
- Compare on same data period
- Adjust risk % if too conservative
- Consider if market regime changed
- Review if strategy still appropriate

---

## Best Practices

1. **Start conservative** - 1.5% risk, increase gradually
2. **Paper trade first** - Minimum 3-5 days
3. **Monitor closely** - Daily checks first month
4. **Slow scale-up** - Don't rush to 2% risk
5. **Track metrics** - Document all changes
6. **Keep eval strategy** - Don't over-optimize
7. **Preserve capital** - DD breach ends account

---

## Common Mistakes

### Mistake 1: Starting Too Aggressive

```bash
# WRONG
RISK_PCT=0.03  # 3% - too high for PA

# RIGHT
RISK_PCT=0.015  # 1.5% - conservative start
```

### Mistake 2: Not Paper Trading

```bash
# WRONG
# Immediately go live after passing eval

# RIGHT
# Paper trade for at least 3-5 days to verify PA logic
```

### Mistake 3: Forgetting to Remove Fixed Contracts

```python
# WRONG
contracts = self.config.contracts  # Still using eval fixed sizing

# RIGHT
contracts = self.risk_manager.get_position_size(atr)  # Dynamic PA sizing
```

### Mistake 4: Not Monitoring DD Room

```bash
# WRONG
# Ignore DD room until too late

# RIGHT
# Alert at 80% of DD, monitor daily
```

---

## Recovery Plan (if DD Breached)

**If you breach drawdown:**
1. Account is terminated (Apex rule)
2. Profit earned is lost
3. Cannot trade this account further

**Prevention is critical:**
- Conservative risk %
- Daily monitoring
- Quick response to losses
- Never trade emotionally
- Follow strategy strictly

**If breach occurs:**
1. Document what happened
2. Review trades to understand cause
3. Adjust strategy if needed
4. Purchase new eval account
5. Start over with lessons learned

---

## See Also

- [EVAL_VS_PA.md](eval-vs-pa.md) - Detailed eval vs PA comparison
- [APEX_RULES.md](apex-compliance.md) - Apex compliance requirements
- [APEX_INTEGRATION.md](../templates/APEX_INTEGRATION.md) - Technical integration
- [RISK_MANAGER.md](../templates/risk_manager.py.md) - Risk manager template
- [REFACTOR.md](workflow-refactor.md) - Main refactoring guide
