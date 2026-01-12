# Available Entry Signals

This document catalogs all 11 entry signals supported by the strategy generator, with backtest performance metrics and configuration details.

---

## Performance Summary

**Backtest Period:** 219 days (May 28, 2025 - January 2, 2026)
**Instrument:** NQ (Nasdaq 100 E-mini futures)
**Timeframe:** 2-minute bars
**Common Settings:** ADX mode=di_rising, threshold=35, ATR SL/TP=3.0, tight trailing stops

| Rank | Signal | Profit Factor | Win Rate | Total PnL | Trades |
|------|--------|--------------|----------|-----------|--------|
| 1 | **keltner** | 10.04 | 87.8% | $42,994 | 247 |
| 2 | **ema_cross** | 6.23 | 82.7% | $61,071 | 310 |
| 3 | **vwap** | 5.20 | 85.3% | $46,146 | 268 |
| 4 | **supertrend** | 4.41 | 82.5% | $44,029 | 285 |
| 5 | **alligator** | 4.16 | 83.5% | $32,333 | 198 |
| 6 | ssl | 4.08 | 79.8% | - | - |
| 7 | squeeze | 3.88 | 82.0% | - | - |
| 8 | aroon | 3.46 | 81.4% | - | - |
| 9 | adx_only | 3.37 | 80.7% | - | - |
| 10 | stochastic | - | - | - | - |
| 11 | macd | - | - | - | - |

*Run `just py-signal <signal>` to get latest metrics for any signal.*

---

## Signal Details

### 1. VWAP (Rolling VWAP Band Breakout)

**Description:** Price breakout above/below rolling VWAP with 1-sigma band. Long when price crosses above upper band, short when price crosses below lower band.

**Entry Logic:**
```
Long:  prev.close <= prev.upper1 AND bar.close > bar.upper1
Short: prev.close >= prev.lower1 AND bar.close < bar.lower1
```

**Re-entry Condition:**
```
Long:  price still > upper band AND adx > 40
Short: price still < lower band AND adx > 40
```

**Parameters:**
| Parameter | Default | Description |
|-----------|---------|-------------|
| `vwap_window` | 720 | Rolling window (24h at 2-min) |
| `band_multiplier` | 1.0 | Standard deviation multiplier |

**Best Use Cases:**
- Mean reversion strategies on trending days
- Catching momentum breakouts with volume confirmation

---

### 2. Keltner (Keltner Channel Breakout)

**Description:** Price breakout above/below Keltner Channel bands (EMA +/- ATR multiplier). High win rate strategy with excellent profit factor.

**Entry Logic:**
```
Long:  prev.close <= prev.keltner_upper AND bar.close > bar.keltner_upper
Short: prev.close >= prev.keltner_lower AND bar.close < bar.keltner_lower
```

**Re-entry Condition:**
```
Long:  price still > keltner_upper AND adx > 40
Short: price still < keltner_lower AND adx > 40
```

**Parameters:**
| Parameter | Default | Optimal | Description |
|-----------|---------|---------|-------------|
| `keltner_ema_period` | 20 | 20 | EMA period for middle line |
| `keltner_atr_mult` | 1.5 | **2.75** | ATR multiplier (wider bands perform better) |

**Best Use Cases:**
- Volatility breakouts
- Trend continuation in strong markets

---

### 3. EMA Cross (EMA Crossover)

**Description:** Fast EMA crosses slow EMA with separation filter. Uses Linda Raschke's 3/8 setup with minimum separation requirement to avoid whipsaws.

**Entry Logic:**
```
Long:  prev.ema_fast <= prev.ema_slow AND bar.ema_fast > bar.ema_slow
       AND abs(ema_fast - ema_slow) >= separation_min
Short: prev.ema_slow <= prev.ema_fast AND bar.ema_slow > bar.ema_fast
       AND abs(ema_fast - ema_slow) >= separation_min
```

**Re-entry Condition:**
```
Long:  ema_fast still > ema_slow AND adx > 40
Short: ema_slow still > ema_fast AND adx > 40
```

**Parameters:**
| Parameter | Default | Description |
|-----------|---------|-------------|
| `ema_fast` | 3 | Fast EMA period (Linda Raschke) |
| `ema_slow` | 8 | Slow EMA period (Linda Raschke) |
| `ema_separation_filter` | true | Require minimum separation |
| `ema_separation_min` | 0.35 | Minimum points between EMAs |

