# Pine Script Input Patterns

Detailed conventions for organizing and defining inputs in TradingView Pine Script indicators.

---

## Standard Group Names (in order)

1. `"Feature Toggles"` - Master enable/disable switches
2. `"Theme"` - Light/dark mode settings
3. `"[Feature Name] Settings"` - Feature-specific inputs
4. `"Session Settings"` - Time-based configuration
5. `"Colors"` - Color customization (if user-configurable)
6. `"Display Options"` - Visual preferences

---

## Input Variable Naming

**Source**: [TradingView Style Guide](https://www.tradingview.com/pine-script-docs/writing/style-guide/)

Suffix input variables with `Input` for clarity when used later in code:

```pine
maLengthInput = input.int(14, "MA Length")
bearColorInput = input.color(color.red, "Bear Color")
showAvgInput = input.bool(true, "Show Average")

// Later in code - clearly identifiable as user inputs
ma = ta.sma(close, maLengthInput)
plotColor = close > ma ? color.green : bearColorInput
```

---

## Tooltip Best Practices

Every user-facing input should have a descriptive tooltip. Pro indicators often have 100+ tooltips.

```pine
enableVWAP = input.bool(true, "Enable VWAP",
    group = "Feature Toggles",
    tooltip = "Master toggle for VWAP calculation and display. When disabled, all VWAP plots and bands are hidden.")

sdMultiplier = input.float(1.0, "SD Multiplier",
    minval = 0.5, maxval = 3.0, step = 0.25,
    group = "VWAP Settings",
    tooltip = "Standard deviation multiplier for VWAP bands. Common values: 1.0 (68%), 2.0 (95%), 3.0 (99.7%)")
```

**Tooltip Guidelines:**
- Explain what the setting does, not just what it is
- Include recommended/common values when helpful
- Mention dependencies on other settings
- Keep under 200 characters for readability

---

## Input Patterns by Type

### Boolean Toggle
```pine
enableFeature = input.bool(true, "Enable Feature",
    group="Feature Toggles",
    tooltip="Master toggle for this feature")
```

### Period/Integer
```pine
period = input.int(14, "Period",
    minval=1, maxval=500, step=1,
    group="Settings",
    tooltip="Lookback period for calculation")
```

### Time Inputs (inline pair)
```pine
startHour = input.int(9, "Start Hour", minval=0, maxval=23, inline="start_time", group="Session")
startMinute = input.int(30, "Min", minval=0, maxval=59, step=5, inline="start_time", group="Session")
```

### Style Selection
```pine
lineStyle = input.string("Solid", "Style",
    options=["Solid", "Dashed", "Dotted"],
    inline="style", group="Settings")
lineWidth = input.int(2, "Width", minval=1, maxval=5, inline="style", group="Settings")
```

### Timezone
```pine
timeZone = input.string("America/New_York", "Time Zone",
    options=["America/New_York", "America/Chicago", "America/Los_Angeles", "Europe/London", "Asia/Tokyo"],
    group="Session Settings")
```

### Float with Range
```pine
multiplier = input.float(1.0, "Multiplier",
    minval=0.1, maxval=5.0, step=0.1,
    group="Settings")
```

---

## Input Grouping Example

```pine
// ═══ FEATURE TOGGLES ═══
enableVWAP = input.bool(true, "Enable VWAP", group="Feature Toggles")
enableBands = input.bool(true, "Enable Bands", group="Feature Toggles")
enableIB = input.bool(false, "Enable Initial Balance", group="Feature Toggles")

// ═══ THEME ═══
useLightTheme = input.bool(false, "Light Theme Mode", group="Theme")

// ═══ VWAP SETTINGS ═══
vwapSource = input.source(hlc3, "Source", group="VWAP Settings")
sdMultiplier = input.float(1.0, "SD Multiplier", group="VWAP Settings")

// ═══ SESSION SETTINGS ═══
timeZone = input.string("America/New_York", "Time Zone", group="Session Settings")
startHour = input.int(9, "Start Hour", inline="start", group="Session Settings")
startMinute = input.int(30, "Min", inline="start", group="Session Settings")
```
