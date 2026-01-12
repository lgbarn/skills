# VPS Setup Guide

Server setup, Python installation, and bot deployment.

---

## VPS Selection

**Recommended:** DigitalOcean or Vultr VPS for reliability and low latency.

**DigitalOcean:**
1. Create Droplet
2. Choose: Ubuntu 22.04, Basic, $6/mo (1 GB RAM)
3. Select region close to Tradovate servers (Chicago preferred)
4. Add SSH key

**Vultr:**
1. Deploy new instance
2. Choose: Ubuntu 22.04, Cloud Compute, $6/mo
3. Select Chicago location

---

## Initial Server Setup

```bash
# Connect to VPS
ssh root@your_server_ip

# Update system
apt update && apt upgrade -y

# Create non-root user
adduser botuser
usermod -aG sudo botuser

# Setup firewall
ufw allow OpenSSH
ufw enable

# Switch to new user
su - botuser
```

---

## Install Python

```bash
# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Verify
python3.11 --version
```

---

## Install Bot

```bash
# Create directory
mkdir -p ~/bots/keltner
cd ~/bots/keltner

# Copy files from local machine (run on your local machine)
scp -r Python/bots/keltner/* botuser@your_server_ip:~/bots/keltner/

# On VPS: Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Configure Environment

```bash
# Create .env file
cp .env.example .env
nano .env

# Add your credentials
# IMPORTANT: Never expose these
```

---

## Test Run

```bash
# Activate venv
source venv/bin/activate

# Run in paper mode
python bot_keltner.py --paper
```

---

## See Also

- [SYSTEMD_SERVICE.md](SYSTEMD_SERVICE.md) - Run bot as system service
- [PRODUCTION_OPS.md](PRODUCTION_OPS.md) - Monitoring, security, backup
- [../DEPLOYMENT.md](../DEPLOYMENT.md) - Deployment overview
