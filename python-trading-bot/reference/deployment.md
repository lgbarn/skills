# Deployment Guide

Production deployment for Python trading bots.

---

## Deployment Options

| Option | Pros | Cons | Cost |
|--------|------|------|------|
| **VPS** | Full control, low latency | Requires maintenance | $5-20/mo |
| **Home Server** | Free, full control | Internet dependent, power issues | $0 |
| **Cloud (AWS/GCP)** | Reliable, scalable | Complex, variable cost | $10-50/mo |
| **Raspberry Pi** | Cheap, low power | Limited resources | $50 one-time |

**Recommended:** DigitalOcean or Vultr VPS for reliability and low latency.

---

## Deployment Phases

### **[1. VPS Setup](deployment-vps.md)**
Initial server configuration:
- VPS selection and creation
- Server hardening (non-root user, firewall)
- Python 3.11 installation
- Bot installation and testing

### **[2. Systemd Service](deployment-systemd.md)**
Run bot as system service:
- Service file creation
- Enable auto-start on boot
- Log management with logrotate
- Service control commands

### **[3. Production Operations](deployment-production.md)**
Ongoing operations:
- Health monitoring and alerts
- Security hardening (SSH, firewall)
- Backup procedures
- Switching to live trading
- Troubleshooting common issues

---

## Quick Reference

| Task | Command |
|------|---------|
| Start bot | `sudo systemctl start keltner-bot` |
| Stop bot | `sudo systemctl stop keltner-bot` |
| Restart bot | `sudo systemctl restart keltner-bot` |
| View status | `sudo systemctl status keltner-bot` |
| View logs | `tail -f ~/bots/keltner/logs/stdout.log` |
| Edit config | `nano ~/bots/keltner/.env` |
| Update code | `cd ~/bots/keltner && git pull` |

---

## See Also

- [SETUP.md](setup.md) - Initial bot setup and configuration
- [ARCHITECTURE.md](architecture.md) - Bot architecture overview
- [config-index.md](config-index.md) - Configuration reference
