# Pine Script Performance & Optimization

Performance optimization, bar states, common calculations, and resource limits for TradingView Pine Script.

---

## Bar State Awareness

Understanding bar states is essential for correct indicator behavior:

| State | When True | Common Use |
|-------|-----------|------------|
| `barstate.isfirst` | First bar of dataset | Initialize arrays, maps, resources |
| `barstate.islast` | Current/rightmost bar | Update drawings, final positioning |
| `barstate.islastconfirmedhistory` | Last historical bar before realtime | One-time historical summary |
| `barstate.isrealtime` | Processing realtime data | Realtime-only operations |
| `barstate.isnew` | First tick of a new bar | Bar-based resets |
| `barstate.isconfirmed` | Bar has closed | Confirmed signals only |

### Common Patterns

```pine
// Initialize resources on first bar
if barstate.isfirst
    var array<float> levels = array.new<float>()
    var map<string, float> pivots = map.new<string, float>()

// Update drawings only on last bar (performance)
if barstate.islast
    label.set_xy(myLabel, bar_index, high)
    line.set_x2(myLine, bar_index)

// Historical processing complete
if barstate.islastconfirmedhistory
    log.info("Historical processing complete: " + str.tostring(bar_index) + " bars")

// Realtime-only operations
if barstate.isrealtime
    varip int tickCount = 0
    tickCount += 1

// Confirmed bar signals only (avoid repainting)
if barstate.isconfirmed
    if crossoverCondition
        alert("Signal confirmed", alert.freq_once_per_bar)
```

### Guard Clauses

Use early returns to prevent processing before sufficient data:

```pine
// Guard: Not enough bars for calculation
if bar_index < requiredBars
    return

// Guard: Avoid processing on first bar
if barstate.isfirst
    return

// Guard: Only process confirmed bars
if not barstate.isconfirmed
    return
```

---

## Performance Optimization

### Avoid Redundant Calculations

```pine
// Bad: Recalculates every bar
currentHour = hour(time, timeZone)
currentMinute = minute(time, timeZone)
totalMinutes = currentHour * 60 + currentMinute

// Good: Calculate once, reuse
cached_totalMinutes = hour(time, timeZone) * 60 + minute(time, timeZone)
```

### Use `var` for Persistence

```pine
// Bad: Reinitializes every bar
runningSum = 0.0

// Good: Persists across bars
var float runningSum = 0.0
```

### Limit Graphics to Last Bar

```pine
// Only draw/update on last bar
if barstate.islast
    // Drawing operations here
```

### Clean Up Old Objects

```pine
// Delete previous before creating new
label.delete(myLabel[1])
myLabel := label.new(...)
```

---

## Mathematical Stability

Prevent runtime errors from invalid mathematical operations:

```pine
// Clamp negative variance before sqrt (float precision can cause negative)
variance = math.max(0, rawVariance)
stdDev = math.sqrt(variance)

// Prevent division by zero
vwap = sumVolume > 0 ? sumPriceVolume / sumVolume : typicalPrice

// Handle na values
safeValue = na(inputValue) ? defaultValue : inputValue

// Prevent log of zero or negative
logValue = value > 0 ? math.log(value) : na
```

---

## Common Calculations

### VWAP
```pine
var float sumPV = 0.0
var float sumV = 0.0

typicalPrice = (high + low + close) / 3
sumPV += typicalPrice * volume
sumV += volume
vwap = sumV > 0 ? sumPV / sumV : typicalPrice
```

### Standard Deviation Bands
```pine
var float sumSquaredPV = 0.0
sumSquaredPV += (typicalPrice * typicalPrice) * volume
variance = sumV > 0 ? (sumSquaredPV / sumV) - (vwap * vwap) : 0
stdDev = math.sqrt(math.max(0, variance))
upperBand = vwap + (multiplier * stdDev)
lowerBand = vwap - (multiplier * stdDev)
```

### Session High/Low
```pine
var float sessionHigh = na
var float sessionLow = na

if isSessionStart()
    sessionHigh := high
    sessionLow := low
else if withinWindow()
    sessionHigh := math.max(sessionHigh, high)
    sessionLow := math.min(sessionLow, low)
```

### Extension Levels
```pine
range = sessionHigh - sessionLow
mid = (sessionHigh + sessionLow) / 2

ext_1x_upper = sessionHigh + range
ext_1x_lower = sessionLow - range
ext_1_5x_upper = sessionHigh + (range * 1.5)
ext_1_5x_lower = sessionLow - (range * 1.5)
```

---

## Resource Limits

Set appropriate limits in indicator declaration:

```pine
indicator("Name",
    max_bars_back=500,      // Historical bars for arrays/series
    max_labels_count=500,   // Maximum label objects
    max_lines_count=500,    // Maximum line objects
    max_boxes_count=500)    // Maximum box objects
```

### Guidelines by Indicator Complexity

| Type | max_bars_back | max_labels/lines/boxes |
|------|---------------|------------------------|
| Simple indicator | 100-200 | 50-100 |
| Session-based | 500 | 200-300 |
| Multi-session history | 500+ | 500 |
| Pro composite | 500 | 500 |

---

## Plotting Patterns

### Conditional Plot
```pine
plot(enableFeature and showLine ? value : na,
    title="Feature",
    color=featureColor,
    linewidth=featureWidth)
```

### Band Fill
```pine
upperPlot = plot(showBands ? upperValue : na, display=display.none, editable=false)
lowerPlot = plot(showBands ? lowerValue : na, display=display.none, editable=false)
fill(upperPlot, lowerPlot, color=color.new(bandColor, 90), title="Band Fill")
```

### Style Conversion
```pine
plotStyle = styleInput == "Dashed" ? plot.style_linebr :
            styleInput == "Dotted" ? plot.style_circles :
            plot.style_line
```

---

## Drawing Objects

### Lines
```pine
if barstate.islast
    if na(myLine)
        myLine := line.new(startBar, startPrice, bar_index, endPrice,
            color=lineColor, width=lineWidth, style=line.style_solid)
    else
        line.set_xy1(myLine, startBar, startPrice)
        line.set_xy2(myLine, bar_index, endPrice)
```

### Labels
```pine
if barstate.islast
    label.delete(myLabel[1])
    myLabel := label.new(bar_index, price, text="Label",
        color=color.new(color.black, 80),
        textcolor=color.white,
        style=label.style_label_left,
        size=size.small)
```

### Tables (Dashboards)
```pine
var table dashboard = table.new(position.top_right, 2, 4,
    bgcolor=color.new(color.black, 80),
    frame_color=color.gray,
    frame_width=1)

if barstate.islast
    table.cell(dashboard, 0, 0, "Title", text_color=color.white, text_size=size.small)
    table.cell(dashboard, 1, 0, str.tostring(value, "#.##"), text_color=valueColor)
```
