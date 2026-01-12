# Alerting System Template

Real-time email and SMS notifications for critical bot events and risk conditions.

---

## Overview

The alerting system monitors bot state and sends notifications when important events occur. This allows you to stay informed without constantly watching logs, and get immediate notification of critical issues that require intervention.

Key features:
- Email alerts (SMTP)
- SMS/Push notifications (Pushover)
- Priority-based alerting (normal, high, critical)
- Configurable alert triggers
- Rate limiting to prevent spam
- Alert history tracking
- Graceful degradation on failure

---

## alert_manager.py

```python
"""
Alert Manager
Author: Luther Barnum

Sends email and SMS/push notifications for bot events.
Supports configurable triggers, priority levels, and rate limiting.
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional, Dict
from dataclasses import dataclass
import aiohttp

from config import Config

logger = logging.getLogger(__name__)


@dataclass
class Alert:
    """Alert message."""

    title: str
    message: str
    priority: str  # "normal", "high", "critical"
    timestamp: datetime
    channel: str  # "email", "sms", "both"


class AlertManager:
    """
    Manages email and SMS/push notifications.

    Handles alert delivery with priority levels and rate limiting.
    """

    def __init__(self, config: Config):
        self.config = config

        # Alert history (for rate limiting)
        self.alert_history: Dict[str, datetime] = {}

        # Rate limiting (prevent spam)
        self.min_alert_interval = timedelta(minutes=5)  # Same alert max once per 5 min

        # HTTP session for Pushover
        self.session: Optional[aiohttp.ClientSession] = None

    async def connect(self):
        """Initialize HTTP session for push notifications."""
        if self.config.alert_pushover_enabled and not self.session:
            self.session = aiohttp.ClientSession()
            logger.info("Alert manager session initialized")

    async def disconnect(self):
        """Clean up HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("Alert manager session closed")

    async def send_alert(
        self,
        title: str,
        message: str,
        priority: str = "normal",
        force: bool = False,
    ):
        """
        Send alert via configured channels.

        Args:
            title: Alert title (short summary)
            message: Alert message (detailed info)
            priority: "normal", "high", or "critical"
            force: Skip rate limiting if True

        Returns:
            None
        """
        # Check rate limiting (unless forced)
        if not force:
            alert_key = f"{title}:{priority}"
            last_sent = self.alert_history.get(alert_key)

            if last_sent:
                time_since = datetime.now() - last_sent
                if time_since < self.min_alert_interval:
                    logger.debug(
                        f"Alert rate limited: {title} "
                        f"(sent {time_since.seconds}s ago)"
                    )
                    return

        # Log alert
        logger.info(f"📢 ALERT [{priority.upper()}]: {title}")

        # Send to configured channels
        email_sent = False
        sms_sent = False

        if self.config.alert_email_enabled:
            try:
                await self._send_email(title, message, priority)
                email_sent = True
            except Exception as e:
                logger.error(f"Failed to send email alert: {e}")

        if self.config.alert_pushover_enabled:
            try:
                await self._send_pushover(title, message, priority)
                sms_sent = True
            except Exception as e:
                logger.error(f"Failed to send Pushover alert: {e}")

        # Update alert history
        alert_key = f"{title}:{priority}"
        self.alert_history[alert_key] = datetime.now()

        # Log delivery status
        channels = []
        if email_sent:
            channels.append("Email")
        if sms_sent:
            channels.append("SMS/Push")

        if channels:
            logger.info(f"Alert sent via: {', '.join(channels)}")
        else:
            logger.warning("Alert not delivered (all channels failed)")

    async def _send_email(self, title: str, message: str, priority: str):
        """
        Send email alert via SMTP.

        Args:
            title: Email subject
            message: Email body
            priority: Alert priority
        """
        # Create message
        msg = MIMEMultipart()
        msg["From"] = self.config.alert_email_from
        msg["To"] = self.config.alert_email_to
        msg["Subject"] = f"[{priority.upper()}] {title}"

        # Build email body
        body = f"""
Trading Bot Alert
=================

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Priority: {priority.upper()}
Bot: {self.config.bot_name if hasattr(self.config, 'bot_name') else 'Trading Bot'}

{message}

---
This is an automated alert from your trading bot.
"""

        msg.attach(MIMEText(body, "plain"))

        # Send via SMTP
        with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
            if self.config.smtp_use_tls:
                server.starttls()

            if self.config.smtp_username:
                server.login(self.config.smtp_username, self.config.smtp_password)

            server.send_message(msg)

        logger.debug(f"Email sent to {self.config.alert_email_to}")

    async def _send_pushover(self, title: str, message: str, priority: str):
        """
        Send push notification via Pushover.

        Args:
            title: Notification title
            message: Notification message
            priority: Alert priority

        Pushover Priority Mapping:
            normal: 0 (no sound/vibration if device silent)
            high: 1 (always notify)
            critical: 2 (requires acknowledgment)
        """
        if not self.session:
            await self.connect()

        # Map priority to Pushover levels
        pushover_priority = {
            "normal": 0,
            "high": 1,
            "critical": 2,
        }.get(priority, 0)

        # Pushover API
        url = "https://api.pushover.net/1/messages.json"

        data = {
            "token": self.config.alert_pushover_token,
            "user": self.config.alert_pushover_user,
            "title": title,
            "message": message,
            "priority": pushover_priority,
        }

        # Critical alerts require retry/expire
        if pushover_priority == 2:
            data["retry"] = 30  # Retry every 30 seconds
            data["expire"] = 3600  # Give up after 1 hour

        async with self.session.post(url, data=data) as response:
            response.raise_for_status()
            result = await response.json()

            if result.get("status") != 1:
                raise Exception(f"Pushover API error: {result}")

        logger.debug(f"Pushover notification sent (priority: {pushover_priority})")

    # Common Alert Triggers

    async def alert_daily_loss_warning(self, current_pnl: float, max_loss: float):
        """Alert when approaching daily max loss."""
        pct_used = abs(current_pnl) / max_loss * 100

        await self.send_alert(
            title="Daily Loss Warning",
            message=f"Daily P&L: ${current_pnl:.2f}\n"
            f"Max Loss: ${max_loss:.2f}\n"
            f"Used: {pct_used:.1f}%",
            priority="high",
        )

    async def alert_daily_loss_hit(self, current_pnl: float, max_loss: float):
        """Alert when daily max loss breached."""
        await self.send_alert(
            title="Daily Max Loss Hit",
            message=f"Daily P&L: ${current_pnl:.2f}\n"
            f"Max Loss: ${max_loss:.2f}\n"
            f"Bot stopped for the day.",
            priority="critical",
        )

    async def alert_drawdown_warning(self, equity: float, dd_threshold: float):
        """Alert when approaching drawdown threshold."""
        room = equity - dd_threshold

        await self.send_alert(
            title="Drawdown Warning",
            message=f"Current Equity: ${equity:.2f}\n"
            f"DD Threshold: ${dd_threshold:.2f}\n"
            f"Room: ${room:.2f}",
            priority="high",
        )

    async def alert_drawdown_breach(self, equity: float, dd_threshold: float):
        """Alert when drawdown breached."""
        await self.send_alert(
            title="DRAWDOWN BREACHED",
            message=f"Current Equity: ${equity:.2f}\n"
            f"DD Threshold: ${dd_threshold:.2f}\n"
            f"STOP TRADING IMMEDIATELY!",
            priority="critical",
            force=True,  # Always send
        )

    async def alert_profit_target_reached(self, equity: float, target: float):
        """Alert when profit target reached."""
        await self.send_alert(
            title="Profit Target Reached! 🎉",
            message=f"Current Equity: ${equity:.2f}\n"
            f"Profit Target: ${target:.2f}\n"
            f"Congrats! Account eligible for PA conversion.",
            priority="high",
            force=True,
        )

    async def alert_connection_lost(self, provider: str):
        """Alert when data connection lost."""
        await self.send_alert(
            title="Connection Lost",
            message=f"Lost connection to {provider}\n"
            f"Attempting reconnect...",
            priority="high",
        )

    async def alert_order_failure(self, reason: str, details: str):
        """Alert on order execution failure."""
        await self.send_alert(
            title="Order Execution Failed",
            message=f"Reason: {reason}\n"
            f"Details: {details}\n"
            f"Check TradersPost dashboard.",
            priority="critical",
        )

    async def alert_bot_started(self):
        """Alert when bot starts."""
        await self.send_alert(
            title="Bot Started",
            message=f"Bot successfully started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            priority="normal",
        )

    async def alert_bot_stopped(self, reason: str = "Manual"):
        """Alert when bot stops."""
        await self.send_alert(
            title="Bot Stopped",
            message=f"Bot stopped: {reason}\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            priority="normal",
        )

    async def alert_losing_streak(self, streak: int, total_loss: float):
        """Alert on consecutive losing trades."""
        await self.send_alert(
            title=f"Losing Streak: {streak} Trades",
            message=f"Consecutive losses: {streak}\n"
            f"Total loss: ${total_loss:.2f}\n"
            f"Consider reviewing strategy.",
            priority="high",
        )

    def get_stats(self) -> dict:
        """Get alert manager statistics."""
        return {
            "email_enabled": self.config.alert_email_enabled,
            "pushover_enabled": self.config.alert_pushover_enabled,
            "alerts_sent": len(self.alert_history),
            "rate_limit_minutes": self.min_alert_interval.seconds // 60,
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

    # Email Alerts
    alert_email_enabled: bool = False
    alert_email_from: str = ""
    alert_email_to: str = ""
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_use_tls: bool = True
    smtp_username: str = ""
    smtp_password: str = ""

    # Pushover (SMS/Push)
    alert_pushover_enabled: bool = False
    alert_pushover_token: str = ""  # App token
    alert_pushover_user: str = ""  # User key

    # Alert Triggers
    alert_daily_loss_pct: float = 0.8  # Alert at 80% of max loss
    alert_drawdown_pct: float = 0.8  # Alert at 80% of DD threshold
    alert_losing_streak: int = 5  # Alert after 5 consecutive losses

    def __post_init__(self):
        # ... existing __post_init__ ...

        # Load alerting settings
        self.alert_email_enabled = os.getenv("ALERT_EMAIL_ENABLED", "false").lower() == "true"
        self.alert_email_from = os.getenv("ALERT_EMAIL_FROM", "")
        self.alert_email_to = os.getenv("ALERT_EMAIL_TO", "")
        self.smtp_host = os.getenv("SMTP_HOST", self.smtp_host)
        self.smtp_port = int(os.getenv("SMTP_PORT", str(self.smtp_port)))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")

        self.alert_pushover_enabled = os.getenv("ALERT_PUSHOVER_ENABLED", "false").lower() == "true"
        self.alert_pushover_token = os.getenv("ALERT_PUSHOVER_TOKEN", "")
        self.alert_pushover_user = os.getenv("ALERT_PUSHOVER_USER", "")

        self.alert_daily_loss_pct = float(os.getenv("ALERT_DAILY_LOSS_PCT", str(self.alert_daily_loss_pct)))
        self.alert_drawdown_pct = float(os.getenv("ALERT_DRAWDOWN_PCT", str(self.alert_drawdown_pct)))
        self.alert_losing_streak = int(os.getenv("ALERT_LOSING_STREAK", str(self.alert_losing_streak)))
```

