# Apex Trader Funding Rules

Compliance guidelines for automated trading on Apex Trader Funding accounts.

---

## Overview

Apex Trader Funding allows automated trading with specific requirements around **active management**. This guide ensures your bot complies with their rules.

---

## Allowed Practices

| Practice | Status | Notes |
|----------|--------|-------|
| Automated bots with active management | ✅ Allowed | Must monitor regularly |
| DCA (Dollar Cost Averaging) bots | ✅ Allowed | |
| Indicator-based strategies | ✅ Allowed | |
| TradersPost integration | ✅ Allowed | Official partner |
| PickMyTrade integration | ✅ Allowed | |
| NinjaTrader automated strategies | ✅ Allowed | |
| Multiple strategies per account | ✅ Allowed | Within position limits |

---

## Prohibited Practices

| Practice | Status | Risk |
|----------|--------|------|
| "Set and forget" autonomous bots | ❌ Prohibited | Account termination |
| High-frequency trading (HFT) | ❌ Scrutiny | May flag account |
| Stealth mode / unauthorized accounts | ❌ Prohibited | Immediate ban |
| Erratic/unpredictable position sizing | ❌ Prohibited | Account review |
| Third-party account trading | ❌ Prohibited | Account termination |
| Sharing account access | ❌ Prohibited | Account termination |

---

## Active Management Requirement

**Key Rule:** You must actively manage and monitor your automated system.

### What "Active Management" Means

✅ **Acceptable:**
- Check bot status multiple times per day
- Review daily P&L and trade log
- Adjust parameters based on market conditions
- Stop bot during major news events
- Manually intervene when necessary

❌ **Not Acceptable:**
- Deploy and ignore for days/weeks
- No monitoring of positions
- No intervention during unusual behavior
- Running without understanding the strategy

### Implementation

1. **Daily Review Checklist:**
   - [ ] Check bot is running
   - [ ] Review overnight trades
   - [ ] Verify daily P&L within limits
   - [ ] Check for any errors/anomalies
   - [ ] Confirm market conditions suitable

2. **Weekly Tasks:**
   - [ ] Compare performance to backtest
   - [ ] Review win rate and profit factor
   - [ ] Adjust parameters if needed
   - [ ] Check for contract roll dates

---

## Position Limits

### Evaluation Accounts

| Account Size | Max Contracts | Max Position |
|--------------|---------------|--------------|
| $25,000 | 3 MNQ | 3 contracts |
| $50,000 | 10 MNQ / 1 NQ | 10 MNQ or 1 NQ |
| $100,000 | 20 MNQ / 2 NQ | 20 MNQ or 2 NQ |
| $150,000 | 30 MNQ / 3 NQ | 30 MNQ or 3 NQ |
| $250,000 | 50 MNQ / 5 NQ | 50 MNQ or 5 NQ |
| $300,000 | 60 MNQ / 6 NQ | 60 MNQ or 6 NQ |

### PA (Performance) Accounts

Similar limits to evaluation, but:
- No trailing drawdown (static drawdown)
- Daily loss limit remains
- Payout eligibility after minimum trading days

---

## Drawdown Rules

### Trailing Drawdown (Evaluation)

- Starts at account start balance
- Trails up as account grows
- Locks when it reaches starting balance
- **Example:** $50K account, $3K trailing → Locks at $50K when balance hits $53K

### Static Drawdown (PA Accounts)

- Fixed drawdown from starting balance
- Does not trail
- Easier to manage with automated systems

---

## News Trading

### Restricted Events

Apex may restrict trading during:
- FOMC announcements
- Non-Farm Payrolls (NFP)
- CPI releases
- Major geopolitical events

### Bot Configuration

Add news filter to avoid these times:

