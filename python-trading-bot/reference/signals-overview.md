# Top 5 Entry Signals

Backtest results from 219-day NQ futures data (May 2025 - Jan 2026) with ADX di_rising mode, threshold 35.

---

## Summary Table

| Rank | Signal | Profit Factor | Win Rate | Total Trades | Net P&L |
|------|--------|--------------|----------|--------------|---------|
| 1 | **keltner** | 10.04 | 87.8% | 123 | $49,962 |
| 2 | **ema_cross** | 6.23 | 82.7% | 110 | $38,540 |
| 3 | **vwap** | 5.20 | 85.3% | 136 | $42,850 |
| 4 | **supertrend** | 4.41 | 82.5% | 97 | $31,220 |
| 5 | **alligator** | 4.16 | 83.5% | 85 | $28,750 |

*All results with 2 contracts, $500 daily max loss, $4 RT commission, 1 tick slippage.*

---

## Quick Reference

| Signal | Key Parameters | Best For |
|--------|---------------|----------|
| **keltner** | EMA=20, ATR_MULT=2.75 | Best overall performance |
| **ema_cross** | Fast=3, Slow=8, Sep=0.35 | Responsive entries |
| **vwap** | Window=720, Mult=1.0 | Volume-weighted |
| **supertrend** | Period=10, Mult=3.0 | Strong trends only |
| **alligator** | Jaw=13, Teeth=8, Lips=5 | Confirmed trends |

---

## Signal Selection Guide

| If you want... | Use... | Why |
|----------------|--------|-----|
| Best overall performance | **keltner** | Highest PF (10.04), best risk-adjusted returns |
| Responsive entries | **ema_cross** | Fast 3/8 EMAs catch moves early |
| Volume-weighted | **vwap** | Incorporates volume in calculations |
| Strong trends only | **supertrend** | Only enters on direction flip |
| Confirmed trends | **alligator** | Requires full line alignment |

---

## Detailed Documentation

### **[Top 5 Signals](signals-top5.md)**
Comprehensive guide with:
- Complete parameter tables
- Full entry/exit logic code
- Re-entry conditions
- SMMA/VWAP calculations
- Common configuration

### Individual Signal Docs
- [keltner.md](signal-keltner.md) - Keltner Channel details
- [ema_cross.md](signal-ema.md) - EMA Crossover details
- [vwap.md](signal-vwap.md) - Rolling VWAP details
- [supertrend.md](signal-supertrend.md) - SuperTrend details
- [alligator.md](signal-alligator.md) - Williams Alligator details

---

## Signals NOT Included

These signals from backtest.py were excluded due to lower performance:

| Signal | Profit Factor | Why Excluded |
|--------|--------------|--------------|
| ssl | 4.08 | Slightly below alligator |
| squeeze | 3.88 | Lower PF, complex setup |
| aroon | 3.46 | More noise than top 5 |
| adx_only | 3.37 | Relies solely on ADX |
| stochastic | N/A | Not optimized for NQ |
| macd | N/A | Not optimized for NQ |

If you need these signals, refer to `Python/backtest.py` for implementation.

---

## See Also

- [signals-top5.md](signals-top5.md) - Detailed signal documentation
- [config/SIGNAL_PARAMS.md](config/SIGNAL_PARAMS.md) - Configuration reference
- [config/ADX_MODES.md](config/ADX_MODES.md) - ADX filter modes
- [Python/backtest.py](../../../Python/backtest.py) - Reference implementation
