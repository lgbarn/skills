# Apex Trader Funding Rules

Comprehensive guide to Apex Trader Funding evaluation and PA (Performance Account) trading rules.

---

## Overview

Apex Trader Funding is a proprietary trading firm that allows traders to trade their capital after passing an evaluation. This guide covers all rules, account types, and compliance requirements.

**Account Progression:**
```
Purchase Eval Account → Pass Evaluation → Receive PA Account → Trade for Profit Splits
```

---

## Account Types

### Evaluation Account (Eval)

**Objective:** Demonstrate profitable trading to earn a funded account

**Available Sizes:**
- 25K: $1,500 profit target, $1,000 max trailing drawdown
- 50K: $3,000 profit target, $2,500 max trailing drawdown
- 100K: $6,000 profit target, $5,000 max trailing drawdown
- 150K: $9,000 profit target, $7,500 max trailing drawdown
- 250K: $15,000 profit target, $12,500 max trailing drawdown

**Key Features:**
- One-time purchase (no recurring fees during eval)
- Unlimited trading days (no time limit)
- Trailing drawdown (moves up with equity)
- Must hit profit target to pass
- Drawdown locks when profit ≥ 100% of target

---

### PA Account (Performance Account / Funded)

**Objective:** Trade profitably for long-term income

**Same Account Sizes as Eval:**
- 25K, 50K, 100K, 150K, 250K

**Key Features:**
- No profit target (trade indefinitely)
- Static maximum drawdown (from starting balance)
- Profit splits: 90% trader / 10% Apex (after first withdrawal)
- First withdrawal: 100% to trader
- Bi-weekly payouts available
- Can scale to larger accounts with consistent profitability

---

## Drawdown Rules

### Trailing Drawdown (Eval Only)

**How it works:**
1. Starts at account size minus max DD
   - Example: 50K account → Breach at $47,500 ($50K - $2,500)
2. Trails up as account equity increases
   - Equity reaches $52,000 → Breach now at $49,500 ($52K - $2.5K)
3. **Locks** when profit ≥ 100% of target
   - 50K account hits $53,000 (100% of $3K target reached)
   - Drawdown threshold locks at $50,500 ($53K - $2.5K)
   - Even if equity grows to $60K, breach is still at $50,500

**Example (50K Eval):**
```
Starting Balance:  $50,000
Max Drawdown:      $2,500
Breach Threshold:  $47,500 (initial)

Day 5:  Equity = $52,000  →  Breach = $49,500 (trailing)
Day 10: Equity = $53,000  →  Breach = $50,500 (LOCKED - 100% of target)
Day 15: Equity = $55,000  →  Breach = $50,500 (still locked)
Day 20: Equity = $54,000  →  Breach = $50,500 (locked)

If equity ever drops below $50,500 → Account BREACHED
```

**Lock Calculation:**
```python
if profit >= profit_target:
    # Lock trailing DD
    dd_threshold = current_equity - max_dd
    dd_locked = True
```

---

### Static Drawdown (PA Only)

**How it works:**
1. Fixed from starting balance (never changes)
   - Example: 50K PA → Breach at $47,500 ($50K - $2,500)
2. Does NOT trail up with equity
   - Equity = $60K → Breach still at $47,500
   - Equity = $80K → Breach still at $47,500
3. Never locks (always measured from original starting balance)

**Example (50K PA):**
```
Starting Balance:  $50,000
Max Drawdown:      $2,500
Breach Threshold:  $47,500 (FIXED)

Day 30:  Equity = $55,000  →  Breach = $47,500 (static)
Day 60:  Equity = $62,000  →  Breach = $47,500 (static)
Day 90:  Equity = $70,000  →  Breach = $47,500 (static)

If equity EVER drops below $47,500 → Account BREACHED
```

**This is why PA mode is harder** - drawdown room doesn't grow with profit.

---

## Trading Rules (Both Account Types)

### Allowed Instruments
- Futures: NQ, ES, YM, RTY, CL, GC, etc. (CME, NYMEX, COMEX)
- **Not Allowed**: Stocks, options, forex, crypto

### Allowed Strategies
- Day trading (close before 4 PM ET)
- Swing trading (hold overnight)
- Scalping (high-frequency)
- Algorithmic trading (bots allowed)

### Prohibited Practices
- ❌ Hedging between accounts
- ❌ Copy trading between accounts
- ❌ Sharing strategies to game the system
- ❌ Exploiting platform bugs
- ❌ Trading during blackout periods (if specified)

---

## Position Sizing Rules

### Evaluation Account (Fixed Contracts)

