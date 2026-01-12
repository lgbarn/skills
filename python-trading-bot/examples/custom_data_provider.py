"""
Custom Data Provider Example

Example implementation of a custom data provider extending the DataProviderBase interface.
This example shows how to integrate Polygon.io as an alternative data source.

Author: Luther Barnum
"""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Callable, List, Optional
import aiohttp
import logging

logger = logging.getLogger(__name__)


class DataProviderBase(ABC):
    """Base class for all data providers."""

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to data provider."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Clean disconnect from data provider."""
        pass

    @abstractmethod
    async def subscribe_bars(self, symbol: str, bar_size: int, callback: Callable) -> None:
        """
        Subscribe to real-time bar data.

        Args:
            symbol: Instrument symbol (e.g., "NQ")
            bar_size: Bar size in minutes (e.g., 2)
            callback: Async function to call with each new bar
        """
        pass

    @abstractmethod
    def load_historical_bars(
        self, symbol: str, start: datetime, end: datetime, bar_size: int = 2
    ) -> List[dict]:
        """
        Load historical bar data for backtesting.

        Args:
            symbol: Instrument symbol
            start: Start datetime
            end: End datetime
            bar_size: Bar size in minutes

        Returns:
            List of bar dicts with OHLCV + timestamp
        """
        pass


