# Tradovate Patterns Reference

Detailed conventions and patterns for Tradovate JavaScript indicators.

## File Structure

```javascript
// Imports
const predef = require("./tools/predef");
const meta = require("./tools/meta");

// Helper functions

// Main class
class IndicatorNameLB {
  init() { }
  map(d, i, history) { }
  filter(d) { }
}

// Module exports
module.exports = { ... };
```

---

## Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Standard | `*LB.js` | `initialBalanceLB.js` |
| Pro/Composite | `*ProLB.js` | `PullbackProLB.js` |
| camelCase | lowercase start | `lbTWAP.js` |

### Class Names
```javascript
class IndicatorNameLB { }     // Standard
class PullbackProLB { }       // Pro
```

### Module Name
```javascript
module.exports = {
  name: "indicatorNameLB",    // lowercase, no spaces
  // ...
};
```

---

## Imports

### Core Imports
```javascript
const predef = require("./tools/predef");
const meta = require("./tools/meta");
const { ParamType } = meta;
```

### Calculator Imports
```javascript
const EMA = require("./tools/EMA");
const SMA = require("./tools/SMA");
const MovingHigh = require("./tools/MovingHigh");
const MovingLow = require("./tools/MovingLow");
const typicalPrice = require("./tools/typicalPrice");
```

### Graphics Imports (Advanced)
```javascript
const { px, du, op, min } = require("./tools/graphics");
const p = require("./tools/plotting");
```

---

## init() Method

Initialize state and calculators:

```javascript
init() {
  // ─── Calculators ───
  this.ema = EMA(this.props.period);
  this.sma = SMA(this.props.signal);
  this.highest = MovingHigh(this.props.lookback);
  this.lowest = MovingLow(this.props.lookback);

  // ─── Session State ───
  this.currentSessionDate = null;
  this.sessionActive = false;

  // ─── Tracking Variables ───
  this.sessionHigh = null;
  this.sessionLow = null;
  this.cumulativeSum = 0;
  this.count = 0;

  // ─── Arrays ───
  this.values = [];
  this.pivotHighs = [];
  this.pivotLows = [];

  // ─── Maps (for complex data) ───
  this.sessionProfile = new Map();
}
```

---

## map() Method

### Parameters
```javascript
map(d, i, history) {
  // d - Current bar data object
  // i - Current bar index (0-based)
  // history - History accessor
}
```

### Bar Data Methods (d)
```javascript
d.high()        // Bar high
d.low()         // Bar low
d.close()       // Bar close
d.open()        // Bar open
d.timestamp()   // JavaScript Date object
d.volume()      // Bar volume
d.isLast()      // True if last bar
d.index()       // Bar index for graphics
d.tradeDate()   // Trading date
d.profile()     // Volume profile data (if available)
```

### History Access
```javascript
// Previous bar
const prev = history.prior();
if (prev) {
  const prevClose = prev.close();
  const prevHigh = prev.high();
}

// Specific bar by index
const bar = history.get(i - 5);

// Full data array
const oldBar = history.data[i - 10];
```

### Return Object
```javascript
return {
  // Plot values
  mainValue: calculatedValue,
  upperBand: upperValue,
  lowerBand: lowerValue,

  // Conditional values
  signal: condition ? signalValue : undefined,

  // Bar coloring (optional)
  barColor: "#FFFFFF",

  // Graphics (only on last bar)
  graphics: d.isLast() ? { items: [...] } : undefined,
};
```

---

## filter() Method

Controls which bars are displayed:

```javascript
// Simple: has valid data
filter(d) {
  return d.mainValue !== undefined;
}

// Multiple conditions
filter(d) {
  return d.value1 !== undefined || d.value2 !== undefined;
}

// Using predef helper
filter(d) {
  return predef.filters.isNumber(d.value);
}
```

---

## Parameters (params)

### Using predef.paramSpecs
```javascript
params: {
  // Boolean toggle
  enabled: predef.paramSpecs.bool(true),

  // Period (integer)
  period: predef.paramSpecs.period(14),

  // Enumeration
  source: predef.paramSpecs.enum(
    {
      close: "Close",
      open: "Open",
      hl2: "HL2",
      hlc3: "HLC3",
      ohlc4: "OHLC4"
    },
    "hlc3"  // default
  ),
}
```