**Recommended Sizing:**
- 25K: 1-2 contracts
- 50K: 2-5 contracts (recommended: 2-3)
- 100K: 5-10 contracts (recommended: 5-7)
- 150K: 7-15 contracts (recommended: 10)
- 250K: 12-25 contracts (recommended: 15-20)

**Risk per Trade:** Typically 1-2% of account

**Example (50K Eval with 2 contracts):**
```
Account Size: $50,000
Contracts: 2 (fixed)
Stop Loss: 30 points (3.0 × ATR with ATR=10)
Risk: 30 pts × $20 × 2 = $1,200 (2.4% of account)
```

---

### PA Account (Dynamic Sizing)

**Risk-Based Position Sizing:**
- Risk 1-2% of current equity per trade
- Contracts scale with account growth
- Calculated dynamically based on ATR and stop loss

**Formula:**
```python
risk_per_trade = equity × risk_pct
sl_distance = atr × sl_atr_mult
contracts = risk_per_trade / (sl_distance × point_value)
contracts = max(1, int(contracts))  # Minimum 1 contract
```

**Example (50K PA starting → 70K after growth):**
```
Start (Equity = $53,000):
  Risk: $795 (1.5% of $53K)
  ATR: 10 pts, SL: 3.0 × ATR = 30 pts
  Contracts: $795 / (30 × $20) = 1.32 → 1 contract

After Profit (Equity = $70,000):
  Risk: $1,050 (1.5% of $70K)
  ATR: 10 pts, SL: 3.0 × ATR = 30 pts
  Contracts: $1,050 / (30 × $20) = 1.75 → 1 contract

After More Profit (Equity = $85,000):
  Risk: $1,275 (1.5% of $85K)
  ATR: 10 pts, SL: 3.0 × ATR = 30 pts
  Contracts: $1,275 / (30 × $20) = 2.12 → 2 contracts
```

**Contracts grow slowly** - need significant equity increase to trade more size.

---

## Profit Targets (Eval Only)

**Per Account Size:**
| Account Size | Profit Target | % of Account |
|--------------|---------------|--------------|
| 25K | $1,500 | 6% |
| 50K | $3,000 | 6% |
| 100K | $6,000 | 6% |
| 150K | $9,000 | 6% |
| 250K | $15,000 | 6% |

**Rules:**
- Must reach profit target to pass evaluation
- No time limit (can take as long as needed)
- Once reached, trading automatically stops (bot should detect and stop)
- Apex reviews and converts to PA account (usually 1-3 business days)

**Bot Implementation:**
```python
if apex_account.equity >= (starting_balance + profit_target):
    apex_account.profit_target_hit = True
    logger.info("🎉 PROFIT TARGET REACHED! Account eligible for PA conversion.")
    return  # Stop trading
```

---

## Drawdown Breach Consequences

**If drawdown is breached:**
1. ❌ **Account is terminated** (cannot be recovered)
2. ❌ **All profit is lost** (no payout)
3. ❌ **Cannot re-activate same account**
4. ✅ Can purchase new evaluation account
5. ⚠️ Must start over from scratch

**This is why risk management is CRITICAL.**

---

## Evaluation Pass Requirements

**Must Have:**
✅ Reached profit target ($3,000 for 50K)
✅ Never breached trailing drawdown
✅ Followed all trading rules
✅ No prohibited practices detected

**Apex Review:**
- Usually completes in 1-3 business days
- Automated system checks compliance
- Manual review for edge cases
- Notification via email when approved

**After Approval:**
- PA account created with starting balance = eval final equity
- Example: Pass 50K eval with $53,245 → PA starts at $53,245
- Static DD threshold = $53,245 - $2,500 = $50,745

---

## PA Account Payouts

### Profit Splits

**First Withdrawal:**
- 100% to trader
- Can request after first profitable trade
- Typically $1,000-$5,000 minimum

**Subsequent Withdrawals:**
- 90% to trader
- 10% to Apex
- Bi-weekly payout schedule available

**Example (50K PA):**
```
Starting Balance: $53,000
After 1 Month: $58,000 (+$5,000 profit)

First Payout:
  Withdraw: $3,000
  Trader receives: $3,000 (100%)
  Remaining balance: $55,000

After 2 More Months: $65,000 (+$10,000 more profit)

Second Payout:
  Withdraw: $5,000
  Trader receives: $4,500 (90%)
  Apex receives: $500 (10%)
  Remaining balance: $60,000
```

### Payout Rules

- Minimum withdrawal: Varies by account size (typically $1,000-$2,000)
- Maximum withdrawal: Cannot reduce balance below starting + 20%
- Frequency: Bi-weekly or on-demand (check latest Apex rules)
- Method: Direct deposit, PayPal, wire transfer

---

## Account Scaling (PA)

