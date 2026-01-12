# Indicators Template

Self-contained indicator calculations for trading bots.

---

## Class Structure

```python
"""
Technical Indicators for Trading Bot
Self-contained calculations - no external dependencies.
"""

from typing import Optional
from config import Config

class Indicators:
    """Calculate and cache technical indicators."""

    def __init__(self, config: Config):
        self.config = config

        # Cached indicator values (lists aligned with bars)
        self._ema_fast: list[float] = []
        self._ema_slow: list[float] = []
        self._atr: list[float] = []
        self._adx: list[float] = []
        self._plus_di: list[float] = []
        self._minus_di: list[float] = []
        self._vol_ma: list[float] = []

        # Signal-specific
        self._vwap: list[dict] = []
        self._keltner: list[dict] = []
        self._supertrend: list[dict] = []
        self._alligator: list[dict] = []

    def update(self, bars: list[dict]):
        """Recalculate all indicators with new bar data."""
        closes = [b["close"] for b in bars]
        volumes = [b["volume"] for b in bars]

        # Core indicators
        self._ema_fast = self._calc_ema(closes, self.config.ema_fast)
        self._ema_slow = self._calc_ema(closes, self.config.ema_slow)
        self._atr = self._calc_atr(bars, self.config.atr_period)
        self._adx, self._plus_di, self._minus_di = self._calc_adx(
            bars, self.config.adx_period
        )
        self._vol_ma = self._calc_ema(volumes, self.config.volume_ma_period)

        # Signal-specific indicators
        signal = self.config.entry_signal
        if signal == "vwap":
            self._vwap = self._calc_rolling_vwap(...)
        elif signal == "keltner":
            self._keltner = self._calc_keltner(...)
        elif signal == "supertrend":
            self._supertrend = self._calc_supertrend(...)
        elif signal == "alligator":
            self._alligator = self._calc_alligator(...)

    def get_bar(self, idx: int) -> dict:
        """Get bar with indicator values attached."""
        bar = {
            "idx": idx,
            "ema_fast": self._ema_fast[idx] if idx < len(self._ema_fast) else 0,
            "ema_slow": self._ema_slow[idx] if idx < len(self._ema_slow) else 0,
            "atr": self._atr[idx] if idx < len(self._atr) else 0,
            "adx": self._adx[idx] if idx < len(self._adx) else 0,
            "plus_di": self._plus_di[idx] if idx < len(self._plus_di) else 0,
            "minus_di": self._minus_di[idx] if idx < len(self._minus_di) else 0,
            "vol_ma": self._vol_ma[idx] if idx < len(self._vol_ma) else 0,
        }

        # Add signal-specific values
        signal = self.config.entry_signal
        if signal == "vwap" and idx < len(self._vwap):
            bar.update(self._vwap[idx])
        elif signal == "keltner" and idx < len(self._keltner):
            bar.update(self._keltner[idx])
        # ... etc

        return bar
```

---

## Indicator Categories

### **[Core Indicators](indicators/CORE_INDICATORS.md)**
Essential indicators used across all signals:
- EMA (Exponential Moving Average)
- SMA (Simple Moving Average)
- SMMA (Smoothed Moving Average)
- ATR (Average True Range)
- ADX (Average Directional Index) with +DI/-DI

### **[Signal-Specific Indicators](indicators/SIGNAL_INDICATORS.md)**
Indicators for entry signals:
- Rolling VWAP with Standard Deviation Bands
- Keltner Channels
- SuperTrend
- Williams Alligator

---

## Usage Pattern

```python
# In bot initialization
self.indicators = Indicators(self.config)

# On each new bar
def on_bar(self, bar):
    self.bars.append(bar)

    # Recalculate all indicators
    self.indicators.update(self.bars)

    # Get current bar with indicators
    idx = len(self.bars) - 1
    curr = self.indicators.get_bar(idx)

    # Use indicators
    if curr["adx"] > self.config.adx_threshold:
        # Check signal-specific conditions
        if self.config.entry_signal == "keltner":
            if curr["close"] > curr["keltner_upper"]:
                # Long entry logic
                pass
```

---

## Key Design Principles

1. **No External Dependencies**: Pure Python, no numpy/pandas
2. **Cached Results**: Calculate once per bar, reuse
3. **Signal-Specific Loading**: Only calculate needed indicators
4. **Aligned Lists**: All indicator lists match bars list index
5. **Safe Access**: Returns 0 for out-of-bounds indices

---

## See Also

- [indicators/CORE_INDICATORS.md](indicators/CORE_INDICATORS.md) - Core implementations
- [indicators/SIGNAL_INDICATORS.md](indicators/SIGNAL_INDICATORS.md) - Signal implementations
- [../signals/TOP_5_SIGNALS.md](../signals/TOP_5_SIGNALS.md) - Usage in signals
- [../config/ADX_MODES.md](../config/ADX_MODES.md) - ADX filter configuration