**Optional Enhancement Filters:**
- `ema_trend_filter`: Triple EMA alignment (3/8/21)
- `rsi_filter`: RSI in acceptable range
- `macd_filter`: MACD confirmation
- `ema_slope_filter`: Minimum EMA slope

**Best Use Cases:**
- Classic momentum trading
- Trend following with noise filtering

---

### 4. SuperTrend

**Description:** SuperTrend direction flip. Uses ATR-based bands that flip based on price position. Very responsive to trend changes.

**Entry Logic:**
```
Long:  prev.supertrend_dir == -1 AND bar.supertrend_dir == 1
Short: prev.supertrend_dir == 1 AND bar.supertrend_dir == -1
```

**Re-entry Condition:**
```
Long:  supertrend_dir still == 1 AND adx > 40
Short: supertrend_dir still == -1 AND adx > 40
```

**Parameters:**
| Parameter | Default | Description |
|-----------|---------|-------------|
| `supertrend_period` | 10 | ATR period |
| `supertrend_mult` | 3.0 | ATR multiplier |

**Best Use Cases:**
- Trend following
- Quick direction changes

---

### 5. Alligator (Williams Alligator)

**Description:** Williams Alligator alignment. Long when Lips > Teeth > Jaw (bullish), short when Lips < Teeth < Jaw (bearish). Uses SMMA (Smoothed Moving Average).

**Entry Logic:**
```
Long:  NOT prev.aligned_up AND bar.aligned_up (lips > teeth > jaw)
Short: NOT prev.aligned_down AND bar.aligned_down (lips < teeth < jaw)
```

**Re-entry Condition:**
```
Long:  still aligned_up AND adx > 40
Short: still aligned_down AND adx > 40
```

**Parameters:**
| Parameter | Default | Description |
|-----------|---------|-------------|
| `alligator_jaw_period` | 13 | Jaw SMMA period (blue) |
| `alligator_jaw_offset` | 8 | Jaw offset |
| `alligator_teeth_period` | 8 | Teeth SMMA period (red) |
| `alligator_teeth_offset` | 5 | Teeth offset |
| `alligator_lips_period` | 5 | Lips SMMA period (green) |
| `alligator_lips_offset` | 3 | Lips offset |

**Best Use Cases:**
- Trend confirmation
- Avoiding choppy markets (mouth closed = no trades)

---

### 6. SSL Channel

**Description:** SSL (Semaphore Signal Level) Channel direction flip. Uses SMA of highs and lows with direction based on close position.

**Entry Logic:**
```
Long:  prev.ssl_dir == -1 AND bar.ssl_dir == 1
Short: prev.ssl_dir == 1 AND bar.ssl_dir == -1
```

**Re-entry Condition:**
```
Long:  ssl_dir still == 1 AND adx > 40
Short: ssl_dir still == -1 AND adx > 40
```

**Parameters:**
| Parameter | Default | Description |
|-----------|---------|-------------|
| `ssl_period` | 10 | SSL Channel SMA period |

**Best Use Cases:**
- Trend following
- Quick signal generation

---

### 7. Squeeze (TTM Squeeze)

**Description:** TTM Squeeze release with momentum direction. Squeeze is ON when Bollinger Bands are inside Keltner Channels. Fires when squeeze releases.

**Entry Logic:**
```
Squeeze fires when: prev.squeeze_on AND NOT bar.squeeze_on
Long:  squeeze_fired AND bar.momentum > 0
Short: squeeze_fired AND bar.momentum < 0
```

**Re-entry Condition:**
```
Long:  momentum still > 0 AND adx > 40
Short: momentum still < 0 AND adx > 40
```

**Parameters:**
| Parameter | Default | Description |
|-----------|---------|-------------|
| `squeeze_bb_period` | 20 | Bollinger Band period |
| `squeeze_bb_mult` | 2.0 | Bollinger Band multiplier |
| `squeeze_kc_period` | 20 | Keltner Channel period |
| `squeeze_kc_mult` | 1.5 | Keltner Channel multiplier |
| `squeeze_mom_period` | 12 | Momentum period |

**Best Use Cases:**
- Volatility expansion trades
- Range breakouts

---

### 8. Aroon

**Description:** Aroon Up crosses above Aroon Down for long (and vice versa). Measures bars since highest high / lowest low.

**Entry Logic:**
```
Long:  prev.aroon_up <= prev.aroon_down AND bar.aroon_up > bar.aroon_down
Short: prev.aroon_down <= prev.aroon_up AND bar.aroon_down > bar.aroon_up
```

