# TradersPost Client Template

Webhook client for order execution via TradersPost.

## traderspost_client.py

```python
"""
TradersPost Webhook Client
Send trading signals to TradersPost for execution on Tradovate/Apex accounts.

Webhook URL format:
https://webhooks.traderspost.io/trading/webhook/{uuid}/{password}
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional

import aiohttp

logger = logging.getLogger(__name__)


class TradersPostClient:
    """TradersPost webhook client for order execution."""

    def __init__(self, webhook_url: str):
        """
        Initialize TradersPost client.

        Args:
            webhook_url: Full webhook URL from TradersPost dashboard
                        e.g., "https://webhooks.traderspost.io/trading/webhook/{uuid}/{password}"
        """
        self.webhook_url = webhook_url
        self._session: Optional[aiohttp.ClientSession] = None
        self._last_signal_time: Optional[datetime] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def send_signal(
        self,
        ticker: str,
        action: str,
        quantity: int = 1,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        signal_price: Optional[float] = None,
        order_type: str = "market",
    ) -> dict:
        """
        Send a trading signal to TradersPost.

        Args:
            ticker: Symbol (e.g., "NQH5", "ESH5", "MNQ")
            action: "buy", "sell", "exit", "cancel", "add"
            quantity: Number of contracts
            stop_loss: Stop loss price (optional)
            take_profit: Take profit price (optional)
            signal_price: Current price for slippage calculation
            order_type: "market", "limit", "stop", etc.

        Returns:
            Response dict from TradersPost
        """
        payload = {
            "ticker": ticker,
            "action": action,
            "orderType": order_type,
        }

        # Add optional fields
        if quantity:
            payload["quantity"] = quantity

        if signal_price:
            payload["signalPrice"] = signal_price

        if stop_loss:
            payload["stopLoss"] = {"stopPrice": stop_loss}

        if take_profit:
            payload["takeProfit"] = {"limitPrice": take_profit}

        # Set sentiment based on action
        if action == "buy":
            payload["sentiment"] = "bullish"
        elif action == "sell":
            payload["sentiment"] = "bearish"
        elif action == "exit":
            payload["sentiment"] = "flat"

        # Send request
        session = await self._get_session()

        try:
            async with session.post(
                self.webhook_url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                self._last_signal_time = datetime.now()
                result = await resp.json()

                if result.get("success"):
                    logger.info(
                        f"Signal sent: {action} {ticker} - ID: {result.get('id')}"
                    )
                else:
                    logger.warning(
                        f"Signal failed: {result.get('message', 'Unknown error')}"
                    )

                return result

        except asyncio.TimeoutError:
            logger.error("TradersPost request timed out")
            return {"success": False, "error": "timeout"}
        except Exception as e:
            logger.error(f"Error sending signal: {e}")
            return {"success": False, "error": str(e)}

    async def buy(
        self,
        ticker: str,
        quantity: int = 1,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
    ) -> dict:
        """Send a buy signal."""
        return await self.send_signal(
            ticker=ticker,
            action="buy",
            quantity=quantity,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )

    async def sell(
        self,
        ticker: str,
        quantity: int = 1,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
    ) -> dict:
        """Send a sell signal."""
        return await self.send_signal(
            ticker=ticker,
            action="sell",
            quantity=quantity,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )

    async def exit(self, ticker: str) -> dict:
        """Exit all positions for a ticker."""
        return await self.send_signal(
            ticker=ticker,
            action="exit",
        )

    async def cancel(self, ticker: str) -> dict:
        """Cancel all open orders for a ticker."""
        return await self.send_signal(
            ticker=ticker,
            action="cancel",
        )

    async def add_to_position(
        self,
        ticker: str,
        quantity: int = 1,
    ) -> dict:
        """Add to existing position."""
        return await self.send_signal(
            ticker=ticker,
            action="add",
            quantity=quantity,
        )


# =============================================================================
# PAYLOAD REFERENCE
# =============================================================================

"""
Full TradersPost Payload Reference:

{
    # Required
    "ticker": "NQH5",                    # Symbol
    "action": "buy",                      # buy, sell, exit, cancel, add

    # Optional - Position
    "sentiment": "bullish",               # bullish, bearish, flat
    "quantity": 2,
    "quantityType": "fixed_quantity",     # fixed_quantity, dollar_amount,
                                          # risk_dollar_amount, percent_of_equity,
                                          # percent_of_position

    # Optional - Order Type
    "orderType": "limit",                 # market, limit, stop, stop_limit, trailing_stop
    "limitPrice": 21450.00,               # Required for limit/stop_limit
    "stopPrice": 21400.00,                # Required for stop/stop_limit
    "timeInForce": "day",                 # day, gtc, opg, cls, ioc, fok

    # Optional - Risk Management
    "stopLoss": {
        "type": "stop",                   # stop, stop_limit, trailing_stop
        "stopPrice": 21400.00,
        "limitPrice": 21395.00,           # For stop_limit
        "trailAmount": 10.00,             # For trailing_stop
        "trailPercent": 0.5               # For trailing_stop (alternative)
    },
    "takeProfit": {
        "limitPrice": 21550.00
        # OR use percent/amount:
        # "percent": 1.0,
        # "amount": 50.00
    },

    # Optional - Signal metadata
    "signalPrice": 21450.00,              # For slippage calculation
}

Response Format:

Success (HTTP 200):
{
    "success": true,
    "id": "47462f2d-378c-4bf5-a016-1c1221aa0e62",
    "logId": "a036eff1-b7db-4f15-b5b6-f5e51995ad29",
    "payload": { /* echoed request */ }
}

Error (HTTP 400):
{
    "success": false,
    "messageCode": "invalid-action",
    "message": "The action field must be one of: buy, sell, exit, cancel, or add."
}

Supported Actions:
| Action | Description |
|--------|-------------|
| buy    | Open long or close short |
| sell   | Open short or close long |
| exit   | Close position (direction-agnostic) |
| cancel | Cancel open orders |
| add    | Add to existing position |
"""
```

## Usage Example

```python
# Initialize client
client = TradersPostClient(
    webhook_url="https://webhooks.traderspost.io/trading/webhook/{uuid}/{password}"
)

# Buy with stop loss and take profit
await client.send_signal(
    ticker="NQH5",
    action="buy",
    quantity=2,
    stop_loss=21400.00,
    take_profit=21550.00,
)

# Exit position
await client.exit("NQH5")

# Clean up
await client.close()
```
