# Pine Script Signal Code Blocks

Signal-specific code blocks for each of the 11 entry signals. Use with TEMPLATE.md.

---

## 1. VWAP (Rolling VWAP Band Breakout)

### Metadata
```
SIGNAL_DISPLAY_NAME = "VWAP Band"
SHORT_NAME = "VWAP"
SIGNAL_GROUP_NAME = "VWAP"
```

### SHOW_SIGNAL_TOGGLE
```pine
showVWAP = input.bool(true, "Show VWAP & Bands", group="Feature Toggles",
     tooltip="Display rolling VWAP and standard deviation bands on chart.")
```

### SIGNAL_INPUTS
```pine
vwapWindow = input.int(720, "Rolling Window (bars)", minval=10, maxval=2000, group="VWAP Settings",
     tooltip="Number of bars for rolling VWAP calculation. Default 720 = 24 hours at 2-min bars.")
bandMult = input.float(1.0, "Band Multiplier (sigma)", minval=0.1, maxval=3.0, step=0.1, group="VWAP Settings",
     tooltip="Standard deviation multiplier for breakout bands.")
```

### SIGNAL_CALCULATION
```pine
// Calculate typical price
float typicalPrice = hlc3

// Rolling sums for VWAP (ring buffer approach)
var float sumTPV = 0.0
var float sumVol = 0.0
var float sumTP2V = 0.0
var array<float> tpvBuffer = array.new_float(vwapWindow, 0.0)
var array<float> volBuffer = array.new_float(vwapWindow, 0.0)
var array<float> tp2vBuffer = array.new_float(vwapWindow, 0.0)
var int bufferIdx = 0

float currentTPV = typicalPrice * volume
float currentVol = volume
float currentTP2V = typicalPrice * typicalPrice * volume

float oldTPV = array.get(tpvBuffer, bufferIdx)
float oldVol = array.get(volBuffer, bufferIdx)
float oldTP2V = array.get(tp2vBuffer, bufferIdx)

sumTPV := sumTPV - oldTPV + currentTPV
sumVol := sumVol - oldVol + currentVol
sumTP2V := sumTP2V - oldTP2V + currentTP2V

array.set(tpvBuffer, bufferIdx, currentTPV)
array.set(volBuffer, bufferIdx, currentVol)
array.set(tp2vBuffer, bufferIdx, currentTP2V)
bufferIdx := (bufferIdx + 1) % vwapWindow

float vwapValue = sumVol > 0 ? sumTPV / sumVol : close
float variance = sumVol > 0 ? math.max(sumTP2V / sumVol - vwapValue * vwapValue, 0.0) : 0.0
float stDev = math.sqrt(variance)
float upperBand = vwapValue + bandMult * stDev
float lowerBand = vwapValue - bandMult * stDev
```

### ENTRY_DETECTION
```pine
// VWAP band breakout detection
bool longBreakout = close[1] <= upperBand[1] and close > upperBand
bool shortBreakout = close[1] >= lowerBand[1] and close < lowerBand
bool stillAboveBand = close > upperBand
bool stillBelowBand = close < lowerBand
```

### REENTRY_CONDITION
```pine
        if lastExitDirection == 1 and stillAboveBand
            longSignal := true
        if lastExitDirection == -1 and stillBelowBand
            shortSignal := true
```

### SIGNAL_PLOTTING
```pine
// VWAP and bands
plot(showVWAP ? vwapValue : na, "VWAP", color.purple, 2)
plot(showVWAP ? upperBand : na, "Upper Band", color.new(color.gray, 50), 1)
plot(showVWAP ? lowerBand : na, "Lower Band", color.new(color.gray, 50), 1)
```

---

## 2. Keltner (Keltner Channel Breakout)

### Metadata
```
SIGNAL_DISPLAY_NAME = "Keltner Channel"
SHORT_NAME = "KC"
SIGNAL_GROUP_NAME = "KELTNER"
```