**Re-entry Condition:**
```
Long:  aroon_up still > aroon_down AND adx > 40
Short: aroon_down still > aroon_up AND adx > 40
```

**Parameters:**
| Parameter | Default | Optimal | Description |
|-----------|---------|---------|-------------|
| `aroon_period` | 25 | **50** | Lookback period |

**Best Use Cases:**
- Trend identification
- Momentum confirmation

---

### 9. ADX Only (+DI/-DI Crossover)

**Description:** Pure DI crossover strategy. Long when +DI crosses above -DI, short when -DI crosses above +DI. Uses the same ADX calculation as the filter.

**Entry Logic:**
```
Long:  prev.plus_di <= prev.minus_di AND bar.plus_di > bar.minus_di
Short: prev.minus_di <= prev.plus_di AND bar.minus_di > bar.plus_di
```

**Re-entry Condition:**
```
Long:  plus_di still > minus_di AND adx > 40
Short: minus_di still > plus_di AND adx > 40
```

**Parameters:**
Uses common ADX parameters (`adx_period`, `di_period`).

**Best Use Cases:**
- Directional movement confirmation
- Simple trend following

---

### 10. Stochastic (Linda Raschke Style)

**Description:** Stochastic %K crosses %D from oversold/overbought zones. Uses Linda Raschke's 7-%K, 16-%D setup from her "Anti" strategy.

**Entry Logic:**
```
Long:  prev.k <= prev.d AND bar.k > bar.d
       AND (prev.k < oversold OR bar.k < 50)
Short: prev.k >= prev.d AND bar.k < bar.d
       AND (prev.k > overbought OR bar.k > 50)
```

**Re-entry Condition:**
```
Long:  k still > d AND adx > 40
Short: k still < d AND adx > 40
```

**Parameters:**
| Parameter | Default | Description |
|-----------|---------|-------------|
| `stoch_k_period` | 7 | %K lookback (Raschke: 7) |
| `stoch_k_slowing` | 4 | %K smoothing |
| `stoch_d_period` | 16 | %D signal period (Raschke: 16) |
| `stoch_overbought` | 80 | Overbought level |
| `stoch_oversold` | 20 | Oversold level |

**Best Use Cases:**
- Mean reversion
- Counter-trend entries in ranging markets

---

### 11. MACD (Linda Raschke Style)

**Description:** MACD line crosses signal line. Uses Linda Raschke's 3-10-16 SMA-based setup (faster than standard 12-26-9).

**Entry Logic:**
```
Long:  prev.macd <= prev.signal AND bar.macd > bar.signal
Short: prev.macd >= prev.signal AND bar.macd < bar.signal
```

**Re-entry Condition:**
```
Long:  macd still > signal AND adx > 40
Short: macd still < signal AND adx > 40
```

**Parameters:**
| Parameter | Default | Description |
|-----------|---------|-------------|
| `macd_fast` | 3 | Fast period (Raschke: 3) |
| `macd_slow` | 10 | Slow period (Raschke: 10) |
| `macd_signal` | 16 | Signal period (Raschke: 16) |
| `macd_use_sma` | true | Use SMA (Raschke) vs EMA |

**Best Use Cases:**
- Momentum confirmation
- Quick signal generation

---

## Choosing a Signal

### For Highest Win Rate
1. **Keltner** (87.8%) - Wide bands, fewer but higher quality signals
2. **VWAP** (85.3%) - Statistical mean reversion
3. **Alligator** (83.5%) - Trend confirmation filter

### For Highest Profit Factor
1. **Keltner** (10.04) - Best risk-adjusted returns
2. **EMA Cross** (6.23) - Classic momentum with separation filter
3. **VWAP** (5.20) - Rolling window adaptation

### For Most Signals
1. **EMA Cross** (310 trades) - Responsive crossover
2. **SuperTrend** (285 trades) - Quick direction changes
3. **VWAP** (268 trades) - Frequent band breakouts

### For Conservative Trading
- Use **Keltner** with `atr_mult=2.75` (wider bands, fewer false signals)
- Enable volume filter
- Use `adx_mode=di_rising` (trend confirmation)

### For Aggressive Trading
- Use **EMA Cross** with separation filter disabled
- Use **SuperTrend** with lower multiplier
- Allow more re-entries (`max_reentries=15`)
