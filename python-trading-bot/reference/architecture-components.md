# Bot Components

Detailed component specifications for the trading bot architecture.

---

## 1. DatabentoClient

Handles connection to Databento API for market data (live and historical).

```python
class DatabentoClient:
    async def connect()           # Authenticate and connect to Databento
    async def disconnect()        # Clean disconnection
    async def subscribe_bars()    # Subscribe to real-time bars
    def load_historical_bars()    # Load historical data for backtesting
    async def _handle_messages()  # Process incoming data
```

**Data Flow (Live):**
1. Authenticate with Databento API key
2. Connect to live data feed
3. Subscribe to symbol (e.g., NQ.FUT) with aggregation (2-min bars)
4. Receive OHLCV data as bars complete
5. Call callback with bar data

**Data Flow (Backtest):**
1. Load CSV file with historical bars
2. Replay bars at real-time speed or fast-forward
3. Call callback for each bar
4. Bot processes as if live trading

---

## 2. Indicators

Self-contained technical indicator calculations.

```python
class Indicators:
    def update(bars)      # Recalculate all indicators
    def get_bar(idx)      # Get bar with indicators attached

    # Core indicators
    _calc_ema()           # Exponential Moving Average
    _calc_sma()           # Simple Moving Average
    _calc_smma()          # Smoothed Moving Average
    _calc_atr()           # Average True Range
    _calc_adx()           # ADX with +DI/-DI

    # Signal-specific
    _calc_rolling_vwap()  # VWAP with std dev bands
    _calc_keltner()       # Keltner Channels
    _calc_supertrend()    # SuperTrend
    _calc_alligator()     # Williams Alligator
```

**Key Design:**
- All calculations are pure functions
- No external dependencies (numpy, pandas)
- Results cached for efficiency
- Signal-specific indicators only calculated when needed

---

## 3. RiskManager

Tracks P&L, enforces risk limits, and manages Apex account state (eval/PA modes).

```python
class RiskManager:
    def check_new_day()          # Reset daily stats
    def record_trade()           # Log trade, update account equity
    def is_stopped()             # Check DD breach or profit target hit
    def get_stats()              # Current risk metrics
    def get_position_size()      # Calculate contracts (fixed or risk-based)
    def check_drawdown()         # Verify not breaching trailing/static DD
    def save_state()             # Persist to SQLite
    def load_state()             # Restore from SQLite
```

**Features:**
- **Eval Mode:** Fixed contracts, profit target tracking, trailing drawdown
- **PA Mode:** Risk-based % sizing, static drawdown, equity compounding
- Daily P&L tracking (resets on new trading day)
- Daily max loss enforcement
- Trade logging to SQLite database
- State persistence across restarts
- Session statistics

---

## 4. Bot Core

Main trading logic orchestration.

```python
class Bot:
    async def start()             # Initialize and run
    async def stop()              # Graceful shutdown
    async def on_bar()            # Process each bar

    def _check_signal()           # Signal detection
    def _check_adx()              # ADX filter
    async def _enter_position()   # Enter trade
    async def _check_exits()      # Exit logic
    async def _exit_position()    # Exit trade
```

---

## 5. TradersPostClient

Sends orders via webhook.

```python
class TradersPostClient:
    async def send_signal()   # Send generic signal
    async def buy()           # Long entry
    async def sell()          # Short entry
    async def exit()          # Close position
    async def cancel()        # Cancel orders
```

---

## See Also

- [DATA_FLOW.md](DATA_FLOW.md) - Data flow diagrams and processing logic
- [../ARCHITECTURE.md](../ARCHITECTURE.md) - Architecture overview
- [../templates/](../templates/) - Implementation templates
