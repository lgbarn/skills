# News Filter Template

Economic calendar integration for automated blackout periods around high-impact news events.

---

## Overview

The news filter prevents trading during high-impact economic events to avoid excessive volatility and unpredictable price action. This is especially important for prop firm accounts where drawdown breaches can end your account.

Key features:
- Automated economic calendar fetching
- Pre-event and post-event blackout periods
- High-impact event filtering
- Manual event override support
- Graceful API failure handling
- Event logging and tracking

---

## news_calendar.py

```python
"""
News Calendar Integration
Author: Luther Barnum

Fetches economic calendar events and enforces trading blackouts around high-impact news.
Supports Financial Modeling Prep API with fallback to manual configuration.
"""

import logging
from datetime import datetime, time, timedelta
from typing import Optional, List
from dataclasses import dataclass
import aiohttp
import pytz

from config import Config

logger = logging.getLogger(__name__)


@dataclass
class EconomicEvent:
    """Economic calendar event."""

    name: str
    date: datetime
    impact: str  # "High", "Medium", "Low"
    country: str
    actual: Optional[str] = None
    estimate: Optional[str] = None
    previous: Optional[str] = None

    def __str__(self):
        return f"{self.date.strftime('%Y-%m-%d %H:%M')} {self.country} - {self.name} ({self.impact})"


class NewsCalendar:
    """
    Economic calendar manager.

    Fetches high-impact events and determines blackout periods.
    """

    def __init__(self, config: Config):
        self.config = config
        self.timezone = pytz.timezone("America/New_York")

        # Event cache
        self.events: List[EconomicEvent] = []
        self.last_fetch: Optional[datetime] = None

        # API session
        self.session: Optional[aiohttp.ClientSession] = None

    async def connect(self):
        """Initialize HTTP session."""
        if not self.session:
            self.session = aiohttp.ClientSession()
            logger.info("News calendar session initialized")

    async def disconnect(self):
        """Clean up HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("News calendar session closed")

    async def fetch_today_events(self) -> List[EconomicEvent]:
        """
        Fetch today's high-impact economic events.

        Returns:
            List of EconomicEvent objects
        """
        if not self.config.news_filter_enabled:
            return []

        today = datetime.now(self.timezone).date()

        # Check cache (refresh daily)
        if self.last_fetch and self.last_fetch.date() == today and self.events:
            logger.debug(f"Using cached events ({len(self.events)} events)")
            return self.events

        # Fetch from API
        try:
            events = await self._fetch_from_api(today)

            # Filter to high-impact only
            high_impact = [e for e in events if e.impact == "High"]

            self.events = high_impact
            self.last_fetch = datetime.now(self.timezone)

            logger.info(f"Fetched {len(high_impact)} high-impact events for {today}")

            for event in high_impact:
                logger.info(f"  Event: {event}")

            return high_impact

        except Exception as e:
            logger.error(f"Failed to fetch economic events: {e}")

            # Fallback to manual config if API fails
            fallback = self._load_fallback_events(today)
            if fallback:
                logger.warning(f"Using {len(fallback)} fallback events from config")
                return fallback

            return []

    async def _fetch_from_api(self, date: datetime.date) -> List[EconomicEvent]:
        """
        Fetch events from Financial Modeling Prep API.

        Args:
            date: Date to fetch events for

        Returns:
            List of EconomicEvent objects
        """
        if not self.session:
            await self.connect()

        # FMP API endpoint
        url = f"https://financialmodelingprep.com/api/v3/economic_calendar"

        params = {
            "apikey": self.config.news_api_key,
            "from": date.isoformat(),
            "to": date.isoformat(),
        }

        async with self.session.get(url, params=params) as response:
            response.raise_for_status()
            data = await response.json()

        events = []
        for item in data:
            # Parse event time
            event_dt = datetime.fromisoformat(item["date"].replace("Z", "+00:00"))
            event_dt = event_dt.astimezone(self.timezone)

            # Determine impact level
            impact = item.get("impact", "Low")

            # Only include US events (configurable)
            country = item.get("country", "US")
            if country != "US":
                continue

            event = EconomicEvent(
                name=item["event"],
                date=event_dt,
                impact=impact,
                country=country,
                actual=item.get("actual"),
                estimate=item.get("estimate"),
                previous=item.get("previous"),
            )

            events.append(event)

        return events

    def _load_fallback_events(self, date: datetime.date) -> List[EconomicEvent]:
        """
        Load fallback events from manual configuration.

        Use this when API is down or for known recurring events.

        Args:
            date: Date to check

        Returns:
            List of manually configured events
        """
        # Common high-impact events (update monthly)
        # Format: (day, time, name)
        known_events = [
            # FOMC meetings (check Fed calendar: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm)
            # Example: (1, time(14, 0), "FOMC Rate Decision"),

            # Non-Farm Payrolls (first Friday of month at 8:30 AM)
            # Example: (5, time(8, 30), "Non-Farm Payrolls"),

            # CPI (around 13th of month at 8:30 AM)
            # Example: (13, time(8, 30), "CPI Report"),
        ]

        events = []
        for day, event_time, name in known_events:
            if date.day == day:
                event_dt = datetime.combine(date, event_time)
                event_dt = self.timezone.localize(event_dt)

                events.append(EconomicEvent(
                    name=name,
                    date=event_dt,
                    impact="High",
                    country="US",
                ))

        return events

    def is_blackout_period(self, current_time: datetime) -> bool:
        """
        Check if current time is within a blackout period.

        Args:
            current_time: Current time (timezone-aware)

        Returns:
            True if in blackout period
        """
        if not self.config.news_filter_enabled:
            return False

        if not self.events:
            return False

        # Ensure current_time is timezone-aware
        if current_time.tzinfo is None:
            current_time = self.timezone.localize(current_time)
        else:
            current_time = current_time.astimezone(self.timezone)

        blackout_delta = timedelta(minutes=self.config.news_blackout_minutes)

        for event in self.events:
            # Blackout window: [event_time - delta, event_time + delta]
            start = event.date - blackout_delta
            end = event.date + blackout_delta

            if start <= current_time <= end:
                logger.info(f"⚠️ BLACKOUT: {event.name} at {event.date.strftime('%H:%M')}")
                return True

        return False

    def get_next_event(self, current_time: datetime) -> Optional[EconomicEvent]:
        """
        Get the next upcoming event.

        Args:
            current_time: Current time (timezone-aware)

        Returns:
            Next EconomicEvent or None
        """
        if not self.events:
            return None

        # Ensure timezone-aware
        if current_time.tzinfo is None:
            current_time = self.timezone.localize(current_time)
        else:
            current_time = current_time.astimezone(self.timezone)

        # Find next event after current time
        upcoming = [e for e in self.events if e.date > current_time]

        if not upcoming:
            return None

        return min(upcoming, key=lambda e: e.date)

    def get_stats(self) -> dict:
        """Get news calendar statistics."""
        return {
            "enabled": self.config.news_filter_enabled,
            "events_today": len(self.events),
            "last_fetch": self.last_fetch.isoformat() if self.last_fetch else None,
            "api": self.config.news_api,
            "blackout_minutes": self.config.news_blackout_minutes,
        }
```

