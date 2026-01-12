# NinjaScript Patterns Reference

Detailed conventions and patterns for NinjaTrader 8 C# indicators.

## Quick Navigation

| Topic | File | Description |
|-------|------|-------------|
| Lifecycle | [LIFECYCLE.md](LIFECYCLE.md) | OnStateChange, OnBarUpdate, multi-timeframe |
| Properties | [PROPERTIES.md](PROPERTIES.md) | Property attributes, plots, drawing objects |
| Helpers/TDD | [HELPERS.md](HELPERS.md) | Test-Driven Development, helper class pattern |
| Testing | [TESTING.md](TESTING.md) | Complete TDD guide, test setup, examples |

---

## Critical Rules (Quick Reference)

### TDD Required

All NinjaScript indicators must follow Test-Driven Development:
1. Write tests FIRST for calculation logic
2. Extract calculations to testable helper classes
3. Run `dotnet test` to verify

See [HELPERS.md](HELPERS.md) and [TESTING.md](TESTING.md) for details.

---

### File Structure

```csharp
#region Using declarations
// Imports
#endregion

// Author comment

namespace NinjaTrader.NinjaScript.Indicators.LB
{
    public class IndicatorNameLB : Indicator
    {
        #region Variables
        #endregion

        protected override void OnStateChange() { }
        protected override void OnBarUpdate() { }

        #region Helper Methods
        #endregion

        #region Properties
        #endregion
    }

    // Helper classes (testable)
}

#region NinjaScript generated code
// Auto-generated - DO NOT MODIFY
#endregion
```

---

### Namespace and Naming

```csharp
namespace NinjaTrader.NinjaScript.Indicators.LB
```

| Type | Pattern | Example |
|------|---------|---------|
| Standard | `*LB` | `VWAPLB`, `KeltnerChannelLB` |
| Pro/Composite | `*_Pro` or `*ProLB` | `VWAP_Pro`, `PullbackProLB` |

---

### Section Dividers

```csharp
// ═══════════════════════════════════════════════════════════
// SECTION TITLE IN CAPS
// ═══════════════════════════════════════════════════════════
```

---

### Guard Clauses

Use guard clauses at the start of OnBarUpdate:

```csharp
protected override void OnBarUpdate()
{
    if (BarsInProgress != 0) return;
    if (CurrentBar < Period) return;
    if (!EnableFeature) return;
    if (double.IsNaN(Close[0])) return;

    // Main logic here
}
```

---

### Plot Indexing Comments

Document plot indices for complex indicators:

```csharp
// ═══════════════════════════════════════════════════════════
// VWAP PLOTS (0-4)
// ═══════════════════════════════════════════════════════════
AddPlot(..., "VWAP");         // 0
AddPlot(..., "UpperBand1");   // 1
AddPlot(..., "LowerBand1");   // 2
AddPlot(..., "UpperBand2");   // 3
AddPlot(..., "LowerBand2");   // 4
```

---

### Helper Class Pattern

Extract calculations into testable classes:

```csharp
// In indicator
private VWAPHelper vwapHelper;

protected override void OnBarUpdate()
{
    var (vwap, stdDev) = vwapHelper.Calculate(
        High[0], Low[0], Close[0], Volume[0]);
    Values[0][0] = vwap;
}

// Helper class (testable)
public class VWAPHelper
{
    public (double vwap, double stdDev) Calculate(
        double high, double low, double close, double volume) { ... }
}
```

See [HELPERS.md](HELPERS.md) for complete pattern.

---

## Common Calculations

### VWAP

```csharp
double typicalPrice = (High[0] + Low[0] + Close[0]) / 3.0;
double volume = Volume[0] > 0 ? Volume[0] : 1;

sumPriceVolume += typicalPrice * volume;
sumVolume += volume;

double vwap = sumVolume > 0 ? sumPriceVolume / sumVolume : typicalPrice;
```

### Standard Deviation

```csharp
sumSquaredPV += (typicalPrice * typicalPrice) * volume;
double variance = sumVolume > 0 ? (sumSquaredPV / sumVolume) - (vwap * vwap) : 0;
double stdDev = Math.Sqrt(Math.Max(0, variance));  // Clamp to prevent negative
```

---

## Timezone Handling

### Enum Definition

```csharp
public enum TimeZoneOption
{
    America_NewYork,
    America_Chicago,
    America_LosAngeles,
    Europe_London,
    Asia_Tokyo
}
```

### Conversion Helper

```csharp
private string GetWindowsTimeZoneId(TimeZoneOption option)
{
    switch (option)
    {
        case TimeZoneOption.America_NewYork:
            return "Eastern Standard Time";
        case TimeZoneOption.America_Chicago:
            return "Central Standard Time";
        // ... etc
        default:
            return "Eastern Standard Time";
    }
}
```

---

## Error Handling

### Timezone with Fallback

```csharp
private DateTime SafeConvertToTimeZone(DateTime barTime)
{
    try
    {
        return TimeZoneInfo.ConvertTime(barTime, selectedTimeZone);
    }
    catch (Exception)
    {
        return barTime;  // Fallback
    }
}
```

### Mathematical Stability

```csharp
// Prevent negative variance
double stdDev = Math.Sqrt(Math.Max(0, variance));

// Prevent division by zero
double ratio = denominator != 0 ? numerator / denominator : 0;
```

---

## Performance Tips

### Use Early Returns

```csharp
if (CurrentBar < requiredBars) return;
if (!EnableFeature) return;
```

### Cache Repeated Calculations

```csharp
int currentHour = Times[0][0].Hour;
if (currentHour >= StartHour && currentHour < EndHour)
```

### Avoid Drawing on Every Bar

```csharp
if (value != previousValue || CurrentBar == Count - 1)
{
    // Update drawing objects
}
```

---

## File Naming

| Type | Pattern | Example |
|------|---------|---------|
| Standard | `*LB.cs` | `VWAPLB.cs` |
| Pro/Composite | `*_Pro.cs` | `VWAP_Pro.cs` |
| Alternative | `*ProLB.cs` | `PullbackProLB.cs` |

---

## Detailed Documentation

For comprehensive patterns and examples, see the linked files:

- **[LIFECYCLE.md](LIFECYCLE.md)** - OnStateChange states, OnBarUpdate patterns, MTF data
- **[PROPERTIES.md](PROPERTIES.md)** - Property attributes, plot definitions, drawing objects
- **[HELPERS.md](HELPERS.md)** - Helper class pattern, dependency injection, TDD workflow
- **[TESTING.md](TESTING.md)** - Complete testing guide, test project setup, examples
