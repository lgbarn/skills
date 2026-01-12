# Strategy Configuration Reference

This document defines all configurable parameters for strategy generation. Values are sourced from `Python/backtest.py` CONFIG (lines 23-111).

---

## Signal-Specific Parameters

### VWAP (Rolling VWAP Band Breakout)
| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `vwap_window` | int | 720 | 10-2000 | Rolling window in bars (720 = 24h at 2-min) |
| `band_multiplier` | float | 1.0 | 0.1-3.0 | Standard deviation multiplier for bands |

### Keltner (Keltner Channel Breakout)
| Parameter | Type | Default | Optimal | Range | Description |
|-----------|------|---------|---------|-------|-------------|
| `keltner_ema_period` | int | 20 | 20 | 5-100 | EMA period for middle line |
| `keltner_atr_mult` | float | 1.5 | **2.75** | 0.5-5.0 | ATR multiplier for bands |

### EMA Cross (EMA Crossover)
| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `ema_fast` | int | 3 | 2-50 | Fast EMA period (Linda Raschke: 3) |
| `ema_slow` | int | 8 | 3-100 | Slow EMA period (Linda Raschke: 8) |
| `ema_separation_filter` | bool | true | - | Require minimum separation |
| `ema_separation_min` | float | 0.35 | 0.0-5.0 | Minimum points between EMAs |
| `ema_trend_filter` | bool | false | - | Use third EMA as trend filter |
| `ema_trend_period` | int | 21 | 10-50 | Trend EMA period (for 3/8/21 setup) |
| `ema_slope_filter` | bool | false | - | Require minimum EMA slope |
| `ema_slope_bars` | int | 3 | 1-10 | Bars to measure slope over |
| `ema_slope_min` | float | 0.5 | 0.0-5.0 | Minimum slope (points/bar) |

### SuperTrend
| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `supertrend_period` | int | 10 | 5-30 | ATR period for SuperTrend |
| `supertrend_mult` | float | 3.0 | 1.0-5.0 | ATR multiplier |

### Alligator (Williams Alligator)
| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `alligator_jaw_period` | int | 13 | 5-30 | Jaw SMMA period (blue line) |
| `alligator_jaw_offset` | int | 8 | 1-15 | Jaw offset |
| `alligator_teeth_period` | int | 8 | 3-20 | Teeth SMMA period (red line) |
| `alligator_teeth_offset` | int | 5 | 1-10 | Teeth offset |
| `alligator_lips_period` | int | 5 | 2-15 | Lips SMMA period (green line) |
| `alligator_lips_offset` | int | 3 | 1-8 | Lips offset |

### SSL Channel
| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `ssl_period` | int | 10 | 5-30 | SSL Channel SMA period |

### Squeeze (TTM Squeeze)
| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `squeeze_bb_period` | int | 20 | 10-50 | Bollinger Band period |
| `squeeze_bb_mult` | float | 2.0 | 1.0-3.0 | Bollinger Band multiplier |
| `squeeze_kc_period` | int | 20 | 10-50 | Keltner Channel period |
| `squeeze_kc_mult` | float | 1.5 | 0.5-3.0 | Keltner Channel multiplier |
| `squeeze_mom_period` | int | 12 | 5-30 | Momentum period |

### Aroon
| Parameter | Type | Default | Optimal | Range | Description |
|-----------|------|---------|---------|-------|-------------|
| `aroon_period` | int | 25 | **50** | 10-100 | Lookback period |

### Stochastic (Linda Raschke Style)
| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `stoch_k_period` | int | 7 | 5-21 | %K lookback period (Raschke: 7) |
| `stoch_k_slowing` | int | 4 | 1-10 | %K slowing/smoothing |
| `stoch_d_period` | int | 16 | 3-30 | %D signal line period (Raschke: 16) |
| `stoch_overbought` | int | 80 | 70-90 | Overbought level |
| `stoch_oversold` | int | 20 | 10-30 | Oversold level |