---

## Configuration

Add to `config.py`:

```python
from dataclasses import dataclass
import os

@dataclass
class Config:
    # ... existing config ...

    # News Calendar Filter
    news_filter_enabled: bool = False
    news_api: str = "fmp"  # "fmp" = Financial Modeling Prep
    news_api_key: str = ""
    news_blackout_minutes: int = 30  # Minutes before/after event

    def __post_init__(self):
        # ... existing __post_init__ ...

        # Load news filter settings
        self.news_filter_enabled = os.getenv("NEWS_FILTER_ENABLED", "false").lower() == "true"
        self.news_api = os.getenv("NEWS_API", self.news_api)
        self.news_api_key = os.getenv("NEWS_API_KEY", "")
        self.news_blackout_minutes = int(os.getenv("NEWS_BLACKOUT_MINUTES", str(self.news_blackout_minutes)))
```

Add to `.env`:

```bash
# News Calendar Filter
NEWS_FILTER_ENABLED=true
NEWS_API=fmp
NEWS_API_KEY=your_fmp_api_key_here
NEWS_BLACKOUT_MINUTES=30
```

---

## Usage in Bot

```python
# In bot_*.py

from news_calendar import NewsCalendar

class TradingBot:
    def __init__(self, config):
        self.config = config
        self.news_calendar = NewsCalendar(config)
        # ... other initialization ...

    async def start(self):
        """Start bot."""
        logger.info("Starting bot...")

        # Connect to news calendar
        if self.config.news_filter_enabled:
            await self.news_calendar.connect()
            await self.news_calendar.fetch_today_events()

        # ... connect to data provider, etc ...

    async def on_bar(self, bar: dict):
        """Process each bar."""
        # ... bar processing ...

        # Check if in blackout period
        bar_time = bar["timestamp"]
        if self.news_calendar.is_blackout_period(bar_time):
            logger.debug("Skipping bar (news blackout)")

            # Exit open position if configured
            if self.config.news_exit_on_blackout and self.position != 0:
                logger.warning("Exiting position due to news blackout")
                await self._exit_position("NewsBlackout", bar["close"])

            return

        # Check for new trading day
        bar_date = bar_time.date()
        self.risk_manager.check_new_day(bar_date)

        # Fetch new events at start of day
        if bar_time.hour == 9 and bar_time.minute == 30:
            await self.news_calendar.fetch_today_events()

        # ... rest of bar processing ...

    async def stop(self):
        """Graceful shutdown."""
        logger.info("Shutting down bot...")

        # ... exit position, close risk manager, etc ...

        # Close news calendar
        if self.config.news_filter_enabled:
            await self.news_calendar.disconnect()

        logger.info("Bot stopped")
```