### SHOW_SIGNAL_TOGGLE
```pine
showKeltner = input.bool(true, "Show Keltner Channel", group="Feature Toggles",
     tooltip="Display Keltner Channel bands on chart.")
```

### SIGNAL_INPUTS
```pine
keltnerEmaPeriod = input.int(20, "EMA Period", minval=5, maxval=100, group="Keltner Settings",
     tooltip="EMA period for middle line.")
keltnerAtrMult = input.float(2.75, "ATR Multiplier", minval=0.5, maxval=5.0, step=0.1, group="Keltner Settings",
     tooltip="ATR multiplier for band width. Optimal: 2.75")
```

### SIGNAL_CALCULATION
```pine
// Keltner Channel calculation
float keltnerMid = ta.ema(close, keltnerEmaPeriod)
float keltnerAtr = ta.atr(atrPeriod)
float keltnerUpper = keltnerMid + keltnerAtrMult * keltnerAtr
float keltnerLower = keltnerMid - keltnerAtrMult * keltnerAtr
```

### ENTRY_DETECTION
```pine
// Keltner channel breakout detection
bool longBreakout = close[1] <= keltnerUpper[1] and close > keltnerUpper
bool shortBreakout = close[1] >= keltnerLower[1] and close < keltnerLower
bool stillAboveBand = close > keltnerUpper
bool stillBelowBand = close < keltnerLower
```

### REENTRY_CONDITION
```pine
        if lastExitDirection == 1 and stillAboveBand
            longSignal := true
        if lastExitDirection == -1 and stillBelowBand
            shortSignal := true
```

### SIGNAL_PLOTTING
```pine
// Keltner Channel
plot(showKeltner ? keltnerMid : na, "KC Mid", color.purple, 2)
plot(showKeltner ? keltnerUpper : na, "KC Upper", color.new(color.gray, 50), 1)
plot(showKeltner ? keltnerLower : na, "KC Lower", color.new(color.gray, 50), 1)
```

---

## 3. EMA Cross (EMA Crossover)

### Metadata
```
SIGNAL_DISPLAY_NAME = "EMA Crossover"
SHORT_NAME = "EMA"
SIGNAL_GROUP_NAME = "EMA CROSS"
```

### SHOW_SIGNAL_TOGGLE
```pine
showEmas = input.bool(true, "Show EMAs", group="Feature Toggles",
     tooltip="Display fast and slow EMAs on chart.")
```

### SIGNAL_INPUTS
```pine
emaFast = input.int(3, "Fast EMA", minval=2, maxval=50, group="EMA Cross Settings",
     tooltip="Fast EMA period. Linda Raschke: 3")
emaSlow = input.int(8, "Slow EMA", minval=3, maxval=100, group="EMA Cross Settings",
     tooltip="Slow EMA period. Linda Raschke: 8")
emaSeparationFilter = input.bool(true, "Separation Filter", group="EMA Cross Settings",
     tooltip="Require minimum separation between EMAs.")
emaSeparationMin = input.float(0.35, "Min Separation", minval=0.0, maxval=5.0, step=0.05, group="EMA Cross Settings",
     tooltip="Minimum points between fast and slow EMA.")
```

### SIGNAL_CALCULATION
```pine
// EMA calculation
float emaFastVal = ta.ema(close, emaFast)
float emaSlowVal = ta.ema(close, emaSlow)
float emaSeparation = math.abs(emaFastVal - emaSlowVal)
bool separationOk = not emaSeparationFilter or emaSeparation >= emaSeparationMin
```

### ENTRY_DETECTION
```pine
// EMA crossover detection
bool goldenCross = emaFastVal[1] <= emaSlowVal[1] and emaFastVal > emaSlowVal
bool deathCross = emaSlowVal[1] <= emaFastVal[1] and emaSlowVal > emaFastVal
bool longBreakout = goldenCross and separationOk
bool shortBreakout = deathCross and separationOk
bool stillLongAligned = emaFastVal > emaSlowVal
bool stillShortAligned = emaSlowVal > emaFastVal
```

