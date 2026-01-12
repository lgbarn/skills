# Data Provider Base Template

Abstract base class for market data providers. Implement this interface to support any data provider.

---

## data_provider_base.py

```python
"""
Data Provider Abstract Base Class
Author: Luther Barnum

Defines the interface all data providers must implement.
Allows swapping between Databento, Polygon, IQFeed, CSV, etc.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Callable, Optional


class DataProviderBase(ABC):
    """
    Abstract base class for market data providers.

    Concrete implementations must provide:
    - Real-time bar streaming (for live trading)
    - Historical bar loading (for backtesting)
    - Clean connection management
    """

    def __init__(self, config):
        """
        Initialize data provider with configuration.

        Args:
            config: Bot configuration object containing:
                - API credentials
                - Symbol/ticker
                - Timeframe settings
        """
        self.config = config
        self._connected = False
        self._callback: Optional[Callable] = None

    @abstractmethod
    async def connect(self) -> None:
        """
        Establish connection to data provider.

        For live providers: Authenticate and open WebSocket/REST connection
        For file providers: Validate file exists and is readable

        Raises:
            ConnectionError: If connection fails
            AuthenticationError: If credentials invalid
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """
        Clean disconnection from data provider.

        - Close WebSocket connections
        - Release resources
        - Cancel subscriptions
        - Mark as disconnected
        """
        pass

    @abstractmethod
    async def subscribe_bars(
        self,
        symbol: str,
        bar_size: int,
        callback: Callable[[dict], None]
    ) -> None:
        """
        Subscribe to real-time bar data stream.

        Args:
            symbol: Ticker symbol (e.g., "NQ.FUT", "ES.FUT")
            bar_size: Bar size in minutes (e.g., 1, 2, 5, 15)
            callback: Async function called when new bar completes
                      Signature: async def on_bar(bar: dict) -> None

        Bar format (dict):
            {
                "timestamp": datetime,  # Bar close time
                "open": float,
                "high": float,
                "low": float,
                "close": float,
                "volume": int,
                "hour": int,  # ET hour (0-23)
                "date": str,  # YYYY-MM-DD
            }

        Raises:
            ValueError: If bar_size not supported
            ConnectionError: If not connected
        """
        pass

    @abstractmethod
    def load_historical_bars(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        bar_size: int = 2
    ) -> list[dict]:
        """
        Load historical bars for backtesting.

        Args:
            symbol: Ticker symbol
            start: Start datetime (inclusive)
            end: End datetime (inclusive)
            bar_size: Bar size in minutes

        Returns:
            List of bar dicts (same format as subscribe_bars)
            Sorted by timestamp ascending

        Raises:
            ValueError: If date range invalid or no data available
        """
        pass

    @property
    def is_connected(self) -> bool:
        """Check if provider is currently connected."""
        return self._connected

    @property
    def provider_name(self) -> str:
        """Return provider name for logging."""
        return self.__class__.__name__
```

---

## Usage Example

```python
# Instantiate a concrete provider
config = Config()

# Option 1: Databento (live + historical)
provider = DatabentoProvider(config)

# Option 2: CSV files (backtest only)
provider = CSVProvider(config)

# Option 3: Polygon (if implemented)
provider = PolygonProvider(config)

# Connect
await provider.connect()

# Subscribe to live data
async def on_bar(bar: dict):
    print(f"New bar: {bar['timestamp']} C={bar['close']}")

await provider.subscribe_bars(
    symbol="NQ.FUT",
    bar_size=2,
    callback=on_bar
)

# Or load historical data
bars = provider.load_historical_bars(
    symbol="NQ.FUT",
    start=datetime(2025, 1, 1),
    end=datetime(2025, 12, 31),
    bar_size=2
)

# Clean up
await provider.disconnect()
```

---

## Implementation Checklist

When implementing a new data provider:

- [ ] Inherit from `DataProviderBase`
- [ ] Implement `connect()` with proper authentication
- [ ] Implement `disconnect()` with resource cleanup
- [ ] Implement `subscribe_bars()` for real-time streaming
- [ ] Implement `load_historical_bars()` for backtesting
- [ ] Ensure bar format matches specification (timestamp, OHLCV, hour, date)
- [ ] Handle timezone conversion to ET (America/New_York)
- [ ] Add error handling for connection failures
- [ ] Add reconnection logic for dropped connections
- [ ] Test with CSV backtest mode first
- [ ] Test with small live data sample before full deployment
- [ ] Document any provider-specific quirks or limitations

---

## Reference Implementations

| Provider | File | Status | Notes |
|----------|------|--------|-------|
| Databento | `databento_client.py` | ✅ Complete | Live + historical, primary data source |
| CSV | `csv_provider.py` | ✅ Complete | Backtest only, reads from files |
| Polygon | `polygon_provider.py` | 📝 Example | Skeleton implementation for reference |

See [DATA_PROVIDER_GUIDE.md](../docs/DATA_PROVIDER_GUIDE.md) for detailed implementation guide.

---

## Testing Your Provider

```python
import pytest
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_provider_connection(provider):
    """Test basic connection."""
    await provider.connect()
    assert provider.is_connected
    await provider.disconnect()
    assert not provider.is_connected

@pytest.mark.asyncio
async def test_subscribe_bars(provider):
    """Test real-time bar subscription."""
    bars_received = []

    async def callback(bar):
        bars_received.append(bar)

    await provider.connect()
    await provider.subscribe_bars("NQ.FUT", 2, callback)

    # Wait for at least one bar (2 min + buffer)
    await asyncio.sleep(130)

    assert len(bars_received) > 0
    bar = bars_received[0]
    assert "timestamp" in bar
    assert "close" in bar
    assert bar["close"] > 0

def test_load_historical(provider):
    """Test historical data loading."""
    start = datetime(2025, 1, 1)
    end = datetime(2025, 1, 31)

    bars = provider.load_historical_bars("NQ.FUT", start, end, bar_size=2)

    assert len(bars) > 0
    assert bars[0]["timestamp"] >= start
    assert bars[-1]["timestamp"] <= end

    # Verify sorted
    timestamps = [b["timestamp"] for b in bars]
    assert timestamps == sorted(timestamps)
```
