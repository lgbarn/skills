# Data Provider Reference

Bar format specification, timezone handling, testing procedures, and best practices.

---

## Bar Format Specification

All providers must return bars in this exact format:

```python
{
    "timestamp": datetime,  # Bar close time (timezone-aware)
    "open": float,          # Opening price
    "high": float,          # High price
    "low": float,           # Low price
    "close": float,         # Closing price
    "volume": int,          # Volume
    "hour": int,            # ET hour (0-23) for session filtering
    "date": str,            # Date string "YYYY-MM-DD"
}
```

---

## Timezone Handling

**CRITICAL:** All timestamps must be in **America/New_York (ET)** timezone.

```python
from datetime import datetime
import pytz

def convert_to_et(utc_timestamp: datetime) -> datetime:
    """Convert UTC timestamp to ET."""
    et_tz = pytz.timezone("America/New_York")

    # If timestamp is naive, assume UTC
    if utc_timestamp.tzinfo is None:
        utc_tz = pytz.UTC
        utc_timestamp = utc_tz.localize(utc_timestamp)

    # Convert to ET
    et_timestamp = utc_timestamp.astimezone(et_tz)
    return et_timestamp

def get_et_hour(timestamp: datetime) -> int:
    """Extract ET hour from timestamp."""
    et_timestamp = convert_to_et(timestamp)
    return et_timestamp.hour
```

### Example Conversion

```python
def _parse_bar(self, raw_bar: dict) -> dict:
    """Convert provider format to standard format."""

    # Parse timestamp (provider-specific)
    raw_time = raw_bar["timestamp"]  # e.g., "2025-01-10T14:30:00Z"
    utc_dt = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))

    # Convert to ET
    et_dt = convert_to_et(utc_dt)

    # Build standard bar
    return {
        "timestamp": et_dt,
        "open": float(raw_bar["open"]),
        "high": float(raw_bar["high"]),
        "low": float(raw_bar["low"]),
        "close": float(raw_bar["close"]),
        "volume": int(raw_bar["volume"]),
        "hour": et_dt.hour,
        "date": et_dt.strftime("%Y-%m-%d"),
    }
```

---

## Testing Your Provider

### Unit Tests

```python
import pytest
from datetime import datetime, timedelta
from my_custom_provider import MyCustomProvider
from config import Config

@pytest.fixture
def provider():
    config = Config()
    config.my_provider_api_key = "test_key"
    return MyCustomProvider(config)

@pytest.mark.asyncio
async def test_connection(provider):
    """Test basic connection."""
    await provider.connect()
    assert provider.is_connected

    await provider.disconnect()
    assert not provider.is_connected

@pytest.mark.asyncio
async def test_bar_format(provider):
    """Test bar format compliance."""
    bars_received = []

    async def callback(bar):
        bars_received.append(bar)

    await provider.connect()
    await provider.subscribe_bars("NQ.FUT", 2, callback)

    # Wait for one bar
    await asyncio.sleep(130)

    assert len(bars_received) > 0

    bar = bars_received[0]

    # Check all required fields
    assert "timestamp" in bar
    assert "open" in bar
    assert "high" in bar
    assert "low" in bar
    assert "close" in bar
    assert "volume" in bar
    assert "hour" in bar
    assert "date" in bar

    # Check types
    assert isinstance(bar["timestamp"], datetime)
    assert isinstance(bar["open"], float)
    assert isinstance(bar["high"], float)
    assert isinstance(bar["low"], float)
    assert isinstance(bar["close"], float)
    assert isinstance(bar["volume"], int)
    assert isinstance(bar["hour"], int)
    assert isinstance(bar["date"], str)

    # Check ET timezone
    assert bar["timestamp"].tzinfo is not None
    assert bar["hour"] >= 0 and bar["hour"] < 24

def test_historical_bars(provider):
    """Test historical data loading."""
    start = datetime(2025, 1, 1)
    end = datetime(2025, 1, 31)

    bars = provider.load_historical_bars("NQ.FUT", start, end, bar_size=2)

    # Check we got data
    assert len(bars) > 0

    # Check date range
    assert bars[0]["timestamp"] >= start
    assert bars[-1]["timestamp"] <= end

    # Check sorted
    timestamps = [b["timestamp"] for b in bars]
    assert timestamps == sorted(timestamps)

    # Check no duplicates
    assert len(timestamps) == len(set(timestamps))
```