### REENTRY_CONDITION
```pine
        if lastExitDirection == 1 and stillLongAligned
            longSignal := true
        if lastExitDirection == -1 and stillShortAligned
            shortSignal := true
```

### SIGNAL_PLOTTING
```pine
// EMAs
plot(showEmas ? emaFastVal : na, "Fast EMA", color.green, 2)
plot(showEmas ? emaSlowVal : na, "Slow EMA", color.red, 2)
```

---

## 4. SuperTrend

### Metadata
```
SIGNAL_DISPLAY_NAME = "SuperTrend"
SHORT_NAME = "ST"
SIGNAL_GROUP_NAME = "SUPERTREND"
```

### SHOW_SIGNAL_TOGGLE
```pine
showSupertrend = input.bool(true, "Show SuperTrend", group="Feature Toggles",
     tooltip="Display SuperTrend line on chart.")
```

### SIGNAL_INPUTS
```pine
stPeriod = input.int(10, "ATR Period", minval=5, maxval=30, group="SuperTrend Settings",
     tooltip="ATR period for SuperTrend calculation.")
stMult = input.float(3.0, "Multiplier", minval=1.0, maxval=5.0, step=0.1, group="SuperTrend Settings",
     tooltip="ATR multiplier for band width.")
```

### SIGNAL_CALCULATION
```pine
// SuperTrend calculation
float hl2Val = hl2
float stAtr = ta.atr(stPeriod)
float basicUpper = hl2Val + stMult * stAtr
float basicLower = hl2Val - stMult * stAtr

var float finalUpper = na
var float finalLower = na
var int stDirection = 1

finalUpper := basicUpper < nz(finalUpper[1]) or close[1] > nz(finalUpper[1]) ? basicUpper : nz(finalUpper[1])
finalLower := basicLower > nz(finalLower[1]) or close[1] < nz(finalLower[1]) ? basicLower : nz(finalLower[1])

if na(stDirection[1])
    stDirection := 1
else if stDirection[1] == -1 and close > finalUpper
    stDirection := 1
else if stDirection[1] == 1 and close < finalLower
    stDirection := -1
else
    stDirection := stDirection[1]

float supertrend = stDirection == 1 ? finalLower : finalUpper
```

### ENTRY_DETECTION
```pine
// SuperTrend direction flip detection
bool longBreakout = stDirection[1] == -1 and stDirection == 1
bool shortBreakout = stDirection[1] == 1 and stDirection == -1
bool stillBullish = stDirection == 1
bool stillBearish = stDirection == -1
```

### REENTRY_CONDITION
```pine
        if lastExitDirection == 1 and stillBullish
            longSignal := true
        if lastExitDirection == -1 and stillBearish
            shortSignal := true
```

### SIGNAL_PLOTTING
```pine
// SuperTrend
plot(showSupertrend ? supertrend : na, "SuperTrend",
     color = stDirection == 1 ? color.green : color.red, linewidth=2)
```

---

## 5. Alligator (Williams Alligator)

### Metadata
```
SIGNAL_DISPLAY_NAME = "Williams Alligator"
SHORT_NAME = "GATOR"
SIGNAL_GROUP_NAME = "ALLIGATOR"
```

### SHOW_SIGNAL_TOGGLE
```pine
showAlligator = input.bool(true, "Show Alligator", group="Feature Toggles",
     tooltip="Display Alligator lines on chart.")
```

### SIGNAL_INPUTS
```pine
jawPeriod = input.int(13, "Jaw Period", minval=5, maxval=30, group="Alligator Settings",
     tooltip="Jaw SMMA period (blue line).")
jawOffset = input.int(8, "Jaw Offset", minval=1, maxval=15, group="Alligator Settings")
teethPeriod = input.int(8, "Teeth Period", minval=3, maxval=20, group="Alligator Settings",
     tooltip="Teeth SMMA period (red line).")
teethOffset = input.int(5, "Teeth Offset", minval=1, maxval=10, group="Alligator Settings")
lipsPeriod = input.int(5, "Lips Period", minval=2, maxval=15, group="Alligator Settings",
     tooltip="Lips SMMA period (green line).")
lipsOffset = input.int(3, "Lips Offset", minval=1, maxval=8, group="Alligator Settings")
```

