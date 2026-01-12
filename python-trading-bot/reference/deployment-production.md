# Production Operations

Monitoring, security, backup, and troubleshooting for live deployments.

---

## Monitoring

### Simple Health Check Script

```bash
#!/bin/bash
# ~/bots/healthcheck.sh

BOT_NAME="keltner-bot"

if ! systemctl is-active --quiet $BOT_NAME; then
    echo "Bot is down! Restarting..."
    sudo systemctl restart $BOT_NAME

    # Optional: Send notification
    # curl -X POST "https://api.telegram.org/bot<token>/sendMessage" \
    #   -d "chat_id=<chat_id>&text=Bot restarted"
fi
```

Add to crontab:

```bash
crontab -e
# Add:
*/5 * * * * /home/botuser/bots/healthcheck.sh
```

### Telegram Notifications (Optional)

Add to bot for trade notifications:

```python
import aiohttp

TELEGRAM_BOT_TOKEN = "your_bot_token"
TELEGRAM_CHAT_ID = "your_chat_id"

async def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    async with aiohttp.ClientSession() as session:
        await session.post(url, data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        })
```

---

## Security

### SSH Hardening

```bash
# Disable password authentication
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no

# Restart SSH
sudo systemctl restart sshd
```

### Firewall Rules

```bash
# Only allow SSH
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw enable
```

### Environment Variables

```bash
# Restrict .env file permissions
chmod 600 ~/.env
```

### Regular Updates

```bash
# Monthly security updates
sudo apt update && sudo apt upgrade -y
```

---

## Backup

### Backup Script

```bash
#!/bin/bash
# ~/bots/backup.sh

BACKUP_DIR="/home/botuser/backups"
BOT_DIR="/home/botuser/bots/keltner"
DATE=$(date +%Y%m%d)

mkdir -p $BACKUP_DIR

# Backup config and logs (NOT .env)
tar -czf $BACKUP_DIR/keltner_$DATE.tar.gz \
    --exclude='.env' \
    --exclude='venv' \
    --exclude='__pycache__' \
    $BOT_DIR

# Keep only last 7 backups
find $BACKUP_DIR -name "keltner_*.tar.gz" -mtime +7 -delete
```

Add to crontab:

```bash
0 0 * * * /home/botuser/bots/backup.sh
```

---

## Switching to Live

**Only after extensive paper trading testing!**

### 1. Update .env

```bash
nano ~/bots/keltner/.env

# Change:
BOT_PAPER_MODE=false
TRADOVATE_ENV=live
```

### 2. Restart Service

```bash
sudo systemctl restart keltner-bot
```

### 3. Monitor Closely

```bash
# Watch logs
tail -f ~/bots/keltner/logs/stdout.log

# Check TradersPost dashboard for orders
# Monitor Tradovate for executions
```

---

## Troubleshooting

### Bot Won't Start

```bash
# Check service status
sudo systemctl status keltner-bot

# Check logs
sudo journalctl -u keltner-bot -n 50

# Check Python errors
tail -50 ~/bots/keltner/logs/stderr.log
```

### Connection Issues

```bash
# Test DNS
ping md.tradovateapi.com

# Test connectivity
curl -I https://demo.tradovateapi.com/v1

# Check firewall
sudo ufw status
```

### High Memory/CPU

```bash
# Check processes
htop

# Kill and restart
sudo systemctl restart keltner-bot
```

### Disk Full

```bash
# Check disk
df -h

# Clean logs
sudo logrotate -f /etc/logrotate.d/keltner-bot

# Clean old backups
find ~/backups -mtime +30 -delete
```

---

## See Also

- [VPS_SETUP.md](VPS_SETUP.md) - Initial server setup
- [SYSTEMD_SERVICE.md](SYSTEMD_SERVICE.md) - Service configuration
- [../DEPLOYMENT.md](../DEPLOYMENT.md) - Deployment overview
