# Performance Account Mode (PA)

Performance account configuration and behavior for Apex Trader Funding.

---

## Purpose

Trade funded capital for ongoing profit share.

---

## Rules

- **No Profit Target:** Trade indefinitely
- **Static Drawdown:** Fixed from starting balance, never trails
- **Dynamic Sizing:** Contracts scale with account equity
- **Risk-Based:** Position size based on % risk per trade
- **Conservative:** Preserve capital, grow slowly

---

## Example: 50K PA Account

```
Starting Balance: $50,000
Static Drawdown: $2,500 (never changes)
Risk Per Trade: 2% of equity

Day 1: Equity = $50,000
  → DD Threshold = $47,500 (fixed forever)
  → Max Risk Per Trade = $1,000 (2% of $50,000)
  → Contracts = calculate_contracts($1,000, ATR, stop_loss)

Day 30: Equity = $55,000 (+$5,000)
  → DD Threshold = $47,500 (still same)
  → Max Risk Per Trade = $1,100 (2% of $55,000)
  → Contracts = recalculated (likely increased)

Day 60: Equity = $48,000 (-$2,000 from peak)
  → DD Threshold = $47,500 (still same)
  → Max Risk Per Trade = $960 (2% of $48,000)
  → Contracts = recalculated (decreased)

Day 90: Equity = $47,400 (getting close!)
  → DD Threshold = $47,500
  → DANGER: Only $100 away from DD breach
  → Bot sends alert warning

Day 91: Equity = $47,450 (daily loss hit limit)
  → Bot stops trading for the day
  → Still above DD threshold
  → Resume tomorrow
```

---

## Configuration

```python
# config.py
account_mode: str = "pa"
account_size: str = "50K"

# Auto-configured from APEX_ACCOUNTS preset:
balance: float = 50000
profit_target: float = 0  # No target in PA mode
trailing_dd: float = 2500  # Used as static DD
risk_pct: float = 0.02  # 2% risk per trade

# Contracts calculated dynamically, not fixed
```

---

## Position Sizing (PA)

**Risk-Based Sizing:**
- Contracts recalculated before each trade
- Based on current equity and ATR
- Formula: `risk_per_trade / (stop_loss_distance * point_value)`

```python
def get_position_size(self, current_equity: float, atr: float) -> int:
    """
    Calculate contracts based on risk %.

    Args:
        current_equity: Current account equity
        atr: Current ATR value

    Returns:
        Number of contracts (capped at max_contracts)
    """
    # Risk amount per trade
    risk_per_trade = current_equity * self.config.risk_pct  # e.g., 2%

    # Stop loss distance in points
    sl_distance = atr * self.config.sl_atr_mult  # e.g., 3.0 × ATR

    # Calculate contracts
    contracts = int(risk_per_trade / (sl_distance * self.config.point_value))

    # Cap at max for account size
    contracts = min(contracts, self.config.max_contracts)

    # Floor at 1 (always trade at least 1 contract)
    contracts = max(1, contracts)

    return contracts
```

---

## Behavior

1. Bot calculates position size before each trade (dynamic)
2. Tracks equity continuously
3. Checks if equity < (starting_balance - static_dd) → STOP TRADING (DD breach)
4. No profit target check (trade indefinitely)
5. Contracts increase as equity grows
6. Contracts decrease as equity shrinks

---

## Configuration Examples

### 50K PA Account (Conservative)

```python
# config.py
account_mode: str = "pa"
account_size: str = "50K"
risk_pct: float = 0.015  # 1.5% (more conservative than default 2%)

# Auto-loaded from preset:
# balance = 50000
# profit_target = 0 (no target in PA)
# trailing_dd = 2500 (used as static DD)
# max_contracts = 10

# Strategy settings (conservative for PA)
entry_signal: str = "ema_cross"
adx_threshold: float = 40.0  # Higher filter
sl_atr_mult: float = 3.5  # Wider stops
tp_atr_mult: float = 2.5  # Tighter profits
reentry_enabled: bool = False  # No re-entries in PA
```

---

## Best Practices

1. **Be Conservative:** Capital preservation first
2. **Start Small:** Use lower risk_pct (1.5% vs 2%)
3. **Scale Slowly:** Let equity compound naturally
4. **Monitor Static DD:** No trailing safety net
5. **Diversify Signals:** Consider multiple strategies
6. **No Hero Trades:** Survive to trade tomorrow

---

## Troubleshooting

### Issue: Bot Trading Too Many Contracts in PA

**Check:**
1. Current equity
2. ATR value
3. risk_pct setting
4. Calculation: `(equity × risk_pct) / (ATR × sl_atr_mult × point_value)`

**Solution:**
- Lower `risk_pct` (e.g., 0.015 instead of 0.02)
- Increase `sl_atr_mult` (wider stops = fewer contracts)
- Manually cap in config: `max_contracts_override = 5`

### Issue: Position Size Not Changing in PA

**Check:**
1. Verify `account_mode = "pa"` in config
2. Check `risk_manager.get_position_size()` is being called
3. Look for "Position size: N contracts (risk-based)" in logs

**Solution:**
- Re-run `/bot:migrate-pa` to ensure PA logic active
- Check bot code calls `risk_manager.get_position_size()` before entry

---

## See Also

- [../EVAL_VS_PA.md](../EVAL_VS_PA.md) - Mode comparison
- [EVAL_MODE.md](EVAL_MODE.md) - Evaluation account mode
- [../apex-accounts.md](../apex-accounts.md) - Account presets
- [apex-rules.md](apex-rules.md) - Compliance guidelines
