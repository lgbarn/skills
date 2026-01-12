# NinjaScript Lifecycle Methods

OnStateChange and OnBarUpdate patterns for NinjaTrader 8 indicators.

---

## OnStateChange States

### State.SetDefaults

Set metadata, plots, and default property values:

```csharp
if (State == State.SetDefaults)
{
    // Metadata
    Description = @"Indicator description";
    Name = "Indicator Name";

    // Calculation mode
    Calculate = Calculate.OnBarClose;  // or OnPriceChange, OnEachTick

    // Visual settings
    IsOverlay = true;                   // Draw on price panel
    DisplayInDataBox = true;
    DrawOnPricePanel = true;
    DrawHorizontalGridLines = true;
    DrawVerticalGridLines = true;
    PaintPriceMarkers = true;
    ScaleJustification = NinjaTrader.Gui.Chart.ScaleJustification.Right;
    IsSuspendedWhileInactive = true;
    MaximumBarsLookBack = MaximumBarsLookBack.Infinite;

    // Plots
    AddPlot(new Stroke(Brushes.MediumOrchid, 2), PlotStyle.Line, "PlotName");

    // Reference lines
    AddLine(Brushes.Gold, 50, "MidLine");

    // Default property values
    Period = 14;
    EnableFeature = true;
}
```

### State.Configure

Add secondary data series for multi-timeframe analysis:

```csharp
else if (State == State.Configure)
{
    // Add secondary data series for multi-timeframe
    AddDataSeries(BarsPeriodType.Week, 1);   // BarsInProgress = 1
    AddDataSeries(BarsPeriodType.Month, 1);  // BarsInProgress = 2
}
```

### State.DataLoaded

Initialize Series, indicators, and collections after data is available:

```csharp
else if (State == State.DataLoaded)
{
    // Initialize Series
    customSeries = new Series<double>(this, MaximumBarsLookBack.Infinite);

    // Create secondary indicators
    emaIndicator = EMA(Close, Period);
    atrIndicator = ATR(14);

    // Initialize collections
    levels = new List<double>();

    // Set up timezone
    selectedTimeZone = TimeZoneInfo.FindSystemTimeZoneById("Eastern Standard Time");

    // Initialize helper classes (for TDD pattern)
    vwapHelper = new VWAPHelper();
}
```

---

## OnBarUpdate Patterns

### Multi-Timeframe Handling

Handle secondary data series before primary series:

```csharp
protected override void OnBarUpdate()
{
    // Handle secondary data series first
    if (BarsInProgress == 1)  // Weekly
    {
        if (CurrentBars[1] > 0)
        {
            prevWeekHigh = Highs[1][1];
            prevWeekLow = Lows[1][1];
        }
        return;  // Early return
    }

    if (BarsInProgress != 0)
        return;

    // Primary series logic continues...
}
```

### Early Returns / Guard Clauses

Use guard clauses to reduce nesting and improve readability:

```csharp
protected override void OnBarUpdate()
{
    // Guard: Handle secondary series
    if (BarsInProgress != 0)
    {
        HandleSecondarySeries();
        return;
    }

    // Guard: Insufficient data
    if (CurrentBar < Period)
        return;

    // Guard: Feature disabled
    if (!EnableFeature)
        return;

    // Guard: Invalid data
    if (double.IsNaN(Close[0]) || Volume[0] <= 0)
        return;

    // Guard: Outside session hours
    if (!IsWithinSession())
        return;

    // Main calculation logic (no nesting needed)
    CalculateIndicator();
    AssignPlotValues();
}
```

### Session Detection

```csharp
// Built-in session detection
if (Bars.IsFirstBarOfSession)
{
    ResetSession();
}

// Manual time-based detection
DateTime currentBarTime = Times[0][0];
if (currentBarTime >= sessionStartTime && currentBarTime < sessionEndTime)
{
    // In session window
}
```

### Output Assignment

```csharp
// Conditional output
if (EnableFeature)
{
    Values[0][0] = calculatedValue;
}
else
{
    Values[0][0] = double.NaN;  // Hide plot
}
```

---

## Multi-Timeframe Data

### Adding Data Series

```csharp
// In State.Configure
AddDataSeries(BarsPeriodType.Week, 1);   // BarsInProgress = 1
AddDataSeries(BarsPeriodType.Month, 1);  // BarsInProgress = 2
```

### Accessing Secondary Data

```csharp
// In OnBarUpdate for BarsInProgress == 1
if (CurrentBars[1] > 0)
{
    double weeklyHigh = Highs[1][1];   // Previous week high
    double weeklyLow = Lows[1][1];     // Previous week low
    double weeklyClose = Closes[1][1]; // Previous week close
    double weeklyVolume = Volumes[1][1];
    DateTime weeklyTime = Times[1][1];
}
```

---

## Series Management

### Creating Series

```csharp
// In State.DataLoaded
customSeries = new Series<double>(this, MaximumBarsLookBack.Infinite);
```

### Using Series

```csharp
// Store values
customSeries[0] = calculatedValue;

// Access historical values
double prevValue = customSeries[1];
```

---

## Session Reset Pattern

```csharp
private void ResetSession()
{
    sumPriceVolume = 0;
    sumVolume = 0;
    sumSquaredPV = 0;
    sessionHigh = double.MinValue;
    sessionLow = double.MaxValue;
    sessionActive = false;

    // Reset helper if using TDD pattern
    vwapHelper?.Reset();
}
```
