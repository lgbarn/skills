# Environment Setup Guide

Complete setup guide for running Python trading bots.

---

## Prerequisites

- Python 3.10 or higher
- Tradovate account (demo or live)
- TradersPost account (for order execution)
- (Optional) Apex Trader Funding account

---

## 1. Python Environment

### Create Virtual Environment

```bash
# Navigate to bot directory
cd Python/bots/keltner

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate

# Windows:
.\venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### requirements.txt

```
aiohttp>=3.9.0
python-dotenv>=1.0.0
```

Optional (for monitoring/analysis):

```
pandas>=2.0.0
plotly>=5.0.0
```

---

## 2. Tradovate Setup

### Create API Credentials

1. Log into [Tradovate](https://trader.tradovate.com)
2. Go to **Settings** → **API Keys**
3. Click **Generate API Key**
4. Save the following:
   - Username
   - Password
   - CID (Client ID - numeric)
   - Secret

### Demo vs Live

| Environment | Base URL | WebSocket |
|-------------|----------|-----------|
| Demo | `https://demo.tradovateapi.com/v1` | `wss://md-demo.tradovateapi.com/v1/websocket` |
| Live | `https://live.tradovateapi.com/v1` | `wss://md.tradovateapi.com/v1/websocket` |

**Start with Demo** for testing before going live.

---

## 3. TradersPost Setup

### Create Webhook

1. Sign up at [TradersPost](https://traderspost.io)
2. Go to **Strategies** → **Create Strategy**
3. Name your strategy (e.g., "Keltner NQ Bot")
4. Copy the webhook URL:
   ```
   https://webhooks.traderspost.io/trading/webhook/{uuid}/{password}
   ```
5. Connect your broker (Tradovate)

### Connect Broker

1. In TradersPost, go to **Brokers**
2. Click **Connect** for Tradovate
3. Authorize TradersPost to access your account
4. Select which account to use (demo or funded)

---

## 4. Configure Environment Variables

### Create .env File

```bash
# Copy example
cp .env.example .env

# Edit with your credentials
nano .env  # or use any text editor
```

### .env Contents

```bash
# Tradovate API Credentials
TRADOVATE_USERNAME=your_username
TRADOVATE_PASSWORD=your_password
TRADOVATE_CID=12345
TRADOVATE_SECRET=your_secret_key
TRADOVATE_ENV=demo  # Use "live" for real trading

# TradersPost Webhook
TRADERSPOST_WEBHOOK_URL=https://webhooks.traderspost.io/trading/webhook/{uuid}/{password}

# Bot Configuration
BOT_TICKER=NQH5  # Current front-month NQ contract
BOT_PAPER_MODE=true  # Set to "false" for live trading
BOT_CONTRACTS=2  # Number of contracts per trade
BOT_DAILY_MAX_LOSS=500  # Stop trading if daily loss exceeds this
```

### Security Notes

- **NEVER commit .env to git** (included in .gitignore)
- Use strong, unique passwords
- Rotate API keys periodically
- Consider using a secrets manager for production

---

## 5. Contract Symbol Format

NQ futures use quarterly expiration codes:

| Month | Code | Example |
|-------|------|---------|
| March | H | NQH5 (Mar 2025) |
| June | M | NQM5 (Jun 2025) |
| September | U | NQU5 (Sep 2025) |
| December | Z | NQZ5 (Dec 2025) |

**Update `BOT_TICKER` when rolling to next contract.**

### Roll Schedule

- Front month expires 3rd Friday of contract month
- Roll 1-2 weeks before expiration to avoid low liquidity
- Volume typically shifts to next contract ~1 week before expiration

---

## 6. Verify Setup

### Test Tradovate Connection

```python
# Quick test script
import asyncio
from tradovate_client import TradovateClient
from config import Config

async def test():
    config = Config()
    client = TradovateClient(config)
    await client.connect()
    print("Connected to Tradovate!")
    await client.disconnect()

asyncio.run(test())
```

### Test TradersPost Webhook

```python
# Test webhook (sends to TradersPost but won't execute if paper mode)
import asyncio
from traderspost_client import TradersPostClient
from config import Config

async def test():
    config = Config()
    client = TradersPostClient(config.traderspost_webhook_url)

    result = await client.send_signal(
        ticker=config.ticker,
        action="buy",
        quantity=1,
    )
    print(f"Webhook response: {result}")
    await client.close()

asyncio.run(test())
```

---

## 7. Run the Bot

### Paper Trading (Recommended First)

```bash
python bot_keltner.py --paper
```

### Live Trading

```bash
# Requires confirmation
python bot_keltner.py --live
```

### Expected Output

```
2026-01-04 09:30:15 [INFO] Starting Keltner Channel Bot
2026-01-04 09:30:15 [INFO] Ticker: NQH5
2026-01-04 09:30:15 [INFO] Paper Mode: True
2026-01-04 09:30:15 [INFO] Contracts: 2
2026-01-04 09:30:15 [INFO] Daily Max Loss: $500
2026-01-04 09:30:16 [INFO] Connecting to Tradovate (demo)...
2026-01-04 09:30:17 [INFO] Connected to Tradovate
2026-01-04 09:30:17 [INFO] Subscribing to NQH5 (2-min bars)
2026-01-04 09:30:18 [DEBUG] Warmup: 1/50 bars
...
```

---

## 8. Monitoring

### Log Files

Logs are written to:
- Console (stdout)
- `bot_keltner_YYYYMMDD.log` (daily file)

### Trade Log

Completed trades are logged to `trades.csv`:

```csv
timestamp,ticker,direction,entry_price,exit_price,stop_loss,take_profit,quantity,pnl,exit_reason,bars_held,is_reentry
2026-01-04T10:15:30,NQH5,long,21450.00,21485.00,21395.00,21505.00,2,350.00,TakeProfit,15,false
```

### TradersPost Dashboard

Monitor executed orders in TradersPost:
1. Go to **Activity** → **Signals**
2. View all sent signals and their status
3. Check **Orders** for execution details

---

## 9. Troubleshooting

### Connection Issues

```
Error: Authentication failed
```
- Verify TRADOVATE_USERNAME and TRADOVATE_PASSWORD
- Check TRADOVATE_CID is numeric
- Ensure TRADOVATE_SECRET is correct

### WebSocket Disconnects

```
Warning: WebSocket closed, reconnecting...
```
- Normal during market close/maintenance
- Bot auto-reconnects
- Check internet connectivity if persistent

### No Signals Received

- Ensure market is open
- Check ADX > 35 (may be ranging market)
- Verify volume filter isn't filtering all signals
- Check session hours include current time

### TradersPost Errors

```
Signal failed: invalid-action
```
- Verify webhook URL is complete (uuid + password)
- Check payload format matches TradersPost spec
- Ensure broker is connected in TradersPost

---

## 10. Next Steps

1. Run in paper mode for at least 1 week
2. Compare results with backtest expectations
3. Verify all entries/exits are executing correctly
4. Monitor daily P&L and drawdown
5. When confident, switch to live mode with small size

See [DEPLOYMENT.md](deployment.md) for VPS setup and production deployment.
