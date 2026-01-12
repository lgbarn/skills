# Pine Script Functions & Session Handling

Function documentation patterns and session time handling for TradingView Pine Script.

---

## Function Documentation

**Source**: [TradingView Style Guide](https://www.tradingview.com/pine-script-docs/writing/style-guide/)

Use library-style annotations for all user-defined functions. This makes code portable to libraries and easier to understand.

### Annotation Syntax

```pine
// @function   Brief description of what the function does
// @param      paramName (type) Description of parameter
// @returns    (type) Description of return value
// Dependencies: List any global variables used
functionName(paramType paramName) =>
    // implementation
```

### Complete Examples

```pine
// @function   Calculates session VWAP from cumulative price*volume and volume
// @param      sumPV (float) Cumulative sum of typical price * volume
// @param      sumV (float) Cumulative sum of volume
// @returns    (float) VWAP value, or na if volume is zero
// Dependencies: None (pure function)
calcVWAP(float sumPV, float sumV) =>
    sumV > 0 ? sumPV / sumV : na

// @function   Determines if current bar is within the trading session window
// @param      startMinutes (int) Session start in minutes from midnight
// @param      endMinutes (int) Session end in minutes from midnight
// @param      currentMinutes (int) Current time in minutes from midnight
// @returns    (bool) True if within session window
// Dependencies: None
isWithinSession(int startMinutes, int endMinutes, int currentMinutes) =>
    if endMinutes < startMinutes  // Crosses midnight
        currentMinutes >= startMinutes or currentMinutes < endMinutes
    else
        currentMinutes >= startMinutes and currentMinutes < endMinutes
```

### Method Documentation

```pine
// @function   Extends session range lines to the current bar
// @param      sr (SessionRange) The session range object to update
// @param      endBar (int) Bar index to extend lines to
// @returns    (void)
method updateLines(SessionRange sr, int endBar) =>
    if not na(sr.highLine)
        line.set_x2(sr.highLine, endBar)
    if not na(sr.lowLine)
        line.set_x2(sr.lowLine, endBar)
```

---

## Session Handling

### Time Calculation Caching

Cache time conversions to avoid redundant calculations:

```pine
cached_hour = hour(time, timeZone)
cached_minute = minute(time, timeZone)
cached_totalMinutes = cached_hour * 60 + cached_minute
```

### Session Window Constants

```pine
var int session_startMinutes = startHour * 60 + startMinute
var int session_endMinutes = endHour * 60 + endMinute
var bool session_crossesMidnight = session_endMinutes < session_startMinutes
```

### Within Window Check

```pine
withinWindow() =>
    if session_crossesMidnight
        cached_totalMinutes >= session_startMinutes or cached_totalMinutes < session_endMinutes
    else
        cached_totalMinutes >= session_startMinutes and cached_totalMinutes < session_endMinutes
```

### Session Start Detection

```pine
isSessionStart() =>
    prev_minutes = hour(time[1], timeZone) * 60 + minute(time[1], timeZone)
    crossed = prev_minutes < session_startMinutes and cached_totalMinutes >= session_startMinutes
    // Handle midnight crossing
    if session_crossesMidnight
        crossed or (prev_minutes > cached_totalMinutes and cached_totalMinutes >= session_startMinutes)
    else
        crossed
```

### Session End Detection

```pine
isSessionEnd() =>
    prev_minutes = hour(time[1], timeZone) * 60 + minute(time[1], timeZone)
    if session_crossesMidnight
        prev_minutes < session_endMinutes and cached_totalMinutes >= session_endMinutes
    else
        prev_minutes < session_endMinutes and cached_totalMinutes >= session_endMinutes
```

---

## Complete Session Handling Example

```pine
// ═══ SESSION INPUTS ═══
timeZone = input.string("America/New_York", "Time Zone", group="Session")
startHour = input.int(9, "Start Hour", inline="start", group="Session")
startMinute = input.int(30, "Min", inline="start", group="Session")
endHour = input.int(16, "End Hour", inline="end", group="Session")
endMinute = input.int(0, "Min", inline="end", group="Session")

// ═══ SESSION CONSTANTS ═══
var int session_start = startHour * 60 + startMinute
var int session_end = endHour * 60 + endMinute
var bool crosses_midnight = session_end < session_start

// ═══ CACHED TIME CALCULATIONS ═══
cached_minutes = hour(time, timeZone) * 60 + minute(time, timeZone)
prev_minutes = hour(time[1], timeZone) * 60 + minute(time[1], timeZone)

// ═══ SESSION FUNCTIONS ═══
isInSession() =>
    if crosses_midnight
        cached_minutes >= session_start or cached_minutes < session_end
    else
        cached_minutes >= session_start and cached_minutes < session_end

isSessionStart() =>
    wasOut = not (crosses_midnight ?
        (prev_minutes >= session_start or prev_minutes < session_end) :
        (prev_minutes >= session_start and prev_minutes < session_end))
    isIn = isInSession()
    wasOut and isIn

// ═══ SESSION STATE ═══
var float sessionHigh = na
var float sessionLow = na

if isSessionStart()
    sessionHigh := high
    sessionLow := low
else if isInSession()
    sessionHigh := math.max(sessionHigh, high)
    sessionLow := math.min(sessionLow, low)
```

---

## Helper Function Patterns

### Pure Calculation Functions

```pine
// @function   Calculates standard deviation from running sums
// @param      sumSquaredPV (float) Sum of (price^2 * volume)
// @param      sumV (float) Sum of volume
// @param      mean (float) Current mean (VWAP)
// @returns    (float) Standard deviation, clamped to prevent negative sqrt
calcStdDev(float sumSquaredPV, float sumV, float mean) =>
    if sumV <= 0
        0.0
    else
        variance = (sumSquaredPV / sumV) - (mean * mean)
        math.sqrt(math.max(0, variance))
```

### Extension Level Calculations

```pine
// @function   Calculates extension levels from a range
// @param      high (float) Range high
// @param      low (float) Range low
// @param      multiplier (float) Extension multiplier (e.g., 1.0, 1.5, 2.0)
// @returns    [float, float] Upper and lower extension levels
calcExtensions(float high, float low, float multiplier) =>
    range = high - low
    [high + (range * multiplier), low - (range * multiplier)]
```
