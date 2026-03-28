---
name: troubleshoot
description: >-
  Deep diagnosis of why the trading bot isn't working, trading, or behaving
  as expected. Use when the user says "troubleshoot", "diagnose", "why isn't
  it trading", "what's wrong with the bot", "bot not working", "debug the
  bot", "investigate", "what happened today", "why did it stop", "check the
  logs", "bot issues", "something's off", or any indication the bot is
  misbehaving and needs investigation. Goes deeper than /bot-status — SSHs
  to the Pi, tails Docker logs, checks multiple API endpoints, analyzes
  signals, and provides a root-cause narrative. Use /bot-status for quick
  checks; use /troubleshoot when something is actually wrong.
---

# Troubleshoot — Deep Bot Diagnosis

Systematic investigation when the bot is misbehaving. Follows a layered approach: connectivity first, then state, then signals, then logs.

## Diagnostic sequence

### Layer 1: Is the bot reachable?

```bash
# Can we reach the Pi?
ping -c 1 raspberrypi.local

# Is the container running?
ssh pi@raspberrypi.local "cd /home/pi/keltner-bot && docker compose ps"

# Basic health
curl -sk https://raspberrypi.local:8080/api/health | python3 -m json.tool
```

If the container is down, check why:

```bash
ssh pi@raspberrypi.local "cd /home/pi/keltner-bot && docker compose logs --tail 50"
```

### Layer 2: What state is the bot in?

```bash
# Position and P&L
curl -sk https://raspberrypi.local:8080/api/status | python3 -m json.tool

# Is trading enabled?
curl -sk https://raspberrypi.local:8080/api/trading | python3 -m json.tool

# Active alerts
curl -sk https://raspberrypi.local:8080/api/alerts | python3 -m json.tool

# Reconciliation status
curl -sk https://raspberrypi.local:8080/api/reconciliation | python3 -m json.tool
```

### Layer 3: Why isn't it entering trades?

```bash
# Signal readiness and indicator values
curl -sk https://raspberrypi.local:8080/api/signals/current | python3 -m json.tool

# Current market data
curl -sk https://raspberrypi.local:8080/api/quotes | python3 -m json.tool
```

Interpret the readiness field:

| State | Problem? | Meaning |
|-------|----------|---------|
| READY | No | Waiting for signal |
| NO_SIGNAL | No | No entry signal on current bar |
| BLOCKED_COOLDOWN | No | Normal cooldown between bars |
| WAITING | No | Waiting for bar close |
| IN_POSITION | No | Currently in a trade |
| BLOCKED_BY_FILTER | Yes | Trend filter blocking — check ADX/Vortex values |
| BLOCKED_DAILY_STOP | Yes | Daily loss limit hit — resets at 6 PM ET |
| BLOCKED_DAILY_PROFIT | Yes | Profit target hit — check if intentional |

### Layer 4: What do the logs say?

```bash
# Recent logs (look for errors, warnings, connection issues)
ssh pi@raspberrypi.local "cd /home/pi/keltner-bot && docker compose logs --tail 200" 2>&1 | head -200

# Search for specific patterns
ssh pi@raspberrypi.local "cd /home/pi/keltner-bot && docker compose logs --tail 500" 2>&1 | grep -i "error\|exception\|traceback\|DRIFT\|reconnect\|stale"
```

### Layer 5: System health

```bash
# Pi system stats
ssh pi@raspberrypi.local "uptime && free -h"

# Docker resource usage
ssh pi@raspberrypi.local "docker stats keltner-bot --no-stream"

# Disk space
ssh pi@raspberrypi.local "df -h /"
```

## Provide a narrative summary

After collecting all data, synthesize findings into a clear narrative:

1. **Current state**: Is the bot running? In a position? What's the daily P&L?
2. **Root cause**: Why isn't it doing what the user expects?
3. **Recommendation**: What action to take (if any)

Be specific — "the Vortex filter is blocking entries because VI+ (1.05) < VI- (1.12), meaning the trend is bearish" is better than "the filter is blocking."

## Common root causes

| Symptom | Likely cause |
|---------|-------------|
| No trades all day | Daily loss limit hit early, or trend filter blocking |
| Stuck in position | Stop loss not triggering — check WebSocket connection |
| Repeated entries | Position reconciliation drift — check reconciliation log |
| Container restarting | OOM or crash — check `docker compose logs` for tracebacks |
| "Not trading" during market hours | WebSocket disconnected — check health endpoint |
