# Top 5 Entry Signals - Detailed Guide

Comprehensive parameter reference and implementation details for the top 5 backtested signals.

---

## Contents

- [1. Keltner Channel Breakout](#1-keltner-channel-breakout)
- [2. EMA Crossover](#2-ema-crossover)
- [3. Rolling VWAP Band Breakout](#3-rolling-vwap-band-breakout)
- [4. SuperTrend](#4-supertrend)
- [5. Williams Alligator](#5-williams-alligator)
- [Common Configuration](#common-configuration)
- [See Also](#see-also)

---

## 1. Keltner Channel Breakout

**Best Overall Performance - Profit Factor: 10.04**

### Parameters

| Parameter | Optimal | Default | Range | Description |
|-----------|---------|---------|-------|-------------|
| EMA Period | 20 | 20 | 5-50 | Middle line EMA |
| ATR Period | 14 | 14 | 5-30 | ATR for bands |
| ATR Multiplier | **2.75** | 1.5 | 0.5-5.0 | Band width |

**Key Insight:** Wider bands (2.75× vs 1.5×) filter out noise and produce fewer but higher-quality signals.

### Entry Logic

```python
# Keltner Channel calculation
middle = calc_ema(closes, ema_period)
atr = calc_atr(rows, atr_period)
upper = middle + (atr * atr_mult)
lower = middle - (atr * atr_mult)

# Entry signals (edge-triggered)
long_signal = prev_close <= prev_upper and close > upper
short_signal = prev_close >= prev_lower and close < lower
```

### Re-entry Condition

```python
if last_exit_direction == 1 and close > upper:
    long_signal = True  # Re-enter long if price still above upper
elif last_exit_direction == -1 and close < lower:
    short_signal = True  # Re-enter short if price still below lower
```

See [keltner.md](signal-keltner.md) for full documentation.

---

## 2. EMA Crossover

**Linda Raschke Style - Profit Factor: 6.23**

### Parameters

| Parameter | Value | Range | Description |
|-----------|-------|-------|-------------|
| Fast EMA | 3 | 2-20 | Linda Raschke fast |
| Slow EMA | 8 | 5-50 | Linda Raschke slow |
| Separation Min | 0.35 | 0.1-2.0 | Min points between EMAs |
| Separation Filter | true | - | Filter weak crossovers |

### Entry Logic

```python
# EMA calculation
ema_fast = calc_ema(closes, fast_period)
ema_slow = calc_ema(closes, slow_period)

# Crossover detection
long_signal = prev_fast <= prev_slow and fast > slow  # Golden cross
short_signal = prev_slow <= prev_fast and slow > fast  # Death cross

# Separation filter (reduces false signals)
if separation_filter:
    separation = abs(ema_fast - ema_slow)
    if separation < separation_min:
        long_signal = short_signal = False
```

See [ema_cross.md](signal-ema.md) for full documentation.

---

## 3. Rolling VWAP Band Breakout

**Volume-Weighted Momentum - Profit Factor: 5.20**

### Parameters

| Parameter | Value | Range | Description |
|-----------|-------|-------|-------------|
| Window | 720 | 60-1440 | 24 hours at 2-min bars |
| Band Multiplier | 1.0 | 0.5-3.0 | 1 standard deviation |

### Entry Logic

```python
# Rolling VWAP calculation
for i in range(len(rows)):
    chunk = rows[max(0, i - window + 1):i + 1]

    # VWAP = Σ(TP × Vol) / Σ(Vol)
    tpv_sum = sum((r["high"] + r["low"] + r["close"]) / 3 * r["volume"] for r in chunk)
    vol_sum = sum(r["volume"] for r in chunk)
    vwap = tpv_sum / vol_sum if vol_sum > 0 else closes[i]

    # Variance = E[X²] - E[X]²
    tp2v_sum = sum(((r["high"] + r["low"] + r["close"]) / 3) ** 2 * r["volume"] for r in chunk)
    variance = (tp2v_sum / vol_sum) - (vwap ** 2) if vol_sum > 0 else 0
    std = variance ** 0.5 if variance > 0 else 0

    upper = vwap + (std * band_multiplier)
    lower = vwap - (std * band_multiplier)

# Entry signals
long_signal = prev_close <= prev_upper and close > upper
short_signal = prev_close >= prev_lower and close < lower
```

See [vwap.md](signal-vwap.md) for full documentation.

---

## 4. SuperTrend

**Trend Following - Profit Factor: 4.41**

### Parameters

| Parameter | Value | Range | Description |
|-----------|-------|-------|-------------|
| Period | 10 | 5-30 | ATR period |
| Multiplier | 3.0 | 1.0-5.0 | ATR multiplier |

### Entry Logic

```python
def calc_supertrend(rows, period, multiplier):
    atr = calc_atr(rows, period)

    for i in range(len(rows)):
        hl2 = (rows[i]["high"] + rows[i]["low"]) / 2

        # Basic bands
        basic_upper = hl2 + (multiplier * atr[i])
        basic_lower = hl2 - (multiplier * atr[i])

        # Final bands (only move in trend direction)
        if i > 0:
            prev_close = rows[i - 1]["close"]
            final_upper = basic_upper if basic_upper < prev_upper or prev_close > prev_upper else prev_upper
            final_lower = basic_lower if basic_lower > prev_lower or prev_close < prev_lower else prev_lower

        # Direction
        if prev_supertrend == prev_upper:
            direction = 1 if close > final_upper else -1
        else:
            direction = -1 if close < final_lower else 1

# Entry signals (direction flip)
long_signal = prev_direction == -1 and direction == 1
short_signal = prev_direction == 1 and direction == -1
```

See [supertrend.md](signal-supertrend.md) for full documentation.

---

## 5. Williams Alligator

**Trend Alignment - Profit Factor: 4.16**

### Parameters

| Parameter | Value | Range | Description |
|-----------|-------|-------|-------------|
| Jaw Period | 13 | 8-21 | Blue line SMMA |
| Jaw Offset | 8 | 5-13 | Blue line offset |
| Teeth Period | 8 | 5-13 | Red line SMMA |
| Teeth Offset | 5 | 3-8 | Red line offset |
| Lips Period | 5 | 3-8 | Green line SMMA |
| Lips Offset | 3 | 1-5 | Green line offset |

### Entry Logic

```python
def calc_alligator(rows, jaw_period, jaw_offset, teeth_period, teeth_offset, lips_period, lips_offset):
    # Median price
    hl2 = [(r["high"] + r["low"]) / 2 for r in rows]

    # SMMA with offsets
    jaw_base = calc_smma(hl2, jaw_period)
    teeth_base = calc_smma(hl2, teeth_period)
    lips_base = calc_smma(hl2, lips_period)

    for i in range(len(rows)):
        jaw = jaw_base[i - jaw_offset] if i >= jaw_offset else jaw_base[0]
        teeth = teeth_base[i - teeth_offset] if i >= teeth_offset else teeth_base[0]
        lips = lips_base[i - lips_offset] if i >= lips_offset else lips_base[0]

        aligned_up = lips > teeth > jaw
        aligned_down = lips < teeth < jaw

# Entry signals (alignment change)
long_signal = not prev_aligned_up and aligned_up
short_signal = not prev_aligned_down and aligned_down
```

### SMMA Calculation

```python
def calc_smma(values, period):
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

See [alligator.md](signal-alligator.md) for full documentation.

---

## Common Configuration

All signals use these common settings:

```python
# ADX Filter (critical for performance)
adx_threshold = 35
adx_mode = "di_rising"  # Dominant DI must be rising

# Exits (ATR-based)
sl_atr_mult = 3.0
tp_atr_mult = 3.0
trail_trigger_atr = 0.15
trail_distance_atr = 0.15

# Re-entry
reentry_bars_wait = 3
reentry_adx_min = 40
max_reentries = 10

# Risk
contracts = 2
daily_max_loss = 500
```

---

## See Also

- [signals-overview.md](signals-overview.md) - Signal overview and selection guide
- [signal-params.md](signal-params.md) - Configuration reference
- Individual signal docs: [keltner.md](signal-keltner.md), [ema_cross.md](signal-ema.md), [vwap.md](signal-vwap.md), [supertrend.md](signal-supertrend.md), [alligator.md](signal-alligator.md)
