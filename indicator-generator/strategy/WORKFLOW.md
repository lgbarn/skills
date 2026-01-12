# Strategy Builder Interactive Workflow

This document defines the interactive prompt workflow for strategy generation. The skill guides users through configuration step-by-step.

---

## Workflow Diagram

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
│  STEP 3: ADX Filter Settings                                      │
│  "ADX filter configuration:"                                      │
└──────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 4: Exit Strategy                                            │
│  "Exit settings (ATR-based):"                                     │
└──────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 5: Optional Features                                        │
│  "Enable optional features:"                                      │
└──────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 6: Platform Selection                                       │
│  "Target platform:"                                               │
└──────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 7: Generate Strategy                                        │
│  [Generate code and display summary]                              │
└──────────────────────────────────────────────────────────────────┘
```

---

## Step 1: Signal Selection

**Question:**
```
Which entry signal would you like to use for your strategy?

| # | Signal | Description | PF | Win% |
|---|--------|-------------|-----|------|
| 1 | vwap | Rolling VWAP band breakout (1σ) | 5.20 | 85.3% |
| 2 | keltner | Keltner Channel breakout | 10.04 | 87.8% |
| 3 | ema_cross | EMA crossover with separation | 6.23 | 82.7% |
| 4 | supertrend | SuperTrend direction flip | 4.41 | 82.5% |
| 5 | alligator | Williams Alligator alignment | 4.16 | 83.5% |
| 6 | ssl | SSL Channel direction flip | 4.08 | 79.8% |
| 7 | squeeze | TTM Squeeze release | 3.88 | 82.0% |
| 8 | aroon | Aroon crossover | 3.46 | 81.4% |
| 9 | adx_only | +DI/-DI crossover | 3.37 | 80.7% |
| 10| stochastic | Stochastic %K/%D crossover | - | - |
| 11| macd | MACD line/signal crossover | - | - |

Enter signal name or number (default: keltner):
```

**Options:**
- Header: "Signal"
- Choices: All 11 signals
- Default: `keltner` (best profit factor)

---

## Step 2: Signal Parameters

**Dynamic based on selected signal.** Show signal-specific parameters with defaults and optimal values.

### Example: Keltner
```
Configure Keltner Channel parameters:

| Parameter | Default | Optimal | Description |
|-----------|---------|---------|-------------|
| EMA Period | 20 | 20 | Middle line EMA period |
| ATR Multiplier | 1.5 | 2.75 | Band width (wider = fewer signals) |

Use optimal settings? [Y/n]:
```

### Example: EMA Cross
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

### Example: VWAP
```
Configure Rolling VWAP parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| Window | 720 | Rolling window in bars (720 = 24h at 2-min) |
| Band Multiplier | 1.0 | Standard deviation multiplier |

Use default settings? [Y/n]:
```

---

## Step 3: ADX Filter Settings

**Question:**
```
ADX Filter Configuration:

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

Use recommended settings (threshold=35, mode=di_rising)? [Y/n]:
```

**Options:**
- Header: "ADX Filter"
- Default: `threshold=35, mode=di_rising`

---

## Step 4: Exit Strategy

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

Use default exit settings? [Y/n]:
```

**Options:**
- Header: "Exits"
- Default: `sl=3.0, tp=3.0, trail=true, trigger=0.15, distance=0.15`

---

## Step 5: Optional Features

**Question:**
```
Optional Features:

| Feature | Default | Description |
|---------|---------|-------------|
| Re-entry | true | Allow trend continuation re-entries |
| Volume Filter | true | Require volume > MA |
| Session Filter | true | Only trade allowed hours |

Re-entry Settings (if enabled):
| Setting | Default | Description |
|---------|---------|-------------|
| Wait Bars | 3 | Bars to wait after exit |
| ADX Min | 40 | Higher ADX for re-entry |
| Max Re-entries | 10 | Per trend direction |

Enable all features with defaults? [Y/n]:
```

**Options:**
- Header: "Features"
- Multi-select allowed
- Default: All enabled

---

## Step 6: Platform Selection

**Question:**
```
Target Platform:

| Platform | Description |
|----------|-------------|
| pine | TradingView Pine Script v6 |
| ninja | NinjaTrader 8 NinjaScript C# |
| both | Generate for both platforms |

Select platform [pine/ninja/both] (default: pine):
```

**Options:**
- Header: "Platform"
- Choices: `pine`, `ninja`, `both`
- Default: `pine`

---

## Step 7: Generate Strategy

**Summary and Generation:**
```
Strategy Configuration Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Signal:        Keltner Channel Breakout
Parameters:    EMA=20, ATR Mult=2.75
ADX Filter:    Enabled (threshold=35, mode=di_rising)
Exits:         SL=3.0×ATR, TP=3.0×ATR, Trailing=0.15×ATR
Features:      Re-entry, Volume Filter, Session Filter
Platform:      Pine Script v6

Generating strategy...

✓ Created: LB_Keltner_Strategy.pine

File written to: Tradingview/LB_Keltner_Strategy.pine
```

---

## Quick Mode

For experienced users, support quick mode that uses all defaults:

```
/strategy:new keltner --quick
```

This skips all prompts and uses:
- Signal's optimal parameters
- ADX: threshold=35, mode=di_rising
- Exits: SL=3.0, TP=3.0, trail=0.15
- Features: all enabled
- Platform: pine (or specified)

---

## Direct Platform Commands

Skip platform selection with direct commands:

```
/strategy:pine keltner    # Pine Script with Keltner signal
/strategy:ninja ema_cross # NinjaScript with EMA Cross signal
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
skip to platform
```

---

## Error Handling

### Invalid Signal
```
"xyz" is not a valid signal.

Available signals: vwap, keltner, ema_cross, supertrend, alligator,
ssl, squeeze, aroon, adx_only, stochastic, macd

Enter signal name:
```

### Invalid Value
```
ATR Multiplier must be between 0.5 and 5.0.
Enter ATR Multiplier (default: 2.75):
```

### Missing Required Parameter
```
Signal is required. Please select an entry signal.
```

---

## Configuration Object

After collecting all inputs, build a configuration object:

```json
{
  "signal": "keltner",
  "signal_params": {
    "keltner_ema_period": 20,
    "keltner_atr_mult": 2.75
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
  "features": {
    "enable_longs": true,
    "enable_shorts": true,
    "reentry_enabled": true,
    "reentry_bars_wait": 3,
    "reentry_adx_min": 40,
    "max_reentries": 10,
    "volume_filter": true,
    "volume_ma_period": 20,
    "session_filter": true
  },
  "platform": "pine"
}
```

This object is passed to the template engine for code generation.