---

## High-Impact Events

Common events to watch (automatically filtered when `impact == "High"`):

### Monthly Events
- **Non-Farm Payrolls (NFP)** - First Friday, 8:30 AM ET
  - Most volatile event of the month
  - Blackout recommended: 8:00 AM - 10:00 AM ET

- **CPI (Consumer Price Index)** - Mid-month (~13th), 8:30 AM ET
  - Major inflation indicator
  - Blackout recommended: 8:00 AM - 9:30 AM ET

- **FOMC Rate Decision** - 8 times per year, 2:00 PM ET
  - Federal Reserve interest rate announcement
  - Blackout recommended: 1:30 PM - 3:00 PM ET
  - Press conference at 2:30 PM adds volatility

- **PPI (Producer Price Index)** - Mid-month, 8:30 AM ET
  - Leading inflation indicator

### Quarterly Events
- **GDP Report** - End of quarter, 8:30 AM ET
  - Major economic growth indicator

- **Fed Chair Testimony** - Varies, usually 10:00 AM ET
  - Can cause large moves

### Weekly Events (Usually Low Impact)
- **Initial Jobless Claims** - Thursday, 8:30 AM ET
  - Can be high-impact if unexpected

---

## Example Output

### Bot Startup (Events Found)

```
2026-01-10 09:30:00 [INFO] Starting bot...
2026-01-10 09:30:00 [INFO] News calendar session initialized
2026-01-10 09:30:00 [INFO] Fetched 2 high-impact events for 2026-01-10
2026-01-10 09:30:00 [INFO]   Event: 2026-01-10 10:00 US - ISM Services PMI (High)
2026-01-10 09:30:00 [INFO]   Event: 2026-01-10 14:00 US - FOMC Rate Decision (High)
2026-01-10 09:30:00 [INFO] Bot started successfully
```

