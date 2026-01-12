# Pine Script Strategy Template

This template generates Pine Script v6 strategies with configurable entry signals, ADX filtering, ATR-based exits, and re-entry logic.

---

## Base Template

```pine
// Released under the Mozilla Public License 2.0 - see https://mozilla.org/MPL/2.0/
// by Luther Barnum - {{SIGNAL_DISPLAY_NAME}} Breakout Strategy
// Generated from backtest configuration

//@version=6
strategy("LB {{SIGNAL_DISPLAY_NAME}} Strategy", shorttitle="LB {{SHORT_NAME}} Strat", overlay=true,
     initial_capital=50000, default_qty_type=strategy.fixed, default_qty_value=1,
     commission_type=strategy.commission.per_order, commission_value=2.5,
     slippage=1, pyramiding=0, calc_on_order_fills=true, calc_on_every_tick=false,
     max_bars_back=1000)

import lgbarn/lw_ind/13 as LW

// ============================================================================
//                         FEATURE TOGGLES
// ============================================================================

enableLongs = input.bool(true, "Enable Long Trades", group="Feature Toggles",
     tooltip="Allow long entries.")
enableShorts = input.bool(true, "Enable Short Trades", group="Feature Toggles",
     tooltip="Allow short entries.")
enableReentry = input.bool({{REENTRY_ENABLED}}, "Enable Re-entry", group="Feature Toggles",
     tooltip="Allow trend continuation re-entries after profitable exits.")
showSignals = input.bool(true, "Show Entry Signals", group="Feature Toggles",
     tooltip="Display entry/exit markers on chart.")
{{SHOW_SIGNAL_TOGGLE}}

// ============================================================================
//                         {{SIGNAL_GROUP_NAME}} SETTINGS
// ============================================================================

{{SIGNAL_INPUTS}}

// ============================================================================
//                         ENTRY FILTERS
// ============================================================================

adxThreshold = input.int({{ADX_THRESHOLD}}, "ADX Threshold", minval=10, maxval=50, group="Entry Filters",
     tooltip="Minimum ADX for initial entry. Higher = stronger trend required.")
adxPeriod = input.int({{ADX_PERIOD}}, "ADX Period", minval=5, maxval=30, group="Entry Filters",
     tooltip="Period for ADX calculation.")
adxMode = input.string("{{ADX_MODE}}", "ADX Mode",
     options=["traditional", "di_aligned", "di_rising", "adx_rising", "combined"], group="Entry Filters",
     tooltip="di_rising: Dominant DI must be rising. Recommended.")
volumeFilter = input.bool({{VOLUME_FILTER}}, "Volume Filter", group="Entry Filters",
     tooltip="Require volume above MA for entry confirmation.")
volumeMaPeriod = input.int({{VOLUME_MA_PERIOD}}, "Volume MA Period", minval=5, maxval=50, group="Entry Filters",
     tooltip="Period for volume moving average.")

// Session hours (ET timezone)
useSessionFilter = input.bool(true, "Use Session Filter", group="Entry Filters",
     tooltip="Only trade during specified hours.")
sessionTimezone = input.string("America/New_York", "Timezone",
     options=["America/New_York", "America/Chicago", "Europe/London"], group="Entry Filters")

// Trading hours checkboxes
hour9 = input.bool(true, "9 AM", inline="hours1", group="Entry Filters")
hour10 = input.bool(true, "10 AM", inline="hours1", group="Entry Filters")
hour11 = input.bool(true, "11 AM", inline="hours1", group="Entry Filters")
hour12 = input.bool(true, "12 PM", inline="hours1", group="Entry Filters")
hour13 = input.bool(true, "1 PM", inline="hours2", group="Entry Filters")
hour14 = input.bool(true, "2 PM", inline="hours2", group="Entry Filters")
hour15 = input.bool(true, "3 PM", inline="hours2", group="Entry Filters")
hour16 = input.bool(true, "4 PM", inline="hours2", group="Entry Filters")
hour18 = input.bool(true, "6 PM", inline="hours3", group="Entry Filters")
hour19 = input.bool(true, "7 PM", inline="hours3", group="Entry Filters")
hour20 = input.bool(true, "8 PM", inline="hours3", group="Entry Filters")

// ============================================================================
//                         EXIT SETTINGS (ATR-based)
// ============================================================================

atrPeriod = input.int({{ATR_PERIOD}}, "ATR Period", minval=5, maxval=30, group="Exit Settings",
     tooltip="Period for ATR calculation used in stop/target sizing.")
slAtrMult = input.float({{SL_ATR_MULT}}, "Stop Loss (ATR x)", minval=0.5, maxval=5.0, step=0.1, group="Exit Settings",
     tooltip="Initial stop loss distance as ATR multiple.")
tpAtrMult = input.float({{TP_ATR_MULT}}, "Take Profit (ATR x)", minval=0.5, maxval=5.0, step=0.1, group="Exit Settings",
     tooltip="Take profit distance as ATR multiple.")
trailTriggerAtr = input.float({{TRAIL_TRIGGER_ATR}}, "Trail Trigger (ATR x)", minval=0.05, maxval=1.0, step=0.05, group="Exit Settings",
     tooltip="Profit level to activate trailing stop.")
trailDistanceAtr = input.float({{TRAIL_DISTANCE_ATR}}, "Trail Distance (ATR x)", minval=0.05, maxval=1.0, step=0.05, group="Exit Settings",
     tooltip="Trailing stop distance from high/low water mark.")

// ============================================================================
//                         RE-ENTRY SETTINGS
// ============================================================================

reentryWaitBars = input.int({{REENTRY_BARS_WAIT}}, "Wait Bars", minval=1, maxval=20, group="Re-entry Settings",
     tooltip="Bars to wait after profitable exit before re-entry.")
reentryAdxMin = input.int({{REENTRY_ADX_MIN}}, "Re-entry ADX Min", minval=20, maxval=60, group="Re-entry Settings",
     tooltip="Minimum ADX required for re-entry (stricter than initial).")
maxReentries = input.int({{MAX_REENTRIES}}, "Max Re-entries", minval=1, maxval=50, group="Re-entry Settings",
     tooltip="Maximum re-entries allowed per trend direction.")

// ============================================================================
//                         SIGNAL CALCULATION
// ============================================================================

{{SIGNAL_CALCULATION}}

// ============================================================================
//                         INDICATOR CALCULATIONS
// ============================================================================

// ATR for stop/target sizing
float atrValue = ta.atr(atrPeriod)

// ADX with +DI/-DI using library
[diPlus, diMinus, adxValue] = LW.ADX(adxPeriod, adxPeriod)

// ADX filter logic
bool adxRising = adxValue > adxValue[1]
bool diPlusRising = diPlus > diPlus[1]
bool diMinusRising = diMinus > diMinus[1]

// ADX condition check function
checkAdxCondition(int direction) =>
    if adxValue <= adxThreshold
        false
    else if adxMode == "traditional"
        true
    else if adxMode == "di_aligned"
        direction == 1 ? diPlus > diMinus : diMinus > diPlus
    else if adxMode == "di_rising"
        direction == 1 ? diPlusRising : diMinusRising
    else if adxMode == "adx_rising"
        adxRising
    else if adxMode == "combined"
        aligned = direction == 1 ? diPlus > diMinus : diMinus > diPlus
        aligned and adxRising
    else
        true

// Volume filter
float volMa = ta.ema(volume, volumeMaPeriod)
bool volumeOk = not volumeFilter or volume > volMa

// Session filter
int currentHour = hour(time, sessionTimezone)
bool hourAllowed = not useSessionFilter or
     (currentHour == 9 and hour9) or (currentHour == 10 and hour10) or
     (currentHour == 11 and hour11) or (currentHour == 12 and hour12) or
     (currentHour == 13 and hour13) or (currentHour == 14 and hour14) or
     (currentHour == 15 and hour15) or (currentHour == 16 and hour16) or
     (currentHour == 18 and hour18) or (currentHour == 19 and hour19) or
     (currentHour == 20 and hour20)

// ============================================================================
//                         ENTRY SIGNAL DETECTION
// ============================================================================

{{ENTRY_DETECTION}}

// ============================================================================
//                         STATE TRACKING
// ============================================================================

// Re-entry state
var int lastExitBar = 0
var bool lastExitProfitable = false
var int lastExitDirection = 0  // 1=long, -1=short
var int reentryCount = 0

// Position state for manual exit management
var float entryPrice = 0.0
var float stopLoss = 0.0
var float takeProfit = 0.0
var float highWaterMark = 0.0
var float lowWaterMark = 0.0
var bool trailActive = false

// ============================================================================
//                         ENTRY LOGIC
// ============================================================================

// Check if flat
bool isFlat = strategy.position_size == 0

// Initial entry signals (need crossover)
bool longSignal = longBreakout and enableLongs and checkAdxCondition(1) and volumeOk and hourAllowed and isFlat
bool shortSignal = shortBreakout and enableShorts and checkAdxCondition(-1) and volumeOk and hourAllowed and isFlat

// Re-entry logic
if enableReentry and isFlat and lastExitProfitable
    barsSinceExit = bar_index - lastExitBar
    if barsSinceExit >= reentryWaitBars and reentryCount < maxReentries and adxValue > reentryAdxMin
        {{REENTRY_CONDITION}}

// Execute entry
if longSignal
    strategy.entry("Long", strategy.long)
    entryPrice := close
    stopLoss := close - slAtrMult * atrValue
    takeProfit := close + tpAtrMult * atrValue
    highWaterMark := close
    trailActive := false
    if lastExitDirection == 1 and lastExitProfitable
        reentryCount += 1
    else
        reentryCount := 0

if shortSignal
    strategy.entry("Short", strategy.short)
    entryPrice := close
    stopLoss := close + slAtrMult * atrValue
    takeProfit := close - tpAtrMult * atrValue
    lowWaterMark := close
    trailActive := false
    if lastExitDirection == -1 and lastExitProfitable
        reentryCount += 1
    else
        reentryCount := 0

// ============================================================================
//                         POSITION MANAGEMENT
// ============================================================================

// Long position management
if strategy.position_size > 0
    // Update high water mark
    if high > highWaterMark
        highWaterMark := high

    // Check trailing stop activation
    if not trailActive and (highWaterMark - entryPrice) >= trailTriggerAtr * atrValue
        trailActive := true

    // Update trailing stop
    if trailActive
        newStop = highWaterMark - trailDistanceAtr * atrValue
        if newStop > stopLoss
            stopLoss := newStop

    // Check exits (priority: Trail/SL > TP)
    if low <= stopLoss
        strategy.close("Long", comment = trailActive ? "Trail" : "SL")
        lastExitBar := bar_index
        lastExitProfitable := close > entryPrice
        lastExitDirection := 1
    else if high >= takeProfit
        strategy.close("Long", comment = "TP")
        lastExitBar := bar_index
        lastExitProfitable := true
        lastExitDirection := 1

// Short position management
if strategy.position_size < 0
    // Update low water mark
    if low < lowWaterMark
        lowWaterMark := low

    // Check trailing stop activation
    if not trailActive and (entryPrice - lowWaterMark) >= trailTriggerAtr * atrValue
        trailActive := true

    // Update trailing stop
    if trailActive
        newStop = lowWaterMark + trailDistanceAtr * atrValue
        if newStop < stopLoss
            stopLoss := newStop

    // Check exits (priority: Trail/SL > TP)
    if high >= stopLoss
        strategy.close("Short", comment = trailActive ? "Trail" : "SL")
        lastExitBar := bar_index
        lastExitProfitable := close < entryPrice
        lastExitDirection := -1
    else if low <= takeProfit
        strategy.close("Short", comment = "TP")
        lastExitBar := bar_index
        lastExitProfitable := true
        lastExitDirection := -1

// ============================================================================
//                         PLOTTING
// ============================================================================

{{SIGNAL_PLOTTING}}

// Entry/exit markers
plotshape(longSignal and showSignals, "Long Entry", shape.triangleup, location.belowbar,
     color.new(color.green, 0), size=size.small)
plotshape(shortSignal and showSignals, "Short Entry", shape.triangledown, location.abovebar,
     color.new(color.red, 0), size=size.small)

// Stop/target lines
plot(strategy.position_size > 0 ? stopLoss : na, "Long SL", color.red, 1, plot.style_linebr)
plot(strategy.position_size > 0 ? takeProfit : na, "Long TP", color.green, 1, plot.style_linebr)
plot(strategy.position_size < 0 ? stopLoss : na, "Short SL", color.red, 1, plot.style_linebr)
plot(strategy.position_size < 0 ? takeProfit : na, "Short TP", color.green, 1, plot.style_linebr)

// ============================================================================
//                         INFO TABLE
// ============================================================================

var table infoTable = table.new(position.top_right, 2, 6, bgcolor=color.new(color.black, 80))

if barstate.islast
    table.cell(infoTable, 0, 0, "ADX", text_color=color.white, text_size=size.small)
    table.cell(infoTable, 1, 0, str.tostring(adxValue, "#.0"), text_color=color.white, text_size=size.small)
    table.cell(infoTable, 0, 1, "+DI", text_color=color.green, text_size=size.small)
    table.cell(infoTable, 1, 1, str.tostring(diPlus, "#.0"), text_color=color.green, text_size=size.small)
    table.cell(infoTable, 0, 2, "-DI", text_color=color.red, text_size=size.small)
    table.cell(infoTable, 1, 2, str.tostring(diMinus, "#.0"), text_color=color.red, text_size=size.small)
    table.cell(infoTable, 0, 3, "ATR", text_color=color.white, text_size=size.small)
    table.cell(infoTable, 1, 3, str.tostring(atrValue, "#.00"), text_color=color.white, text_size=size.small)
    table.cell(infoTable, 0, 4, "Re-entries", text_color=color.white, text_size=size.small)
    table.cell(infoTable, 1, 4, str.tostring(reentryCount) + "/" + str.tostring(maxReentries),
         text_color=color.white, text_size=size.small)
```

