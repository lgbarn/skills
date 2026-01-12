# Pine Script State Management

State persistence, arrays, maps, and custom types for TradingView Pine Script.

---

## `var` vs `varip` Distinction

Understanding when to use each is critical for correct indicator behavior:

| Keyword | Behavior | Use Case |
|---------|----------|----------|
| `var` | Persists across all bars (historical + realtime) | Session totals, running sums, historical tracking |
| `varip` | Persists only in realtime (resets on historical bars) | Realtime-only state, intrabar tracking |

```pine
// var - value persists historically
var float sessionHigh = na
var float runningVWAP = 0.0

// varip - only persists in realtime, resets on historical bars
varip bool alertTriggered = false
varip int tickCount = 0
```

**When to use `varip`:**
- Tracking events that should only fire once in realtime
- Intrabar tick counting
- Alert state that shouldn't replay on historical bars

---

## Persistent Variables

```pine
var float runningTotal = 0.0
var int barCount = 0
var bool sessionActive = false
var float sessionHigh = na
var float sessionLow = na
```

---

## Arrays

### Declaration
```pine
var array<float> levels = array.new<float>()
var array<line> lines = array.new<line>()
var array<label> labels = array.new<label>()
```

### Common Operations
```pine
// Add element
array.push(levels, newValue)

// Get element (with bounds check)
if array.size(levels) > 0
    lastLevel = array.get(levels, array.size(levels) - 1)

// Remove oldest (FIFO)
if array.size(levels) >= MAX_SIZE
    array.shift(levels)

// Clear array
array.clear(levels)

// Iterate
for i = 0 to array.size(levels) - 1
    value = array.get(levels, i)
```

### Safe Array Access
```pine
// Always validate array indices before access
safeIndex = math.min(array.size(myArray) - 1, requestedIndex)
safeIndex := math.max(0, safeIndex)
value = array.get(myArray, safeIndex)

// Check size before operations
if array.size(levels) > 0
    lastLevel = array.get(levels, array.size(levels) - 1)

// Limit array growth
if array.size(history) >= MAX_HISTORY_SIZE
    array.shift(history)  // Remove oldest
array.push(history, newValue)
```

---

## Maps (Pine v5+)

```pine
var map<string, float> pivotLevels = map.new<string, float>()

// Set values
map.put(pivotLevels, "R1", resistance1)
map.put(pivotLevels, "S1", support1)

// Get values
r1Value = map.get(pivotLevels, "R1")

// Check existence
if map.contains(pivotLevels, "R2")
    // use R2
```

---

## Custom Types

### Type Definition
```pine
type SessionRange
    float high
    float low
    float mid
    line highLine
    line lowLine
    label highLabel
    label lowLabel
    box rangeBox
```

### Type Instantiation
```pine
var SessionRange currentSession = SessionRange.new()

// Or with initial values
var SessionRange ib = SessionRange.new(
    high = na,
    low = na,
    mid = na,
    highLine = na,
    lowLine = na,
    highLabel = na,
    lowLabel = na,
    rangeBox = na
)
```

### Methods on Types
```pine
method deleteGraphics(SessionRange sr) =>
    line.delete(sr.highLine)
    line.delete(sr.lowLine)
    label.delete(sr.highLabel)
    label.delete(sr.lowLabel)
    box.delete(sr.rangeBox)

method updateLines(SessionRange sr, int endBar) =>
    if not na(sr.highLine)
        line.set_x2(sr.highLine, endBar)
    if not na(sr.lowLine)
        line.set_x2(sr.lowLine, endBar)

method reset(SessionRange sr) =>
    sr.deleteGraphics()
    sr.high := na
    sr.low := na
    sr.mid := na
```

---

## Complex State Example

```pine
type VWAPState
    float sumPV
    float sumV
    float sumSquaredPV
    float vwap
    float stdDev

var VWAPState daily = VWAPState.new(0.0, 0.0, 0.0, na, na)
var VWAPState weekly = VWAPState.new(0.0, 0.0, 0.0, na, na)

method reset(VWAPState state) =>
    state.sumPV := 0.0
    state.sumV := 0.0
    state.sumSquaredPV := 0.0
    state.vwap := na
    state.stdDev := na

method update(VWAPState state, float tp, float vol) =>
    state.sumPV += tp * vol
    state.sumV += vol
    state.sumSquaredPV += (tp * tp) * vol
    if state.sumV > 0
        state.vwap := state.sumPV / state.sumV
        variance = (state.sumSquaredPV / state.sumV) - (state.vwap * state.vwap)
        state.stdDev := math.sqrt(math.max(0, variance))
```