### Custom Number Helper
```javascript
function number(defValue, step, min, max) {
  return {
    type: ParamType.NUMBER,
    def: defValue,
    restrictions: {
      step: step || 1,
      min: min >= 0 ? min : 0,
      max: max,
    },
  };
}

// Usage
params: {
  multiplier: number(1.0, 0.1, 0.1, 5.0),
  startHour: number(9, 1, 0, 23),
  duration: number(60, 5, 5, 240),
}
```

---

## Plots

### Basic Plot Definition
```javascript
plots: {
  value: { title: "Value" },
}
```

### With Color
```javascript
plots: {
  vwap: { title: "VWAP", color: "#CE95D8" },
}
```

### With Line Properties
```javascript
plots: {
  signal: {
    title: "Signal",
    color: "#FFD700",
    lineWidth: 2,
    lineStyle: "dash",  // or "dots"
  },
}
```

### Arrow Plots
```javascript
plots: {
  entryUp: { title: "Long Entry", color: "#00FF00", plotType: "arrows_up" },
  entryDown: { title: "Short Entry", color: "#FF0000", plotType: "arrows_down" },
}
```

---

## Scheme Styles

```javascript
schemeStyles: {
  dark: {
    mainValue: predef.styles.plot("#CE95D8", 2),      // Color, width
    upperBand: predef.styles.plot("#40a9ff", 1),
    lowerBand: predef.styles.plot("#40a9ff", 1),
  },
}
```

### Style Options
```javascript
predef.styles.plot(color, lineWidth)
predef.styles.plot({ color: "#HEXCOLOR", lineStyle: 1, lineWidth: 2 })
// lineStyle: 1 = solid, 3 = dash
```

---

## Session Handling

### Session Reset Pattern
```javascript
map(d, i, history) {
  const timestamp = d.timestamp();
  const currentDate = timestamp.toDateString();

  // Check for new trading day
  if (this.currentSessionDate && this.currentSessionDate !== currentDate) {
    this.resetSession();
  }
  this.currentSessionDate = currentDate;
}

resetSession() {
  this.sessionHigh = null;
  this.sessionLow = null;
  this.sessionActive = false;
}
```

### Time-Based Session Start
```javascript
const hour = timestamp.getHours();
const minute = timestamp.getMinutes();
const currentTimeMinutes = hour * 60 + minute;
const startTimeMinutes = this.props.startHour * 60 + this.props.startMinute;

let isSessionStart = false;
if (history.prior()) {
  const priorTimestamp = history.prior().timestamp();
  const priorTimeMinutes = priorTimestamp.getHours() * 60 + priorTimestamp.getMinutes();

  if (priorTimeMinutes < startTimeMinutes && currentTimeMinutes >= startTimeMinutes) {
    isSessionStart = true;
  }
}
```

### "Hacky" Time Comparison (Tick Chart Compatible)
```javascript
const time = +("" + hour + (minute < 10 ? "0" : "") + minute);
const startTime = +("" + startHour + (startMinute < 10 ? "0" : "") + startMinute);

if (priorTime < startTime && time >= startTime) {
  isSessionStart = true;
}
```

---

## Graphics

### Text Labels (on last bar)
```javascript
graphics: d.isLast() && {
  items: [
    {
      tag: "Text",
      key: "uniqueKey",
      point: {
        x: d.index() + labelOffset,
        y: priceLevel,
      },
      text: "Label Text",
      style: {
        fontSize: 9,
        fontWeight: "bold",
        fill: "#00FF00",
      },
      textAlignment: "centerMiddle",
    },
  ],
}
```

### Using Graphics Utilities
```javascript
const { px, du, op } = require("./tools/graphics");

point: {
  x: du(d.index() + offset),
  y: op(du(price), "-", px(0)),
}
```

### ScaleBound Values (Critical)