class PolygonProvider(DataProviderBase):
    """
    Polygon.io data provider implementation.

    Example of extending DataProviderBase for a custom data source.
    Polygon provides stocks, options, and crypto data (not futures).

    API Docs: https://polygon.io/docs/stocks
    """

    def __init__(self, api_key: str, symbol: str = "SPY"):
        """
        Initialize Polygon provider.

        Args:
            api_key: Polygon.io API key
            symbol: Stock symbol (e.g., "SPY", "AAPL")
        """
        self.api_key = api_key
        self.symbol = symbol
        self.session: Optional[aiohttp.ClientSession] = None
        self.ws = None
        self.connected = False

    async def connect(self) -> None:
        """Establish connection to Polygon WebSocket."""
        self.session = aiohttp.ClientSession()

        # Polygon WebSocket endpoint
        ws_url = f"wss://socket.polygon.io/stocks"

        try:
            self.ws = await self.session.ws_connect(ws_url)
            self.connected = True

            # Authenticate
            await self.ws.send_json({"action": "auth", "params": self.api_key})

            # Wait for auth confirmation
            msg = await self.ws.receive_json()
            if msg[0]["status"] != "auth_success":
                raise ConnectionError(f"Polygon auth failed: {msg}")

            logger.info("Connected to Polygon.io")

        except Exception as e:
            logger.error(f"Failed to connect to Polygon: {e}")
            await self.disconnect()
            raise

    async def disconnect(self) -> None:
        """Clean disconnect from Polygon."""
        if self.ws:
            await self.ws.close()
        if self.session:
            await self.session.close()
        self.connected = False
        logger.info("Disconnected from Polygon.io")

    async def subscribe_bars(
        self, symbol: str, bar_size: int, callback: Callable
    ) -> None:
        """
        Subscribe to aggregated bar data.

        Polygon aggregates trades into bars server-side.

        Args:
            symbol: Stock symbol (e.g., "SPY")
            bar_size: Bar size in minutes
            callback: Async function(bar: dict) to call with each bar
        """
        if not self.connected:
            await self.connect()

        # Subscribe to aggregate bars
        subscribe_msg = {
            "action": "subscribe",
            "params": f"AM.{symbol}",  # AM = Minute Aggregate
        }
        await self.ws.send_json(subscribe_msg)

        logger.info(f"Subscribed to {symbol} {bar_size}-min bars")

        # Start bar aggregation task
        asyncio.create_task(
            self._aggregate_bars(symbol, bar_size, callback)
        )

    async def _aggregate_bars(
        self, symbol: str, bar_size: int, callback: Callable
    ):
        """
        Aggregate minute bars into custom bar size.

        Polygon sends 1-min bars, we aggregate to desired size.
        """
        current_bar = None
        bar_start_time = None

        async for msg in self.ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                data = msg.json()

                for event in data:
                    if event.get("ev") != "AM":
                        continue  # Not a minute aggregate

                    # Parse bar data
                    timestamp = datetime.fromtimestamp(event["s"] / 1000)
                    minute_bar = {
                        "timestamp": timestamp,
                        "open": event["o"],
                        "high": event["h"],
                        "low": event["l"],
                        "close": event["c"],
                        "volume": event["v"],
                    }

                    # Initialize or update current bar
                    if current_bar is None:
                        bar_start_time = self._get_bar_start(timestamp, bar_size)
                        current_bar = minute_bar.copy()
                    else:
                        # Check if still in same bar period
                        if timestamp < bar_start_time + timedelta(minutes=bar_size):
                            # Update current bar
                            current_bar["high"] = max(
                                current_bar["high"], minute_bar["high"]
                            )
                            current_bar["low"] = min(
                                current_bar["low"], minute_bar["low"]
                            )
                            current_bar["close"] = minute_bar["close"]
                            current_bar["volume"] += minute_bar["volume"]
                        else:
                            # Bar complete, send to callback
                            await callback(current_bar)

                            # Start new bar
                            bar_start_time = self._get_bar_start(timestamp, bar_size)
                            current_bar = minute_bar.copy()

            elif msg.type == aiohttp.WSMsgType.ERROR:
                logger.error(f"WebSocket error: {msg}")
                break

    def _get_bar_start(self, timestamp: datetime, bar_size: int) -> datetime:
        """Get start time of bar period for given timestamp."""
        minutes = (timestamp.hour * 60 + timestamp.minute) // bar_size * bar_size
        return timestamp.replace(
            hour=minutes // 60, minute=minutes % 60, second=0, microsecond=0
        )

    def load_historical_bars(
        self, symbol: str, start: datetime, end: datetime, bar_size: int = 2
    ) -> List[dict]:
        """
        Load historical bars from Polygon REST API.

        Uses aggregates endpoint with custom timespan.

        Args:
            symbol: Stock symbol
            start: Start datetime
            end: End datetime
            bar_size: Bar size in minutes

        Returns:
            List of OHLCV bar dicts
        """
        # Polygon aggregates endpoint
        url = (
            f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/"
            f"{bar_size}/minute/{start.strftime('%Y-%m-%d')}/{end.strftime('%Y-%m-%d')}"
        )

        params = {"apiKey": self.api_key, "adjusted": "true", "sort": "asc", "limit": 50000}

        import requests

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        if data["status"] != "OK":
            raise ValueError(f"Polygon API error: {data}")

        bars = []
        for result in data["results"]:
            bars.append(
                {
                    "timestamp": datetime.fromtimestamp(result["t"] / 1000),
                    "open": result["o"],
                    "high": result["h"],
                    "low": result["l"],
                    "close": result["c"],
                    "volume": result["v"],
                }
            )

        logger.info(f"Loaded {len(bars)} historical bars for {symbol}")
        return bars


# Example usage
async def main():
    """Example of using custom Polygon provider."""
    # Initialize provider
    provider = PolygonProvider(api_key="YOUR_POLYGON_API_KEY", symbol="SPY")

    # Define callback for bar data
    async def on_bar(bar: dict):
        print(
            f"Bar: {bar['timestamp']} O:{bar['open']} H:{bar['high']} "
            f"L:{bar['low']} C:{bar['close']} V:{bar['volume']}"
        )

    try:
        # Connect
        await provider.connect()

        # Subscribe to 2-min bars
        await provider.subscribe_bars("SPY", bar_size=2, callback=on_bar)

        # Run for 5 minutes
        await asyncio.sleep(300)

    finally:
        # Disconnect
        await provider.disconnect()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