**Consistent Profit = Larger Accounts**

**Scaling Path:**
- 50K → 100K (after 3+ months of consistent profit)
- 100K → 150K (after 3+ months at 100K)
- 150K → 250K (after 6+ months at 150K)
- 250K+ (elite traders only)

**Requirements for Scaling:**
- Consistent monthly profit
- No drawdown violations
- Following all rules
- Request scaling through Apex dashboard

**Example Progression:**
```
Month 1-3:  50K PA  → Profit: $12,000
Month 4-6:  100K PA → Profit: $25,000
Month 7-12: 150K PA → Profit: $45,000
Year 2:     250K PA → Profit: $120,000+
```

---

## Bot Implementation Guidelines

### Evaluation Mode Bot

**Must Implement:**
1. ✅ Fixed position sizing (contracts parameter)
2. ✅ Trailing drawdown tracking
3. ✅ Profit target detection and auto-stop
4. ✅ Drawdown lock when profit ≥ 100% of target
5. ✅ Daily P&L tracking
6. ✅ Daily max loss enforcement

**Example Code:**
```python
class ApexAccountState:
    def __init__(self, config):
        self.mode = "eval"
        self.account_size = 50000
        self.profit_target = 3000
        self.max_trailing_dd = 2500
        self.equity = 0
        self.high_water_mark = 0
        self.dd_threshold = self.account_size - self.max_trailing_dd
        self.dd_locked = False
        self.profit_target_hit = False

    def update_equity(self, pnl: float):
        self.equity += pnl

        # Update high water mark
        if self.equity > self.high_water_mark:
            self.high_water_mark = self.equity

        # Check profit target
        if self.equity >= self.profit_target and not self.profit_target_hit:
            self.profit_target_hit = True
            logger.info("🎉 PROFIT TARGET REACHED!")

        # Lock DD if profit >= 100% of target
        if self.equity >= self.profit_target and not self.dd_locked:
            self.dd_threshold = self.equity - self.max_trailing_dd
            self.dd_locked = True
            logger.info(f"Drawdown locked at ${self.dd_threshold:,.2f}")

        # Update trailing DD if not locked
        elif not self.dd_locked:
            self.dd_threshold = max(
                self.account_size - self.max_trailing_dd,
                self.high_water_mark - self.max_trailing_dd
            )
```

---

### PA Mode Bot

**Must Implement:**
1. ✅ Dynamic position sizing (risk-based %)
2. ✅ Static drawdown tracking (never changes)
3. ✅ No profit target (trade indefinitely)
4. ✅ Equity tracking for position size calculation
5. ✅ Daily P&L tracking
6. ✅ Daily max loss enforcement

**Example Code:**
```python
class ApexAccountState:
    def __init__(self, config):
        self.mode = "pa"
        self.account_size = 53000  # Starting balance from eval
        self.max_static_dd = 2500
        self.equity = 0
        self.dd_threshold = self.account_size - self.max_static_dd  # FIXED

    def update_equity(self, pnl: float):
        self.equity += pnl

        # DD threshold NEVER changes in PA mode
        # Always measured from starting balance

    def check_drawdown_breach(self) -> bool:
        current_balance = self.account_size + self.equity
        return current_balance < self.dd_threshold

def get_position_size(self, atr: float) -> int:
    """Calculate position size based on risk %"""
    current_equity = self.apex_account.account_size + self.apex_account.equity
    risk_per_trade = current_equity * self.config.risk_pct
    sl_distance = atr * self.config.sl_atr_mult
    contracts = risk_per_trade / (sl_distance * self.config.point_value)
    return max(1, int(contracts))  # Minimum 1 contract
```

---

## Common Mistakes to Avoid

### 1. Not Tracking Drawdown Correctly

**Wrong (Eval):**
```python
# Static DD in eval mode
dd_threshold = account_size - max_dd  # This never updates!
```

**Right (Eval):**
```python
# Trailing DD that updates with equity
dd_threshold = max(
    account_size - max_dd,
    high_water_mark - max_dd
)
```

---

### 2. Not Locking Drawdown at 100% Target

**Wrong:**
```python
# DD continues to trail even after profit target
if equity > high_water_mark:
    high_water_mark = equity
dd_threshold = high_water_mark - max_dd
```

**Right:**
```python
# Lock DD when profit >= 100% of target
if equity >= profit_target and not dd_locked:
    dd_threshold = equity - max_dd
    dd_locked = True

if not dd_locked:
    # Only trail if not locked
    dd_threshold = high_water_mark - max_dd
```

---

### 3. Using Fixed Contracts in PA Mode

**Wrong:**
```python
# PA mode with fixed contracts
contracts = 2  # This doesn't scale with equity!
```

