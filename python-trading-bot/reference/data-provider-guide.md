# Data Provider Implementation Guide

How to implement custom data providers for the trading bot.

---

## Overview

The bot uses a provider-agnostic adapter pattern for market data. This allows you to:
- Swap data sources without changing bot code
- Test with CSV files before going live
- Support multiple data providers
- Implement your own custom adapters

**Built-in Providers:**
- **DatabentoProvider** - Primary live/historical data source
- **CSVProvider** - Backtest from CSV files

**Example Providers:**
- **PolygonProvider** - Skeleton for Polygon.io integration

---

## Quick Start

### Using Built-in Databento Provider

```python
from config import Config
from databento_client import DatabentoClient

config = Config()
config.databento_api_key = "your_api_key"
config.data_source = "databento"

provider = DatabentoClient(config)
await provider.connect()

# Subscribe to live data
await provider.subscribe_bars(
    symbol="NQ.FUT",
    bar_size=2,
    callback=bot.on_bar
)
```

### Using CSV Provider for Backtesting

```python
from config import Config
from csv_provider import CSVProvider

config = Config()
config.data_source = "csv"
config.csv_path = "data/nq_2m_2025.csv"

provider = CSVProvider(config)
await provider.connect()

# Load all bars and replay
bars = provider.load_historical_bars(
    symbol="NQ.FUT",
    start=datetime(2025, 1, 1),
    end=datetime(2025, 12, 31)
)

for bar in bars:
    await bot.on_bar(bar)
```

---

## Provider Comparison

| Provider | Live Data | Historical | Cost | Latency | Reliability |
|----------|-----------|------------|------|---------|-------------|
| **Databento** | ✅ Yes | ✅ Yes | $$ | Low | High |
| **CSV** | ❌ No | ✅ Yes | Free | N/A | High |
| **Polygon** | ✅ Yes | ✅ Yes | $ | Medium | Medium |
| **IQFeed** | ✅ Yes | ✅ Yes | $$$ | Very Low | Very High |
| **Interactive Brokers** | ✅ Yes | ✅ Limited | Free* | Medium | Medium |
| **TradingView** | ❌ No** | ✅ Export | Free-$$ | N/A | N/A |

*Requires funded account
**No official API for live streaming

---

## Implementation Guides

### **[Custom Provider Tutorial](data-provider-custom.md)**
Step-by-step guide for implementing your own data provider:
- Step 1: Create Provider Class
- Step 2: Add Configuration
- Step 3: Update Bot Integration

### **[Provider Reference](data-provider-reference.md)**
Bar format specification and best practices:
- Bar Format Spec (required fields and types)
- Timezone Handling (critical for session filtering)
- Testing Procedures (unit and integration tests)
- Common Issues and Solutions
- Best Practices

---

## Next Steps

1. Review [templates/DATA_PROVIDER_BASE.md](../templates/DATA_PROVIDER_BASE.md) for interface specification
2. Check [data-provider-custom.md](data-provider-custom.md) for implementation steps
3. Read [data-provider-reference.md](data-provider-reference.md) for bar format and testing
4. Implement your provider class
5. Write unit tests
6. Test with CSV backtest first
7. Test with small live sample
8. Deploy to production

---

## Support

If you implement a provider for a popular service (Polygon, IQFeed, etc.), consider contributing it back to the skill for others to use!
