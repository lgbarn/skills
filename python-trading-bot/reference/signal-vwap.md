# Rolling VWAP Signal

**Volume-Weighted Momentum** - Profit Factor: 5.20 | Win Rate: 85.3%

## Signal Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| `vwap_window` | 720 | Rolling window in bars (24h at 2-min) |
| `band_multiplier` | 1.0 | Standard deviation multiplier |

## Code Blocks

### Signal Detection (`{{SIGNAL_DETECTION_CODE}}`)

```python
# Rolling VWAP band breakout
# Long: Price crosses above upper band (VWAP + 1σ)
# Short: Price crosses below lower band (VWAP - 1σ)
long_sig = (
    prev["close"] <= prev["upper"]
    and curr["close"] > curr["upper"]
)
short_sig = (
    prev["close"] >= prev["lower"]
    and curr["close"] < curr["lower"]
)
```

### Re-entry Logic (`{{REENTRY_LOGIC_CODE}}`)

```python
# Re-enter if price still beyond VWAP band
if self.last_exit_direction == 1 and curr["close"] > curr["upper"]:
    long_sig = True
    is_reentry = True
elif self.last_exit_direction == -1 and curr["close"] < curr["lower"]:
    short_sig = True
    is_reentry = True
```

### Config Parameters (`{{SIGNAL_PARAMS}}`)

```python
# VWAP Parameters
vwap_window: int = 720  # 24 hours at 2-min bars
band_multiplier: float = 1.0  # 1 standard deviation
```

## Placeholder Values

| Placeholder | Value |
|-------------|-------|
| `{{SIGNAL}}` | `vwap` |
| `{{SIGNAL_NAME}}` | `Rolling VWAP` |
| `{{SIGNAL_CLASS}}` | `Vwap` |
| `{{SIGNAL_DESCRIPTION}}` | `Band breakout` |
| `{{PROFIT_FACTOR}}` | `5.20` |
| `{{WIN_RATE}}` | `85.3%` |
| `{{WARMUP_BARS}}` | `720` |

## VWAP Calculation

```python
def calc_rolling_vwap(bars, window, band_mult):
    for i in range(len(bars)):
        chunk = bars[max(0, i - window + 1):i + 1]

        # VWAP = Σ(Typical Price × Volume) / Σ(Volume)
        # Typical Price = (High + Low + Close) / 3
        tpv_sum = sum(
            (r["high"] + r["low"] + r["close"]) / 3 * r["volume"]
            for r in chunk
        )
        vol_sum = sum(r["volume"] for r in chunk)
        vwap = tpv_sum / vol_sum if vol_sum > 0 else bars[i]["close"]

        # Variance = E[X²] - E[X]² (numerically stable)
        tp2v_sum = sum(
            ((r["high"] + r["low"] + r["close"]) / 3) ** 2 * r["volume"]
            for r in chunk
        )
        variance = (tp2v_sum / vol_sum) - (vwap ** 2) if vol_sum > 0 else 0
        std = variance ** 0.5 if variance > 0 else 0

        upper = vwap + (std * band_mult)
        lower = vwap - (std * band_mult)
```

## Entry Conditions

1. **Base Signal**: Price crosses VWAP band
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
4. Price still above/below VWAP band
5. Max 10 re-entries per trend

## Performance Notes

- 720-bar window = 24 hours of data (at 2-min bars)
- Uses rolling VWAP (not session-reset VWAP)
- 1σ bands capture meaningful moves without over-filtering
- Incorporates volume weighting for institutional-level signals
- Works best when volume spikes accompany breakouts
- Higher window = smoother bands but slower signals

## Window Considerations

| Window | Period | Use Case |
|--------|--------|----------|
| 180 | 6 hours | Intraday scalping |
| 360 | 12 hours | Day trading |
| 720 | 24 hours | Default (recommended) |
| 1440 | 48 hours | Swing trading |
