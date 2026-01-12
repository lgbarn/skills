# Core Indicators

EMA, SMA, SMMA, ATR, and ADX calculation implementations.

---

## EMA (Exponential Moving Average)

```python
@staticmethod
def _calc_ema(values: list[float], period: int) -> list[float]:
    """Calculate Exponential Moving Average."""
    if not values:
        return []

    ema = []
    k = 2 / (period + 1)

    for i, v in enumerate(values):
        if i == 0:
            ema.append(v)
        else:
            ema.append(v * k + ema[-1] * (1 - k))

    return ema
```

---

## SMA (Simple Moving Average)

```python
@staticmethod
def _calc_sma(values: list[float], period: int) -> list[float]:
    """Calculate Simple Moving Average."""
    if not values:
        return []

    results = []
    for i in range(len(values)):
        if i < period - 1:
            results.append(values[i])
        else:
            results.append(sum(values[i - period + 1 : i + 1]) / period)

    return results
```

---

## SMMA (Smoothed Moving Average)

```python
@staticmethod
def _calc_smma(values: list[float], period: int) -> list[float]:
    """Calculate Smoothed Moving Average (Wilder's smoothing)."""
    if not values:
        return []

    results = []
    for i in range(len(values)):
        if i == 0:
            results.append(values[0])
        elif i < period:
            results.append(sum(values[: i + 1]) / (i + 1))
        else:
            # SMMA = (prev_smma * (period - 1) + value) / period
            results.append((results[-1] * (period - 1) + values[i]) / period)

    return results
```

---

## ATR (Average True Range)

```python
@staticmethod
def _calc_atr(bars: list[dict], period: int) -> list[float]:
    """Calculate Average True Range."""
    if not bars:
        return []

    trs = []
    for i, bar in enumerate(bars):
        if i == 0:
            tr = bar["high"] - bar["low"]
        else:
            prev = bars[i - 1]
            tr = max(
                bar["high"] - bar["low"],
                abs(bar["high"] - prev["close"]),
                abs(bar["low"] - prev["close"]),
            )
        trs.append(tr)

    return Indicators._calc_ema(trs, period)
```

---

## ADX (Average Directional Index)

```python
@staticmethod
def _calc_adx(
    bars: list[dict], period: int
) -> tuple[list[float], list[float], list[float]]:
    """
    Calculate ADX with +DI and -DI.

    Returns:
        (adx_values, plus_di_values, minus_di_values)
    """
    if not bars:
        return [], [], []

    # True Range
    trs = []
    for i, bar in enumerate(bars):
        if i == 0:
            tr = bar["high"] - bar["low"]
        else:
            prev = bars[i - 1]
            tr = max(
                bar["high"] - bar["low"],
                abs(bar["high"] - prev["close"]),
                abs(bar["low"] - prev["close"]),
            )
        trs.append(tr)

    # +DM and -DM
    plus_dm = [0]
    minus_dm = [0]
    for i in range(1, len(bars)):
        up = bars[i]["high"] - bars[i - 1]["high"]
        down = bars[i - 1]["low"] - bars[i]["low"]
        plus_dm.append(up if up > down and up > 0 else 0)
        minus_dm.append(down if down > up and down > 0 else 0)

    # Smooth with EMA
    plus_dm_ema = Indicators._calc_ema(plus_dm, period)
    minus_dm_ema = Indicators._calc_ema(minus_dm, period)
    atr_ema = Indicators._calc_ema(trs, period)

    # Calculate +DI, -DI, DX
    plus_di_vals = []
    minus_di_vals = []
    dx_vals = []

    for i in range(len(bars)):
        if atr_ema[i] == 0:
            plus_di_vals.append(0)
            minus_di_vals.append(0)
            dx_vals.append(0)
            continue

        plus_di = 100 * plus_dm_ema[i] / atr_ema[i]
        minus_di = 100 * minus_dm_ema[i] / atr_ema[i]
        plus_di_vals.append(plus_di)
        minus_di_vals.append(minus_di)

        di_sum = plus_di + minus_di
        dx = 100 * abs(plus_di - minus_di) / di_sum if di_sum > 0 else 0
        dx_vals.append(dx)

    # Smooth DX to get ADX
    adx_vals = Indicators._calc_ema(dx_vals, period)

    return adx_vals, plus_di_vals, minus_di_vals
```

---

## See Also

- [SIGNAL_INDICATORS.md](SIGNAL_INDICATORS.md) - Signal-specific indicators
- [../INDICATORS.md](../INDICATORS.md) - Indicators class overview
- [../../config/ADX_MODES.md](../../config/ADX_MODES.md) - ADX filter modes
