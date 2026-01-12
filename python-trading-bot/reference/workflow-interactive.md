# Bot Builder Interactive Workflow

This document defines the interactive workflow for bot creation and refactoring. The skill guides users through configuration and modification step-by-step.

**Creation:** Generate new bots from scratch with 7-step guided workflow
**Refactoring:** Modify existing bots (add/remove features, change indicators, migrate eval→PA)

---

## Contents

- [Workflow Diagram (Bot Creation)](#workflow-diagram-bot-creation)
- [Step 1: Signal Selection](#step-1-signal-selection)
- [Step 2: Signal Parameters](#step-2-signal-parameters)
- [Step 3: Account Mode (Eval vs PA)](#step-3-account-mode-eval-vs-pa)
- [Step 4: Risk Settings](#step-4-risk-settings)
- [Step 5: Exit Strategy](#step-5-exit-strategy)
- [Step 6: API Credentials Guidance](#step-6-api-credentials-guidance)
- [Step 7: Generate Bot](#step-7-generate-bot)
- [Quick Mode](#quick-mode)
- [Direct Signal Commands](#direct-signal-commands)
- [Handling User Responses](#handling-user-responses)
- [Error Handling](#error-handling)
- [Configuration Object](#configuration-object)
- [Refactoring Commands](#refactoring-commands)

---

## Workflow Diagram (Bot Creation)

```
┌──────────────────────────────────────────────────────────────────┐
│  STEP 1: Signal Selection                                         │
│  "Which entry signal would you like to use?"                      │
└──────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 2: Signal Parameters                                        │
│  "Configure [signal] parameters:"                                 │
└──────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 3: Account Mode (Eval vs PA)                                │
│  "Is this for evaluation or funded (PA) trading?"                 │
└──────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 4: Risk Settings                                            │
│  "Risk management configuration:"                                 │
│  (Eval: fixed contracts + profit target)                          │
│  (PA: risk % + dynamic sizing)                                    │
└──────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 5: Exit Strategy                                            │
│  "Exit settings (ATR-based):"                                     │
└──────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 6: API Credentials Guidance                                 │
│  "Configure your API credentials:"                                │
└──────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 7: Generate Bot                                             │
│  [Generate all files and display summary]                         │
└──────────────────────────────────────────────────────────────────┘
```

---

## Step 1: Signal Selection

**Question:**
```
Which entry signal would you like to use for your bot?

| # | Signal | Description | PF | Win% |
|---|--------|-------------|-----|------|
| 1 | keltner | Keltner Channel breakout | 10.04 | 87.8% |
| 2 | ema_cross | EMA crossover with separation | 6.23 | 82.7% |
| 3 | vwap | Rolling VWAP band breakout (1σ) | 5.20 | 85.3% |
| 4 | supertrend | SuperTrend direction flip | 4.41 | 82.5% |
| 5 | alligator | Williams Alligator alignment | 4.16 | 83.5% |

Enter signal name or number (default: keltner):
```

**Options:**
- Header: "Signal"
- Choices: Top 5 signals only
- Default: `keltner` (best profit factor)

---

## Step 2: Signal Parameters

**Dynamic based on selected signal.** Show signal-specific parameters with defaults and optimal values.

### Keltner
```
Configure Keltner Channel parameters:

| Parameter | Default | Optimal | Description |
|-----------|---------|---------|-------------|
| EMA Period | 20 | 20 | Middle line EMA period |
| ATR Period | 14 | 14 | ATR calculation period |
| ATR Multiplier | 1.5 | 2.75 | Band width (wider = fewer signals) |

Use optimal settings? [Y/n]:
```

### EMA Cross
```
Configure EMA Crossover parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| Fast EMA | 3 | Fast EMA period (Linda Raschke) |
| Slow EMA | 8 | Slow EMA period (Linda Raschke) |
| Separation Min | 0.35 | Min points between EMAs |
| Separation Filter | true | Enable separation filter |

Use default settings? [Y/n]:
```

### VWAP
```
Configure Rolling VWAP parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| Window | 720 | Rolling window in bars (720 = 24h at 2-min) |
| Band Multiplier | 1.0 | Standard deviation multiplier |

Use default settings? [Y/n]:
```

### SuperTrend
```
Configure SuperTrend parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| Period | 10 | ATR period for SuperTrend |
| Multiplier | 3.0 | ATR multiplier for bands |

Use default settings? [Y/n]:
```

### Alligator
```
Configure Williams Alligator parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| Jaw Period | 13 | Jaw SMMA period |
| Jaw Offset | 8 | Jaw offset |
| Teeth Period | 8 | Teeth SMMA period |
| Teeth Offset | 5 | Teeth offset |
| Lips Period | 5 | Lips SMMA period |
| Lips Offset | 3 | Lips offset |

Use default settings? [Y/n]:
```

---

## Step 3: Account Mode (Eval vs PA)

**Question:**
```
Account Configuration:

Is this bot for evaluation trading or funded (PA) trading?

┌─────────────────────────────────────────────────────────────┐
│  EVAL (Evaluation Account)                                  │
│  ├─ Objective: Hit profit target to pass evaluation         │
│  ├─ Drawdown: Trailing (moves up with equity)               │
│  ├─ Position Sizing: Fixed contracts                        │
│  ├─ Auto-Stop: When profit target reached                   │
│  └─ Best For: Passing prop firm evaluations                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  PA (Performance Account / Funded)                          │
│  ├─ Objective: Consistent profitability                     │
│  ├─ Drawdown: Static (fixed from starting balance)          │
│  ├─ Position Sizing: Risk-based % of equity (dynamic)       │
│  ├─ Auto-Stop: None (trade indefinitely)                    │
│  └─ Best For: Trading funded accounts                       │
└─────────────────────────────────────────────────────────────┘

Select mode: [1] Eval  [2] PA  (default: Eval):
```

### If Eval Mode Selected

```
Evaluation Account Size:
  [1] 25K  ($1,500 profit target, $1,000 DD)
  [2] 50K  ($3,000 profit target, $2,500 DD)  (default)
  [3] 100K ($6,000 profit target, $5,000 DD)
  [4] 150K ($9,000 profit target, $7,500 DD)

Select account size [1-4] (default: 2):
```

**Configuration Set:**
```python
account_mode: "eval"
account_size: "50K"
profit_target: 3000.0  # Auto-calculated
trailing_dd: 2500.0    # Auto-calculated
contracts: <will be set in Step 4>
```

### If PA Mode Selected

```
PA Account Size:
  [1] 25K  (static DD: $1,000)
  [2] 50K  (static DD: $2,500)  (default)
  [3] 100K (static DD: $5,000)
  [4] 150K (static DD: $7,500)

Select account size [1-4] (default: 2):

Risk Per Trade (%):
Enter risk percentage (0.5-2.5%, default: 1.5%):
```

**Configuration Set:**
```python
account_mode: "pa"
account_size: "50K"
risk_pct: 0.015        # 1.5% of equity per trade
static_dd: 2500.0      # Auto-calculated
# Position sizing will be dynamic based on risk_pct and ATR
```

**Options:**
- Header: "Account Mode"
- Default: `mode=eval, account_size=50K`
- Eval: Sets profit_target and trailing_dd
- PA: Sets risk_pct and static_dd

---

## Step 4: Risk Settings

**Context:** Configuration differs based on account mode (from Step 3)

### If Eval Mode (Fixed Position Sizing)

**Question:**
```
Risk Management Configuration:

| Setting | Default | Description |
|---------|---------|-------------|
| Contracts | 2 | Number of contracts per trade |
| Daily Max Loss | $500 | Stop trading for day if loss exceeds |
| Slippage Ticks | 1 | Assumed slippage per side (1 tick = 0.25 pts) |
| Commission RT | $4.00 | Round-trip commission per contract |

ADX Filter:
| Setting | Default | Options | Description |
|---------|---------|---------|-------------|
| Enable | true | true/false | Use ADX filter for entries |
| Threshold | 35 | 10-50 | Minimum ADX for entry |
| Mode | di_rising | see below | Filter logic |
| Period | 14 | 5-30 | ADX calculation period |

ADX Modes:
- traditional: ADX > threshold only
- di_aligned: + DI aligned with direction
- di_rising: Dominant DI is rising (RECOMMENDED)
- adx_rising: ADX itself is rising
- combined: All conditions

Use recommended settings? [Y/n]:
```

**Options:**
- Header: "Risk (Eval Mode)"
- Default: `contracts=2, daily_max_loss=500, adx_mode=di_rising`

### If PA Mode (Dynamic Position Sizing)

**Question:**
```
Risk Management Configuration:

Position Sizing: DYNAMIC (risk-based)
- Contracts calculated per trade based on:
  * Account equity (grows with profit)
  * Risk percentage (from Step 3)
  * Current ATR
  * Stop loss distance

Example for 50K PA with 1.5% risk:
  Equity: $53,000  Risk: $795  ATR: 10pts  SL: 3.0×ATR
  → Contracts = $795 / (30pts × $20) = 1.32 → 1 contract

| Setting | Default | Description |
|---------|---------|-------------|
| Daily Max Loss | $500 | Stop trading for day if loss exceeds |
| Slippage Ticks | 1 | Assumed slippage per side (1 tick = 0.25 pts) |
| Commission RT | $4.00 | Round-trip commission per contract |

ADX Filter:
| Setting | Default | Options | Description |
|---------|---------|---------|-------------|
| Enable | true | true/false | Use ADX filter for entries |
| Threshold | 35 | 10-50 | Minimum ADX for entry |
| Mode | di_rising | see below | Filter logic |
| Period | 14 | 5-30 | ADX calculation period |

ADX Modes:
- traditional: ADX > threshold only
- di_aligned: + DI aligned with direction
- di_rising: Dominant DI is rising (RECOMMENDED)
- adx_rising: ADX itself is rising
- combined: All conditions

Use recommended settings? [Y/n]:
```

**Options:**
- Header: "Risk (PA Mode)"
- Default: `daily_max_loss=500, adx_mode=di_rising`
- Note: Contracts dynamically calculated per trade

---

## Step 5: Exit Strategy

**Question:**
```
Exit Settings (ATR-based):

| Setting | Default | Description |
|---------|---------|-------------|
| ATR Period | 14 | ATR calculation period |
| Stop Loss | 3.0× ATR | Distance from entry |
| Take Profit | 3.0× ATR | Distance from entry |

Trailing Stop:
| Setting | Default | Description |
|---------|---------|-------------|
| Enable Trailing | true | Use trailing stops |
| Trigger | 0.15× ATR | Profit to activate trail |
| Distance | 0.15× ATR | Trail distance from high/low |

Re-entry:
| Setting | Default | Description |
|---------|---------|-------------|
| Enable Re-entry | true | Allow trend continuation re-entries |
| Wait Bars | 3 | Bars to wait after exit |
| ADX Min | 40 | Higher ADX required for re-entry |
| Max Re-entries | 10 | Per trend direction |

Use default exit settings? [Y/n]:
```

**Options:**
- Header: "Exits"
- Default: `sl=3.0, tp=3.0, trail=true, trigger=0.15, distance=0.15`

---

## Step 6: API Credentials Guidance

**Information (not a question):**
```
API Credentials Setup:

┌─────────────────────────────────────────────────────────────┐
│  DATABENTO                                                   │
│  1. Sign up at databento.com                                 │
│  2. Get API key from dashboard                               │
│  3. Subscribe to GLBX-MDP3 dataset (CME futures)             │
│  4. Save API key for .env file                               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  TRADOVATE (Optional - for execution only)                   │
│  1. Log into Tradovate                                       │
│  2. Go to Settings → API Key                                 │
│  3. Generate a new API key                                   │
│  4. Save: username, password, cid, secret                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  TRADERSPOST                                                 │
│  1. Create account at traderspost.io                         │
│  2. Create a new strategy                                    │
│  3. Get webhook URL:                                         │
│     https://webhooks.traderspost.io/trading/webhook/{uuid}/{password}
│  4. Connect to your Tradovate/Apex account                   │
└─────────────────────────────────────────────────────────────┘

These credentials go in your .env file (never commit to git!).

Press Enter to continue...
```

---

## Step 7: Generate Bot

**Summary and Generation:**
```
Bot Configuration Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Signal:        Keltner Channel Breakout
Parameters:    EMA=20, ATR=14, Mult=2.75
Account:       Eval - 50K ($3,000 target, $2,500 DD)
Risk:          2 contracts (fixed), $500 daily max loss
ADX Filter:    Enabled (threshold=35, mode=di_rising)
Exits:         SL=3.0×ATR, TP=3.0×ATR, Trailing=0.15×ATR
Re-entry:      Enabled (wait=3 bars, ADX>40, max=10)

Generating bot files...

✓ Created: Python/bots/keltner/bot_keltner.py
✓ Created: Python/bots/keltner/config.py
✓ Created: Python/bots/keltner/tradovate_client.py
✓ Created: Python/bots/keltner/traderspost_client.py
✓ Created: Python/bots/keltner/risk_manager.py
✓ Created: Python/bots/keltner/indicators.py
✓ Created: Python/bots/keltner/requirements.txt
✓ Created: Python/bots/keltner/.env.example
✓ Created: Python/bots/keltner/.gitignore
✓ Created: Python/bots/keltner/README.md

Bot generated successfully!

Next steps:
1. cd Python/bots/keltner
2. cp .env.example .env
3. Edit .env with your API credentials
4. pip install -r requirements.txt
5. python bot_keltner.py --paper  # Test in paper mode first!
```

---

## Quick Mode

For experienced users, support quick mode that uses all defaults:

```
/bot:new keltner --quick
```

This skips all prompts and uses:
- Signal's optimal parameters
- ADX: threshold=35, mode=di_rising
- Exits: SL=3.0, TP=3.0, trail=0.15
- Re-entry: enabled, wait=3, adx_min=40, max=10

---

## Direct Signal Commands

Skip signal selection with direct commands:

```
/bot:keltner     # Keltner Channel bot
/bot:ema         # EMA Cross bot
/bot:vwap        # Rolling VWAP bot
/bot:supertrend  # SuperTrend bot
/bot:alligator   # Williams Alligator bot
```

---

## Handling User Responses

### Accept Defaults
User can type:
- `Y`, `y`, `yes`, `Enter` (empty) = Accept defaults
- `N`, `n`, `no` = Customize

### Specify Values
User can provide values inline:
```
EMA Period: 25
ATR Multiplier: 2.5
```

### Skip Steps
User can skip ahead:
```
skip to generate
```

---

## Error Handling

### Invalid Signal
```
"xyz" is not a valid signal.

Available signals: keltner, ema_cross, vwap, supertrend, alligator

Enter signal name:
```

### Invalid Value
```
ATR Multiplier must be between 0.5 and 5.0.
Enter ATR Multiplier (default: 2.75):
```

---

## Configuration Object

After collecting all inputs, build a configuration object:

```json
{
  "signal": "keltner",
  "signal_params": {
    "keltner_ema_period": 20,
    "keltner_atr_period": 14,
    "keltner_atr_mult": 2.75
  },
  "account": {
    "mode": "eval",
    "account_size": "50K",
    "profit_target": 3000.0,
    "trailing_dd": 2500.0,
    "static_dd": null,
    "risk_pct": null
  },
  "risk": {
    "contracts": 2,
    "daily_max_loss": 500.0,
    "slippage_ticks": 1,
    "commission_rt": 4.00,
    "point_value": 20.0
  },
  "adx": {
    "enabled": true,
    "threshold": 35,
    "mode": "di_rising",
    "period": 14
  },
  "exits": {
    "atr_period": 14,
    "sl_atr_mult": 3.0,
    "tp_atr_mult": 3.0,
    "trail_enabled": true,
    "trail_trigger_atr": 0.15,
    "trail_distance_atr": 0.15
  },
  "reentry": {
    "enabled": true,
    "bars_wait": 3,
    "adx_min": 40,
    "max_reentries": 10
  },
  "filters": {
    "volume_filter": true,
    "volume_ma_period": 20,
    "session_filter": true,
    "allowed_hours": [9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20]
  },
  "production": {
    "persistence_enabled": false,
    "news_filter_enabled": false,
    "alert_email_enabled": false,
    "alert_pushover_enabled": false
  }
}
```

**PA Mode Example:**
```json
{
  "account": {
    "mode": "pa",
    "account_size": "50K",
    "profit_target": null,
    "trailing_dd": null,
    "static_dd": 2500.0,
    "risk_pct": 0.015
  },
  "risk": {
    "contracts": null,  // Dynamic - calculated per trade
    "daily_max_loss": 500.0,
    "slippage_ticks": 1,
    "commission_rt": 4.00,
    "point_value": 20.0
  }
}
```

This object is used to generate the bot code with proper parameter values.

---

## Refactoring Commands

After bot creation, you can modify existing bots using refactoring commands.

### /bot:refactor <bot_name>

Start interactive refactoring session for an existing bot.

**Example:**
```
/bot:refactor keltner
```

**Workflow:**
1. Reads all bot files (bot_*.py, config.py, indicators.py, etc.)
2. Asks: "What would you like to change?"
3. Presents options:
   - Add feature (news filter, alerting, new indicator)
   - Remove feature (re-entry, volume filter, etc.)
   - Change indicator (Keltner→Bollinger, EMA→SMA)
   - Update parameters
   - Migrate eval→PA mode
4. Makes changes to necessary files
5. Updates tests if they exist
6. Suggests CSV backtest to validate

See [REFACTOR.md](REFACTOR.md) for detailed workflows.

---

### /bot:add-feature <bot_name> <feature>

Add specific feature to existing bot.

**Examples:**
```
/bot:add-feature keltner news_filter
/bot:add-feature ema_cross alerting
/bot:add-feature vwap persistence
```

**Supported Features:**
- `news_filter` - Economic calendar integration
- `alerting` - Email + SMS notifications
- `persistence` - SQLite state management
- `volume_filter` - Volume-based entry filter
- `adx_filter` - ADX trend filter
- Custom indicator (specify name)

See [workflow-add-feature.md](workflow-add-feature.md) for details.

---

### /bot:remove-feature <bot_name> <feature>

Remove feature cleanly from existing bot.

**Examples:**
```
/bot:remove-feature keltner reentry
/bot:remove-feature supertrend volume_filter
/bot:remove-feature alligator trailing_stop
```

See [workflow-remove-feature.md](workflow-remove-feature.md) for details.

---

### /bot:migrate-pa <bot_name>

Convert evaluation bot to PA (funded) mode.

**Example:**
```
/bot:migrate-pa keltner
```

**What it does:**
1. Validates bot passed evaluation (profit target reached)
2. Changes `account_mode: eval` → `account_mode: pa`
3. Adds `risk_pct` parameter (1.5% default)
4. Removes fixed `contracts` (now dynamic)
5. Updates drawdown mode (trailing → static)
6. Removes profit target checks
7. Updates documentation and tests

**Prerequisites:**
- Profit target reached in eval mode
- Apex confirmed PA conversion
- Bot not currently running
- Backup created

See [workflow-migrate-eval-pa.md](workflow-migrate-eval-pa.md) for detailed workflow.

---

### /bot:analyze <bot_name>

Analyze bot code quality and suggest improvements.

**Example:**
```
/bot:analyze keltner
```

**Checks:**
- Code structure and organization
- Indicator calculations (accuracy, efficiency)
- Risk management implementation
- State persistence correctness
- Test coverage
- Documentation completeness
- Potential bugs or edge cases

**Output:**
- Code quality score
- List of suggested improvements
- Optional: Auto-fix common issues

---

## Custom Strategy Workflow

Build bots with custom trading strategies not covered by pre-built signals.

### /bot:custom

Start custom strategy builder.

**Example:**
```
/bot:custom
```

**Interactive Workflow:**

**Step 1:** Describe your strategy
```
Describe your trading strategy (entry/exit logic):
Example: "Enter long when price crosses above 21 EMA and RSI > 50,
exit when price crosses below 21 EMA or RSI < 40."
```

**Step 2:** Specify indicators needed
```
What indicators does your strategy need?
- EMA(21)
- RSI(14)
- ADX(14)
```

**Step 3:** Define entry logic
```
Long entry conditions:
1. Price crosses above EMA(21)
2. RSI > 50
3. ADX > 30

Short entry conditions:
1. Price crosses below EMA(21)
2. RSI < 50
3. ADX > 30
```

**Step 4:** Define exit logic
```
Exit method: [1] Fixed TP/SL  [2] Indicator-based  [3] Trailing  [4] Combination

If indicator-based:
- Exit long when: price crosses below EMA OR RSI < 40
- Exit short when: price crosses above EMA OR RSI > 60
```

**Step 5:** Specify parameters
```
Configurable parameters:
- ema_period: int = 21
- rsi_period: int = 14
- rsi_entry_threshold: float = 50.0
- rsi_exit_threshold: float = 40.0
- adx_threshold: float = 30.0
```

**Step 6:** Generate custom bot
```
Generated files:
✓ bot_custom_rsi_ema.py
✓ config.py (with custom params)
✓ indicators.py (with RSI, EMA, ADX)
✓ tests/ (basic test suite)
```

See [workflow-custom-strategy.md](workflow-custom-strategy.md) for detailed workflow and examples.

---

## Pre-Built Signal Shortcuts

Skip the 7-step workflow with direct signal commands:

```
/bot:keltner      # Keltner Channel breakout (PF: 10.04)
/bot:ema          # EMA Cross (PF: 6.23)
/bot:vwap         # Rolling VWAP (PF: 5.20)
/bot:supertrend   # SuperTrend (PF: 4.41)
/bot:alligator    # Williams Alligator (PF: 4.16)
```

These use optimal default parameters from backtesting.

---

## See Also

- [SKILL.md](SKILL.md) - Main skill documentation
- [REFACTOR.md](REFACTOR.md) - Refactoring guide
- [workflow-custom-strategy.md](workflow-custom-strategy.md) - Custom strategy workflow
- [workflow-add-feature.md](workflow-add-feature.md) - Add feature workflow
- [workflow-remove-feature.md](workflow-remove-feature.md) - Remove feature workflow
- [workflow-change-indicator.md](workflow-change-indicator.md) - Change indicator workflow
- [workflow-migrate-eval-pa.md](workflow-migrate-eval-pa.md) - Eval to PA migration
- [SIGNALS.md](SIGNALS.md) - Pre-built signals reference
- [CONFIG.md](CONFIG.md) - Configuration reference
- [docs/TESTING_GUIDE.md](docs/TESTING_GUIDE.md) - Testing strategies
