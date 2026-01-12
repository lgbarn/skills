# Tradovate Client Template

WebSocket client for Tradovate market data.

## tradovate_client.py

```python
"""
Tradovate WebSocket Client
Connects to Tradovate market data feed for real-time bar data.

Endpoints:
- Demo: wss://md-demo.tradovateapi.com/v1/websocket
- Live: wss://md.tradovateapi.com/v1/websocket
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Callable, Optional

import aiohttp

from config import Config

logger = logging.getLogger(__name__)


class TradovateClient:
    """Tradovate WebSocket client for market data."""

    def __init__(self, config: Config):
        self.config = config
        self._ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self._session: Optional[aiohttp.ClientSession] = None
        self._access_token: Optional[str] = None
        self._running = False
        self._bar_callback: Optional[Callable] = None
        self._current_bar: Optional[dict] = None
        self._request_id = 0

    @property
    def _base_url(self) -> str:
        """REST API base URL."""
        env = self.config.tradovate_env
        return f"https://{env}.tradovateapi.com/v1"

    @property
    def _ws_url(self) -> str:
        """WebSocket URL."""
        env = self.config.tradovate_env
        if env == "demo":
            return "wss://md-demo.tradovateapi.com/v1/websocket"
        return "wss://md.tradovateapi.com/v1/websocket"

    async def connect(self):
        """Connect to Tradovate and authenticate."""
        logger.info(f"Connecting to Tradovate ({self.config.tradovate_env})...")

        # Create session
        self._session = aiohttp.ClientSession()

        # Authenticate
        await self._authenticate()

        # Connect WebSocket
        await self._connect_websocket()

        logger.info("Connected to Tradovate")

    async def disconnect(self):
        """Disconnect from Tradovate."""
        self._running = False

        if self._ws:
            await self._ws.close()
            self._ws = None

        if self._session:
            await self._session.close()
            self._session = None

        logger.info("Disconnected from Tradovate")

    async def subscribe_bars(
        self,
        symbol: str,
        bar_size: int,
        callback: Callable,
    ):
        """
        Subscribe to bar data.

        Args:
            symbol: Contract symbol (e.g., "NQH5")
            bar_size: Bar size in minutes (e.g., 2)
            callback: Async function called with each completed bar
        """
        self._bar_callback = callback
        self._running = True

        # Get contract ID
        contract_id = await self._get_contract_id(symbol)
        if not contract_id:
            raise ValueError(f"Contract not found: {symbol}")

        logger.info(f"Subscribing to {symbol} ({bar_size}-min bars)")

        # Subscribe to chart data
        self._request_id += 1
        subscribe_msg = {
            "symbol": symbol,
            "chartDescription": {
                "underlyingType": "MinuteBar",
                "elementSize": bar_size,
                "elementSizeUnit": "UnderlyingUnits",
            },
            "timeRange": {
                "asFarAsTimestamp": datetime.now().isoformat(),
            },
        }

        await self._send_ws_message("md/getChart", subscribe_msg)

        # Start message handler
        asyncio.create_task(self._handle_messages())

    async def _authenticate(self):
        """Get access token from Tradovate."""
        auth_data = {
            "name": self.config.tradovate_username,
            "password": self.config.tradovate_password,
            "appId": "TradingBot",
            "appVersion": "1.0",
            "cid": self.config.tradovate_cid,
            "sec": self.config.tradovate_secret,
        }

        async with self._session.post(
            f"{self._base_url}/auth/accesstokenrequest",
            json=auth_data,
        ) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise Exception(f"Authentication failed: {text}")

            data = await resp.json()
            self._access_token = data["accessToken"]
            logger.debug("Authentication successful")

    async def _connect_websocket(self):
        """Connect and authorize WebSocket."""
        self._ws = await self._session.ws_connect(self._ws_url)

        # Authorize
        auth_msg = f"authorize\n0\n\n{self._access_token}"
        await self._ws.send_str(auth_msg)

        # Wait for auth response
        msg = await self._ws.receive()
        if msg.type == aiohttp.WSMsgType.TEXT:
            if "authorized" not in msg.data.lower():
                raise Exception(f"WebSocket auth failed: {msg.data}")

        logger.debug("WebSocket authorized")

    async def _send_ws_message(self, endpoint: str, data: dict):
        """Send a message to the WebSocket."""
        self._request_id += 1
        msg = f"{endpoint}\n{self._request_id}\n\n{json.dumps(data)}"
        await self._ws.send_str(msg)

    async def _get_contract_id(self, symbol: str) -> Optional[int]:
        """Get contract ID for a symbol."""
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

        async with self._session.get(
            f"{self._base_url}/contract/find",
            headers=headers,
            params={"name": symbol},
        ) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            return data.get("id")

    async def _handle_messages(self):
        """Handle incoming WebSocket messages."""
        while self._running:
            try:
                msg = await asyncio.wait_for(
                    self._ws.receive(),
                    timeout=30,
                )

                if msg.type == aiohttp.WSMsgType.TEXT:
                    await self._process_message(msg.data)
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    logger.warning("WebSocket closed, reconnecting...")
                    await self._reconnect()
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {msg.data}")
                    await self._reconnect()

            except asyncio.TimeoutError:
                # Send heartbeat
                await self._ws.ping()
            except Exception as e:
                logger.error(f"Message handler error: {e}")
                await asyncio.sleep(1)

    async def _reconnect(self):
        """Reconnect to WebSocket."""
        if not self._running:
            return

        logger.info("Reconnecting...")
        await asyncio.sleep(5)

        try:
            await self._connect_websocket()
            logger.info("Reconnected")
        except Exception as e:
            logger.error(f"Reconnect failed: {e}")
            await self._reconnect()

    async def _process_message(self, raw: str):
        """Process a WebSocket message."""
        # Parse Tradovate message format:
        # endpoint\nrequest_id\n\njson_data
        parts = raw.split("\n", 3)
        if len(parts) < 4:
            return

        endpoint = parts[0]
        # request_id = parts[1]
        # empty = parts[2]
        data_str = parts[3] if len(parts) > 3 else ""

        if not data_str:
            return

        try:
            data = json.loads(data_str)
        except json.JSONDecodeError:
            return

        # Handle chart data
        if endpoint == "md/chart" or "charts" in data:
            await self._handle_chart_data(data)

    async def _handle_chart_data(self, data: dict):
        """Handle chart/bar data."""
        charts = data.get("charts", [data])

        for chart in charts:
            bars = chart.get("bars", [])

            for bar_data in bars:
                # Convert to standard bar format
                bar = {
                    "timestamp": datetime.fromisoformat(
                        bar_data.get("timestamp", datetime.now().isoformat())
                    ),
                    "open": bar_data.get("open", 0),
                    "high": bar_data.get("high", 0),
                    "low": bar_data.get("low", 0),
                    "close": bar_data.get("close", 0),
                    "volume": bar_data.get("upVolume", 0) + bar_data.get("downVolume", 0),
                    "hour": datetime.fromisoformat(
                        bar_data.get("timestamp", datetime.now().isoformat())
                    ).hour,
                }

                # Check if bar is complete (new bar started)
                if self._current_bar is None:
                    self._current_bar = bar
                elif bar["timestamp"] > self._current_bar["timestamp"]:
                    # Previous bar is complete, notify callback
                    if self._bar_callback:
                        await self._bar_callback(self._current_bar)
                    self._current_bar = bar
                else:
                    # Update current bar
                    self._current_bar["high"] = max(
                        self._current_bar["high"], bar["high"]
                    )
                    self._current_bar["low"] = min(
                        self._current_bar["low"], bar["low"]
                    )
                    self._current_bar["close"] = bar["close"]
                    self._current_bar["volume"] += bar["volume"]
```