### MACD (Linda Raschke Style)
| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `macd_fast` | int | 3 | 2-20 | Fast period (Raschke: 3) |
| `macd_slow` | int | 10 | 5-50 | Slow period (Raschke: 10) |
| `macd_signal` | int | 16 | 5-30 | Signal period (Raschke: 16) |
| `macd_use_sma` | bool | true | - | Use SMA (Raschke) vs EMA (standard) |

### ADX Only (DI Crossover)
Uses the common ADX parameters below.

---

## Common Parameters (All Signals)

### ADX Filter
| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `adx_calculation` | string | "standard" | standard, wilder | Calculation method |
| `adx_period` | int | 14 | 5-30 | ADX smoothing period (8 for ADXcellence) |
| `di_period` | int | 14 | 5-30 | DI calculation period (13 for ADXcellence) |
| `adx_threshold` | int | 35 | 10-50 | Minimum ADX for initial entry |
| `adx_mode` | string | "di_rising" | see below | Filter mode |

**ADX Modes:**
| Mode | Description |
|------|-------------|
| `traditional` | ADX > threshold only |
| `di_aligned` | ADX > threshold AND DIs aligned with trade direction |
| `di_rising` | ADX > threshold AND dominant DI rising **(RECOMMENDED)** |
| `adx_rising` | ADX > threshold AND ADX itself rising |
| `combined` | All conditions must be true |

### Volume Filter
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `volume_filter` | bool | true | Require volume > MA for entry |
| `volume_ma_period` | int | 20 | Volume EMA period |

### Session Filter
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `allowed_hours` | set | {9-16, 18-20} | Trading hours (ET) |

Default allowed hours: 9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20 (ET)

---

## Exit Settings (ATR-Based)

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `atr_period` | int | 14 | 5-30 | ATR calculation period |
| `sl_atr_mult` | float | 3.0 | 0.5-5.0 | Stop loss = ATR x multiplier |
| `tp_atr_mult` | float | 3.0 | 0.5-5.0 | Take profit = ATR x multiplier |
| `trail_trigger_atr` | float | 0.15 | 0.05-1.0 | Trail activates at this ATR profit |
| `trail_distance_atr` | float | 0.15 | 0.05-1.0 | Trail distance = ATR x multiplier |

**Exit Priority Order (Conservative):**
```
1. Trailing Stop (if active AND hit)
2. Stop Loss (hard protective stop)
3. Take Profit (profit target)
```

This is industry standard for backtesting - assume worst outcome when both SL and TP could be hit on same bar.

---

## Re-entry Settings

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `reentry_enabled` | bool | true | - | Enable trend continuation re-entries |
| `reentry_bars_wait` | int | 3 | 1-20 | Bars to wait after exit |
| `reentry_adx_min` | int | 40 | 20-60 | ADX required for re-entry (higher than initial) |
| `max_reentries` | int | 10 | 1-50 | Maximum re-entries per trend direction |

**Re-entry Logic:**
- Only after profitable exits
- Wait `reentry_bars_wait` bars
- Requires `reentry_adx_min` ADX (stricter than initial)
- Price must still be beyond original signal level
- Resets count when trend direction changes

---

## Contract/Cost Settings (for reference)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `point_value` | float | 5.0 | $5 per point for NQ |
| `tick_size` | float | 0.25 | NQ tick size |
| `contracts` | int | 2 | Number of contracts |
| `slippage_ticks` | int | 1 | Slippage per side (1 tick = 0.25 pts) |
| `commission_rt` | float | 4.00 | Round-trip commission per contract |
| `daily_max_loss` | float | 500.0 | Daily drawdown limit |

---

## Quick Reference: Optimal Settings by Signal

From 219-day NQ backtest with ADX di_rising, threshold 35:

| Signal | Key Optimal Settings |
|--------|---------------------|
| keltner | `atr_mult=2.75` (vs default 1.5) |
| ema_cross | `fast=3, slow=8, separation=0.35` |
| aroon | `period=50` (vs default 25) |
| supertrend | `period=7, mult=2.0` |
| ssl | `period=8` |

All signals benefit from:
- `adx_mode="di_rising"` (vs traditional)
- `adx_threshold=35`
- `sl_atr_mult=3.0, tp_atr_mult=3.0`
- `trail_trigger_atr=0.15, trail_distance_atr=0.15` (very tight trailing)
