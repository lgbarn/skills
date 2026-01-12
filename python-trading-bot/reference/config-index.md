# Bot Configuration Reference

Complete parameter reference for Python trading bots - organized by topic.

---

## Configuration Topics

### Account & Risk
- **[Apex Account Configuration](config/APEX_ACCOUNTS.md)** - Account modes (eval/PA), presets, position sizing
- **[Risk Management & Filters](config/RISK_FILTERS.md)** - Risk params, session/volume/news filters, alerts, persistence

### Trading Logic
- **[Signal Parameters](config/SIGNAL_PARAMS.md)** - All 5 entry signals (Keltner, EMA, VWAP, SuperTrend, Alligator)
- **[ADX Filter Modes](config/ADX_MODES.md)** - ADX configuration and modes (traditional, di_rising, etc.)
- **[Exits & Re-entry](config/EXITS_REENTRY.md)** - Stop loss, take profit, trailing stops, re-entry logic

---

## Quick Reference

| Category | Key Parameters | See |
|----------|---------------|-----|
| **Account** | account_mode, account_size, risk_pct | [APEX_ACCOUNTS.md](config/APEX_ACCOUNTS.md) |
| **Signals** | entry_signal, keltner_*, ema_*, vwap_*, etc. | [SIGNAL_PARAMS.md](config/SIGNAL_PARAMS.md) |
| **ADX Filter** | adx_threshold, adx_mode (di_rising) | [ADX_MODES.md](config/ADX_MODES.md) |
| **Exits** | sl_atr_mult, tp_atr_mult, trail_* | [EXITS_REENTRY.md](config/EXITS_REENTRY.md) |
| **Re-entry** | reentry_enabled, max_reentries | [EXITS_REENTRY.md](config/EXITS_REENTRY.md) |
| **Risk** | contracts, daily_max_loss, commission_rt | [RISK_FILTERS.md](config/RISK_FILTERS.md) |
| **Filters** | session_filter, volume_filter, news_filter | [RISK_FILTERS.md](config/RISK_FILTERS.md) |
| **Alerts** | alert_email_*, alert_pushover_* | [RISK_FILTERS.md](config/RISK_FILTERS.md) |
| **Persistence** | persistence_enabled, db_path | [RISK_FILTERS.md](config/RISK_FILTERS.md) |

---

## Environment Variables

Required in `.env` file:

```bash
# Tradovate API
TRADOVATE_USERNAME=your_username
TRADOVATE_PASSWORD=your_password
TRADOVATE_CID=your_cid
TRADOVATE_SECRET=your_secret
TRADOVATE_ENV=demo  # or "live"

# TradersPost Webhook
TRADERSPOST_WEBHOOK_URL=https://webhooks.traderspost.io/trading/webhook/{uuid}/{password}

# Bot Settings
BOT_TICKER=NQH5  # Current front-month contract
BOT_PAPER_MODE=true  # Start in paper mode
```

---

## Complete Default Configuration

```python
CONFIG = {
    # Signal
    "entry_signal": "keltner",

    # Keltner Parameters
    "keltner_ema_period": 20,
    "keltner_atr_period": 14,
    "keltner_atr_mult": 2.75,

    # ADX Filter
    "adx_enabled": True,
    "adx_period": 14,
    "di_period": 14,
    "adx_threshold": 35,
    "adx_mode": "di_rising",

    # Exits
    "atr_period": 14,
    "sl_atr_mult": 3.0,
    "tp_atr_mult": 3.0,
    "trail_enabled": True,
    "trail_trigger_atr": 0.15,
    "trail_distance_atr": 0.15,

    # Re-entry
    "reentry_enabled": True,
    "reentry_bars_wait": 3,
    "reentry_adx_min": 40,
    "max_reentries": 10,

    # Risk Management
    "contracts": 2,
    "daily_max_loss": 500.0,
    "slippage_ticks": 1,
    "commission_rt": 4.00,
    "point_value": 5.0,
    "tick_size": 0.25,

    # Filters
    "volume_filter": True,
    "volume_ma_period": 20,
    "session_filter": True,
    "allowed_hours": {9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20},
}
```

---

## Contract Settings (NQ Futures)

| Constant | Value | Description |
|----------|-------|-------------|
| `POINT_VALUE` | 5.0 | $5 per point for NQ |
| `TICK_SIZE` | 0.25 | Minimum price increment |
| `TICK_VALUE` | 1.25 | $1.25 per tick |

**P&L Calculation:**
```python
# Points * Point Value * Contracts - Costs
pnl = (exit_price - entry_price) * direction * point_value * contracts
pnl -= slippage * 2 * point_value * contracts  # Entry + exit
pnl -= commission_rt * contracts
```

---

## See Also

- [SIGNALS.md](SIGNALS.md) - Signal selection guide with backtest metrics
- [docs/EVAL_VS_PA.md](docs/EVAL_VS_PA.md) - Eval vs PA mode comparison
- [docs/SETUP.md](docs/SETUP.md) - Environment setup guide
- [templates/](templates/) - Implementation templates
