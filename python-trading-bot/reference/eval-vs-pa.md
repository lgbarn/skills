# Eval vs PA Mode Guide

Understanding and configuring evaluation vs performance account modes for Apex Trader Funding.

---

## Overview

The bot supports two distinct operating modes for Apex Trader Funding accounts:

1. **Eval Mode** - Evaluation accounts (path to funded account)
2. **PA Mode** - Performance Accounts (funded accounts)

Each mode has different rules, position sizing, and risk management requirements.

---

## Quick Comparison

| Feature | Eval Mode | PA Mode |
|---------|-----------|---------|
| **Goal** | Hit profit target | Consistent profitability |
| **Drawdown Type** | Trailing (moves up with equity) | Static (fixed from start) |
| **Position Sizing** | Fixed contracts | Risk-based % of equity |
| **Contracts** | Set once, doesn't change | Scales with account growth |
| **Auto-Stop** | Yes (profit target hit) | No (trade indefinitely) |
| **Risk Profile** | Aggressive (hit target fast) | Conservative (preserve capital) |

---

## Detailed Guides

### **[Eval Mode](apex-eval-mode.md)**
Evaluation account details:
- Purpose and rules
- Example 50K account walkthrough
- Configuration
- Fixed position sizing
- Behavior and best practices

### **[PA Mode](apex-pa-mode.md)**
Performance account details:
- Purpose and rules
- Example 50K account walkthrough
- Configuration
- Risk-based position sizing formula
- Behavior and best practices
- Troubleshooting

---

## Switching Between Modes

### Eval → PA Migration

After passing eval, convert your bot to PA mode:

**Option 1: Using Refactoring Command**
```
/bot:migrate-pa keltner
```

The bot will:
1. Read current bot configuration
2. Update `account_mode` from "eval" to "pa"
3. Keep same starting balance
4. Convert trailing DD to static DD
5. Enable dynamic position sizing
6. Remove profit target check
7. Update config comments
8. Test with CSV backtest to verify behavior

**Option 2: Manual Configuration**

Edit `config.py`:

```python
# Before (Eval)
account_mode: str = "eval"
account_size: str = "50K"
contracts: int = 5  # Fixed

# After (PA)
account_mode: str = "pa"
account_size: str = "50K"
risk_pct: float = 0.02  # 2% risk (contracts dynamic)
```

**IMPORTANT:** Always CSV backtest after migration to verify behavior changed correctly!

### PA → Eval (Rare)

If you want to test eval rules on a PA account:

```python
account_mode: str = "eval"
# Bot will enforce trailing DD and profit target again
```

---

## Account Size Presets

| Size | Balance | Profit Target | Trailing DD | Initial Contracts | Max Contracts |
|------|---------|---------------|-------------|-------------------|---------------|
| 25K | $25,000 | $1,500 | $1,500 | 2 | 4 |
| 50K | $50,000 | $3,000 | $2,500 | 5 | 10 |
| 75K | $75,000 | $4,000 | $2,750 | 6 | 12 |
| 100K | $100,000 | $6,000 | $3,000 | 7 | 14 |
| 150K | $150,000 | $8,000 | $5,000 | 8 | 17 |
| 250K | $250,000 | $12,500 | $6,500 | 13 | 27 |
| 300K | $300,000 | $15,000 | $7,500 | 17 | 35 |

**Special Preset:**
| Size | Balance | Profit Target | DD | Contracts | Notes |
|------|---------|---------------|-----|-----------|-------|
| 100K_STATIC | $100,000 | $2,000 | $625 (static) | 2 (fixed) | Special static eval |

---

## Best Practices

### Universal
1. **CSV Backtest First:** Always test changes in backtest mode
2. **Monitor Daily:** Check account state every day
3. **Alert on 80% DD:** Get warning before breach
4. **Keep Logs:** SQLite db tracks everything
5. **Review Weekly:** Analyze what's working

---

## See Also

- [apex-eval-mode.md](apex-eval-mode.md) - Eval account detailed guide
- [apex-pa-mode.md](apex-pa-mode.md) - PA account detailed guide
- [APEX_RULES.md](apex-rules.md) - Apex Trader Funding compliance
- [apex-accounts.md](apex-accounts.md) - Account configuration
- [../templates/APEX_INTEGRATION.md](../templates/APEX_INTEGRATION.md) - Integration template
