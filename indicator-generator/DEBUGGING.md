# Debugging Trading Indicators

Cross-platform debugging strategies for TradingView, NinjaTrader, and Tradovate indicators.

---

## Pine Script (TradingView)

### Using `log.info()` for Debugging

Pine Script v5+ supports logging to the Pine Logs pane:

```pine
//@version=6
indicator("Debug Example")

// Log values at specific conditions
if barstate.islast
    log.info("VWAP: " + str.tostring(vwapValue))
    log.info("Session High: " + str.tostring(sessionHigh, format.mintick))
    log.info("Bar Index: " + str.tostring(bar_index))

// Log on specific events
if crossover(fast, slow)
    log.info("Crossover at bar " + str.tostring(bar_index) + " price: " + str.tostring(close))
```

### Using Plot for Visual Debugging

```pine
// Create debug plot (hide in production)
debugMode = input.bool(false, "Debug Mode", group="Debug")

// Temporary debug plots
plot(debugMode ? intermediateValue : na, "Debug Value", color=color.orange)
plotchar(debugMode and condition ? high : na, "Debug Signal", "▲", location.abovebar)
```

### Using Labels for Point-in-Time Debugging

```pine
if barstate.islast and debugMode
    // Show value at current bar
    label.new(bar_index, high,
        "VWAP: " + str.tostring(vwapValue, "#.##") + "\n" +
        "StdDev: " + str.tostring(stdDev, "#.####"),
        color=color.new(color.black, 80),
        textcolor=color.white)
```

### Using Tables for Dashboard Debugging

```pine
var table debugTable = table.new(position.bottom_left, 2, 10)

if barstate.islast and debugMode
    table.cell(debugTable, 0, 0, "Variable", text_color=color.white)
    table.cell(debugTable, 1, 0, "Value", text_color=color.white)
    table.cell(debugTable, 0, 1, "sumPV")
    table.cell(debugTable, 1, 1, str.tostring(sumPV))
    table.cell(debugTable, 0, 2, "sumV")
    table.cell(debugTable, 1, 2, str.tostring(sumV))
    // ... more rows
```

### Common Pine Script Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `line X: Undeclared identifier` | Variable not declared or typo | Check spelling, ensure declaration |
| `Cannot call 'X' with argument type 'Y'` | Type mismatch | Check function signature, use explicit types |
| `Script could not be translated` | Syntax error | Check line continuation, brackets |
| `Study Error: na encountered in output` | na value in plot | Use conditional: `value ? value : na` |
| `max_bars_back exceeded` | Referencing too far back | Increase `max_bars_back` parameter |

---

## NinjaScript (NinjaTrader)

### Using Print() for Debugging

```csharp
protected override void OnBarUpdate()
{
    // Basic value logging
    Print($"Bar {CurrentBar}: Close={Close[0]:F2}, VWAP={vwapValue:F2}");

    // Conditional logging
    if (Bars.IsFirstBarOfSession)
    {
        Print($"New Session Started at {Time[0]}");
        Print($"  Previous Session High: {prevSessionHigh:F2}");
        Print($"  Previous Session Low: {prevSessionLow:F2}");
    }

    // Debug specific bars
    if (CurrentBar >= debugStartBar && CurrentBar <= debugEndBar)
    {
        Print($"Debug Bar {CurrentBar}:");
        Print($"  High: {High[0]:F2}, Low: {Low[0]:F2}");
        Print($"  Volume: {Volume[0]:N0}");
        Print($"  Indicator Value: {Values[0][0]:F4}");
    }
}
```

### Using Draw.TextFixed for On-Chart Debug

```csharp
// Show debug info on chart
Draw.TextFixed(this, "DebugInfo",
    $"VWAP: {vwapValue:F2}\n" +
    $"Upper Band: {upperBand:F2}\n" +
    $"Session: {(sessionActive ? "Active" : "Inactive")}",
    TextPosition.TopLeft);
```

### Using Log Levels

```csharp
// In State.SetDefaults
LogLevel = LogLevels.Trace;  // Maximum verbosity

// In OnBarUpdate
Log($"Trace: Processing bar {CurrentBar}", LogLevel.Trace);
Log($"Info: Session started", LogLevel.Information);
Log($"Warning: Volume is zero", LogLevel.Warning);
Log($"Error: Invalid calculation", LogLevel.Error);
```

### NinjaTrader Output Window

- **View > Output Window** to see Print() statements
- Use **Clear** button frequently to find recent output
- Output is also saved to log files in `Documents\NinjaTrader 8\log\`

### Common NinjaScript Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Index out of range` | Accessing negative bar index | Add `if (CurrentBar < Period) return;` |
| `Object reference not set` | Null indicator or series | Initialize in `State.DataLoaded` |
| `The indicator 'X' has not been created` | Missing AddPlot | Add `AddPlot()` in `State.SetDefaults` |
| `Unable to compile` | Syntax error | Check error list in NinjaScript Editor |
| `BarsInProgress out of range` | Wrong series access | Verify `BarsInProgress` before accessing |

### Visual Studio Integration

For complex debugging:

