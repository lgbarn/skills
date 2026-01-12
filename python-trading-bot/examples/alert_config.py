"""
Alert Configuration Example

Example configuration for email and SMS alerting in trading bots.
Shows how to set up SMTP email and Pushover notifications.

Author: Luther Barnum
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class AlertConfig:
    """
    Alert configuration for trading bot notifications.

    Supports:
    - Email (SMTP)
    - SMS via Pushover (https://pushover.net)
    """

    # Email Configuration
    alert_email_enabled: bool = True
    alert_email_to: str = ""
    alert_email_from: str = ""
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""  # App password, not account password

    # SMS Configuration (via Pushover)
    alert_pushover_enabled: bool = True
    pushover_token: str = ""  # Application API token
    pushover_user: str = ""  # User key
    pushover_device: Optional[str] = None  # Optional: specific device

    # Alert Thresholds
    daily_loss_warning_pct: float = 0.80  # Alert at 80% of daily max loss
    dd_room_warning_pct: float = 0.80  # Alert at 80% of DD room used
    consecutive_losses: int = 5  # Alert after N consecutive losses

    def __post_init__(self):
        """Load configuration from environment variables."""
        # Email settings
        self.alert_email_enabled = os.getenv(
            "ALERT_EMAIL_ENABLED", str(self.alert_email_enabled)
        ).lower() in ("true", "1", "yes")

        self.alert_email_to = os.getenv("ALERT_EMAIL_TO", self.alert_email_to)
        self.alert_email_from = os.getenv("ALERT_EMAIL_FROM", self.alert_email_from)
        self.smtp_server = os.getenv("SMTP_SERVER", self.smtp_server)
        self.smtp_port = int(os.getenv("SMTP_PORT", str(self.smtp_port)))
        self.smtp_username = os.getenv("SMTP_USERNAME", self.smtp_username)
        self.smtp_password = os.getenv("SMTP_PASSWORD", self.smtp_password)

        # Pushover settings
        self.alert_pushover_enabled = os.getenv(
            "ALERT_PUSHOVER_ENABLED", str(self.alert_pushover_enabled)
        ).lower() in ("true", "1", "yes")

        self.pushover_token = os.getenv("PUSHOVER_TOKEN", self.pushover_token)
        self.pushover_user = os.getenv("PUSHOVER_USER", self.pushover_user)
        self.pushover_device = os.getenv("PUSHOVER_DEVICE", self.pushover_device)

        # Thresholds
        self.daily_loss_warning_pct = float(
            os.getenv("DAILY_LOSS_WARNING_PCT", str(self.daily_loss_warning_pct))
        )
        self.dd_room_warning_pct = float(
            os.getenv("DD_ROOM_WARNING_PCT", str(self.dd_room_warning_pct))
        )
        self.consecutive_losses = int(
            os.getenv("CONSECUTIVE_LOSSES", str(self.consecutive_losses))
        )

    def validate(self) -> bool:
        """
        Validate alert configuration.

        Returns:
            True if at least one alert method is properly configured
        """
        email_ok = False
        pushover_ok = False

        if self.alert_email_enabled:
            email_ok = all(
                [
                    self.alert_email_to,
                    self.alert_email_from,
                    self.smtp_server,
                    self.smtp_username,
                    self.smtp_password,
                ]
            )
            if not email_ok:
                print("⚠️  Email alerts enabled but configuration incomplete")

        if self.alert_pushover_enabled:
            pushover_ok = all([self.pushover_token, self.pushover_user])
            if not pushover_ok:
                print("⚠️  Pushover alerts enabled but configuration incomplete")

        return email_ok or pushover_ok


# Example .env configuration
ENV_EXAMPLE = """
# Email Alerts (SMTP)
ALERT_EMAIL_ENABLED=true
ALERT_EMAIL_TO=your-email@gmail.com
ALERT_EMAIL_FROM=trading-bot@yourserver.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your_app_password_here  # NOT your Google password!

# Pushover Alerts (SMS)
ALERT_PUSHOVER_ENABLED=true
PUSHOVER_TOKEN=your_pushover_app_token
PUSHOVER_USER=your_pushover_user_key
PUSHOVER_DEVICE=pixel5  # Optional: target specific device

# Alert Thresholds
DAILY_LOSS_WARNING_PCT=0.80  # Alert at 80% of daily max loss
DD_ROOM_WARNING_PCT=0.80     # Alert at 80% of drawdown room used
CONSECUTIVE_LOSSES=5         # Alert after 5 consecutive losses
"""


# Gmail Setup Instructions
GMAIL_SETUP = """
Gmail SMTP Setup (2-Factor Authentication Required):

1. Enable 2-Factor Authentication on Google Account
   - Go to: https://myaccount.google.com/security
   - Enable 2-Step Verification

2. Generate App Password
   - Go to: https://myaccount.google.com/apppasswords
   - Select app: "Mail"
   - Select device: "Other (Custom name)" → "Trading Bot"
   - Click "Generate"
   - Copy the 16-character password

3. Configure .env
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=<16-character app password>
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587

4. Test
   python test_alerts.py
"""


# Pushover Setup Instructions
PUSHOVER_SETUP = """
Pushover SMS Setup:

1. Create Account
   - Go to: https://pushover.net
   - Sign up for free account ($5 one-time fee after 30-day trial)

2. Create Application
   - Go to: https://pushover.net/apps/build
   - Name: "Trading Bot"
   - Type: "Application"
   - Description: "Automated trading alerts"
   - Click "Create Application"

3. Get Credentials
   - Application Token: Shown on app page
   - User Key: Shown on dashboard (https://pushover.net)

4. Configure .env
   PUSHOVER_TOKEN=<application token>
   PUSHOVER_USER=<user key>

5. Install Pushover Mobile App
   - iOS: https://apps.apple.com/app/pushover-notifications/id506088175
   - Android: https://play.google.com/store/apps/details?id=net.superblock.pushover

6. Test
   python test_alerts.py

Pushover Pricing:
- Free 30-day trial
- $5 one-time purchase per platform (iOS/Android)
- Unlimited notifications
"""


# Alert Priority Levels (Pushover)
class AlertPriority:
    """Pushover alert priority levels."""

    LOW = -2  # No notification, badge only
    NORMAL = -1  # Normal notification
    HIGH = 0  # High priority (default)
    EMERGENCY = 2  # Bypass quiet hours, repeat until acknowledged


# Example alert scenarios
ALERT_SCENARIOS = {
    "daily_loss_warning": {
        "title": "⚠️  Daily Loss Warning",
        "priority": AlertPriority.HIGH,
        "example": "Daily P&L: -$400 / -$500 max (80%)",
    },
    "daily_max_loss_hit": {
        "title": "🛑 Daily Max Loss Hit",
        "priority": AlertPriority.EMERGENCY,
        "example": "Daily max loss reached: -$500. Trading stopped.",
    },
    "dd_breach_warning": {
        "title": "⚠️  Drawdown Warning",
        "priority": AlertPriority.HIGH,
        "example": "DD room: $500 / $2,500 (80% used). Equity: $47,500",
    },
    "dd_breach": {
        "title": "🚨 DRAWDOWN BREACHED",
        "priority": AlertPriority.EMERGENCY,
        "example": "Account breached! Equity: $47,400 < Threshold: $47,500",
    },
    "profit_target_reached": {
        "title": "🎉 Profit Target Reached",
        "priority": AlertPriority.HIGH,
        "example": "Profit target hit! Equity: $53,000. Target: $3,000 ✅",
    },
    "consecutive_losses": {
        "title": "⚠️  Consecutive Losses",
        "priority": AlertPriority.HIGH,
        "example": "5 consecutive losing trades. Review strategy.",
    },
    "connection_lost": {
        "title": "🔌 Connection Lost",
        "priority": AlertPriority.EMERGENCY,
        "example": "Data feed disconnected > 2 minutes. Bot paused.",
    },
    "order_failed": {
        "title": "❌ Order Failed",
        "priority": AlertPriority.EMERGENCY,
        "example": "Failed to enter long position @ 18,500. Retry or manual.",
    },
    "trade_entry": {
        "title": "📈 Trade Entry",
        "priority": AlertPriority.NORMAL,
        "example": "ENTRY: Long 2 @ 18,500. SL: 18,470 TP: 18,560",
    },
    "trade_exit": {
        "title": "📉 Trade Exit",
        "priority": AlertPriority.NORMAL,
        "example": "EXIT: Long 2 @ 18,540. P&L: +$800",
    },
}


# Test script
if __name__ == "__main__":
    print("Alert Configuration Example\n")

    # Load config
    config = AlertConfig()

    # Validate
    if config.validate():
        print("✅ Alert configuration valid")
        if config.alert_email_enabled:
            print(f"   Email: {config.alert_email_to}")
        if config.alert_pushover_enabled:
            print(f"   Pushover: {config.pushover_user[:8]}...")
    else:
        print("❌ Alert configuration incomplete")
        print("\nSee setup instructions:")
        print(GMAIL_SETUP)
        print(PUSHOVER_SETUP)

    print("\nExample .env configuration:")
    print(ENV_EXAMPLE)

    print("\nAlert Scenarios:")
    for name, scenario in ALERT_SCENARIOS.items():
        priority_name = {
            -2: "LOW",
            -1: "NORMAL",
            0: "HIGH",
            2: "EMERGENCY",
        }.get(scenario["priority"], "UNKNOWN")

        print(f"\n{scenario['title']} ({priority_name})")
        print(f"  Example: {scenario['example']}")