**Right:**
```python
# PA mode with dynamic sizing
equity = account_size + cumulative_pnl
risk = equity * 0.015  # 1.5%
contracts = int(risk / (sl_distance * point_value))
```

---

### 4. Over-Risking Eval Account

**Wrong:**
```python
# 50K eval with 5 contracts and wide stops
contracts = 5
sl_distance = 50  # 50 points
risk = 50 * 20 * 5 = $5,000  # 10% risk - WAY TOO HIGH
```

**Right:**
```python
# 50K eval with 2 contracts and reasonable stops
contracts = 2
sl_distance = 30  # 3.0 × ATR (ATR=10)
risk = 30 * 20 * 2 = $1,200  # 2.4% risk - reasonable
```

---

### 5. Not Stopping at Profit Target

**Wrong:**
```python
# Continue trading after hitting target
if equity >= profit_target:
    logger.info("Profit target reached!")
    # But continue trading anyway...
```

**Right:**
```python
# Stop trading when target hit
if equity >= profit_target:
    profit_target_hit = True
    logger.info("🎉 PROFIT TARGET REACHED! Stopping trading.")
    return  # Exit, stop processing bars
```

---

## Risk Management Best Practices

### Evaluation Account

**Conservative Approach (Recommended):**
- Risk: 1-2% per trade
- Contracts: Lower end of range for account size
- Daily max loss: $300-$500
- Target time: 2-4 weeks (be patient, don't rush)

**Aggressive Approach (Higher Risk):**
- Risk: 2-3% per trade
- Contracts: Upper end of range
- Daily max loss: $500-$1,000
- Target time: 1-2 weeks (faster but riskier)

**Example (50K Eval):**
```
Conservative:
  Contracts: 2
  Risk per trade: $800 (1.6%)
  Daily max loss: $400
  Expected time: 3-4 weeks

Aggressive:
  Contracts: 3-4
  Risk per trade: $1,200 (2.4%)
  Daily max loss: $800
  Expected time: 1-2 weeks
```

---

### PA Account

**Start Conservative:**
- Risk: 1.5% (can increase to 2% after 1 month)
- Monitor drawdown room closely
- Alert at 80% of DD used ($2,000 remaining for 50K)
- Never exceed 2.5% risk per trade

**Scaling Risk:**
```
Week 1-4:   1.5% risk (prove consistency)
Month 2-3:  1.7% risk (if performing well)
Month 4+:   2.0% risk (standard PA risk)
Max ever:   2.5% risk (absolute ceiling)
```

---

## Monitoring and Alerts

**Critical Alerts (Must Have):**
1. 🚨 **Drawdown Breach** - Immediate notification
2. ⚠️ **DD Warning (80%)** - When 80% of DD room used
3. 🎉 **Profit Target Reached** - Eval mode only
4. 📉 **Daily Max Loss (80%)** - When approaching daily limit
5. 💰 **Large Profit/Loss** - Any trade > 10% of daily limit
6. 🔌 **Connection Lost** - Data feed disconnected

**Recommended Alerts:**
- 5 consecutive losing trades
- Unusual market conditions (high volatility)
- News events during blackout period
- Weekly P&L summary

---

## FAQ

### Can I trade multiple Apex accounts?

Yes, but **not simultaneously on the same strategy**. Trading identical strategies across multiple accounts to game the system is prohibited.

### What happens if I breach drawdown by $1?

Account is terminated. There is no grace period. Apex's systems are automated and enforce strictly.

### Can I withdraw during evaluation?

No. Evaluation accounts are simulated (not real money). Only PA accounts allow withdrawals.

### How long does PA conversion take?

Typically 1-3 business days after hitting profit target.

### Can I use bots/algos on Apex?

Yes! Algorithmic trading is explicitly allowed.

### Do I need to close positions before 4 PM ET?

No, swing trading (holding overnight) is allowed.

### What if I'm consistently profitable but hit DD?

Account is still terminated. Drawdown rules are absolute. Must purchase new eval account.

### Can I scale from 50K directly to 250K?

No. Scaling is gradual (50K → 100K → 150K → 250K). Must demonstrate consistency at each level.

---

## See Also

- [EVAL_VS_PA.md](docs/EVAL_VS_PA.md) - Detailed comparison of eval and PA modes
- [APEX_INTEGRATION.md](templates/APEX_INTEGRATION.md) - Technical implementation
- [RISK_MANAGER.md](templates/RISK_MANAGER.md) - Risk management template
- [workflow-migrate-eval-pa.md](workflow-migrate-eval-pa.md) - Migration workflow
- [Apex Trader Funding Website](https://apextraderfunding.com) - Official rules and updates
