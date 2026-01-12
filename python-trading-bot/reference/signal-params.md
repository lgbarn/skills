# Signal Parameters

Configuration parameters for all 5 entry signals.

---

## Keltner Channel

| Parameter | Type | Default | Optimal | Range | Description |
|-----------|------|---------|---------|-------|-------------|
| `keltner_ema_period` | int | 20 | 20 | 5-50 | EMA period for middle line |
| `keltner_atr_period` | int | 14 | 14 | 5-30 | ATR calculation period |
| `keltner_atr_mult` | float | 1.5 | 2.75 | 0.5-5.0 | ATR multiplier for bands |

**Entry Logic:**
- Long: `prev_close <= prev_upper AND close > upper`
- Short: `prev_close >= prev_lower AND close < lower`

---

## EMA Crossover

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `ema_fast` | int | 3 | 2-20 | Fast EMA period (Linda Raschke) |
| `ema_slow` | int | 8 | 5-50 | Slow EMA period (Linda Raschke) |
| `ema_separation_filter` | bool | true | - | Require minimum EMA separation |
| `ema_separation_min` | float | 0.35 | 0.1-2.0 | Min points between EMAs |

**Entry Logic:**
- Long: `prev_fast <= prev_slow AND fast > slow` (Golden Cross)
- Short: `prev_fast >= prev_slow AND fast < slow` (Death Cross)
- Additional: Separation filter requires `abs(fast - slow) >= separation_min`

---

## Rolling VWAP

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `vwap_window` | int | 720 | 60-1440 | Rolling window in bars (720 = 24h at 2-min) |
| `band_multiplier` | float | 1.0 | 0.5-3.0 | Standard deviation multiplier |

**Entry Logic:**
- Long: `prev_close <= prev_upper AND close > upper` (upper = VWAP + mult × σ)
- Short: `prev_close >= prev_lower AND close < lower` (lower = VWAP - mult × σ)

---

## SuperTrend

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `supertrend_period` | int | 10 | 5-30 | ATR period |
| `supertrend_mult` | float | 3.0 | 1.0-5.0 | ATR multiplier |

**Entry Logic:**
- Long: `prev_direction == -1 AND direction == 1` (flip to bullish)
- Short: `prev_direction == 1 AND direction == -1` (flip to bearish)

---

## Williams Alligator

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `alligator_jaw_period` | int | 13 | 8-21 | Jaw SMMA period (Blue) |
| `alligator_jaw_offset` | int | 8 | 5-13 | Jaw offset |
| `alligator_teeth_period` | int | 8 | 5-13 | Teeth SMMA period (Red) |
| `alligator_teeth_offset` | int | 5 | 3-8 | Teeth offset |
| `alligator_lips_period` | int | 5 | 3-8 | Lips SMMA period (Green) |
| `alligator_lips_offset` | int | 3 | 1-5 | Lips offset |

**Entry Logic:**
- Long: `NOT prev_aligned_up AND aligned_up` (lips > teeth > jaw)
- Short: `NOT prev_aligned_down AND aligned_down` (lips < teeth < jaw)

---

## See Also

- [SIGNALS.md](signals-overview.md) - Signal overview with backtest metrics
- [signals-top5.md](signals-top5.md) - Detailed signal documentation
- [signal-keltner.md](signal-keltner.md) - Keltner signal details
- [signal-ema.md](signal-ema.md) - EMA cross signal details
- [signal-vwap.md](signal-vwap.md) - VWAP signal details
- [signal-supertrend.md](signal-supertrend.md) - SuperTrend signal details
- [signal-alligator.md](signal-alligator.md) - Alligator signal details
