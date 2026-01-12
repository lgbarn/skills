# Williams Alligator Signal

**Trend Alignment** - Profit Factor: 4.16 | Win Rate: 83.5%

## Signal Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| `alligator_jaw_period` | 13 | Jaw SMMA period (Blue) |
| `alligator_jaw_offset` | 8 | Jaw offset |
| `alligator_teeth_period` | 8 | Teeth SMMA period (Red) |
| `alligator_teeth_offset` | 5 | Teeth offset |
| `alligator_lips_period` | 5 | Lips SMMA period (Green) |
| `alligator_lips_offset` | 3 | Lips offset |

## Code Blocks

### Signal Detection (`{{SIGNAL_DETECTION_CODE}}`)

```python
# Williams Alligator alignment change
# Long: Lines become bullish aligned (lips > teeth > jaw)
# Short: Lines become bearish aligned (lips < teeth < jaw)
prev_up = prev.get("aligned_up", False)
curr_up = curr.get("aligned_up", False)
long_sig = not prev_up and curr_up

prev_down = prev.get("aligned_down", False)
curr_down = curr.get("aligned_down", False)
short_sig = not prev_down and curr_down
```

### Re-entry Logic (`{{REENTRY_LOGIC_CODE}}`)

```python
# Re-enter if Alligator still aligned
if self.last_exit_direction == 1 and curr.get("aligned_up", False):
    long_sig = True
    is_reentry = True
elif self.last_exit_direction == -1 and curr.get("aligned_down", False):
    short_sig = True
    is_reentry = True
```

### Config Parameters (`{{SIGNAL_PARAMS}}`)

```python
# Alligator Parameters
alligator_jaw_period: int = 13
alligator_jaw_offset: int = 8
alligator_teeth_period: int = 8
alligator_teeth_offset: int = 5
alligator_lips_period: int = 5
alligator_lips_offset: int = 3
```

## Placeholder Values

| Placeholder | Value |
|-------------|-------|
| `{{SIGNAL}}` | `alligator` |
| `{{SIGNAL_NAME}}` | `Williams Alligator` |
| `{{SIGNAL_CLASS}}` | `Alligator` |
| `{{SIGNAL_DESCRIPTION}}` | `Line alignment` |
| `{{PROFIT_FACTOR}}` | `4.16` |
| `{{WIN_RATE}}` | `83.5%` |
| `{{WARMUP_BARS}}` | `50` |

## Alligator Calculation

```python
def calc_alligator(bars, jaw_period, jaw_offset, teeth_period, teeth_offset, lips_period, lips_offset):
    # Median price (HL2)
    hl2 = [(b["high"] + b["low"]) / 2 for b in bars]

    # Calculate SMMA (Smoothed Moving Average)
    jaw_base = calc_smma(hl2, jaw_period)
    teeth_base = calc_smma(hl2, teeth_period)
    lips_base = calc_smma(hl2, lips_period)

    for i in range(len(bars)):
        # Apply offset (look back)
        jaw = jaw_base[i - jaw_offset] if i >= jaw_offset else jaw_base[0]
        teeth = teeth_base[i - teeth_offset] if i >= teeth_offset else teeth_base[0]
        lips = lips_base[i - lips_offset] if i >= lips_offset else lips_base[0]

        # Alignment check
        aligned_up = lips > teeth > jaw    # Bullish
        aligned_down = lips < teeth < jaw  # Bearish


def calc_smma(values, period):
    """Smoothed Moving Average (Wilder's smoothing)."""
    results = []
    for i in range(len(values)):
        if i == 0:
            results.append(values[0])
        elif i < period:
            results.append(sum(values[:i + 1]) / (i + 1))
        else:
            # SMMA = (prev_smma * (period - 1) + value) / period
            results.append((results[-1] * (period - 1) + values[i]) / period)
    return results
```

## Entry Conditions

1. **Base Signal**: Alligator lines become aligned
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
4. Alligator still in same alignment
5. Max 10 re-entries per trend

## Performance Notes

- Bill Williams indicator with classic parameters
- SMMA provides smooth, less noisy lines
- Offsets create "future shifted" lines for better alignment detection
- Works best in established trends
- May miss early trend entries due to lag

## Alligator States

| State | Description | Action |
|-------|-------------|--------|
| **Sleeping** | Lines intertwined | No trade |
| **Awakening** | Lines starting to spread | Prepare |
| **Eating** (Up) | Lips > Teeth > Jaw | Long signal |
| **Eating** (Down) | Lips < Teeth < Jaw | Short signal |
| **Sated** | Lines converging | Exit approaching |

## Visual Reference

```
Bullish Alignment:        Bearish Alignment:

    Lips ─────             ───── Jaw
     Teeth ─────           ───── Teeth
      Jaw ─────            ───── Lips

Entry on TRANSITION from non-aligned to aligned
```

## Line Colors (Traditional)

| Line | Color | Period | Offset |
|------|-------|--------|--------|
| Jaw | Blue | 13 | 8 |
| Teeth | Red | 8 | 5 |
| Lips | Green | 5 | 3 |