Add to `.env`:

```bash
# Email Alerts
ALERT_EMAIL_ENABLED=true
ALERT_EMAIL_FROM=your_bot@gmail.com
ALERT_EMAIL_TO=your_email@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_bot@gmail.com
SMTP_PASSWORD=your_app_specific_password

# Pushover Alerts (optional)
ALERT_PUSHOVER_ENABLED=true
ALERT_PUSHOVER_TOKEN=your_pushover_app_token
ALERT_PUSHOVER_USER=your_pushover_user_key

# Alert Triggers
ALERT_DAILY_LOSS_PCT=0.8
ALERT_DRAWDOWN_PCT=0.8
ALERT_LOSING_STREAK=5
```

---

## Usage in Bot

```python
# In bot_*.py

from alert_manager import AlertManager

class TradingBot:
    def __init__(self, config):
        self.config = config
        self.alert_manager = AlertManager(config)
        # ... other initialization ...

        # Track losing streaks
        self.current_losing_streak = 0
        self.losing_streak_pnl = 0.0

    async def start(self):
        """Start bot."""
        logger.info("Starting bot...")

        # Connect alert manager
        await self.alert_manager.connect()

        # ... connect to data, etc ...

        # Send startup alert
        await self.alert_manager.alert_bot_started()

    async def on_bar(self, bar: dict):
        """Process each bar."""
        # ... bar processing ...

        # Check daily loss warning
        if self.config.alert_email_enabled or self.config.alert_pushover_enabled:
            daily_pnl = self.risk_manager.daily_pnl
            max_loss = self.config.daily_max_loss

            # Warning at 80% of max loss
            if daily_pnl < 0:
                loss_pct = abs(daily_pnl) / max_loss
                if loss_pct >= self.config.alert_daily_loss_pct:
                    await self.alert_manager.alert_daily_loss_warning(daily_pnl, max_loss)

        # Check drawdown warning
        stats = self.risk_manager.get_stats()
        equity = stats["equity"]
        dd_threshold = stats["dd_threshold"]
        dd_room = stats["drawdown_room"]

        if dd_room > 0:
            dd_pct_used = 1.0 - (dd_room / abs(dd_threshold))
            if dd_pct_used >= self.config.alert_drawdown_pct:
                await self.alert_manager.alert_drawdown_warning(equity, dd_threshold)

        # ... rest of bar processing ...

    async def _exit_position(self, reason, exit_price=None):
        """Exit position and update risk manager."""
        # ... exit logic ...

        # Calculate P&L
        pnl = (exit_price - self.entry_price) * self.position
        pnl *= self.config.point_value * self.contracts
        pnl -= self.config.commission_rt * self.contracts

        # Track losing streaks
        if pnl < 0:
            self.current_losing_streak += 1
            self.losing_streak_pnl += pnl

            # Alert on losing streak
            if self.current_losing_streak >= self.config.alert_losing_streak:
                await self.alert_manager.alert_losing_streak(
                    self.current_losing_streak,
                    self.losing_streak_pnl
                )
        else:
            # Reset on winning trade
            self.current_losing_streak = 0
            self.losing_streak_pnl = 0.0

        # Update risk manager
        self.risk_manager.record_trade(pnl, self.contracts)

        # Check if daily max loss hit
        if self.risk_manager.daily_stopped:
            await self.alert_manager.alert_daily_loss_hit(
                self.risk_manager.daily_pnl,
                self.config.daily_max_loss
            )

        # Check if profit target reached
        if self.risk_manager.apex_account.profit_target_hit:
            await self.alert_manager.alert_profit_target_reached(
                self.risk_manager.apex_account.equity,
                self.risk_manager.apex_account.profit_target
            )

        # Check if drawdown breached
        if self.risk_manager.apex_account.check_drawdown_breach():
            await self.alert_manager.alert_drawdown_breach(
                self.risk_manager.apex_account.equity,
                self.risk_manager.apex_account.dd_threshold
            )

        # ... reset position state ...

    async def stop(self):
        """Graceful shutdown."""
        logger.info("Shutting down bot...")

        # ... exit position, close risk manager, etc ...

        # Send shutdown alert
        await self.alert_manager.alert_bot_stopped()

        # Close alert manager
        await self.alert_manager.disconnect()

        logger.info("Bot stopped")
```

