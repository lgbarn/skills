# Custom Data Provider Tutorial

Step-by-step guide for implementing custom data providers.

---

## Step 1: Create Provider Class

Inherit from `DataProviderBase` and implement all abstract methods.

```python
from data_provider_base import DataProviderBase
from datetime import datetime
from typing import Callable
import asyncio

class MyCustomProvider(DataProviderBase):
    """Custom data provider implementation."""

    def __init__(self, config):
        super().__init__(config)
        self.api_key = config.my_provider_api_key
        self.ws_connection = None

    async def connect(self) -> None:
        """Establish connection to custom API."""
        # Authenticate
        auth_url = f"https://api.myprovider.com/auth?key={self.api_key}"
        response = await self._authenticate(auth_url)

        if response.status != 200:
            raise ConnectionError("Authentication failed")

        # Open WebSocket
        self.ws_connection = await self._open_websocket()
        self._connected = True

        print(f"Connected to {self.provider_name}")

    async def disconnect(self) -> None:
        """Clean disconnect."""
        if self.ws_connection:
            await self.ws_connection.close()
        self._connected = False
        print(f"Disconnected from {self.provider_name}")

    async def subscribe_bars(
        self,
        symbol: str,
        bar_size: int,
        callback: Callable[[dict], None]
    ) -> None:
        """Subscribe to real-time bars."""
        if not self._connected:
            raise ConnectionError("Not connected")

        self._callback = callback

        # Send subscription message
        subscribe_msg = {
            "action": "subscribe",
            "symbol": symbol,
            "interval": f"{bar_size}m"
        }
        await self.ws_connection.send(subscribe_msg)

        # Start message handler
        asyncio.create_task(self._handle_messages())

    def load_historical_bars(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        bar_size: int = 2
    ) -> list[dict]:
        """Load historical bars from API."""
        url = (
            f"https://api.myprovider.com/bars"
            f"?symbol={symbol}"
            f"&start={start.isoformat()}"
            f"&end={end.isoformat()}"
            f"&interval={bar_size}m"
        )

        response = self._fetch_historical(url)
        bars = self._parse_bars(response)

        return bars

    async def _handle_messages(self):
        """Process incoming WebSocket messages."""
        async for message in self.ws_connection:
            bar = self._parse_bar(message)
            if bar and self._callback:
                await self._callback(bar)

    def _parse_bar(self, message: dict) -> dict:
        """Convert provider format to standard bar format."""
        # Convert provider-specific format to standard format
        return {
            "timestamp": self._parse_timestamp(message["time"]),
            "open": float(message["o"]),
            "high": float(message["h"]),
            "low": float(message["l"]),
            "close": float(message["c"]),
            "volume": int(message["v"]),
            "hour": self._get_et_hour(message["time"]),
            "date": self._get_date_str(message["time"]),
        }
```

---

## Step 2: Add Configuration

Update `config.py` to support your provider:

```python
@dataclass
class Config:
    # ... existing fields ...

    # Custom Provider
    my_provider_api_key: str = ""
    data_source: str = "databento"  # or "csv" or "my_custom"

    def __post_init__(self):
        # ... existing code ...

        # Load custom provider settings
        self.my_provider_api_key = os.getenv("MY_PROVIDER_API_KEY", "")
```

---

## Step 3: Update Bot to Use Your Provider

Modify bot instantiation to select provider based on config:

```python
# In bot_*.py

async def start(self):
    """Start the bot and connect to data feed."""

    # Select data provider
    if self.config.data_source == "databento":
        self.data_client = DatabentoClient(self.config)
    elif self.config.data_source == "csv":
        self.data_client = CSVProvider(self.config)
    elif self.config.data_source == "my_custom":
        self.data_client = MyCustomProvider(self.config)
    else:
        raise ValueError(f"Unknown data source: {self.config.data_source}")

    await self.data_client.connect()

    # Subscribe to bars
    await self.data_client.subscribe_bars(
        symbol=self.config.ticker,
        bar_size=2,
        callback=self.on_bar,
    )
```

---

## See Also

- [PROVIDER_REFERENCE.md](PROVIDER_REFERENCE.md) - Bar format spec, testing, best practices
- [../DATA_PROVIDER_GUIDE.md](../DATA_PROVIDER_GUIDE.md) - Overview and quick start
- [../templates/data_provider_base.py.md](../templates/data_provider_base.py.md) - Base class interface
