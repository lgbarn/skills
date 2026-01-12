# Evaluation Mode (Eval)

Evaluation account configuration and behavior for Apex Trader Funding.

---

## Purpose

Prove you can trade profitably to earn a funded account.

---

## Rules

- **Profit Target:** Must reach target profit (e.g., $3,000 on 50K account)
- **Trailing Drawdown:** Starts at account balance, trails up as you profit
- **Drawdown Lock:** Stops trailing once you reach 100% of profit target
- **Auto-Stop:** Bot stops trading when profit target reached

---

## Example: 50K Eval Account

```
Starting Balance: $50,000
Profit Target: $3,000
Trailing Drawdown: $2,500

Day 1: Equity = $50,500 (+$500)
  → DD Threshold = $48,000 ($50,500 - $2,500)
  → Still trailing

Day 2: Equity = $51,200 (+$1,200 total)
  → DD Threshold = $48,700 ($51,200 - $2,500)
  → Still trailing

Day 3: Equity = $53,100 (+$3,100 total - PROFIT TARGET HIT!)
  → DD Threshold = $50,000 (locked at starting balance)
  → Bot stops trading
  → Account eligible for PA conversion
```

---

## Configuration

```python
# config.py
account_mode: str = "eval"
account_size: str = "50K"  # 25K, 50K, 75K, 100K, 150K, 250K, 300K

# Auto-configured from APEX_ACCOUNTS preset:
balance: float = 50000
profit_target: float = 3000
trailing_dd: float = 2500
contracts: int = 5  # initial_contracts from preset
```

---

## Position Sizing (Eval)

**Fixed Contracts:**
- Contracts set at bot startup
- Never changes during eval period
- Based on account size and risk tolerance

```python
# Fixed for entire eval
self.contracts = config.initial_contracts  # e.g., 5 for 50K account
```

---

## Behavior

1. Bot tracks equity after each trade
2. Updates high water mark (HWM)
3. Calculates trailing DD threshold: `HWM - trailing_dd`
4. Checks if equity < threshold → STOP TRADING (DD breach)
5. Checks if equity >= starting_balance + profit_target → STOP TRADING (target hit!)
6. Locks DD at starting balance once profit >= target

---

## Configuration Examples

### 50K Eval Account (Aggressive)

```python
# config.py
account_mode: str = "eval"
account_size: str = "50K"

# Auto-loaded from preset:
# balance = 50000
# profit_target = 3000
# trailing_dd = 2500
# contracts = 5 (initial_contracts)
# max_contracts = 10

# Strategy settings (aggressive for eval)
entry_signal: str = "keltner"
adx_threshold: float = 35.0
sl_atr_mult: float = 3.0
tp_atr_mult: float = 3.0
reentry_enabled: bool = True
max_reentries: int = 10
```

### 25K Eval (Small Account)

```python
# config.py
account_mode: str = "eval"
account_size: str = "25K"

# Auto-loaded:
# balance = 25000
# profit_target = 1500
# trailing_dd = 1500
# contracts = 2
# max_contracts = 4

# Keep it simple for small account
daily_max_loss: float = 250.0  # Tighter than default $500
sl_atr_mult: float = 2.5  # Tighter stops
```

---

## Best Practices

1. **Be Aggressive (Safely):** Goal is to hit target quickly
2. **Use Re-Entries:** Trend continuation can multiply profits
3. **Watch Trailing DD:** Don't give back profits carelessly
4. **Track HWM:** Know how close you are to DD lock
5. **Stop When Target Hit:** Don't keep trading and risk giveback

---

## See Also

- [../EVAL_VS_PA.md](../EVAL_VS_PA.md) - Mode comparison
- [PA_MODE.md](PA_MODE.md) - Performance account mode
- [../apex-accounts.md](../apex-accounts.md) - Account presets
- [apex-rules.md](apex-rules.md) - Compliance guidelines
