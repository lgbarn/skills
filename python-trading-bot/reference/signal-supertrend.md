# SuperTrend Signal

**Trend Following** - Profit Factor: 4.41 | Win Rate: 82.5%

## Signal Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| `supertrend_period` | 10 | ATR period |
| `supertrend_mult` | 3.0 | ATR multiplier |

## Code Blocks

### Signal Detection (`{{SIGNAL_DETECTION_CODE}}`)

```python
# SuperTrend direction flip
# Long: Direction changes from bearish (-1) to bullish (1)
# Short: Direction changes from bullish (1) to bearish (-1)
prev_dir = prev.get("supertrend_dir", 1)
curr_dir = curr.get("supertrend_dir", 1)
long_sig = prev_dir == -1 and curr_dir == 1
short_sig = prev_dir == 1 and curr_dir == -1
```

### Re-entry Logic (`{{REENTRY_LOGIC_CODE}}`)

```python
# Re-enter if SuperTrend still in same direction
if self.last_exit_direction == 1 and curr.get("supertrend_dir", 1) == 1:
    long_sig = True
    is_reentry = True
elif self.last_exit_direction == -1 and curr.get("supertrend_dir", 1) == -1:
    short_sig = True
    is_reentry = True
```

### Config Parameters (`{{SIGNAL_PARAMS}}`)

```python
# SuperTrend Parameters
supertrend_period: int = 10
supertrend_mult: float = 3.0
```

## Placeholder Values

| Placeholder | Value |
|-------------|-------|
| `{{SIGNAL}}` | `supertrend` |
| `{{SIGNAL_NAME}}` | `SuperTrend` |
| `{{SIGNAL_CLASS}}` | `Supertrend` |
| `{{SIGNAL_DESCRIPTION}}` | `Direction flip` |
| `{{PROFIT_FACTOR}}` | `4.41` |
| `{{WIN_RATE}}` | `82.5%` |
| `{{WARMUP_BARS}}` | `50` |

## SuperTrend Calculation

```python
def calc_supertrend(bars, period, multiplier):
    atr = calc_atr(bars, period)

    for i in range(len(bars)):
        hl2 = (bars[i]["high"] + bars[i]["low"]) / 2

        # Basic bands around HL2
        basic_upper = hl2 + (multiplier * atr[i])
        basic_lower = hl2 - (multiplier * atr[i])

        # Final bands (only move in trend direction)
        if i > 0:
            prev_close = bars[i - 1]["close"]
            # Upper band only moves down in downtrend
            final_upper = (
                basic_upper
                if basic_upper < prev_upper or prev_close > prev_upper
                else prev_upper
            )
            # Lower band only moves up in uptrend
            final_lower = (
                basic_lower
                if basic_lower > prev_lower or prev_close < prev_lower
                else prev_lower
            )

        # Determine direction
        if prev_supertrend == prev_upper:
            direction = 1 if close > final_upper else -1
        else:
            direction = -1 if close < final_lower else 1

        supertrend = final_lower if direction == 1 else final_upper
```

## Entry Conditions

1. **Base Signal**: SuperTrend direction flips
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
4. SuperTrend still in same direction
5. Max 10 re-entries per trend

## Performance Notes

- Direction-based signals (only on flip, not continuous)
- 3.0× ATR multiplier provides good noise filtering
- Works well in trending markets
- May lag at trend reversals
- Combines well with ADX for trend strength confirmation

## Multiplier Considerations

| Multiplier | Behavior |
|------------|----------|
| 1.5-2.0 | More sensitive, more signals, more whipsaws |
| 2.5-3.0 | Balanced (recommended) |
| 3.5-4.0 | Less sensitive, fewer signals, misses early entries |

## Visual Reference

```
Price
  |
  |    ╭──────────────╮  Direction = 1 (Bullish)
  |   /                \
  |  /   SuperTrend ────────────────
  | /                    \
  |/                      \
  ├─────────────────────────────────────
  |                        ╲
  |                         ╲  Direction = -1 (Bearish)
  |                          ──────────── SuperTrend
  |
  └──────────────────────────────────────► Time

Entry on direction FLIP (not on direction confirmation)
```