**Source**: [Tradovate Custom Indicators - Graphics](https://tradovate.github.io/custom-indicators/pages/Tutorial/Graphics.html)

When declaring points for graphics, you MUST use ScaleBound values with special helper operators:

| Operator | Description | Example |
|----------|-------------|---------|
| `px(n)` | Pixel units - absolute screen pixels | `px(5)` = 5 pixels |
| `du(n)` | Domain units - X: bar index, Y: price | `du(d.index())`, `du(1234.50)` |
| `op(a, op, b)` | Combine values | `op(du(price), "+", px(10))` |

```javascript
const { px, du, op, min, max } = require("./tools/graphics");

// Position text label 5 bars to the right and 10 pixels above price
point: {
  x: du(d.index() + 5),
  y: op(du(priceLevel), "+", px(10)),
}

// Price in domain units (required for Y-axis)
linePoint: {
  x: du(barIndex),
  y: du(supportLevel),  // du() required for price values
}

// Combine operations
point: {
  x: op(du(startBar), "+", px(labelOffset)),
  y: max(du(highPrice), du(prevHigh)),  // Use the higher value
}
```

### Complete Graphics Example

```javascript
map(d, i, history) {
  const graphics = d.isLast() ? {
    items: [
      // Horizontal line at price level
      {
        tag: "Line",
        key: "supportLine",
        a: { x: du(startBarIndex), y: du(supportPrice) },
        b: { x: du(d.index()), y: du(supportPrice) },
        style: {
          stroke: "#00FF00",
          strokeWidth: 2,
          dash: [5, 3],  // Dashed line
        },
      },
      // Text label
      {
        tag: "Text",
        key: "supportLabel",
        point: {
          x: op(du(d.index()), "+", px(5)),
          y: du(supportPrice),
        },
        text: `Support: ${supportPrice.toFixed(2)}`,
        style: {
          fontSize: 10,
          fontWeight: "bold",
          fill: "#00FF00",
        },
        textAlignment: "centerMiddle",
      },
    ],
  } : undefined;

  return {
    value: calculatedValue,
    graphics,
  };
}
```

---

## Validation

```javascript
validate(obj) {
  if (obj.slow < obj.fast) {
    return meta.error("slow", "Slow period should be larger than fast period");
  }
  if (obj.period < 1) {
    return meta.error("period", "Period must be at least 1");
  }
  // Return nothing if valid
}
```

---

## Tags

Always include author tag:
```javascript
tags: ["Luther Barnum"]
```

With category tags:
```javascript
tags: ["Luther Barnum", predef.tags.Oscillators]
```

---

## Color Palette

### Standard Colors
```javascript
// Bullish
"#00FF00"  // Lime
"#008000"  // Green
"#1E90FF"  // Dodger blue

// Bearish
"#FF0000"  // Red
"#800000"  // Maroon
"#8B0000"  // Dark red

// Neutral
"#FFD700"  // Gold
"#FFFF00"  // Yellow
"#808080"  // Gray

// Features
"#CE95D8"  // Orchid (VWAP)
"#00FFFF"  // Cyan
"#FF00FF"  // Magenta
"#dd7a28"  // Orange

// Bands
"#40a9ff"  // Light blue (upper)
"#1e88e5"  // Medium blue
"#0d47a1"  // Dark blue (lower)
```

---

## Calculator Usage

### EMA
```javascript
// In init()
this.ema = EMA(this.props.period);

// In map()
const value = this.ema(close);

// Access previous value
const prevValue = this.ema.prev();
```

### SMA
```javascript
this.sma = SMA(this.props.period);
const value = this.sma(close);
```

### MovingHigh/Low
```javascript
this.highest = MovingHigh(this.props.lookback);
this.lowest = MovingLow(this.props.lookback);

const high = this.highest(d.high());
const low = this.lowest(d.low());
```

---

## Common Patterns

### Conditional Return
```javascript
return {
  mainValue: calculatedValue,
  fastMA: this.props.showMAs ? fastValue : undefined,
  slowMA: this.props.showMAs ? slowValue : undefined,
  signal: condition ? signalValue : undefined,
};
```

### Array Tracking with Fallback
```javascript
if (pivotHigh !== null) {
  result.pivotHigh = pivotHigh;
  this.pivotHighPrices[i] = pivotHigh;
} else {
  this.pivotHighPrices[i] = this.pivotHighPrices[i - 1] || d.high();
}
```

### Rolling Window
```javascript
if (type === "rolling") {
  const period = this.props.rollingPeriod + 1;
  const pastData = history.data[i - period];
  if (pastData) {
    const pastValue = (pastData.high() + pastData.low() + pastData.close()) / 3;
    this.cumulativeSum -= pastValue;
    this.count -= 1;
  }
}
```

### Bar Coloring
```javascript
getBarColor(open, close, signal) {
  if (close > signal && open > signal) {
    return "#1E90FF";  // Bullish
  } else if (close < signal && open < signal) {
    return "#FF0000";  // Bearish
  }
  return "#FFFF00";    // Neutral
}

// In map()
return {
  barColor: this.props.colorBars ? this.getBarColor(open, close, signal) : undefined,
};
```

---

## Module Export Template

```javascript
module.exports = {
  name: "indicatorNameLB",
  description: "User-friendly description",
  calculator: IndicatorNameLB,

  params: {
    // Feature toggles first
    enabled: predef.paramSpecs.bool(true),
    showBands: predef.paramSpecs.bool(false),

    // Calculation params
    period: predef.paramSpecs.period(14),
    multiplier: number(1.0, 0.1, 0.1, 5.0),

    // Session params
    startHour: number(9, 1, 0, 23),
    startMinute: number(30, 1, 0, 59),
  },

  plots: {
    mainValue: { title: "Main" },
    upperBand: { title: "Upper" },
    lowerBand: { title: "Lower" },
  },

  inputType: meta.InputType.BARS,
  areaChoice: meta.AreaChoice.MAIN,  // or NEW for separate pane

  tags: ["Luther Barnum"],

  schemeStyles: {
    dark: {
      mainValue: predef.styles.plot("#CE95D8", 2),
      upperBand: predef.styles.plot("#40a9ff", 1),
      lowerBand: predef.styles.plot("#40a9ff", 1),
    },
  },

  validate(obj) {
    // Optional validation
  },
};
```

---

## Volume Profile Access

```javascript
const volumeProfile = d.profile();

if (volumeProfile && volumeProfile.length) {
  for (let i = 0; i < volumeProfile.length; ++i) {
    const level = volumeProfile[i];
    const vol = level[this.props.volType];  // "vol", "bidVol", "askVol"
    const price = level.price;
    // Process level
  }
}
```

For volume profile indicators, add:
```javascript
requirements: {
  volumeProfiles: true,
},
```

---

## Performance Optimization

### Graphics Only on Last Bar

Graphics rendering is expensive. Only render on the last bar:

```javascript
map(d, i, history) {
  // Calculations run on every bar
  const value = this.calculate(d);

  // Graphics ONLY on last bar
  const graphics = d.isLast() ? this.createGraphics(d) : undefined;

  return { value, graphics };
}
```

### Cache Repeated Calculations

```javascript
init() {
  // Pre-compute constants
  this.startTimeMinutes = this.props.startHour * 60 + this.props.startMinute;
  this.endTimeMinutes = this.props.endHour * 60 + this.props.endMinute;
}

map(d, i, history) {
  // Use cached values instead of recalculating
  const currentMinutes = d.timestamp().getHours() * 60 + d.timestamp().getMinutes();
  const isWithinSession = currentMinutes >= this.startTimeMinutes &&
                          currentMinutes < this.endTimeMinutes;
}
```

### Limit Array Size

```javascript
const MAX_HISTORY = 500;

map(d, i, history) {
  // Track values in array
  this.values.push(calculatedValue);

  // Prevent unbounded growth
  if (this.values.length > MAX_HISTORY) {
    this.values.shift();  // Remove oldest
  }
}
```

### Use Calculator Instances Efficiently

```javascript
init() {
  // Create calculators once in init()
  this.ema = EMA(this.props.period);
  this.sma = SMA(this.props.signal);
}

map(d, i, history) {
  // Reuse calculator instances
  const emaValue = this.ema(d.close());
  const smaValue = this.sma(d.close());
}
```

### Conditional Feature Calculation

```javascript
map(d, i, history) {
  let bands = undefined;

  // Only calculate if feature is enabled
  if (this.props.showBands) {
    bands = {
      upper: value + stdDev * this.props.multiplier,
      lower: value - stdDev * this.props.multiplier,
    };
  }

  return {
    mainValue: value,
    upperBand: bands?.upper,
    lowerBand: bands?.lower,
  };
}
```

### Mathematical Stability

```javascript
// Prevent division by zero
const vwap = this.sumVolume > 0 ? this.sumPriceVolume / this.sumVolume : typicalPrice;

// Clamp variance before sqrt
const variance = Math.max(0, rawVariance);
const stdDev = Math.sqrt(variance);

// Safe array access
const prevValue = i > 0 ? history.data[i - 1]?.close() : d.close();
```

### History Access Optimization

```javascript
// GOOD - access history once
const prior = history.prior();
if (prior) {
  const prevClose = prior.close();
  const prevHigh = prior.high();
  const prevLow = prior.low();
}

// BAD - multiple history accesses
const prevClose = history.prior()?.close();  // First access
const prevHigh = history.prior()?.high();    // Second access (redundant)
```