### During Blackout Period

```
2026-01-10 09:45:00 [DEBUG] Bar received: 2026-01-10 09:45:00
2026-01-10 09:45:00 [DEBUG] Skipping bar (news blackout)

2026-01-10 09:50:00 [DEBUG] Bar received: 2026-01-10 09:50:00
2026-01-10 09:50:00 [INFO] ⚠️ BLACKOUT: ISM Services PMI at 10:00
2026-01-10 09:50:00 [DEBUG] Skipping bar (news blackout)

2026-01-10 10:00:00 [DEBUG] Bar received: 2026-01-10 10:00:00
2026-01-10 10:00:00 [INFO] ⚠️ BLACKOUT: ISM Services PMI at 10:00
2026-01-10 10:00:00 [DEBUG] Skipping bar (news blackout)

2026-01-10 10:35:00 [DEBUG] Bar received: 2026-01-10 10:35:00
2026-01-10 10:35:00 [DEBUG] Processing bar (no blackout)
```

### API Failure with Fallback

```
2026-01-10 09:30:00 [ERROR] Failed to fetch economic events: HTTPError 429 Too Many Requests
2026-01-10 09:30:00 [WARNING] Using 1 fallback events from config
2026-01-10 09:30:00 [INFO]   Event: 2026-01-10 14:00 US - FOMC Rate Decision (High)
```

---

## API Setup

### Financial Modeling Prep (Recommended)

1. Sign up: https://site.financialmodelingprep.com/developer/docs
2. Free tier: 250 requests/day (sufficient for daily event fetching)
3. Get API key from dashboard
4. Add to `.env`: `NEWS_API_KEY=your_key_here`

### Alternative: Trading Economics

```python
# In _fetch_from_api()
url = f"https://api.tradingeconomics.com/calendar"

params = {
    "c": self.config.news_api_key,
    "d1": date.isoformat(),
    "d2": date.isoformat(),
    "importance": "3",  # High importance only
}
```

### Manual Fallback (No API)

If you don't want to use an API, update `_load_fallback_events()` with your calendar:

```python
def _load_fallback_events(self, date: datetime.date) -> List[EconomicEvent]:
    """Load events from manual calendar."""

    # January 2026 events
    if date.year == 2026 and date.month == 1:
        jan_events = [
            (3, time(8, 30), "Non-Farm Payrolls"),
            (10, time(8, 30), "CPI Report"),
            (15, time(8, 30), "PPI Report"),
            (29, time(14, 0), "FOMC Rate Decision"),
        ]

        for day, event_time, name in jan_events:
            if date.day == day:
                # ... create event ...

    # February 2026 events
    # ...
```

---

## Testing