### SIGNAL_CALCULATION
```pine
// SMMA calculation function
smma(src, length) =>
    var float result = na
    result := na(result[1]) ? ta.sma(src, length) : (result[1] * (length - 1) + src) / length

// Alligator lines (with offset applied by looking back)
float jaw = smma(hl2, jawPeriod)[jawOffset]
float teeth = smma(hl2, teethPeriod)[teethOffset]
float lips = smma(hl2, lipsPeriod)[lipsOffset]

bool alignedUp = lips > teeth and teeth > jaw
bool alignedDown = lips < teeth and teeth < jaw
```

### ENTRY_DETECTION
```pine
// Alligator alignment detection
bool longBreakout = not alignedUp[1] and alignedUp
bool shortBreakout = not alignedDown[1] and alignedDown
bool stillAlignedUp = alignedUp
bool stillAlignedDown = alignedDown
```

### REENTRY_CONDITION
```pine
        if lastExitDirection == 1 and stillAlignedUp
            longSignal := true
        if lastExitDirection == -1 and stillAlignedDown
            shortSignal := true
```

### SIGNAL_PLOTTING
```pine
// Alligator lines
plot(showAlligator ? jaw : na, "Jaw", color.blue, 2)
plot(showAlligator ? teeth : na, "Teeth", color.red, 2)
plot(showAlligator ? lips : na, "Lips", color.green, 2)
```

---

## 6. SSL Channel

### Metadata
```
SIGNAL_DISPLAY_NAME = "SSL Channel"
SHORT_NAME = "SSL"
SIGNAL_GROUP_NAME = "SSL"
```

### SHOW_SIGNAL_TOGGLE
```pine
showSSL = input.bool(true, "Show SSL Channel", group="Feature Toggles",
     tooltip="Display SSL Channel lines on chart.")
```

### SIGNAL_INPUTS
```pine
sslPeriod = input.int(10, "Period", minval=5, maxval=30, group="SSL Settings",
     tooltip="SSL Channel SMA period.")
```

### SIGNAL_CALCULATION
```pine
// SSL Channel calculation
float smaHigh = ta.sma(high, sslPeriod)
float smaLow = ta.sma(low, sslPeriod)

var int sslDir = 1
if close > smaHigh
    sslDir := 1
else if close < smaLow
    sslDir := -1

float sslUp = sslDir == 1 ? smaLow : smaHigh
float sslDown = sslDir == 1 ? smaHigh : smaLow
```

### ENTRY_DETECTION
```pine
// SSL direction flip detection
bool longBreakout = sslDir[1] == -1 and sslDir == 1
bool shortBreakout = sslDir[1] == 1 and sslDir == -1
bool stillBullish = sslDir == 1
bool stillBearish = sslDir == -1
```

### REENTRY_CONDITION
```pine
        if lastExitDirection == 1 and stillBullish
            longSignal := true
        if lastExitDirection == -1 and stillBearish
            shortSignal := true
```

### SIGNAL_PLOTTING
```pine
// SSL Channel
plot(showSSL ? sslUp : na, "SSL Up", color.green, 2)
plot(showSSL ? sslDown : na, "SSL Down", color.red, 2)
```

---

## 7. Squeeze (TTM Squeeze)

### Metadata
```
SIGNAL_DISPLAY_NAME = "TTM Squeeze"
SHORT_NAME = "SQZ"
SIGNAL_GROUP_NAME = "SQUEEZE"
```

### SHOW_SIGNAL_TOGGLE
```pine
showSqueeze = input.bool(true, "Show Squeeze Indicator", group="Feature Toggles",
     tooltip="Display squeeze momentum histogram.")
```