---

## Email Setup

### Gmail (Recommended for Testing)

1. Enable 2-factor authentication on your Google account
2. Generate app-specific password: https://myaccount.google.com/apppasswords
3. Use app password in `.env`:

```bash
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_16_char_app_password
```

### SendGrid (Recommended for Production)

1. Sign up: https://sendgrid.com/
2. Create API key
3. Update config:

```python
smtp_host: str = "smtp.sendgrid.net"
smtp_port: int = 587
smtp_username: str = "apikey"  # Literal string "apikey"
smtp_password: str = os.getenv("SENDGRID_API_KEY", "")
```

### Other SMTP Providers

- **Mailgun**: `smtp.mailgun.org:587`
- **Amazon SES**: `email-smtp.us-east-1.amazonaws.com:587`
- **Outlook**: `smtp-mail.outlook.com:587`

---

## Pushover Setup

Pushover provides instant push notifications to your phone (iOS/Android).

### Sign Up

1. Visit: https://pushover.net/
2. Create account ($5 one-time fee after 30-day trial)
3. Install Pushover app on your phone

### Get Credentials

1. **User Key**: Found on Pushover dashboard (starts with `u...`)
2. **App Token**: Create new application, get token (starts with `a...`)

### Configure

```bash
# .env
ALERT_PUSHOVER_ENABLED=true
ALERT_PUSHOVER_TOKEN=your_app_token_here
ALERT_PUSHOVER_USER=your_user_key_here
```

