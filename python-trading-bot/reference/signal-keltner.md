# Keltner Channel Signal

**Best Overall Performance** - Profit Factor: 10.04 | Win Rate: 87.8%

## Signal Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| `keltner_ema_period` | 20 | EMA period for middle line |
| `keltner_atr_period` | 14 | ATR calculation period |
| `keltner_atr_mult` | 2.75 | ATR multiplier for bands |

## Code Blocks

### Signal Detection (`{{SIGNAL_DETECTION_CODE}}`)

```python
# Keltner Channel breakout
# Long: Price crosses above upper band
# Short: Price crosses below lower band
long_sig = (
    prev["close"] <= prev["keltner_upper"]
    and curr["close"] > curr["keltner_upper"]
)
short_sig = (
    prev["close"] >= prev["keltner_lower"]
    and curr["close"] < curr["keltner_lower"]
)
```

### Re-entry Logic (`{{REENTRY_LOGIC_CODE}}`)

```python
# Re-enter if price still beyond band
if self.last_exit_direction == 1 and curr["close"] > curr["keltner_upper"]:
    long_sig = True
    is_reentry = True
elif self.last_exit_direction == -1 and curr["close"] < curr["keltner_lower"]:
    short_sig = True
    is_reentry = True
```

### Config Parameters (`{{SIGNAL_PARAMS}}`)

```python
# Keltner Parameters
keltner_ema_period: int = 20
keltner_atr_period: int = 14
keltner_atr_mult: float = 2.75
```

## Placeholder Values

| Placeholder | Value |
|-------------|-------|
| `{{SIGNAL}}` | `keltner` |
| `{{SIGNAL_NAME}}` | `Keltner Channel` |
| `{{SIGNAL_CLASS}}` | `Keltner` |
| `{{SIGNAL_DESCRIPTION}}` | `Channel breakout` |
| `{{PROFIT_FACTOR}}` | `10.04` |
| `{{WIN_RATE}}` | `87.8%` |
| `{{WARMUP_BARS}}` | `50` |

## Entry Conditions

1. **Base Signal**: Price crosses Keltner band
2. **ADX Filter**: ADX > 35 with dominant DI rising
3. **Volume Filter**: Volume > 20-period EMA
4. **Session Filter**: Within allowed trading hours

## Exit Conditions

1. **Stop Loss**: Entry ± (3.0 × ATR)
2. **Take Profit**: Entry ± (3.0 × ATR)
3. **Trailing Stop**: Activates at 0.15 × ATR profit, trails at 0.15 × ATR

## Re-entry Conditions

1. After profitable exit
2. Wait 3 bars
3. ADX > 40 (stricter than initial entry)
4. Price still above/below band
5. Max 10 re-entries per trend

## Performance Notes

- Optimal ATR multiplier of 2.75 (vs default 1.5) filters out noise
- Wider bands = fewer signals but higher quality
- Works best in trending markets with ADX > 35
- Best hours: 9-11 AM and 1-3 PM ET