### SIGNAL_INPUTS
```pine
sqzBbPeriod = input.int(20, "BB Period", minval=10, maxval=50, group="Squeeze Settings",
     tooltip="Bollinger Band period.")
sqzBbMult = input.float(2.0, "BB Multiplier", minval=1.0, maxval=3.0, step=0.1, group="Squeeze Settings")
sqzKcPeriod = input.int(20, "KC Period", minval=10, maxval=50, group="Squeeze Settings",
     tooltip="Keltner Channel period.")
sqzKcMult = input.float(1.5, "KC Multiplier", minval=0.5, maxval=3.0, step=0.1, group="Squeeze Settings")
sqzMomPeriod = input.int(12, "Momentum Period", minval=5, maxval=30, group="Squeeze Settings")
```

### SIGNAL_CALCULATION
```pine
// Bollinger Bands
float bbBasis = ta.sma(close, sqzBbPeriod)
float bbDev = ta.stdev(close, sqzBbPeriod)
float bbUpper = bbBasis + sqzBbMult * bbDev
float bbLower = bbBasis - sqzBbMult * bbDev

// Keltner Channels
float kcBasis = ta.ema(close, sqzKcPeriod)
float kcAtr = ta.atr(sqzKcPeriod)
float kcUpper = kcBasis + sqzKcMult * kcAtr
float kcLower = kcBasis - sqzKcMult * kcAtr

// Squeeze detection
bool squeezeOn = bbLower > kcLower and bbUpper < kcUpper
bool squeezeFired = squeezeOn[1] and not squeezeOn

// Momentum (donchian midline + SMA midline)
float highest = ta.highest(high, sqzMomPeriod)
float lowest = ta.lowest(low, sqzMomPeriod)
float donchianMid = (highest + lowest) / 2
float smaMid = ta.sma(close, sqzMomPeriod)
float sqzMomentum = close - (donchianMid + smaMid) / 2
```

### ENTRY_DETECTION
```pine
// Squeeze release with momentum direction
bool longBreakout = squeezeFired and sqzMomentum > 0
bool shortBreakout = squeezeFired and sqzMomentum < 0
bool stillBullish = sqzMomentum > 0
bool stillBearish = sqzMomentum < 0
```

### REENTRY_CONDITION
```pine
        if lastExitDirection == 1 and stillBullish
            longSignal := true
        if lastExitDirection == -1 and stillBearish
            shortSignal := true
```

### SIGNAL_PLOTTING
```pine
// Squeeze momentum histogram
plot(showSqueeze ? sqzMomentum : na, "Momentum", style=plot.style_columns,
     color = sqzMomentum >= 0 ?
         (sqzMomentum > sqzMomentum[1] ? color.lime : color.green) :
         (sqzMomentum < sqzMomentum[1] ? color.red : color.maroon))
// Squeeze dots (on zero line in separate pane)
plotshape(showSqueeze and squeezeOn, "Squeeze On", shape.circle, location.bottom,
     color.red, size=size.tiny)
plotshape(showSqueeze and not squeezeOn, "Squeeze Off", shape.circle, location.bottom,
     color.green, size=size.tiny)
```

---

## 8. Aroon

### Metadata
```
SIGNAL_DISPLAY_NAME = "Aroon"
SHORT_NAME = "AROON"
SIGNAL_GROUP_NAME = "AROON"
```

### SHOW_SIGNAL_TOGGLE
```pine
showAroon = input.bool(true, "Show Aroon", group="Feature Toggles",
     tooltip="Display Aroon Up/Down lines.")
```

### SIGNAL_INPUTS
```pine
aroonPeriod = input.int(50, "Period", minval=10, maxval=100, group="Aroon Settings",
     tooltip="Lookback period for Aroon calculation. Optimal: 50")
```

### SIGNAL_CALCULATION
```pine
// Aroon calculation
float aroonUp = 100 * (aroonPeriod - ta.highestbars(high, aroonPeriod + 1)) / aroonPeriod
float aroonDown = 100 * (aroonPeriod - ta.lowestbars(low, aroonPeriod + 1)) / aroonPeriod
```

