# Bot Architecture

Technical overview of the trading bot internals.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        MARKET DATA                                   │
│                                                                      │
│    ┌────────────────────────────────────────────────────────────┐   │
│    │              DATABENTO API / CSV FILES                      │   │
│    │    https://databento.com/api                                │   │
│    │    - Authenticate with API key                              │   │
│    │    - Subscribe to real-time 2-min bars                      │   │
│    │    - Historical data download                               │   │
│    │    - CSV file replay for backtesting                        │   │
│    └────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│                              ▼                                       │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        PYTHON BOT                                    │
│                                                                      │
│    ┌────────────────┐    ┌────────────────┐    ┌────────────────┐   │
│    │ DatabentoClient │    │   Indicators    │    │   RiskManager   │   │
│    │  - Connect       │    │  - EMA, ATR     │    │  - Apex acct    │   │
│    │  - Subscribe     │───▶│  - ADX, VWAP    │───▶│  - Eval/PA mode │   │
│    │  - Receive bars  │    │  - Signal ind.  │    │  - Sizing logic │   │
│    └────────────────┘    └────────────────┘    └────────────────┘   │
│                                                         │            │
│    ┌────────────────────────────────────────────────────▼───────┐   │
│    │                      BOT CORE                               │   │
│    │  - Signal detection (edge-triggered crossovers)            │   │
│    │  - Position management (entry, SL, TP, trailing)           │   │
│    │  - Re-entry logic (3 bars wait, ADX > 40)                  │   │
│    │  - Session/volume/ADX filters                              │   │
│    │  - News calendar blackouts                                 │   │
│    │  - State persistence (SQLite)                              │   │
│    └────────────────────────────────────────────────────────────┘   │
│                              │                                       │
└──────────────────────────────│───────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      ORDER EXECUTION                                 │
│                                                                      │
│    ┌────────────────────────────────────────────────────────────┐   │
│    │              TRADERSPOST WEBHOOK                            │   │
│    │    POST https://webhooks.traderspost.io/trading/webhook/...│   │
│    │    - Send {ticker, action, quantity, stopLoss, takeProfit} │   │
│    │    - Receive confirmation with order ID                     │   │
│    └────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│                              ▼                                       │
│    ┌────────────────────────────────────────────────────────────┐   │
│    │              TRADOVATE / APEX                               │   │
│    │    - Execute market orders                                  │   │
│    │    - Manage OCO brackets (SL/TP)                           │   │
│    │    - Track positions                                        │   │
│    └────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Details

See [architecture-components.md](architecture-components.md) for detailed information on:
- DatabentoClient (market data)
- Indicators (technical calculations)
- RiskManager (P&L tracking, Apex modes)
- Bot Core (trading logic)
- TradersPostClient (order execution)

---

## Data Flow

See [architecture-dataflow.md](architecture-dataflow.md) for detailed flow diagrams:
- Bar processing flow
- Entry flow with filters
- Exit flow with priority order
- Signal detection (edge-triggered)
- ADX filter modes
- Position state machine
- Error handling

---

## File Structure

```
Python/bots/<signal>/
├── bot_<signal>.py              # Main entry point
├── config.py                    # Configuration from .env
├── databento_client.py          # Market data (Databento API)
├── traderspost_client.py        # Order execution (TradersPost webhook)
├── risk_manager.py              # Apex account tracking (eval/PA modes)
├── indicators.py                # Self-contained indicator calculations
├── news_calendar.py             # Economic calendar filtering (optional)
├── alerting.py                  # Email/SMS alerts (optional)
├── bot_state.db                 # SQLite persistence (created at runtime)
├── requirements.txt             # Python dependencies
├── .env.example                 # Credential template
├── .gitignore                   # Exclude .env, logs, *.db
└── README.md                    # Bot documentation
```

---

## Performance Considerations

1. **Indicator Caching**: Calculate once per bar, not per check
2. **No NumPy/Pandas**: Pure Python for minimal dependencies
3. **Async I/O**: Non-blocking WebSocket and HTTP
4. **Memory Management**: Keep only necessary bar history
5. **Reconnection Logic**: Auto-recover from disconnects

---

## See Also

- [architecture-components.md](architecture-components.md) - Detailed component specifications
- [architecture-dataflow.md](architecture-dataflow.md) - Flow diagrams and logic
- [DEPLOYMENT.md](deployment.md) - Production deployment guide
- [config-index.md](config-index.md) - Configuration reference