1. Open NinjaScript in Visual Studio
2. Attach debugger to NinjaTrader process
3. Set breakpoints in your indicator code
4. Step through execution

---

## Tradovate (JavaScript)

### Using Console Logging

```javascript
map(d, i, history) {
  // Basic logging
  console.log(`Bar ${i}: Close=${d.close()}, VWAP=${vwapValue}`);

  // Object logging
  console.log("Current bar data:", {
    index: i,
    high: d.high(),
    low: d.low(),
    close: d.close(),
    volume: d.volume(),
    timestamp: d.timestamp(),
  });

  // Conditional logging (last bar only to reduce noise)
  if (d.isLast()) {
    console.log("Final calculation:", {
      vwap: this.vwapValue,
      stdDev: this.stdDev,
      upperBand: this.upperBand,
      lowerBand: this.lowerBand,
    });
  }
}
```

### Debug Parameter Pattern

```javascript
params: {
  // Add debug toggle
  debug: predef.paramSpecs.bool(false),
}

map(d, i, history) {
  if (this.props.debug) {
    console.log(`[DEBUG] Bar ${i}:`, {
      sessionActive: this.sessionActive,
      sumPV: this.sumPriceVolume,
      sumV: this.sumVolume,
    });
  }
}
```

### Visual Debugging with Graphics

```javascript
map(d, i, history) {
  const debugGraphics = this.props.debug && d.isLast() ? {
    items: [
      // Show calculation boundaries
      {
        tag: "Line",
        key: "debugSessionStart",
        a: { x: du(this.sessionStartBar), y: du(d.low() * 0.99) },
        b: { x: du(this.sessionStartBar), y: du(d.high() * 1.01) },
        style: { stroke: "#FF00FF", strokeWidth: 2 },
      },
      // Show debug values as text
      {
        tag: "Text",
        key: "debugValues",
        point: { x: du(d.index() + 2), y: du(d.high()) },
        text: `SumPV: ${this.sumPriceVolume.toFixed(2)}\nSumV: ${this.sumVolume.toFixed(0)}`,
        style: { fontSize: 8, fill: "#FFFF00" },
      },
    ],
  } : undefined;

  return {
    value: calculatedValue,
    graphics: debugGraphics,
  };
}
```

### Browser Developer Tools

1. Open Tradovate in browser (not desktop app for easier debugging)
2. Press **F12** to open Developer Tools
3. Go to **Console** tab to see `console.log()` output
4. Use **Sources** tab to set breakpoints in your indicator code

### Common Tradovate Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `undefined is not a function` | Calling method on null/undefined | Check object exists before calling |
| `Cannot read property 'X' of undefined` | Accessing property on undefined | Use optional chaining: `obj?.property` |
| Indicator doesn't appear | Invalid return from `map()` | Ensure returning object with plot values |
| Graphics don't render | Missing `du()` wrapper | Use ScaleBound operators for all points |
| Values show as NaN | Division by zero | Add guards: `if (divisor > 0)` |

---

## Cross-Platform Debugging Strategies

### 1. Isolate the Problem

```
Start with simple cases:
- Test on a single symbol
- Use daily bars (fewer calculations)
- Disable optional features
- Reduce lookback periods
```

### 2. Binary Search for Bugs

```
If indicator works on historical but fails on realtime:
1. Add logging at session boundaries
2. Check bar state conditions
3. Verify time zone conversions
4. Look for realtime-specific code paths
```

### 3. Validate Calculations Manually

```
For known values (e.g., VWAP):
1. Calculate expected value by hand for specific bar
2. Log actual value from indicator
3. Compare and trace differences
```

### 4. Test Session Boundaries

Session-based indicators often fail at:
- Market open/close
- Midnight crossings
- Daylight saving time transitions
- Holiday schedules

### 5. Check Edge Cases

```
Always test:
- First bar of chart
- First bar of session
- Last bar of session
- Bars with zero volume
- Gaps in data
- Extended hours trading
```

---

## Performance Profiling

### Pine Script

```pine
// Use Pine Profiler (built into TradingView)
// Hover over line numbers to see execution time

// Optimize hot paths identified by profiler
if barstate.islast  // Expensive operations only on last bar
    // drawing code
```

### NinjaScript

```csharp
// Use System.Diagnostics for timing
private Stopwatch sw = new Stopwatch();

protected override void OnBarUpdate()
{
    sw.Restart();

    // Your calculation code

    sw.Stop();
    if (CurrentBar == Count - 1)
        Print($"Average calculation time: {sw.ElapsedMilliseconds}ms");
}
```

### Tradovate

```javascript
map(d, i, history) {
  const start = performance.now();

  // Your calculation code

  const end = performance.now();
  if (d.isLast()) {
    console.log(`Calculation time: ${(end - start).toFixed(2)}ms`);
  }
}
```

---

## Logging Best Practices

1. **Use structured output** - Include bar index, timestamp, variable name
2. **Reduce noise** - Log only on conditions or last bar
3. **Include context** - Show related values, not just the problematic one
4. **Clean up before production** - Remove or disable debug code
5. **Use debug toggles** - Make debugging activatable via input parameter