### ENTRY_DETECTION
```pine
// Aroon crossover detection
bool longBreakout = aroonUp[1] <= aroonDown[1] and aroonUp > aroonDown
bool shortBreakout = aroonDown[1] <= aroonUp[1] and aroonDown > aroonUp
bool stillBullish = aroonUp > aroonDown
bool stillBearish = aroonDown > aroonUp
```

### REENTRY_CONDITION
```pine
        if lastExitDirection == 1 and stillBullish
            longSignal := true
        if lastExitDirection == -1 and stillBearish
            shortSignal := true
```

### SIGNAL_PLOTTING
```pine
// Aroon lines (in separate pane)
plot(showAroon ? aroonUp : na, "Aroon Up", color.green, 2)
plot(showAroon ? aroonDown : na, "Aroon Down", color.red, 2)
hline(50, "Middle", color.gray)
```

---

## 9. ADX Only (+DI/-DI Crossover)

### Metadata
```
SIGNAL_DISPLAY_NAME = "DI Crossover"
SHORT_NAME = "DI"
SIGNAL_GROUP_NAME = "ADX"
```

### SHOW_SIGNAL_TOGGLE
```pine
showDI = input.bool(true, "Show +DI/-DI", group="Feature Toggles",
     tooltip="Display +DI and -DI lines.")
```

### SIGNAL_INPUTS
```pine
// Uses standard ADX settings from Entry Filters section
// No additional inputs needed
```

### SIGNAL_CALCULATION
```pine
// ADX/DI already calculated in main indicator section
// Uses diPlus, diMinus, adxValue from LW.ADX()
```

### ENTRY_DETECTION
```pine
// DI crossover detection
bool longBreakout = diPlus[1] <= diMinus[1] and diPlus > diMinus
bool shortBreakout = diMinus[1] <= diPlus[1] and diMinus > diPlus
bool stillBullish = diPlus > diMinus
bool stillBearish = diMinus > diPlus
```

### REENTRY_CONDITION
```pine
        if lastExitDirection == 1 and stillBullish
            longSignal := true
        if lastExitDirection == -1 and stillBearish
            shortSignal := true
```

### SIGNAL_PLOTTING
```pine
// +DI/-DI lines (uses values from main indicator section)
// Already displayed in info table
// Can add separate pane plots if desired
```

---

## 10. Stochastic (Linda Raschke Style)

### Metadata
```
SIGNAL_DISPLAY_NAME = "Stochastic"
SHORT_NAME = "STOCH"
SIGNAL_GROUP_NAME = "STOCHASTIC"
```

### SHOW_SIGNAL_TOGGLE
```pine
showStoch = input.bool(true, "Show Stochastic", group="Feature Toggles",
     tooltip="Display Stochastic %K and %D lines.")
```

### SIGNAL_INPUTS
```pine
stochK = input.int(7, "%K Period", minval=5, maxval=21, group="Stochastic Settings",
     tooltip="Linda Raschke: 7")
stochSlowing = input.int(4, "%K Slowing", minval=1, maxval=10, group="Stochastic Settings")
stochD = input.int(16, "%D Period", minval=3, maxval=30, group="Stochastic Settings",
     tooltip="Linda Raschke: 16")
stochOB = input.int(80, "Overbought", minval=70, maxval=90, group="Stochastic Settings")
stochOS = input.int(20, "Oversold", minval=10, maxval=30, group="Stochastic Settings")
```

### SIGNAL_CALCULATION
```pine
// Stochastic calculation
float stochKVal = ta.sma(ta.stoch(close, high, low, stochK), stochSlowing)
float stochDVal = ta.sma(stochKVal, stochD)
```

### ENTRY_DETECTION
```pine
// Stochastic crossover with zone filtering
bool kCrossAboveD = stochKVal[1] <= stochDVal[1] and stochKVal > stochDVal
bool kCrossBelowD = stochKVal[1] >= stochDVal[1] and stochKVal < stochDVal
bool fromOversold = stochKVal[1] < stochOS or stochKVal < 50
bool fromOverbought = stochKVal[1] > stochOB or stochKVal > 50

bool longBreakout = kCrossAboveD and fromOversold
bool shortBreakout = kCrossBelowD and fromOverbought
bool stillBullish = stochKVal > stochDVal
bool stillBearish = stochKVal < stochDVal
```

