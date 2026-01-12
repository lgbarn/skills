# NinjaScript Properties & Plots

Property attributes, plot definitions, and display settings for NinjaTrader 8 indicators.

---

## Property Attributes

### Complete Property Pattern

```csharp
[NinjaScriptProperty]
[Range(1, int.MaxValue)]
[Display(Name = "Period",
         Description = "Lookback period for calculation",
         Order = 1,
         GroupName = "Parameters")]
public int Period { get; set; }
```

### Boolean Toggle

```csharp
[NinjaScriptProperty]
[Display(Name = "Enable Feature",
         Order = 1,
         GroupName = "Feature Toggles")]
public bool EnableFeature { get; set; }
```

### Double with Range

```csharp
[NinjaScriptProperty]
[Range(0.1, 10.0)]
[Display(Name = "Multiplier",
         Order = 2,
         GroupName = "Parameters")]
public double Multiplier { get; set; }
```

### Color Property (with serialization)

```csharp
[NinjaScriptProperty]
[XmlIgnore]
[Display(Name = "Line Color",
         Order = 1,
         GroupName = "Colors")]
public Brush LineColor { get; set; }

[Browsable(false)]
public string LineColorSerializable
{
    get { return Serialize.BrushToString(LineColor); }
    set { LineColor = Serialize.StringToBrush(value); }
}
```

### Enum Property

```csharp
[NinjaScriptProperty]
[Display(Name = "Time Zone",
         Order = 5,
         GroupName = "Session Settings")]
public TimeZoneOption SessionTimeZone { get; set; }
```

### Internal Series Property

```csharp
[Browsable(false)]
[XmlIgnore]
public Series<double> VWAP
{
    get { return Values[0]; }
}
```

---

## Standard GroupNames

Use consistent grouping across indicators:

```csharp
GroupName = "Feature Toggles"    // Order 1-20
GroupName = "Parameters"         // Order 21-40
GroupName = "Session Settings"   // Order 41-60
GroupName = "Bands"              // Order 61-80
GroupName = "Visual Options"     // Order 81-100
GroupName = "Colors"             // Order 101-120
GroupName = "Display Options"    // Order 121-140
```

---

## Plot Definitions

### Plot Indexing Comments

For complex indicators with many plots, document the plot index ranges:

```csharp
// In State.SetDefaults

// ═══════════════════════════════════════════════════════════
// INTRADAY VWAP PLOTS (0-4)
// ═══════════════════════════════════════════════════════════
AddPlot(new Stroke(Brushes.MediumOrchid, 3), PlotStyle.Line, "VWAP");              // 0
AddPlot(new Stroke(Brushes.MediumOrchid, 1), PlotStyle.Line, "UpperBand1");        // 1
AddPlot(new Stroke(Brushes.MediumOrchid, 1), PlotStyle.Line, "LowerBand1");        // 2
AddPlot(new Stroke(Brushes.Orchid, DashStyleHelper.Dash, 1), PlotStyle.Line, "UpperBand2");  // 3
AddPlot(new Stroke(Brushes.Orchid, DashStyleHelper.Dash, 1), PlotStyle.Line, "LowerBand2");  // 4

// ═══════════════════════════════════════════════════════════
// WEEKLY VWAP PLOTS (5-9)
// ═══════════════════════════════════════════════════════════
AddPlot(new Stroke(Brushes.Cyan, DashStyleHelper.Dash, 2), PlotStyle.Line, "WeeklyVWAP");     // 5
AddPlot(new Stroke(Brushes.Cyan, 1), PlotStyle.Line, "WeeklyUpperBand1");  // 6
AddPlot(new Stroke(Brushes.Cyan, 1), PlotStyle.Line, "WeeklyLowerBand1");  // 7
```

This makes it easy to:
- Find which `Values[n]` corresponds to which plot
- Add new plots without breaking existing index references
- Debug plot assignment issues

### Basic Plot

```csharp
AddPlot(Brushes.MediumOrchid, "PlotName");
```

### Plot with Stroke

```csharp
AddPlot(new Stroke(Brushes.Blue, 2), PlotStyle.Line, "PlotName");
```

### Dashed Line

```csharp
AddPlot(new Stroke(Brushes.Cyan, DashStyleHelper.Dash, 2), PlotStyle.Line, "DashedLine");
```

### Dotted Line

```csharp
AddPlot(new Stroke(Brushes.Yellow, DashStyleHelper.Dot, 1), PlotStyle.Line, "DottedLine");
```

### Modify Plot After Creation

```csharp
Plots[0].Width = 3;
Plots[0].PlotStyle = PlotStyle.Dot;
```

### Plot Styles

- `PlotStyle.Line` - Standard line
- `PlotStyle.Dot` - Dots
- `PlotStyle.Hash` - Hash marks
- `PlotStyle.HLine` - Horizontal line
- `PlotStyle.Cross` - Crosses
- `PlotStyle.Bar` - Bars
- `PlotStyle.PriceBox` - OHLC box

---

## Drawing Objects

### Lines

```csharp
Draw.Line(this, "LineTag", false,
    startTime, startPrice,
    endTime, endPrice,
    Brushes.Gold, DashStyleHelper.Solid, 2);
```

### Text Labels

```csharp
Draw.Text(this, "TextTag", false,
    "Label Text",
    endTime, price,
    10,  // Y offset
    Brushes.Gold,
    ChartControl.Properties.LabelFont,
    TextAlignment.Center,
    Brushes.Transparent,  // Outline
    Brushes.Transparent,  // Area
    0);  // Area opacity
```

### Arrows

```csharp
Draw.ArrowUp(this, "ArrowUp_" + CurrentBar, false,
    Times[0][0], Low[0] - TickSize,
    Brushes.Lime);

Draw.ArrowDown(this, "ArrowDown_" + CurrentBar, false,
    Times[0][0], High[0] + TickSize,
    Brushes.Red);
```

### Regions (Shaded Areas)

```csharp
Draw.Region(this, "RegionTag",
    startTime, endTime,
    upperSeries, lowerSeries,
    Brushes.Transparent,  // Outline
    Brushes.LightGray,    // Area
    30);  // Opacity
```

### Rectangles

```csharp
Draw.Rectangle(this, "RectTag", false,
    startTime, highPrice,
    endTime, lowPrice,
    Brushes.Transparent,  // Outline
    Brushes.Blue,         // Area
    30);  // Opacity
```

### Tag Management

```csharp
private int sessionCounter;
private string currentSessionTag;
private readonly List<string> historicalTags = new List<string>();

// Create unique tags per session
currentSessionTag = "Session_" + sessionCounter.ToString();
Draw.Line(this, currentSessionTag + "_High", ...);

// Cleanup old sessions
foreach (string tag in tagsToRemove)
{
    RemoveDrawObject(tag);
}
```

---

## Color Palette

### Standard Colors

```csharp
// Bullish
Brushes.Lime           // Strong bullish
Brushes.Green          // Moderate bullish
Brushes.LimeGreen      // Mild bullish

// Bearish
Brushes.Red            // Strong bearish
Brushes.DarkRed        // Moderate bearish
Brushes.Maroon         // Mild bearish

// Neutral
Brushes.Yellow         // Caution
Brushes.Gold           // Highlight
Brushes.Orange         // Warning

// Features
Brushes.MediumOrchid   // VWAP
Brushes.Cyan           // Weekly
Brushes.DeepSkyBlue    // Monthly
Brushes.DodgerBlue     // Support

// UI
Brushes.White
Brushes.Gray
Brushes.DimGray
```
