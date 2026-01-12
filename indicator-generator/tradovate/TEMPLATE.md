# Tradovate JavaScript Indicator Template

Use this template as the starting point for new Tradovate indicators.

## Complete Template

```javascript
const predef = require("./tools/predef");
const meta = require("./tools/meta");
const EMA = require("./tools/EMA");
const SMA = require("./tools/SMA");
const { ParamType } = meta;

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Create a number parameter with constraints
 * @param {number} defValue - Default value
 * @param {number} step - Step increment
 * @param {number} min - Minimum value
 * @param {number} max - Maximum value (optional)
 */
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

/**
 * Convert time to minutes for comparison
 */
function timeToMinutes(hour, minute) {
  return hour * 60 + minute;
}

// ============================================================================
// MAIN INDICATOR CLASS
// ============================================================================

class [INDICATOR_NAME]LB {
  /**
   * Initialize state and calculators
   * Called once before processing bars
   */
  init() {
    // ─── Calculators ───
    this.ema = EMA(this.props.period);
    this.sma = SMA(this.props.period);

    // ─── Session State ───
    this.currentSessionDate = null;
    this.sessionActive = false;

    // ─── Tracking Variables ───
    this.sessionHigh = null;
    this.sessionLow = null;
    this.cumulativeValue = 0;
    this.count = 0;

    // ─── Arrays for Historical Data ───
    this.values = [];
  }

  /**
   * Main calculation loop
   * @param {Object} d - Current bar data
   * @param {number} i - Current bar index
   * @param {Object} history - History accessor
   */
  map(d, i, history) {
    const timestamp = d.timestamp();
    const hour = timestamp.getHours();
    const minute = timestamp.getMinutes();
    const currentDate = timestamp.toDateString();

    const high = d.high();
    const low = d.low();
    const close = d.close();
    const open = d.open();

    // ─── Session Reset Check ───
    if (this.currentSessionDate && this.currentSessionDate !== currentDate) {
      this.resetSession();
    }
    this.currentSessionDate = currentDate;

    // ─── Session Start Detection ───
    const { startHour, startMinute, endHour, endMinute } = this.props;
    const startTimeMinutes = timeToMinutes(startHour, startMinute);
    const endTimeMinutes = timeToMinutes(endHour, endMinute);
    const currentTimeMinutes = timeToMinutes(hour, minute);

    let isSessionStart = false;
    if (history.prior()) {
      const priorTimestamp = history.prior().timestamp();
      const priorTimeMinutes = timeToMinutes(
        priorTimestamp.getHours(),
        priorTimestamp.getMinutes()
      );
      if (priorTimeMinutes < startTimeMinutes && currentTimeMinutes >= startTimeMinutes) {
        isSessionStart = true;
      }
    }

    // ─── Session Start ───
    if (isSessionStart) {
      this.sessionHigh = high;
      this.sessionLow = low;
      this.sessionActive = true;
      this.cumulativeValue = 0;
      this.count = 0;
    }

    // ─── Within Session Window ───
    const inSessionWindow = currentTimeMinutes >= startTimeMinutes &&
                           currentTimeMinutes < endTimeMinutes;

    // ─── Main Calculation ───
    let mainValue = undefined;
    let upperBand = undefined;
    let lowerBand = undefined;

    if (this.props.enableFeature && this.sessionActive) {
      // Track session high/low
      if (inSessionWindow) {
        this.sessionHigh = Math.max(this.sessionHigh, high);
        this.sessionLow = Math.min(this.sessionLow, low);
      }

      // Example: EMA calculation
      const typicalPrice = (high + low + close) / 3;
      mainValue = this.ema(typicalPrice);

      // Store for later use
      this.values[i] = mainValue;

      // Optional bands
      if (this.props.showBands && mainValue !== undefined) {
        const range = this.sessionHigh - this.sessionLow;
        const multiplier = this.props.multiplier;
        upperBand = mainValue + (range * multiplier);
        lowerBand = mainValue - (range * multiplier);
      }
    }

    // ─── Build Result ───
    const result = {};

    if (mainValue !== undefined) {
      result.mainValue = mainValue;
    }
    if (upperBand !== undefined) {
      result.upperBand = upperBand;
    }
    if (lowerBand !== undefined) {
      result.lowerBand = lowerBand;
    }
    if (this.sessionHigh !== null) {
      result.sessionHigh = this.sessionHigh;
      result.sessionLow = this.sessionLow;
    }

    // ─── Graphics (only on last bar) ───
    if (d.isLast() && this.props.showLabels && this.sessionHigh !== null) {
      result.graphics = {
        items: [
          {
            tag: "Text",
            key: "sessionHighLabel",
            point: {
              x: d.index() + 2,
              y: this.sessionHigh,
            },
            text: "H: " + this.sessionHigh.toFixed(2),
            style: { fontSize: 9, fontWeight: "bold", fill: "#00FF00" },
            textAlignment: "centerMiddle",
          },
          {
            tag: "Text",
            key: "sessionLowLabel",
            point: {
              x: d.index() + 2,
              y: this.sessionLow,
            },
            text: "L: " + this.sessionLow.toFixed(2),
            style: { fontSize: 9, fontWeight: "bold", fill: "#FF0000" },
            textAlignment: "centerMiddle",
          },
        ],
      };
    }

    return result;
  }

  /**
   * Filter which bars to display
   * @param {Object} d - Result from map()
   */
  filter(d) {
    return d.mainValue !== undefined || d.sessionHigh !== undefined;
  }

  // ─── Helper Methods ───

  resetSession() {
    this.sessionHigh = null;
    this.sessionLow = null;
    this.sessionActive = false;
    this.cumulativeValue = 0;
    this.count = 0;
  }
}

// ============================================================================
// MODULE EXPORTS
// ============================================================================

module.exports = {
  name: "[indicatorName]LB",
  description: "[DESCRIPTION]",
  calculator: [INDICATOR_NAME]LB,

  // ─── Parameters ───
  params: {
    // Feature toggles
    enableFeature: predef.paramSpecs.bool(true),
    showBands: predef.paramSpecs.bool(false),
    showLabels: predef.paramSpecs.bool(true),

    // Calculation parameters
    period: predef.paramSpecs.period(14),
    multiplier: number(1.0, 0.1, 0.1, 5.0),

    // Session settings
    startHour: number(9, 1, 0, 23),
    startMinute: number(30, 1, 0, 59),
    endHour: number(16, 1, 0, 23),
    endMinute: number(0, 1, 0, 59),
  },

  // ─── Plots ───
  plots: {
    mainValue: { title: "Main Value" },
    upperBand: { title: "Upper Band" },
    lowerBand: { title: "Lower Band" },
    sessionHigh: { title: "Session High" },
    sessionLow: { title: "Session Low" },
  },

  // ─── Input/Output Settings ───
  inputType: meta.InputType.BARS,
  areaChoice: meta.AreaChoice.MAIN,

  // ─── Tags ───
  tags: ["Luther Barnum"],

  // ─── Styling ───
  schemeStyles: {
    dark: {
      mainValue: predef.styles.plot("#CE95D8", 2),      // Orchid
      upperBand: predef.styles.plot("#40a9ff", 1),      // Light blue
      lowerBand: predef.styles.plot("#40a9ff", 1),      // Light blue
      sessionHigh: predef.styles.plot("#00FF00", 1),    // Lime
      sessionLow: predef.styles.plot("#FF0000", 1),     // Red
    },
  },

  // ─── Validation (optional) ───
  validate(obj) {
    if (obj.endHour < obj.startHour) {
      return meta.error("endHour", "End hour must be after start hour");
    }
    if (obj.period < 1) {
      return meta.error("period", "Period must be at least 1");
    }
  },
};
```