### REENTRY_CONDITION
```pine
        if lastExitDirection == 1 and stillBullish
            longSignal := true
        if lastExitDirection == -1 and stillBearish
            shortSignal := true
```

### SIGNAL_PLOTTING
```pine
// Stochastic lines (in separate pane)
plot(showStoch ? stochKVal : na, "%K", color.blue, 2)
plot(showStoch ? stochDVal : na, "%D", color.orange, 2)
hline(stochOB, "Overbought", color.red, hline.style_dashed)
hline(stochOS, "Oversold", color.green, hline.style_dashed)
hline(50, "Middle", color.gray)
```

---

## 11. MACD (Linda Raschke Style)

### Metadata
```
SIGNAL_DISPLAY_NAME = "MACD"
SHORT_NAME = "MACD"
SIGNAL_GROUP_NAME = "MACD"
```

### SHOW_SIGNAL_TOGGLE
```pine
showMACD = input.bool(true, "Show MACD", group="Feature Toggles",
     tooltip="Display MACD histogram.")
```

### SIGNAL_INPUTS
```pine
macdFast = input.int(3, "Fast Period", minval=2, maxval=20, group="MACD Settings",
     tooltip="Linda Raschke: 3")
macdSlow = input.int(10, "Slow Period", minval=5, maxval=50, group="MACD Settings",
     tooltip="Linda Raschke: 10")
macdSignal = input.int(16, "Signal Period", minval=5, maxval=30, group="MACD Settings",
     tooltip="Linda Raschke: 16")
macdUseSma = input.bool(true, "Use SMA (Raschke)", group="MACD Settings",
     tooltip="Use SMA instead of EMA for Linda Raschke style.")
```

### SIGNAL_CALCULATION
```pine
// MACD calculation (SMA or EMA based)
float macdFastMA = macdUseSma ? ta.sma(close, macdFast) : ta.ema(close, macdFast)
float macdSlowMA = macdUseSma ? ta.sma(close, macdSlow) : ta.ema(close, macdSlow)
float macdLine = macdFastMA - macdSlowMA
float macdSignalLine = macdUseSma ? ta.sma(macdLine, macdSignal) : ta.ema(macdLine, macdSignal)
float macdHist = macdLine - macdSignalLine
```

### ENTRY_DETECTION
```pine
// MACD crossover detection
bool longBreakout = macdLine[1] <= macdSignalLine[1] and macdLine > macdSignalLine
bool shortBreakout = macdLine[1] >= macdSignalLine[1] and macdLine < macdSignalLine
bool stillBullish = macdLine > macdSignalLine
bool stillBearish = macdLine < macdSignalLine
```

### REENTRY_CONDITION
```pine
        if lastExitDirection == 1 and stillBullish
            longSignal := true
        if lastExitDirection == -1 and stillBearish
            shortSignal := true
```

### SIGNAL_PLOTTING
```pine
// MACD histogram (in separate pane)
plot(showMACD ? macdHist : na, "Histogram", style=plot.style_columns,
     color = macdHist >= 0 ? color.green : color.red)
plot(showMACD ? macdLine : na, "MACD", color.blue, 2)
plot(showMACD ? macdSignalLine : na, "Signal", color.orange, 2)
hline(0, "Zero", color.gray)
```

---

## ADX Calculation Fallback

If `lgbarn/lw_ind` library is unavailable, use this built-in ADX calculation:

```pine
// Built-in ADX calculation (fallback)
[diPlusBuiltin, diMinusBuiltin, adxBuiltin] = ta.dmi(adxPeriod, adxPeriod)

// Use these instead:
float diPlus = diPlusBuiltin
float diMinus = diMinusBuiltin
float adxValue = adxBuiltin
```
