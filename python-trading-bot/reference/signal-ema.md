# EMA Crossover Signal

**Linda Raschke Style** - Profit Factor: 6.23 | Win Rate: 82.7%

## Signal Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| `ema_fast` | 3 | Fast EMA period (Linda Raschke) |
| `ema_slow` | 8 | Slow EMA period (Linda Raschke) |
| `ema_separation_filter` | true | Enable separation filter |
| `ema_separation_min` | 0.35 | Min points between EMAs |

## Code Blocks

### Signal Detection (`{{SIGNAL_DETECTION_CODE}}`)

```python
# EMA Crossover with separation filter
# Long: Fast EMA crosses above Slow EMA (Golden Cross)
# Short: Fast EMA crosses below Slow EMA (Death Cross)
prev_long = prev["ema_fast"] > prev["ema_slow"]
curr_long = curr["ema_fast"] > curr["ema_slow"]
long_sig = not prev_long and curr_long

prev_short = prev["ema_slow"] > prev["ema_fast"]
curr_short = curr["ema_slow"] > curr["ema_fast"]
short_sig = not prev_short and curr_short

# Separation filter - require minimum distance between EMAs
if self.config.ema_separation_filter:
    separation = abs(curr["ema_fast"] - curr["ema_slow"])
    if separation < self.config.ema_separation_min:
        long_sig = False
        short_sig = False
```

### Re-entry Logic (`{{REENTRY_LOGIC_CODE}}`)

```python
# Re-enter if EMAs still aligned
if self.last_exit_direction == 1 and curr["ema_fast"] > curr["ema_slow"]:
    long_sig = True
    is_reentry = True
elif self.last_exit_direction == -1 and curr["ema_slow"] > curr["ema_fast"]:
    short_sig = True
    is_reentry = True
```

### Config Parameters (`{{SIGNAL_PARAMS}}`)

```python
# EMA Cross Parameters
ema_fast: int = 3
ema_slow: int = 8
ema_separation_filter: bool = True
ema_separation_min: float = 0.35
```

## Placeholder Values

| Placeholder | Value |
|-------------|-------|
| `{{SIGNAL}}` | `ema_cross` |
| `{{SIGNAL_NAME}}` | `EMA Crossover` |
| `{{SIGNAL_CLASS}}` | `EmaCross` |
| `{{SIGNAL_DESCRIPTION}}` | `3/8 EMA crossover` |
| `{{PROFIT_FACTOR}}` | `6.23` |
| `{{WIN_RATE}}` | `82.7%` |
| `{{WARMUP_BARS}}` | `20` |

## Entry Conditions

1. **Base Signal**: Fast EMA crosses Slow EMA
2. **Separation Filter**: |Fast - Slow| >= 0.35 points
3. **ADX Filter**: ADX > 35 with dominant DI rising
4. **Volume Filter**: Volume > 20-period EMA
5. **Session Filter**: Within allowed trading hours

## Exit Conditions

1. **Stop Loss**: Entry ± (3.0 × ATR)
2. **Take Profit**: Entry ± (3.0 × ATR)
3. **Trailing Stop**: Activates at 0.15 × ATR profit, trails at 0.15 × ATR

## Re-entry Conditions

1. After profitable exit
2. Wait 3 bars
3. ADX > 40 (stricter than initial entry)
4. EMAs still in same alignment
5. Max 10 re-entries per trend

## Performance Notes

- 3/8 EMA combination from Linda Raschke
- Separation filter reduces whipsaws in choppy markets
- Fast and responsive to trend changes
- Works well with ADX filter to confirm trend strength
- Best combined with momentum confirmation

## Optional Enhancements

Available in backtest.py but disabled by default:

```python
# Triple EMA trend filter
ema_trend_filter: bool = False
ema_trend_period: int = 21

# RSI filter
rsi_filter: bool = False
rsi_period: int = 14
rsi_long_min: float = 45
rsi_long_max: float = 70

# MACD confirmation
macd_filter: bool = False
macd_fast: int = 3
macd_slow: int = 10
macd_signal: int = 16

# Slope filter
ema_slope_filter: bool = False
ema_slope_bars: int = 3
ema_slope_min: float = 0.5
```
