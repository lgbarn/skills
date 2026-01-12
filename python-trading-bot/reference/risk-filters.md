# Risk Management & Filters

Risk management, session/volume/news filters, alerting, and state persistence configuration.

---

## Risk Management

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `contracts` | int | 2 | 1-10 | Contracts per trade |
| `daily_max_loss` | float | 500.0 | 100-2000 | Stop trading if daily loss exceeds |
| `slippage_ticks` | int | 1 | 0-5 | Assumed slippage per side |
| `commission_rt` | float | 4.00 | 0-10 | Round-trip commission per contract |
| `point_value` | float | 5.0 | - | NQ point value ($5/point) |
| `tick_size` | float | 0.25 | - | NQ tick size |

**Daily P&L Tracking:**
```python
# Reset on new trading day
if bar_date != current_date:
    current_date = bar_date
    daily_pnl = 0.0
    daily_stopped = False

# Check daily max loss
if daily_pnl <= -daily_max_loss:
    daily_stopped = True
    # Exit any open position
    # Stop trading for rest of day
```

---

## Session Filter

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `session_filter` | bool | true | Only trade during allowed hours |
| `allowed_hours` | list | [9,10,11,12,13,14,15,16,18,19,20] | Hours (ET) when trading allowed |

**Excluded Hours:**
- Pre-market: 0-8 (before RTH)
- Lunch: 17 (low volume)
- Overnight: 21-23 (thin markets)

---

## Volume Filter

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `volume_filter` | bool | true | - | Require volume > MA |
| `volume_ma_period` | int | 20 | 10-50 | Volume MA period |

**Logic:**
```python
if volume_filter:
    if bar["volume"] < bar["vol_ma"]:
        # Skip entry - low volume
        long_sig = short_sig = False
```

---

## News Calendar Filter

| Parameter | Type | Default | Options | Description |
|-----------|------|---------|---------|-------------|
| `news_filter_enabled` | bool | false | - | Enable economic calendar blackout periods |
| `news_api` | str | "fmp" | "fmp", "tradingeconomics", "manual" | News data provider |
| `news_api_key` | str | "" | - | API key for news provider |
| `news_blackout_minutes` | int | 30 | 15-60 | Minutes before/after high-impact events to avoid |
| `news_config_file` | str | "" | - | Path to manual JSON config (if news_api="manual") |

**High-Impact Events Tracked:**
- FOMC announcements (Federal Reserve policy decisions)
- Non-Farm Payrolls (NFP - first Friday of month, 8:30 AM ET)
- CPI/PPI releases (Consumer/Producer Price Index)
- GDP reports (quarterly)
- Fed Chair speeches
- Jobless claims (weekly, Thursdays 8:30 AM ET)

**Provider Options:**
- **fmp**: Financial Modeling Prep API (free tier available)
- **tradingeconomics**: Trading Economics API (paid)
- **manual**: JSON file with hardcoded event times

See [docs/ECONOMIC_CALENDAR.md](economic-calendar.md) for detailed integration guide.

---

## Alerting

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `alert_email_enabled` | bool | false | Enable email alerts |
| `alert_email_to` | str | "" | Destination email address |
| `alert_email_from` | str | "" | Sender email (SMTP) |
| `alert_email_smtp_host` | str | "smtp.gmail.com" | SMTP server |
| `alert_email_smtp_port` | int | 587 | SMTP port |
| `alert_email_smtp_user` | str | "" | SMTP username |
| `alert_email_smtp_password` | str | "" | SMTP password or app token |

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `alert_sms_enabled` | bool | false | Enable SMS/push alerts (via Pushover) |
| `alert_pushover_token` | str | "" | Pushover app token |
| `alert_pushover_user` | str | "" | Pushover user key |

**Alert Triggers:**
- Daily P&L approaching limit (80%, 90%, 100%)
- Trailing drawdown approaching breach (eval mode)
- Static drawdown approaching breach (PA mode)
- Profit target reached (eval mode)
- Connection loss > 2 minutes
- Order execution failures
- Consecutive losing trades (5+)
- Bot crash/restart

**Alert Priority Levels:**
- **Low (-2):** Informational (trade executed, daily summary)
- **Normal (0):** Standard notification (approaching limits)
- **High (1):** Important warning (80% of daily limit, connection issues)
- **Emergency (2):** Critical alert (DD breach, order failures) - requires acknowledgment on phone

See [templates/ALERTING.md](../templates/alerting.py.md) for implementation template.

---

## State Persistence

| Parameter | Type | Default | Description |
|-----------|------|---------|-------|-------------|
| `persistence_enabled` | bool | true | Enable SQLite state persistence |
| `db_path` | str | "bot_state.db" | Path to SQLite database file |
| `save_interval` | int | 1 | Save state every N trades (1 = after each trade) |

**Persisted Data:**
- Account state (equity, HWM, DD status)
- Open position details (entry, SL, TP, direction)
- Daily P&L records
- Full trade history
- Re-entry tracking (last exit, count)

**Benefits:**
- Survive bot restarts mid-day without losing state
- Resume trading with exact position/P&L knowledge
- Historical trade analysis from database
- Audit trail for Apex compliance

**Database Schema:**
```sql
-- account_state table
CREATE TABLE account_state (
    id INTEGER PRIMARY KEY,
    equity REAL,
    high_water_mark REAL,
    dd_threshold REAL,
    dd_locked BOOLEAN,
    profit_target_hit BOOLEAN,
    last_updated TIMESTAMP
);

-- positions table
CREATE TABLE positions (
    id INTEGER PRIMARY KEY,
    direction INTEGER,  -- 1=long, -1=short, 0=flat
    entry_price REAL,
    stop_loss REAL,
    take_profit REAL,
    trail_on BOOLEAN,
    hwm REAL,
    lwm REAL,
    opened_at TIMESTAMP
);

-- daily_pnl table
CREATE TABLE daily_pnl (
    date TEXT PRIMARY KEY,
    pnl REAL,
    trades INTEGER,
    stopped BOOLEAN
);

-- trades table
CREATE TABLE trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP,
    direction INTEGER,
    entry_price REAL,
    exit_price REAL,
    exit_reason TEXT,
    pnl REAL,
    contracts INTEGER
);
```

See [templates/PERSISTENCE.md](../templates/persistence.py.md) for implementation template.

---

## See Also

- [templates/RISK_MANAGER.md](../templates/risk_manager.py.md) - Risk manager implementation
- [templates/NEWS_FILTER.md](../templates/news_filter.py.md) - News calendar integration
- [templates/ALERTING.md](../templates/alerting.py.md) - Alert system implementation
- [templates/PERSISTENCE.md](../templates/persistence.py.md) - State persistence template