### Test

```python
# test_pushover.py
import asyncio
from alert_manager import AlertManager
from config import Config

async def test():
    config = Config()
    alert_mgr = AlertManager(config)
    await alert_mgr.connect()

    await alert_mgr.send_alert(
        title="Test Alert",
        message="If you receive this, Pushover is working!",
        priority="normal"
    )

    await alert_mgr.disconnect()

asyncio.run(test())
```

---

## Alert Examples

### Normal Priority (Email Only)

```
Subject: [NORMAL] Bot Started

Trading Bot Alert
=================

Time: 2026-01-10 09:30:00
Priority: NORMAL
Bot: Keltner Strategy

Bot successfully started at 2026-01-10 09:30:00

---
This is an automated alert from your trading bot.
```

### High Priority (Email + Push)

```
Subject: [HIGH] Daily Loss Warning

Trading Bot Alert
=================

Time: 2026-01-10 13:45:00
Priority: HIGH
Bot: Keltner Strategy

Daily P&L: $-400.00
Max Loss: $500.00
Used: 80.0%

---
This is an automated alert from your trading bot.
```

Phone notification:
```
Keltner Strategy
Daily Loss Warning

Daily P&L: $-400.00
Max Loss: $500.00
Used: 80.0%
```

### Critical Priority (Email + Push with Acknowledgment)