```python
# test_news_calendar.py

import pytest
from datetime import datetime, timedelta
import pytz
from news_calendar import NewsCalendar, EconomicEvent
from config import Config

@pytest.fixture
def config():
    config = Config()
    config.news_filter_enabled = True
    config.news_blackout_minutes = 30
    return config

@pytest.fixture
def news_calendar(config):
    return NewsCalendar(config)

def test_blackout_period_before_event(news_calendar):
    """Test blackout period starts before event."""
    tz = pytz.timezone("America/New_York")

    # Event at 10:00 AM
    event_time = tz.localize(datetime(2026, 1, 10, 10, 0))
    news_calendar.events = [
        EconomicEvent(
            name="Test Event",
            date=event_time,
            impact="High",
            country="US"
        )
    ]

    # 20 minutes before (within 30-minute blackout)
    check_time = event_time - timedelta(minutes=20)
    assert news_calendar.is_blackout_period(check_time) is True

def test_blackout_period_after_event(news_calendar):
    """Test blackout period continues after event."""
    tz = pytz.timezone("America/New_York")

    event_time = tz.localize(datetime(2026, 1, 10, 10, 0))
    news_calendar.events = [
        EconomicEvent(
            name="Test Event",
            date=event_time,
            impact="High",
            country="US"
        )
    ]

    # 20 minutes after (within 30-minute blackout)
    check_time = event_time + timedelta(minutes=20)
    assert news_calendar.is_blackout_period(check_time) is True

def test_no_blackout_outside_window(news_calendar):
    """Test no blackout outside event window."""
    tz = pytz.timezone("America/New_York")

    event_time = tz.localize(datetime(2026, 1, 10, 10, 0))
    news_calendar.events = [
        EconomicEvent(
            name="Test Event",
            date=event_time,
            impact="High",
            country="US"
        )
    ]

    # 40 minutes before (outside 30-minute blackout)
    check_time = event_time - timedelta(minutes=40)
    assert news_calendar.is_blackout_period(check_time) is False

    # 40 minutes after
    check_time = event_time + timedelta(minutes=40)
    assert news_calendar.is_blackout_period(check_time) is False

def test_get_next_event(news_calendar):
    """Test finding next upcoming event."""
    tz = pytz.timezone("America/New_York")

    now = tz.localize(datetime(2026, 1, 10, 9, 0))

    news_calendar.events = [
        EconomicEvent(
            name="Event 1",
            date=tz.localize(datetime(2026, 1, 10, 10, 0)),
            impact="High",
            country="US"
        ),
        EconomicEvent(
            name="Event 2",
            date=tz.localize(datetime(2026, 1, 10, 14, 0)),
            impact="High",
            country="US"
        ),
    ]

    next_event = news_calendar.get_next_event(now)
    assert next_event is not None
    assert next_event.name == "Event 1"

@pytest.mark.asyncio
async def test_api_integration(news_calendar):
    """Test live API integration (requires API key)."""
    await news_calendar.connect()

    today = datetime.now(news_calendar.timezone).date()
    events = await news_calendar.fetch_today_events()

    # Should return list (may be empty if no events today)
    assert isinstance(events, list)

    await news_calendar.disconnect()
```

Run tests:

```bash
# Run all news calendar tests
pytest test_news_calendar.py -v

# Run with API integration (requires API key in .env)
pytest test_news_calendar.py::test_api_integration -v
```

---

## Advanced Configuration

### Exit Position on Blackout

```python
# config.py
news_exit_on_blackout: bool = False  # Exit open positions during blackout
```

```python
# In on_bar()
if self.news_calendar.is_blackout_period(bar_time):
    if self.config.news_exit_on_blackout and self.position != 0:
        logger.warning("Exiting position due to news blackout")
        await self._exit_position("NewsBlackout", bar["close"])
    return
```

### Custom Blackout Windows

```python
# Different blackout periods for different event types
def get_blackout_minutes(self, event: EconomicEvent) -> int:
    """Get custom blackout period based on event."""

    # FOMC needs longer blackout
    if "FOMC" in event.name or "Fed" in event.name:
        return 60  # 1 hour before/after

    # NFP is very volatile
    if "Non-Farm Payrolls" in event.name or "NFP" in event.name:
        return 90  # 1.5 hours before/after

    # Default
    return self.config.news_blackout_minutes
```

### Event Notifications

```python
# Warn user of upcoming events
next_event = self.news_calendar.get_next_event(bar_time)
if next_event:
    time_until = (next_event.date - bar_time).total_seconds() / 60

    if 5 <= time_until <= 10:
        logger.warning(f"⚠️ UPCOMING EVENT in {int(time_until)} min: {next_event.name}")
```

---

## See Also

- [ECONOMIC_CALENDAR.md](../docs/ECONOMIC_CALENDAR.md) - High-impact events reference
- [BASE_BOT.md](BASE_BOT.md) - Main bot template integration
- [CONFIG.md](../CONFIG.md) - Configuration reference
- [ALERTING.md](ALERTING.md) - Event notifications and alerts