## Template Sections

### 1. Imports
```javascript
const predef = require("./tools/predef");
const meta = require("./tools/meta");
const EMA = require("./tools/EMA");
// Add other tools as needed
```

### 2. Helper Functions
- `number()` - Custom number parameter creator
- `timeToMinutes()` - Time conversion utility
- Add other reusable helpers

### 3. Class Definition
- `init()` - Initialize state and calculators
- `map(d, i, history)` - Main calculation loop
- `filter(d)` - Control which bars display
- Helper methods

### 4. Module Exports
- `name` - Unique identifier
- `description` - User-facing description
- `calculator` - Class reference
- `params` - Parameter definitions
- `plots` - Output definitions
- `inputType` - Data type
- `tags` - Metadata tags
- `schemeStyles` - Color schemes
- `validate` - Optional validation

## Key Methods

### init()
Called once before processing. Initialize:
- Calculator instances (EMA, SMA)
- State variables
- Arrays/collections

### map(d, i, history)
Called for each bar. Parameters:
- `d` - Current bar (high(), low(), close(), open(), timestamp(), volume(), isLast())
- `i` - Bar index
- `history` - Access prior bars via `history.prior()`, `history.get(i)`, `history.data`

Returns object with plot values and optional graphics.

### filter(d)
Called after map(). Return truthy to display bar, falsy to hide.