## Alternative: REST API Polling

If WebSocket is unreliable, use REST API polling:

```python
async def poll_bars(self, symbol: str, bar_size: int, callback: Callable):
    """Poll for new bars via REST API (fallback)."""
    headers = {
        "Authorization": f"Bearer {self._access_token}",
        "Content-Type": "application/json",
    }

    last_bar_time = None

    while self._running:
        try:
            # Get recent bars
            async with self._session.get(
                f"{self._base_url}/chart/item",
                headers=headers,
                params={
                    "symbol": symbol,
                    "resolution": f"{bar_size}m",
                    "count": 5,
                },
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    bars = data.get("bars", [])

                    for bar_data in bars:
                        bar_time = datetime.fromisoformat(bar_data["timestamp"])
                        if last_bar_time is None or bar_time > last_bar_time:
                            bar = {
                                "timestamp": bar_time,
                                "open": bar_data["open"],
                                "high": bar_data["high"],
                                "low": bar_data["low"],
                                "close": bar_data["close"],
                                "volume": bar_data.get("volume", 0),
                                "hour": bar_time.hour,
                            }
                            await callback(bar)
                            last_bar_time = bar_time

            # Poll every bar_size minutes
            await asyncio.sleep(bar_size * 60)

        except Exception as e:
            logger.error(f"Poll error: {e}")
            await asyncio.sleep(10)
```