```
Subject: [CRITICAL] DRAWDOWN BREACHED

Trading Bot Alert
=================

Time: 2026-01-10 14:30:00
Priority: CRITICAL
Bot: Keltner Strategy

Current Equity: $-2,600.00
DD Threshold: $-2,500.00
STOP TRADING IMMEDIATELY!

---
This is an automated alert from your trading bot.
```

Phone notification (requires acknowledgment):
```
Keltner Strategy
DRAWDOWN BREACHED

Current Equity: $-2,600.00
DD Threshold: $-2,500.00
STOP TRADING IMMEDIATELY!

[Acknowledge]
```

---

## Rate Limiting

Prevents alert spam by limiting same alert to once per 5 minutes:

```python
# Same alert sent twice in 3 minutes

await alert_mgr.send_alert("Daily Loss Warning", "...", "high")  # Sent
await asyncio.sleep(180)  # 3 minutes later
await alert_mgr.send_alert("Daily Loss Warning", "...", "high")  # Skipped (rate limited)

# Different alerts are not rate limited
await alert_mgr.send_alert("Daily Loss Warning", "...", "high")  # Sent
await alert_mgr.send_alert("Connection Lost", "...", "high")  # Sent (different alert)

# Force bypass rate limiting
await alert_mgr.send_alert("Daily Loss Warning", "...", "high", force=True)  # Always sent
```

---

## Testing