---

## Template Placeholders

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{SIGNAL_DISPLAY_NAME}}` | Full signal name for title | "Keltner Channel" |
| `{{SHORT_NAME}}` | Abbreviated name | "KC" |
| `{{SIGNAL_GROUP_NAME}}` | Input group name | "KELTNER" |
| `{{SIGNAL_INPUTS}}` | Signal-specific input declarations | See SIGNALS.md |
| `{{SIGNAL_CALCULATION}}` | Signal calculation code | See SIGNALS.md |
| `{{ENTRY_DETECTION}}` | Breakout detection variables | See SIGNALS.md |
| `{{REENTRY_CONDITION}}` | Re-entry specific logic | See SIGNALS.md |
| `{{SIGNAL_PLOTTING}}` | Signal-specific plots | See SIGNALS.md |
| `{{SHOW_SIGNAL_TOGGLE}}` | Optional show/hide toggle | `showKeltner = input.bool(true, ...)` |
| `{{REENTRY_ENABLED}}` | Default re-entry state | `true` or `false` |
| `{{ADX_THRESHOLD}}` | Default ADX threshold | `35` |
| `{{ADX_PERIOD}}` | ADX calculation period | `14` |
| `{{ADX_MODE}}` | ADX filter mode | `di_rising` |
| `{{VOLUME_FILTER}}` | Enable volume filter | `true` |
| `{{VOLUME_MA_PERIOD}}` | Volume MA period | `20` |
| `{{ATR_PERIOD}}` | ATR calculation period | `14` |
| `{{SL_ATR_MULT}}` | Stop loss multiplier | `3.0` |
| `{{TP_ATR_MULT}}` | Take profit multiplier | `3.0` |
| `{{TRAIL_TRIGGER_ATR}}` | Trail activation | `0.15` |
| `{{TRAIL_DISTANCE_ATR}}` | Trail distance | `0.15` |
| `{{REENTRY_BARS_WAIT}}` | Bars to wait | `3` |
| `{{REENTRY_ADX_MIN}}` | Re-entry ADX minimum | `40` |
| `{{MAX_REENTRIES}}` | Maximum re-entries | `10` |

---

## Default Values (from backtest.py CONFIG)

```
REENTRY_ENABLED = true
ADX_THRESHOLD = 35
ADX_PERIOD = 14
ADX_MODE = "di_rising"
VOLUME_FILTER = true
VOLUME_MA_PERIOD = 20
ATR_PERIOD = 14
SL_ATR_MULT = 3.0
TP_ATR_MULT = 3.0
TRAIL_TRIGGER_ATR = 0.15
TRAIL_DISTANCE_ATR = 0.15
REENTRY_BARS_WAIT = 3
REENTRY_ADX_MIN = 40
MAX_REENTRIES = 10
```

---

## File Naming Convention

- Standard: `LB_{{SignalName}}_Strategy.pine`
- Examples:
  - `LB_Keltner_Strategy.pine`
  - `LB_VWAP_Strategy.pine`
  - `LB_EMA_Cross_Strategy.pine`

---

## Key Implementation Notes

### Exit Priority Order
The template implements conservative exit priority (assume worst outcome on wide bars):
1. Trailing Stop (if active AND hit)
2. Stop Loss (hard protective stop)
3. Take Profit (profit target)

### Re-entry Logic
- Requires `enableReentry` toggle
- Only after profitable exits
- Waits `reentryWaitBars` bars
- Requires higher ADX (`reentryAdxMin`)
- Tracks count per direction (`maxReentries`)
- Resets count when trend direction changes

### ADX Filter Modes
- `traditional`: ADX > threshold only
- `di_aligned`: ADX > threshold AND DIs aligned with direction
- `di_rising`: ADX > threshold AND dominant DI rising (RECOMMENDED)
- `adx_rising`: ADX > threshold AND ADX itself rising
- `combined`: All conditions

### Library Dependency
Uses `lgbarn/lw_ind/13` for ADX calculation. This library provides:
- `LW.ADX(adxPeriod, diPeriod)` returns `[+DI, -DI, ADX]`

If library is unavailable, use built-in calculations (see SIGNALS.md for fallback code).