### Integration Test with Bot

```python
@pytest.mark.asyncio
async def test_bot_with_custom_provider():
    """Test full bot with custom provider."""
    config = Config()
    config.data_source = "my_custom"
    config.my_provider_api_key = "test_key"
    config.csv_path = "tests/data/test_bars.csv"  # Fallback for testing

    bot = KeltnerBot(config)

    # Run for 5 minutes
    task = asyncio.create_task(bot.start())
    await asyncio.sleep(300)

    await bot.stop()

    # Check bot received bars and processed them
    assert len(bot.bars) > 0
```

---

## Common Provider Issues

### Issue: Timestamps in Wrong Timezone

**Problem:** Bot trading outside allowed hours or at weird times.

**Solution:** Always convert to ET timezone.

```python
# ❌ Wrong - using provider's native timezone
bar["timestamp"] = raw_bar["timestamp"]

# ✅ Correct - convert to ET
bar["timestamp"] = convert_to_et(raw_bar["timestamp"])
```

### Issue: Missing Bars

**Problem:** Provider skips bars with zero volume or outside market hours.

**Solution:** Decide on strategy:
1. Accept gaps (most common)
2. Fill with previous bar's close (forward fill)
3. Filter during bot processing

```python
def load_historical_bars(self, symbol, start, end, bar_size=2):
    bars = self._fetch_from_api(symbol, start, end, bar_size)

    # Option 1: Return as-is (gaps allowed)
    return bars

    # Option 2: Forward fill gaps
    return self._forward_fill_gaps(bars, bar_size)
```

### Issue: Rate Limiting

**Problem:** Provider throttles requests, connection drops.

**Solution:** Implement backoff and retry logic.

```python
async def connect(self, max_retries=3):
    for attempt in range(max_retries):
        try:
            await self._do_connect()
            return
        except RateLimitError:
            wait_time = 2 ** attempt  # Exponential backoff
            await asyncio.sleep(wait_time)

    raise ConnectionError("Max retries exceeded")
```

### Issue: WebSocket Disconnections

**Problem:** Connection drops randomly, bot stops receiving data.

**Solution:** Auto-reconnect logic.

```python
async def _handle_messages(self):
    """Process messages with auto-reconnect."""
    while self._connected:
        try:
            async for message in self.ws_connection:
                bar = self._parse_bar(message)
                if bar and self._callback:
                    await self._callback(bar)
        except WebSocketDisconnect:
            logger.warning("WebSocket disconnected, reconnecting...")
            await asyncio.sleep(5)
            await self._reconnect()
```

---

## Best Practices

1. **Start with CSV:** Always test your bot with CSV backtest before connecting live provider
2. **Handle Errors Gracefully:** Network issues, API downtime, rate limits are inevitable
3. **Log Everything:** Debug connection issues by logging all API calls and responses
4. **Validate Data:** Check for missing bars, bad ticks, outlier prices
5. **Timezone Awareness:** Always work in ET timezone for consistency
6. **Test Reconnection:** Manually disconnect during testing to verify auto-reconnect works
7. **Monitor Performance:** Track latency, message throughput, dropped bars
8. **Document Quirks:** Every provider has oddities - document them for future reference

---

## See Also

- [CUSTOM_PROVIDER_TUTORIAL.md](CUSTOM_PROVIDER_TUTORIAL.md) - Step-by-step implementation guide
- [../DATA_PROVIDER_GUIDE.md](../DATA_PROVIDER_GUIDE.md) - Overview and provider comparison
- [../templates/data_provider_base.py.md](../templates/data_provider_base.py.md) - Base class specification