```python
# test_alerting.py

import pytest
import asyncio
from alert_manager import AlertManager
from config import Config

@pytest.fixture
def config():
    config = Config()
    config.alert_email_enabled = True
    config.alert_pushover_enabled = True
    return config

@pytest.fixture
def alert_mgr(config):
    return AlertManager(config)

@pytest.mark.asyncio
async def test_email_alert(alert_mgr):
    """Test email sending."""
    await alert_mgr.connect()

    await alert_mgr._send_email(
        title="Test Alert",
        message="This is a test message",
        priority="normal"
    )

    await alert_mgr.disconnect()

@pytest.mark.asyncio
async def test_pushover_alert(alert_mgr):
    """Test Pushover notification."""
    await alert_mgr.connect()

    await alert_mgr._send_pushover(
        title="Test Alert",
        message="This is a test message",
        priority="high"
    )

    await alert_mgr.disconnect()

@pytest.mark.asyncio
async def test_rate_limiting(alert_mgr):
    """Test alert rate limiting."""
    await alert_mgr.connect()

    # First alert should send
    await alert_mgr.send_alert("Test", "Message 1", "normal")
    assert "Test:normal" in alert_mgr.alert_history

    # Second identical alert should be rate limited
    # (would normally skip, but we can verify the history)
    await alert_mgr.send_alert("Test", "Message 2", "normal")

    # Different alert should send
    await alert_mgr.send_alert("Other", "Message 3", "normal")
    assert "Other:normal" in alert_mgr.alert_history

    await alert_mgr.disconnect()

@pytest.mark.asyncio
async def test_all_triggers(alert_mgr):
    """Test all built-in alert triggers."""
    await alert_mgr.connect()

    await alert_mgr.alert_daily_loss_warning(-400, 500)
    await alert_mgr.alert_daily_loss_hit(-500, 500)
    await alert_mgr.alert_drawdown_warning(-2000, -2500)
    await alert_mgr.alert_drawdown_breach(-2600, -2500)
    await alert_mgr.alert_profit_target_reached(3100, 3000)
    await alert_mgr.alert_connection_lost("Databento")
    await alert_mgr.alert_order_failure("Timeout", "TradersPost webhook timeout")
    await alert_mgr.alert_bot_started()
    await alert_mgr.alert_bot_stopped("Manual shutdown")
    await alert_mgr.alert_losing_streak(5, -1500)

    await alert_mgr.disconnect()
```

Run tests:

```bash
# Run all alerting tests
pytest test_alerting.py -v

# Test only email (requires SMTP config)
pytest test_alerting.py::test_email_alert -v

# Test only Pushover (requires API keys)
pytest test_alerting.py::test_pushover_alert -v
```

---

## Troubleshooting

### Email Not Sending

**Check SMTP credentials:**
```python
# Test SMTP connection
import smtplib

try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login("your_email@gmail.com", "your_app_password")
    print("✅ SMTP connection successful")
    server.quit()
except Exception as e:
    print(f"❌ SMTP failed: {e}")
```

**Common issues:**
- Gmail: Must use app-specific password (not account password)
- 2FA required for Gmail
- Some providers block SMTP from unknown IPs (use SendGrid instead)

### Pushover Not Working

**Test API directly:**
```bash
curl -s \
  --form-string "token=YOUR_APP_TOKEN" \
  --form-string "user=YOUR_USER_KEY" \
  --form-string "message=Test from curl" \
  https://api.pushover.net/1/messages.json
```

**Common issues:**
- Invalid token or user key
- App token vs user key confusion (need both)
- Trial period expired (requires $5 one-time purchase)

### Too Many Alerts

Adjust rate limiting:
```python
# In AlertManager.__init__()
self.min_alert_interval = timedelta(minutes=10)  # Increase to 10 min
```

Or disable specific triggers:
```python
# In config.py
alert_daily_loss_pct: float = 0.9  # Only alert at 90% instead of 80%
alert_losing_streak: int = 10  # Only alert after 10 losses instead of 5
```

---

## See Also

- [RISK_MANAGER.md](RISK_MANAGER.md) - Integration with risk manager
- [BASE_BOT.md](BASE_BOT.md) - Main bot template
- [CONFIG.md](../CONFIG.md) - Configuration reference
- [NEWS_FILTER.md](NEWS_FILTER.md) - News calendar alerts
