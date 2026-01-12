# Apex Account Configuration

Apex Trader Funding account modes and presets.

---

## Account Mode

| Parameter | Type | Default | Options | Description |
|-----------|------|---------|---------|-------------|
| `account_mode` | str | "eval" | "eval", "pa" | Operating mode for Apex Trader Funding |
| `account_size` | str | "50K" | "25K", "50K", "75K", "100K", "150K", "250K", "300K", "100K_STATIC" | Account size preset |
| `balance` | float | Auto | - | Starting balance (auto-loaded from preset) |
| `profit_target` | float | Auto | - | Profit target in $ (eval mode only, auto-loaded) |
| `trailing_dd` | float | Auto | - | Trailing/static drawdown amount (auto-loaded) |
| `max_contracts` | int | Auto | - | Maximum contracts allowed (auto-loaded) |
| `initial_contracts` | int | Auto | - | Starting contracts for eval mode (auto-loaded) |
| `risk_pct` | float | 0.02 | 0.01-0.03 | Risk % per trade for PA mode (e.g., 0.02 = 2%) |

**Account Mode Details:**
- **eval**: Evaluation account - fixed contracts, profit target, trailing drawdown
- **pa**: Performance account - risk-based sizing, static drawdown, no target

**Example:**
```python
# Eval Mode (50K account)
account_mode: str = "eval"
account_size: str = "50K"
# Auto-loaded: balance=50000, profit_target=3000, trailing_dd=2500, initial_contracts=5

# PA Mode (50K account)
account_mode: str = "pa"
account_size: str = "50K"
risk_pct: float = 0.02  # 2% risk per trade
# Auto-loaded: balance=50000, trailing_dd=2500 (used as static DD), max_contracts=10
```

See [docs/EVAL_VS_PA.md](eval-vs-pa.md) for detailed explanation.

---

## Account Size Presets

| Size | Balance | Profit Target | Trailing DD | Initial Contracts | Max Contracts |
|------|---------|---------------|-------------|-------------------|---------------|
| 25K | $25,000 | $1,500 | $1,500 | 2 | 4 |
| 50K | $50,000 | $3,000 | $2,500 | 5 | 10 |
| 75K | $75,000 | $4,000 | $2,750 | 6 | 12 |
| 100K | $100,000 | $6,000 | $3,000 | 7 | 14 |
| 150K | $150,000 | $8,000 | $5,000 | 8 | 17 |
| 250K | $250,000 | $12,500 | $6,500 | 13 | 27 |
| 300K | $300,000 | $15,000 | $7,500 | 17 | 35 |

**Special Preset:**
| Size | Balance | Profit Target | DD | Contracts | Notes |
|------|---------|---------------|-----|-----------|-------|
| 100K_STATIC | $100,000 | $2,000 | $625 (static) | 2 (fixed) | Special static eval |

---

## See Also

- [docs/EVAL_VS_PA.md](eval-vs-pa.md) - Detailed mode comparison
- [docs/apex-eval-mode.md](../docs/apex-eval-mode.md) - Eval account rules
- [docs/apex-pa-mode.md](../docs/apex-pa-mode.md) - PA account rules
- [docs/APEX_RULES.md](apex-compliance.md) - Apex compliance guidelines
