# Signal-Specific Indicators

VWAP, Keltner Channels, SuperTrend, and Williams Alligator implementations.

---

## Rolling VWAP with Standard Deviation Bands

```python
@staticmethod
def _calc_rolling_vwap(
    bars: list[dict], window: int, band_mult: float
) -> list[dict]:
    """
    Calculate Rolling VWAP with standard deviation bands.

    Returns list of dicts with 'vwap', 'upper', 'lower' keys.
    """
    results = []

    for i in range(len(bars)):
        start = max(0, i - window + 1)
        chunk = bars[start : i + 1]

        # VWAP = Σ(TP × Vol) / Σ(Vol)
        tpv_sum = sum(
            (r["high"] + r["low"] + r["close"]) / 3 * r["volume"] for r in chunk
        )
        vol_sum = sum(r["volume"] for r in chunk)

        if vol_sum == 0:
            results.append(
                {
                    "vwap": bars[i]["close"],
                    "upper": bars[i]["close"],
                    "lower": bars[i]["close"],
                }
            )
            continue

        vwap = tpv_sum / vol_sum

        # Variance = E[X²] - E[X]²
        tp2v_sum = sum(
            ((r["high"] + r["low"] + r["close"]) / 3) ** 2 * r["volume"]
            for r in chunk
        )
        variance = (tp2v_sum / vol_sum) - (vwap**2)
        std = variance**0.5 if variance > 0 else 0

        results.append(
            {
                "vwap": vwap,
                "upper": vwap + (std * band_mult),
                "lower": vwap - (std * band_mult),
            }
        )

    return results
```

---

## Keltner Channels

```python
@staticmethod
def _calc_keltner(
    bars: list[dict], ema_period: int, atr_period: int, atr_mult: float
) -> list[dict]:
    """
    Calculate Keltner Channels.

    Returns list of dicts with 'middle', 'upper', 'lower' keys.
    """
    closes = [b["close"] for b in bars]
    middle = Indicators._calc_ema(closes, ema_period)
    atr = Indicators._calc_atr(bars, atr_period)

    results = []
    for i in range(len(bars)):
        band_width = atr[i] * atr_mult
        results.append(
            {
                "keltner_middle": middle[i],
                "keltner_upper": middle[i] + band_width,
                "keltner_lower": middle[i] - band_width,
            }
        )

    return results
```

---

## SuperTrend

```python
@staticmethod
def _calc_supertrend(
    bars: list[dict], period: int, multiplier: float
) -> list[dict]:
    """
    Calculate SuperTrend indicator.

    Returns list of dicts with 'supertrend', 'supertrend_dir' keys.
    """
    atr = Indicators._calc_atr(bars, period)

    results = []
    prev_upper = prev_lower = prev_st = 0

    for i in range(len(bars)):
        hl2 = (bars[i]["high"] + bars[i]["low"]) / 2

        # Basic bands
        basic_upper = hl2 + (multiplier * atr[i])
        basic_lower = hl2 - (multiplier * atr[i])

        # Final bands (only move in trend direction)
        if i == 0:
            final_upper = basic_upper
            final_lower = basic_lower
        else:
            prev_close = bars[i - 1]["close"]
            final_upper = (
                basic_upper
                if basic_upper < prev_upper or prev_close > prev_upper
                else prev_upper
            )
            final_lower = (
                basic_lower
                if basic_lower > prev_lower or prev_close < prev_lower
                else prev_lower
            )

        # Determine direction
        close = bars[i]["close"]
        if i == 0:
            direction = 1
            supertrend = final_lower
        else:
            if prev_st == prev_upper:
                direction = 1 if close > final_upper else -1
            else:
                direction = -1 if close < final_lower else 1

            supertrend = final_lower if direction == 1 else final_upper

        results.append({"supertrend": supertrend, "supertrend_dir": direction})

        prev_upper = final_upper
        prev_lower = final_lower
        prev_st = supertrend

    return results
```

---

## Williams Alligator

```python
@staticmethod
def _calc_alligator(
    bars: list[dict],
    jaw_period: int,
    jaw_offset: int,
    teeth_period: int,
    teeth_offset: int,
    lips_period: int,
    lips_offset: int,
) -> list[dict]:
    """
    Calculate Williams Alligator indicator.

    Returns list of dicts with 'jaw', 'teeth', 'lips', 'aligned_up', 'aligned_down' keys.
    """
    # Median price (HL2)
    hl2 = [(b["high"] + b["low"]) / 2 for b in bars]

    # Calculate base SMAs (without offset)
    jaw_base = Indicators._calc_smma(hl2, jaw_period)
    teeth_base = Indicators._calc_smma(hl2, teeth_period)
    lips_base = Indicators._calc_smma(hl2, lips_period)

    results = []
    for i in range(len(bars)):
        # Apply offset (shift values forward, so we look back)
        jaw = jaw_base[i - jaw_offset] if i >= jaw_offset else jaw_base[0]
        teeth = (
            teeth_base[i - teeth_offset] if i >= teeth_offset else teeth_base[0]
        )
        lips = lips_base[i - lips_offset] if i >= lips_offset else lips_base[0]

        # Alignment check
        aligned_up = lips > teeth > jaw  # Bullish alignment
        aligned_down = lips < teeth < jaw  # Bearish alignment

        results.append(
            {
                "alligator_jaw": jaw,
                "alligator_teeth": teeth,
                "alligator_lips": lips,
                "aligned_up": aligned_up,
                "aligned_down": aligned_down,
            }
        )

    return results
```

---

## See Also

- [CORE_INDICATORS.md](CORE_INDICATORS.md) - Core indicator implementations
- [../INDICATORS.md](../INDICATORS.md) - Indicators class overview
- [../../signals/TOP_5_SIGNALS.md](../../signals/TOP_5_SIGNALS.md) - Signal usage examples
