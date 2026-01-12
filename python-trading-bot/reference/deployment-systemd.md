# Systemd Service Configuration

Run bot as a system service for auto-restart and persistence.

---

## Create Service File

```bash
sudo nano /etc/systemd/system/keltner-bot.service
```

```ini
[Unit]
Description=Keltner Channel Trading Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/bots/keltner
Environment="PATH=/home/botuser/bots/keltner/venv/bin"
ExecStart=/home/botuser/bots/keltner/venv/bin/python bot_keltner.py --paper
Restart=always
RestartSec=10

# Logging
StandardOutput=append:/home/botuser/bots/keltner/logs/stdout.log
StandardError=append:/home/botuser/bots/keltner/logs/stderr.log

[Install]
WantedBy=multi-user.target
```

---

## Enable and Start

```bash
# Create log directory
mkdir -p ~/bots/keltner/logs

# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable keltner-bot

# Start service
sudo systemctl start keltner-bot

# Check status
sudo systemctl status keltner-bot

# View logs
sudo journalctl -u keltner-bot -f
```

---

## Service Commands

```bash
# Stop
sudo systemctl stop keltner-bot

# Restart
sudo systemctl restart keltner-bot

# Disable
sudo systemctl disable keltner-bot
```

---

## Log Management

### Logrotate

Prevent logs from filling disk:

```bash
sudo nano /etc/logrotate.d/keltner-bot
```

```
/home/botuser/bots/keltner/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 640 botuser botuser
}
```

### View Logs

```bash
# Real-time logs
tail -f ~/bots/keltner/logs/stdout.log

# Last 100 lines
tail -100 ~/bots/keltner/bot_keltner_*.log

# Search for errors
grep -i error ~/bots/keltner/logs/*.log
```

---

## See Also

- [VPS_SETUP.md](VPS_SETUP.md) - Initial server setup
- [PRODUCTION_OPS.md](PRODUCTION_OPS.md) - Monitoring, security, backup
- [../DEPLOYMENT.md](../DEPLOYMENT.md) - Deployment overview