```python
# Major news events to avoid (add to config)
NEWS_BLACKOUT_TIMES = [
    # FOMC - typically 2:00 PM ET
    # NFP - first Friday 8:30 AM ET
    # CPI - monthly 8:30 AM ET
]

def check_news_blackout(current_time):
    # Skip trading 30 min before/after major news
    for event_time in NEWS_BLACKOUT_TIMES:
        if abs(current_time - event_time) < timedelta(minutes=30):
            return True
    return False
```

---

## Daily Loss Limit

### Apex Rule

- Maximum daily loss varies by account size
- Bot should enforce this before Apex does
- Better to stop early than get flagged

### Bot Implementation

Already included in RiskManager:

```python
# config.py
daily_max_loss: float = 500.0  # Conservative limit

# risk_manager.py
if daily_pnl <= -daily_max_loss:
    daily_stopped = True
    # Exit positions and stop trading
```

---

## Trading Hours

### Recommended Hours

| Session | ET Hours | Bot Activity |
|---------|----------|--------------|
| Pre-market | 6:00-9:30 | Optional |
| Regular | 9:30-16:00 | Primary |
| After-hours | 16:00-18:00 | Reduced |
| Overnight | 18:00-6:00 | Minimal |

### Default allowed_hours

```python
allowed_hours = {9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20}
```

Excludes:
- Pre-market (low volume)
- 17:00 (market close, spread widening)
- Late night (thin markets)

---

## Account Health Monitoring

### Daily Metrics to Track

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Daily P&L | > $0 | -$250 | < -$400 |
| Win Rate | > 75% | 60-75% | < 60% |
| Drawdown | < 50% of max | 50-75% | > 75% |
| Trade Count | 1-10/day | 10-20 | > 20 |

### Automated Alerts

```python
def check_account_health():
    stats = risk_manager.get_stats()

    if stats["daily_pnl"] < -400:
        send_alert("WARNING: Near daily loss limit")

    if stats["total_trades"] > 15:
        send_alert("WARNING: High trade count today")

    if stats["max_drawdown"] > 1500:
        send_alert("CRITICAL: High drawdown")
```

---

## Best Practices

### 1. Start Conservative

- Use smaller position sizes than backtested
- Set tighter daily loss limits
- Run in paper mode first

### 2. Document Everything

- Keep trade logs
- Record parameter changes
- Note market conditions

### 3. Regular Review

- Daily P&L review
- Weekly performance analysis
- Monthly strategy review

### 4. Have Kill Switch

- Manual stop button/command
- Auto-stop on critical errors
- Emergency flatten all positions

### 5. Communication

- Respond to Apex inquiries promptly
- Be transparent about automation use
- Report technical issues

---

## Payout Considerations

### Evaluation to PA

1. Meet profit target
2. Trade minimum days
3. Pass consistency rule (if applicable)
4. No rule violations

### PA Payouts

- Request payout after minimum trading days
- 100% of first $25K profit
- 90% of profits after $25K
- Process time: 1-3 business days

### Bot Impact on Payouts

- Consistent profits look better
- Avoid "home run" trades (suspicious)
- Gradual account growth preferred
- Document strategy for review

---

## Red Flags to Avoid

| Behavior | Why It's Flagged |
|----------|------------------|
| Perfect profit every day | Looks like manipulation |
| Same profit target hit exactly | Suspicious pattern |
| Trading only news events | May indicate gambling |
| Rapid position flipping | HFT-like behavior |
| Huge positions on one trade | Irresponsible risk |

---

## Quick Compliance Checklist

- [ ] Bot has daily max loss limit
- [ ] Position size within account limits
- [ ] Session hours configured appropriately
- [ ] News events avoided
- [ ] Daily monitoring plan in place
- [ ] Emergency stop procedure documented
- [ ] Trade logs being kept
- [ ] No prohibited practices

---

## Resources

- [Apex Official Rules](https://apextraderfunding.com/faq)
- [Apex Automated Trading FAQ](https://www.quantvps.com/blog/apex-trader-funding-automated-trading-bots)
- [TradersPost Apex Integration](https://traderspost.io/connections/apex-trader-funding)
