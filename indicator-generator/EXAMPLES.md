# Cross-Platform Indicator Examples

Examples of implementing common indicator types across all three platforms.

## Quick Reference: Platform Equivalents

| Concept | Pine Script | NinjaScript | Tradovate |
|---------|-------------|-------------|-----------|
| Entry point | Script body | `OnBarUpdate()` | `map()` |
| State init | `var` keyword | `State.DataLoaded` | `init()` |
| EMA | `ta.ema()` | `EMA()` indicator | `EMA()` from tools |
| Session start | `session.isfirstbar` | `Bars.IsFirstBarOfSession` | Compare dates |
| Plot | `plot()` | `Values[0][0] =` | Return object |
| Hide plot | `na` | `double.NaN` | `undefined` |

---

## 1. Simple VWAP

### Pine Script
```pine
// Released under the Mozilla Public License 2.0
// by Luther Barnum - Simple VWAP

//@version=6
indicator("Simple VWAP", overlay=true)

// ═══ INPUTS ═══
enableVWAP = input.bool(true, "Enable VWAP", group="Feature Toggles")

// ═══ STATE ═══
var float sumPV = 0.0
var float sumV = 0.0

// ═══ RESET ON NEW SESSION ═══
if session.isfirstbar
    sumPV := 0.0
    sumV := 0.0

// ═══ CALCULATION ═══
tp = (high + low + close) / 3
sumPV += tp * volume
sumV += volume
vwapValue = sumV > 0 ? sumPV / sumV : tp

// ═══ PLOT ═══
plot(enableVWAP ? vwapValue : na, "VWAP", color.purple, 2)
```

### NinjaScript
```csharp
namespace NinjaTrader.NinjaScript.Indicators.LB
{
    public class SimpleVWAPLB : Indicator
    {
        private double sumPV, sumV;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Name = "Simple VWAP LB";
                IsOverlay = true;
                AddPlot(Brushes.Purple, "VWAP");
                EnableVWAP = true;
            }
        }

        protected override void OnBarUpdate()
        {
            if (Bars.IsFirstBarOfSession)
            {
                sumPV = 0;
                sumV = 0;
            }

            double tp = (High[0] + Low[0] + Close[0]) / 3.0;
            double vol = Volume[0] > 0 ? Volume[0] : 1;
            sumPV += tp * vol;
            sumV += vol;

            Values[0][0] = EnableVWAP && sumV > 0 ? sumPV / sumV : double.NaN;
        }

        [NinjaScriptProperty]
        [Display(Name = "Enable VWAP", GroupName = "Feature Toggles")]
        public bool EnableVWAP { get; set; }
    }
}
```

### Tradovate
```javascript
const predef = require("./tools/predef");
const meta = require("./tools/meta");

class SimpleVWAPLB {
  init() {
    this.sumPV = 0;
    this.sumV = 0;
    this.currentDate = null;
  }

  map(d, i, history) {
    const date = d.timestamp().toDateString();
    if (this.currentDate !== date) {
      this.sumPV = 0;
      this.sumV = 0;
      this.currentDate = date;
    }

    const tp = (d.high() + d.low() + d.close()) / 3;
    const vol = d.volume() || 1;
    this.sumPV += tp * vol;
    this.sumV += vol;

    return {
      vwap: this.props.enableVWAP && this.sumV > 0 ? this.sumPV / this.sumV : undefined,
    };
  }

  filter(d) {
    return d.vwap !== undefined;
  }
}

module.exports = {
  name: "simpleVWAPLB",
  description: "Simple VWAP",
  calculator: SimpleVWAPLB,
  params: {
    enableVWAP: predef.paramSpecs.bool(true),
  },
  plots: {
    vwap: { title: "VWAP" },
  },
  inputType: meta.InputType.BARS,
  tags: ["Luther Barnum"],
  schemeStyles: {
    dark: {
      vwap: predef.styles.plot("#CE95D8", 2),
    },
  },
};
```

---

## 2. Session-Based: Initial Balance

### Pine Script
```pine
// by Luther Barnum - Initial Balance

//@version=6
indicator("Initial Balance", overlay=true, max_lines_count=500)

// ═══ INPUTS ═══
enableIB = input.bool(true, "Enable IB", group="Feature Toggles")
ibDuration = input.int(60, "Duration (min)", minval=5, maxval=240, group="IB Settings")
ibTimeZone = input.string("America/New_York", "Time Zone", group="Session")
ibStartHour = input.int(9, "Start Hour", inline="start", group="Session")
ibStartMinute = input.int(30, "Min", inline="start", group="Session")

// ═══ THEME ═══
useLightTheme = input.bool(false, "Light Theme", group="Theme")
theme_gold = useLightTheme ? color.new(#806600, 0) : color.yellow

// ═══ STATE ═══
var float ibHigh = na
var float ibLow = na
var bool ibComplete = false

// ═══ TIME CALC ═══
cached_minutes = hour(time, ibTimeZone) * 60 + minute(time, ibTimeZone)
var int ib_start = ibStartHour * 60 + ibStartMinute
var int ib_end = ib_start + ibDuration

isIBStart() =>
    prev_minutes = hour(time[1], ibTimeZone) * 60 + minute(time[1], ibTimeZone)
    prev_minutes < ib_start and cached_minutes >= ib_start

inIBWindow() =>
    cached_minutes >= ib_start and cached_minutes < ib_end

// ═══ LOGIC ═══
if isIBStart()
    ibHigh := high
    ibLow := low
    ibComplete := false

if inIBWindow() and not ibComplete
    ibHigh := math.max(ibHigh, high)
    ibLow := math.min(ibLow, low)

if cached_minutes >= ib_end and not ibComplete
    ibComplete := true

// ═══ PLOT ═══
plot(enableIB and ibComplete ? ibHigh : na, "IB High", theme_gold, 2)
plot(enableIB and ibComplete ? ibLow : na, "IB Low", theme_gold, 2)
plot(enableIB and ibComplete ? (ibHigh + ibLow) / 2 : na, "IB Mid", theme_gold, 1, plot.style_circles)
```

### NinjaScript
```csharp
namespace NinjaTrader.NinjaScript.Indicators.LB
{
    public class InitialBalanceLB : Indicator
    {
        private double ibHigh, ibLow;
        private bool ibComplete;
        private DateTime ibStart, ibEnd;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Name = "Initial Balance LB";
                IsOverlay = true;
                AddPlot(Brushes.Gold, "IB High");
                AddPlot(Brushes.Gold, "IB Low");
                AddPlot(new Stroke(Brushes.Gold, DashStyleHelper.Dot, 1), PlotStyle.Line, "IB Mid");

                EnableIB = true;
                Duration = 60;
                StartHour = 9;
                StartMinute = 30;
            }
        }

        protected override void OnBarUpdate()
        {
            if (BarsInProgress != 0) return;

            DateTime barTime = Times[0][0];
            DateTime today = barTime.Date;
            ibStart = today.AddHours(StartHour).AddMinutes(StartMinute);
            ibEnd = ibStart.AddMinutes(Duration);

            // Reset at session start
            if (Bars.IsFirstBarOfSession)
            {
                ibHigh = double.MinValue;
                ibLow = double.MaxValue;
                ibComplete = false;
            }

            // Track during IB window
            if (barTime >= ibStart && barTime < ibEnd && !ibComplete)
            {
                ibHigh = Math.Max(ibHigh, High[0]);
                ibLow = Math.Min(ibLow, Low[0]);
            }

            // Mark complete
            if (barTime >= ibEnd && !ibComplete)
            {
                ibComplete = true;
            }

            // Output
            if (EnableIB && ibComplete)
            {
                Values[0][0] = ibHigh;
                Values[1][0] = ibLow;
                Values[2][0] = (ibHigh + ibLow) / 2;
            }
        }

        [NinjaScriptProperty]
        [Display(Name = "Enable IB", GroupName = "Feature Toggles")]
        public bool EnableIB { get; set; }

        [NinjaScriptProperty]
        [Range(5, 240)]
        [Display(Name = "Duration (min)", GroupName = "IB Settings")]
        public int Duration { get; set; }

        [NinjaScriptProperty]
        [Range(0, 23)]
        [Display(Name = "Start Hour", GroupName = "Session")]
        public int StartHour { get; set; }

        [NinjaScriptProperty]
        [Range(0, 59)]
        [Display(Name = "Start Minute", GroupName = "Session")]
        public int StartMinute { get; set; }
    }
}
```

### Tradovate
```javascript
const predef = require("./tools/predef");
const meta = require("./tools/meta");
const { ParamType } = meta;

function number(def, step, min, max) {
  return { type: ParamType.NUMBER, def, restrictions: { step, min, max } };
}

class InitialBalanceLB {
  init() {
    this.ibHigh = null;
    this.ibLow = null;
    this.ibComplete = false;
    this.currentDate = null;
  }

  map(d, i, history) {
    const ts = d.timestamp();
    const date = ts.toDateString();
    const minutes = ts.getHours() * 60 + ts.getMinutes();

    const { startHour, startMinute, duration } = this.props;
    const ibStart = startHour * 60 + startMinute;
    const ibEnd = ibStart + duration;

    // Reset on new day
    if (this.currentDate !== date) {
      this.ibHigh = null;
      this.ibLow = null;
      this.ibComplete = false;
      this.currentDate = date;
    }

    // Detect IB start
    if (history.prior()) {
      const prevMin = history.prior().timestamp().getHours() * 60 +
                      history.prior().timestamp().getMinutes();
      if (prevMin < ibStart && minutes >= ibStart) {
        this.ibHigh = d.high();
        this.ibLow = d.low();
        this.ibComplete = false;
      }
    }

    // Track during window
    if (minutes >= ibStart && minutes < ibEnd && !this.ibComplete) {
      this.ibHigh = Math.max(this.ibHigh || d.high(), d.high());
      this.ibLow = Math.min(this.ibLow || d.low(), d.low());
    }

    // Complete
    if (minutes >= ibEnd && !this.ibComplete) {
      this.ibComplete = true;
    }

    if (!this.props.enableIB || !this.ibComplete) {
      return {};
    }

    return {
      ibHigh: this.ibHigh,
      ibLow: this.ibLow,
      ibMid: (this.ibHigh + this.ibLow) / 2,
    };
  }

  filter(d) {
    return d.ibHigh !== undefined;
  }
}

module.exports = {
  name: "initialBalanceLB",
  description: "Initial Balance",
  calculator: InitialBalanceLB,
  params: {
    enableIB: predef.paramSpecs.bool(true),
    duration: number(60, 5, 5, 240),
    startHour: number(9, 1, 0, 23),
    startMinute: number(30, 1, 0, 59),
  },
  plots: {
    ibHigh: { title: "IB High" },
    ibLow: { title: "IB Low" },
    ibMid: { title: "IB Mid", lineStyle: "dots" },
  },
  inputType: meta.InputType.BARS,
  tags: ["Luther Barnum"],
  schemeStyles: {
    dark: {
      ibHigh: predef.styles.plot("#FFD700", 2),
      ibLow: predef.styles.plot("#FFD700", 2),
      ibMid: predef.styles.plot("#FFD700", 1),
    },
  },
};
```

---

## 3. Oscillator: Simple RSI

### Pine Script
```pine
// by Luther Barnum - Simple RSI

//@version=6
indicator("Simple RSI", overlay=false)

// ═══ INPUTS ═══
period = input.int(14, "Period", minval=1, group="Parameters")
overbought = input.int(70, "Overbought", group="Levels")
oversold = input.int(30, "Oversold", group="Levels")

// ═══ CALCULATION ═══
rsiValue = ta.rsi(close, period)

// ═══ PLOT ═══
plot(rsiValue, "RSI", color.purple, 2)
hline(overbought, "Overbought", color.red)
hline(oversold, "Oversold", color.green)
hline(50, "Midline", color.gray)

// ═══ BACKGROUND ═══
bgcolor(rsiValue > overbought ? color.new(color.red, 90) : rsiValue < oversold ? color.new(color.green, 90) : na)
```

### NinjaScript
```csharp
namespace NinjaTrader.NinjaScript.Indicators.LB
{
    public class SimpleRSILB : Indicator
    {
        private RSI rsiIndicator;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Name = "Simple RSI LB";
                IsOverlay = false;
                AddPlot(Brushes.Purple, "RSI");
                AddLine(Brushes.Red, 70, "Overbought");
                AddLine(Brushes.Green, 30, "Oversold");
                AddLine(Brushes.Gray, 50, "Midline");

                Period = 14;
                Overbought = 70;
                Oversold = 30;
            }
            else if (State == State.DataLoaded)
            {
                rsiIndicator = RSI(Close, Period, 1);
            }
        }

        protected override void OnBarUpdate()
        {
            if (CurrentBar < Period) return;

            double rsi = rsiIndicator[0];
            Values[0][0] = rsi;

            // Background coloring
            if (rsi > Overbought)
                BackBrush = new SolidColorBrush(Color.FromArgb(25, 255, 0, 0));
            else if (rsi < Oversold)
                BackBrush = new SolidColorBrush(Color.FromArgb(25, 0, 255, 0));
            else
                BackBrush = null;
        }

        [NinjaScriptProperty]
        [Range(1, 100)]
        [Display(Name = "Period", GroupName = "Parameters")]
        public int Period { get; set; }

        [NinjaScriptProperty]
        [Range(50, 100)]
        [Display(Name = "Overbought", GroupName = "Levels")]
        public int Overbought { get; set; }

        [NinjaScriptProperty]
        [Range(0, 50)]
        [Display(Name = "Oversold", GroupName = "Levels")]
        public int Oversold { get; set; }
    }
}
```

### Tradovate
```javascript
const predef = require("./tools/predef");
const meta = require("./tools/meta");

class SimpleRSILB {
  init() {
    this.gains = [];
    this.losses = [];
    this.period = this.props.period;
  }

  map(d, i, history) {
    if (i < 1) return {};

    const change = d.close() - history.prior().close();
    const gain = change > 0 ? change : 0;
    const loss = change < 0 ? -change : 0;

    this.gains.push(gain);
    this.losses.push(loss);

    if (this.gains.length > this.period) {
      this.gains.shift();
      this.losses.shift();
    }

    if (this.gains.length < this.period) return {};

    const avgGain = this.gains.reduce((a, b) => a + b, 0) / this.period;
    const avgLoss = this.losses.reduce((a, b) => a + b, 0) / this.period;

    const rs = avgLoss > 0 ? avgGain / avgLoss : 100;
    const rsi = 100 - (100 / (1 + rs));

    return { rsi };
  }

  filter(d) {
    return d.rsi !== undefined;
  }
}

module.exports = {
  name: "simpleRSILB",
  description: "Simple RSI",
  calculator: SimpleRSILB,
  params: {
    period: predef.paramSpecs.period(14),
  },
  plots: {
    rsi: { title: "RSI" },
  },
  inputType: meta.InputType.BARS,
  areaChoice: meta.AreaChoice.NEW,
  tags: ["Luther Barnum"],
  schemeStyles: {
    dark: {
      rsi: predef.styles.plot("#CE95D8", 2),
    },
  },
};
```

---

## 4. Multi-Feature Composite (Pro Pattern)

### Architecture Overview

Pro indicators combine multiple features:

```
┌─────────────────────────────────────────────────┐
│ Feature Toggles                                  │
│   □ Enable VWAP                                  │
│   □ Enable Bands                                 │
│   □ Enable IB                                    │
│   □ Enable Pivots                                │
└─────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│ Feature-Specific Settings                        │
│   ├── VWAP Settings (period, source)            │
│   ├── Band Settings (multiplier)                │
│   ├── IB Settings (duration, times)             │
│   └── Pivot Settings (type, levels)             │
└─────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│ Calculations (guarded by toggles)                │
│   if enableVWAP: calculate VWAP                 │
│   if enableBands: calculate bands               │
│   if enableIB: calculate IB levels              │
│   if enablePivots: calculate pivots             │
└─────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│ Outputs (conditional)                            │
│   plot vwap if enableVWAP                       │
│   plot bands if enableBands                     │
│   plot IB levels if enableIB                    │
│   plot pivots if enablePivots                   │
└─────────────────────────────────────────────────┘
```

### Key Patterns

**1. Feature Toggles First**
```pine
// Pine
enableVWAP = input.bool(true, "Enable VWAP", group="Feature Toggles")
enableBands = input.bool(true, "Enable Bands", group="Feature Toggles")
enableIB = input.bool(false, "Enable IB", group="Feature Toggles")
```

```csharp
// NinjaScript
[Display(GroupName = "Feature Toggles", Order = 1)]
public bool EnableVWAP { get; set; }
[Display(GroupName = "Feature Toggles", Order = 2)]
public bool EnableBands { get; set; }
```

```javascript
// Tradovate
params: {
  enableVWAP: predef.paramSpecs.bool(true),
  enableBands: predef.paramSpecs.bool(true),
  enableIB: predef.paramSpecs.bool(false),
}
```

**2. Conditional Calculation**
```pine
// Only calculate if enabled
if enableVWAP
    // VWAP calculation

if enableBands and enableVWAP  // Bands depend on VWAP
    // Band calculation
```

**3. Conditional Output**
```pine
plot(enableVWAP ? vwapValue : na, "VWAP")
plot(enableBands and enableVWAP ? upperBand : na, "Upper Band")
```

**4. Modular Organization**
- Separate sections for each feature
- Clear dependencies documented
- Independent reset logic per feature

---

## Platform Conversion Checklist

When converting between platforms:

### Pine → NinjaScript
- [ ] Replace `input.*()` with `[NinjaScriptProperty]` properties
- [ ] Replace `var` state with class fields
- [ ] Replace `plot()` with `Values[n][0] =`
- [ ] Replace `ta.*()` with built-in indicators
- [ ] Replace `session.isfirstbar` with `Bars.IsFirstBarOfSession`
- [ ] Add namespace and class structure
- [ ] Add `OnStateChange()` lifecycle

### Pine → Tradovate
- [ ] Create class with `init()`, `map()`, `filter()`
- [ ] Replace `input.*()` with `params` object
- [ ] Replace `var` state with `this.*` in `init()`
- [ ] Replace `plot()` with return object
- [ ] Replace `ta.*()` with tools calculators
- [ ] Add `module.exports` structure

### NinjaScript → Pine
- [ ] Replace properties with `input.*()` functions
- [ ] Replace class fields with `var` variables
- [ ] Replace `Values[n][0]` with `plot()`
- [ ] Replace built-in indicators with `ta.*()` functions
- [ ] Remove class structure, flatten to script

### NinjaScript → Tradovate
- [ ] Replace C# class with JavaScript class
- [ ] Replace `OnStateChange` init with `init()`
- [ ] Replace `OnBarUpdate` with `map()`
- [ ] Replace properties with `params`
- [ ] Replace `Values[n][0]` with return object
- [ ] Add `filter()` method

---

## 5. Strategy Examples

Strategy templates generate automated trading strategies from backtested configurations. See [strategy/](strategy/) for full documentation.

### Keltner Strategy (Pine Script)

Complete example of a generated Keltner Channel Breakout strategy:

```pine
// Released under the Mozilla Public License 2.0
// by Luther Barnum - Keltner Channel Breakout Strategy

//@version=6
strategy("LB Keltner Strategy", overlay=true, default_qty_type=strategy.percent_of_equity,
      default_qty_value=100, initial_capital=100000, commission_type=strategy.commission.cash_per_order,
      commission_value=2.0, slippage=1, pyramiding=1)

// ═══════════════════════════════════════════════════════════════════════════
// FEATURE TOGGLES
// ═══════════════════════════════════════════════════════════════════════════
enableLongs = input.bool(true, "Enable Long Trades", group="Feature Toggles")
enableShorts = input.bool(true, "Enable Short Trades", group="Feature Toggles")
enableReentry = input.bool(true, "Enable Re-entry", group="Feature Toggles")
showSignals = input.bool(true, "Show Entry Signals", group="Feature Toggles")

// ═══════════════════════════════════════════════════════════════════════════
// KELTNER SETTINGS
// ═══════════════════════════════════════════════════════════════════════════
keltnerEmaPeriod = input.int(20, "EMA Period", minval=5, maxval=50, group="Signal Settings")
keltnerAtrMult = input.float(2.75, "ATR Multiplier", minval=0.5, maxval=5.0, step=0.25,
     group="Signal Settings", tooltip="Wider bands = fewer but higher quality signals")

// ═══════════════════════════════════════════════════════════════════════════
// ADX FILTER
// ═══════════════════════════════════════════════════════════════════════════
useAdxFilter = input.bool(true, "Use ADX Filter", group="ADX Filter")
adxThreshold = input.int(35, "ADX Threshold", minval=10, maxval=60, group="ADX Filter")
adxPeriod = input.int(14, "ADX Period", minval=5, maxval=30, group="ADX Filter")
adxMode = input.string("di_rising", "ADX Mode", options=["traditional", "di_aligned", "di_rising", "adx_rising", "combined"],
     group="ADX Filter", tooltip="di_rising recommended for best results")

// ═══════════════════════════════════════════════════════════════════════════
// EXIT SETTINGS
// ═══════════════════════════════════════════════════════════════════════════
atrPeriod = input.int(14, "ATR Period", minval=5, maxval=30, group="Exit Settings")
slAtrMult = input.float(3.0, "Stop Loss (ATR×)", minval=0.5, maxval=10.0, step=0.5, group="Exit Settings")
tpAtrMult = input.float(3.0, "Take Profit (ATR×)", minval=0.5, maxval=10.0, step=0.5, group="Exit Settings")
trailEnabled = input.bool(true, "Enable Trailing Stop", group="Exit Settings")
trailTriggerAtr = input.float(0.15, "Trail Trigger (ATR×)", minval=0.05, maxval=2.0, step=0.05, group="Exit Settings")
trailDistanceAtr = input.float(0.15, "Trail Distance (ATR×)", minval=0.05, maxval=2.0, step=0.05, group="Exit Settings")

// ═══════════════════════════════════════════════════════════════════════════
// RE-ENTRY SETTINGS
// ═══════════════════════════════════════════════════════════════════════════
reentryWaitBars = input.int(3, "Wait Bars After Exit", minval=1, maxval=20, group="Re-entry Settings")
reentryAdxMin = input.int(40, "Re-entry ADX Min", minval=20, maxval=70, group="Re-entry Settings")
maxReentries = input.int(10, "Max Re-entries Per Trend", minval=1, maxval=50, group="Re-entry Settings")

// ═══════════════════════════════════════════════════════════════════════════
// VOLUME & SESSION FILTERS
// ═══════════════════════════════════════════════════════════════════════════
useVolumeFilter = input.bool(true, "Use Volume Filter", group="Filters")
volumeMaPeriod = input.int(20, "Volume MA Period", minval=5, maxval=50, group="Filters")
useSessionFilter = input.bool(true, "Use Session Filter", group="Filters")

// ═══════════════════════════════════════════════════════════════════════════
// CALCULATIONS
// ═══════════════════════════════════════════════════════════════════════════

// Keltner Channel
keltnerMid = ta.ema(close, keltnerEmaPeriod)
keltnerAtr = ta.atr(keltnerEmaPeriod)
keltnerUpper = keltnerMid + keltnerAtrMult * keltnerAtr
keltnerLower = keltnerMid - keltnerAtrMult * keltnerAtr

// ADX (using library if available, otherwise calculate)
[diPlus, diMinus, adxValue] = ta.dmi(adxPeriod, adxPeriod)
adxRising = adxValue > adxValue[1]
diPlusRising = diPlus > diPlus[1]
diMinusRising = diMinus > diMinus[1]

checkAdxCondition(isLong) =>
    if not useAdxFilter
        true
    else if adxValue <= adxThreshold
        false
    else
        switch adxMode
            "traditional" => true
            "di_aligned" => isLong ? diPlus > diMinus : diMinus > diPlus
            "di_rising" => isLong ? diPlusRising : diMinusRising
            "adx_rising" => adxRising
            "combined" => (isLong ? diPlus > diMinus and diPlusRising : diMinus > diPlus and diMinusRising) and adxRising
            => true

// Volume filter
volumeOk = not useVolumeFilter or volume > ta.sma(volume, volumeMaPeriod)

// Session filter (simplified - all standard hours)
hourOk = not useSessionFilter or (hour >= 9 and hour <= 16)

// ATR for exits
atrValue = ta.atr(atrPeriod)

// ═══════════════════════════════════════════════════════════════════════════
// STATE VARIABLES
// ═══════════════════════════════════════════════════════════════════════════
var float entryPrice = na
var float stopLoss = na
var float takeProfit = na
var float highWaterMark = na
var float lowWaterMark = na
var bool trailActive = false
var float trailTriggerPrice = na
var float trailDistancePoints = na
var int lastExitBar = -999
var bool lastExitProfitable = false
var int lastExitDirection = 0
var int reentryCount = 0

// ═══════════════════════════════════════════════════════════════════════════
// ENTRY SIGNALS
// ═══════════════════════════════════════════════════════════════════════════
longBreakout = close[1] <= keltnerUpper[1] and close > keltnerUpper
shortBreakout = close[1] >= keltnerLower[1] and close < keltnerLower
stillAboveBand = close > keltnerUpper
stillBelowBand = close < keltnerLower

longSignal = longBreakout and checkAdxCondition(true) and volumeOk and hourOk and enableLongs
shortSignal = shortBreakout and checkAdxCondition(false) and volumeOk and hourOk and enableShorts

// Re-entry logic
reentryAllowed = enableReentry and lastExitProfitable and
     (bar_index - lastExitBar) >= reentryWaitBars and
     reentryCount < maxReentries and adxValue > reentryAdxMin

if reentryAllowed
    if lastExitDirection == 1 and stillAboveBand and hourOk and volumeOk and enableLongs
        longSignal := true
    if lastExitDirection == -1 and stillBelowBand and hourOk and volumeOk and enableShorts
        shortSignal := true

// Reset reentry on fresh breakout
if (longBreakout or shortBreakout) and not reentryAllowed
    reentryCount := 0

// ═══════════════════════════════════════════════════════════════════════════
// ENTRY EXECUTION
// ═══════════════════════════════════════════════════════════════════════════
if strategy.position_size == 0
    slPoints = atrValue * slAtrMult
    tpPoints = atrValue * tpAtrMult

    if longSignal
        strategy.entry("Long", strategy.long)
        entryPrice := close
        stopLoss := close - slPoints
        takeProfit := close + tpPoints
        highWaterMark := close
        trailActive := false
        trailTriggerPrice := close + atrValue * trailTriggerAtr
        trailDistancePoints := atrValue * trailDistanceAtr
        if reentryAllowed and lastExitDirection == 1
            reentryCount += 1

    if shortSignal
        strategy.entry("Short", strategy.short)
        entryPrice := close
        stopLoss := close + slPoints
        takeProfit := close - tpPoints
        lowWaterMark := close
        trailActive := false
        trailTriggerPrice := close - atrValue * trailTriggerAtr
        trailDistancePoints := atrValue * trailDistanceAtr
        if reentryAllowed and lastExitDirection == -1
            reentryCount += 1

// ═══════════════════════════════════════════════════════════════════════════
// POSITION MANAGEMENT
// ═══════════════════════════════════════════════════════════════════════════
if strategy.position_size > 0  // Long position
    highWaterMark := math.max(highWaterMark, high)
    if trailEnabled and not trailActive and highWaterMark >= trailTriggerPrice
        trailActive := true
    if trailActive
        newStop = highWaterMark - trailDistancePoints
        stopLoss := math.max(stopLoss, newStop)

    if trailActive and low <= stopLoss
        strategy.close("Long", comment="Trail")
        lastExitBar := bar_index
        lastExitProfitable := stopLoss > entryPrice
        lastExitDirection := 1
    else if low <= stopLoss
        strategy.close("Long", comment="SL")
        lastExitBar := bar_index
        lastExitProfitable := false
        lastExitDirection := 1
    else if high >= takeProfit
        strategy.close("Long", comment="TP")
        lastExitBar := bar_index
        lastExitProfitable := true
        lastExitDirection := 1

if strategy.position_size < 0  // Short position
    lowWaterMark := math.min(lowWaterMark, low)
    if trailEnabled and not trailActive and lowWaterMark <= trailTriggerPrice
        trailActive := true
    if trailActive
        newStop = lowWaterMark + trailDistancePoints
        stopLoss := math.min(stopLoss, newStop)

    if trailActive and high >= stopLoss
        strategy.close("Short", comment="Trail")
        lastExitBar := bar_index
        lastExitProfitable := entryPrice > stopLoss
        lastExitDirection := -1
    else if high >= stopLoss
        strategy.close("Short", comment="SL")
        lastExitBar := bar_index
        lastExitProfitable := false
        lastExitDirection := -1
    else if low <= takeProfit
        strategy.close("Short", comment="TP")
        lastExitBar := bar_index
        lastExitProfitable := true
        lastExitDirection := -1

// ═══════════════════════════════════════════════════════════════════════════
// PLOTTING
// ═══════════════════════════════════════════════════════════════════════════
plot(keltnerMid, "Keltner Mid", color.gray, 1)
plot(keltnerUpper, "Keltner Upper", color.lime, 1)
plot(keltnerLower, "Keltner Lower", color.red, 1)

plotshape(showSignals and longBreakout ? low : na, "Long Signal",
     shape.triangleup, location.belowbar, color.lime, size=size.small)
plotshape(showSignals and shortBreakout ? high : na, "Short Signal",
     shape.triangledown, location.abovebar, color.red, size=size.small)
```

### EMA Cross Strategy (NinjaScript)

Complete example of a generated EMA Crossover strategy for NinjaTrader 8:

```csharp
#region Using declarations
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Windows.Media;
using NinjaTrader.Cbi;
using NinjaTrader.Gui;
using NinjaTrader.Gui.Chart;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
using NinjaTrader.NinjaScript.Indicators;
using NinjaTrader.NinjaScript.DrawingTools;
#endregion

// Author: Luther Barnum
// EMA Cross Strategy with Re-entry Logic
// Linda Raschke 3/8 EMA crossover with separation filter

namespace NinjaTrader.NinjaScript.Strategies.LB
{
    public class EMACrossStrategyLB : Strategy
    {
        #region Variables

        // EMA indicators
        private EMA emaFast;
        private EMA emaSlow;
        private double fastEma, slowEma, prevFastEma, prevSlowEma;

        // Core indicators
        private ATR atrIndicator;
        private ADX adxIndicator;
        private EMA volumeEma;

        // ADX components
        private double plusDI, minusDI, prevPlusDI, prevMinusDI, prevADX;

        // Position management
        private double entryPrice, stopLoss, takeProfit;
        private double highWaterMark, lowWaterMark;
        private bool trailActive;
        private double trailTriggerPrice, trailDistancePoints;

        // Re-entry tracking
        private int lastExitBar;
        private bool lastExitProfitable;
        private int lastExitDirection;
        private int reentryCount;

        // Signal names
        private const string LONG_SIGNAL = "EMACrossLong";
        private const string SHORT_SIGNAL = "EMACrossShort";

        // Session management
        private HashSet<int> allowedHours;

        #endregion

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = @"EMA Crossover Strategy with Linda Raschke 3/8 setup.";
                Name = "EMACrossStrategyLB";

                Calculate = Calculate.OnBarClose;
                EntriesPerDirection = 1;
                EntryHandling = EntryHandling.AllEntries;
                IsExitOnSessionCloseStrategy = true;
                ExitOnSessionCloseSeconds = 30;
                BarsRequiredToTrade = 30;
                IsInstantiatedOnEachOptimizationIteration = true;

                // Feature Toggles
                EnableLongTrades = true;
                EnableShortTrades = true;
                EnableReentry = true;
                UseVolumeFilter = true;
                UseSessionFilter = true;

                // EMA Settings (Linda Raschke)
                EMAFastPeriod = 3;
                EMASLowPeriod = 8;
                EMASeparationFilter = true;
                EMASeparationMin = 0.35;

                // ADX Filter
                UseADXFilter = true;
                ADXThreshold = 35;
                ADXPeriod = 14;
                ADXMode = ADXFilterMode.DIRising;

                // Exit Settings
                ATRPeriod = 14;
                StopLossATR = 3.0;
                TakeProfitATR = 3.0;
                TrailTriggerATR = 0.15;
                TrailDistanceATR = 0.15;

                // Volume/Re-entry
                VolumeMAPeriod = 20;
                ReentryWaitBars = 3;
                ReentryADXMin = 40;
                MaxReentries = 10;

                // Session Hours
                Hour9 = true; Hour10 = true; Hour11 = true; Hour12 = true;
                Hour13 = true; Hour14 = true; Hour15 = true; Hour16 = true;
            }
            else if (State == State.DataLoaded)
            {
                // Initialize indicators
                emaFast = EMA(Close, EMAFastPeriod);
                emaSlow = EMA(Close, EMASLowPeriod);
                atrIndicator = ATR(ATRPeriod);
                adxIndicator = ADX(ADXPeriod);
                volumeEma = EMA(Volume, VolumeMAPeriod);

                AddChartIndicator(emaFast);
                AddChartIndicator(emaSlow);

                // Build allowed hours
                allowedHours = new HashSet<int>();
                if (Hour9) allowedHours.Add(9);
                if (Hour10) allowedHours.Add(10);
                if (Hour11) allowedHours.Add(11);
                if (Hour12) allowedHours.Add(12);
                if (Hour13) allowedHours.Add(13);
                if (Hour14) allowedHours.Add(14);
                if (Hour15) allowedHours.Add(15);
                if (Hour16) allowedHours.Add(16);

                // Initialize state
                lastExitBar = -999;
                lastExitProfitable = false;
                lastExitDirection = 0;
                reentryCount = 0;
            }
        }

        protected override void OnBarUpdate()
        {
            if (BarsInProgress != 0 || CurrentBar < BarsRequiredToTrade)
                return;

            // Store previous values
            prevFastEma = fastEma;
            prevSlowEma = slowEma;
            fastEma = emaFast[0];
            slowEma = emaSlow[0];

            // Get indicator values
            double atr = atrIndicator[0];
            double adx = adxIndicator[0];
            prevADX = adxIndicator[1];
            CalculateDI();

            double vol = Volume[0];
            double volMa = volumeEma[0];

            // Apply filters
            bool adxOk = !UseADXFilter || CheckADXCondition(adx, true);
            bool adxOkShort = !UseADXFilter || CheckADXCondition(adx, false);
            bool volumeOk = !UseVolumeFilter || vol > volMa;
            bool hourOk = !UseSessionFilter || allowedHours.Contains(Time[0].Hour);

            // Entry detection
            double separation = Math.Abs(fastEma - slowEma);
            bool separationOk = !EMASeparationFilter || separation >= EMASeparationMin;

            bool longBreakout = prevFastEma <= prevSlowEma && fastEma > slowEma && separationOk;
            bool shortBreakout = prevSlowEma <= prevFastEma && slowEma > fastEma && separationOk;
            bool stillAboveBand = fastEma > slowEma;
            bool stillBelowBand = fastEma < slowEma;

            // Position Management
            if (Position.MarketPosition == MarketPosition.Long)
                ManageLongPosition(atr);
            else if (Position.MarketPosition == MarketPosition.Short)
                ManageShortPosition(atr);
            else
            {
                // Entry Logic
                double slPoints = atr * StopLossATR;
                double tpPoints = atr * TakeProfitATR;

                bool longSignal = longBreakout && adxOk && volumeOk && hourOk && EnableLongTrades;
                bool shortSignal = shortBreakout && adxOkShort && volumeOk && hourOk && EnableShortTrades;

                // Re-entry check
                bool reentryAllowed = EnableReentry && lastExitProfitable &&
                    (CurrentBar - lastExitBar) >= ReentryWaitBars &&
                    reentryCount < MaxReentries && adx > ReentryADXMin;

                if (reentryAllowed)
                {
                    if (lastExitDirection == 1 && stillAboveBand && hourOk && volumeOk && EnableLongTrades)
                        longSignal = true;
                    if (lastExitDirection == -1 && stillBelowBand && hourOk && volumeOk && EnableShortTrades)
                        shortSignal = true;
                }

                if ((longBreakout || shortBreakout) && !reentryAllowed)
                    reentryCount = 0;

                // Execute entries
                if (longSignal)
                {
                    EnterLong(DefaultQuantity, LONG_SIGNAL);
                    entryPrice = Close[0];
                    stopLoss = Close[0] - slPoints;
                    takeProfit = Close[0] + tpPoints;
                    highWaterMark = Close[0];
                    trailActive = false;
                    trailTriggerPrice = Close[0] + atr * TrailTriggerATR;
                    trailDistancePoints = atr * TrailDistanceATR;
                    if (reentryAllowed && lastExitDirection == 1) reentryCount++;
                }
                else if (shortSignal)
                {
                    EnterShort(DefaultQuantity, SHORT_SIGNAL);
                    entryPrice = Close[0];
                    stopLoss = Close[0] + slPoints;
                    takeProfit = Close[0] - tpPoints;
                    lowWaterMark = Close[0];
                    trailActive = false;
                    trailTriggerPrice = Close[0] - atr * TrailTriggerATR;
                    trailDistancePoints = atr * TrailDistanceATR;
                    if (reentryAllowed && lastExitDirection == -1) reentryCount++;
                }
            }
        }

        #region Helper Methods
        // DI calculation, ADX check, position management methods...
        // (Same as base template - omitted for brevity)
        #endregion

        #region Properties

        [NinjaScriptProperty]
        [Display(Name = "Enable Long Trades", Order = 1, GroupName = "Feature Toggles")]
        public bool EnableLongTrades { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Enable Short Trades", Order = 2, GroupName = "Feature Toggles")]
        public bool EnableShortTrades { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Enable Re-entry", Order = 3, GroupName = "Feature Toggles")]
        public bool EnableReentry { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Use Volume Filter", Order = 4, GroupName = "Feature Toggles")]
        public bool UseVolumeFilter { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Use Session Filter", Order = 5, GroupName = "Feature Toggles")]
        public bool UseSessionFilter { get; set; }

        [NinjaScriptProperty]
        [Range(1, 20)]
        [Display(Name = "Fast EMA Period", Order = 1, GroupName = "Signal Settings")]
        public int EMAFastPeriod { get; set; }

        [NinjaScriptProperty]
        [Range(3, 50)]
        [Display(Name = "Slow EMA Period", Order = 2, GroupName = "Signal Settings")]
        public int EMASLowPeriod { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Use Separation Filter", Order = 3, GroupName = "Signal Settings")]
        public bool EMASeparationFilter { get; set; }

        [NinjaScriptProperty]
        [Range(0.0, 5.0)]
        [Display(Name = "Separation Min (points)", Order = 4, GroupName = "Signal Settings")]
        public double EMASeparationMin { get; set; }

        // ... Additional properties for ADX, exits, re-entry, session hours
        // (Same pattern as base template)

        #endregion
    }

    public enum ADXFilterMode { Traditional, DIAligned, DIRising, ADXRising, Combined }
}
```

### Strategy Generation Notes

Key features demonstrated in these examples:

1. **Configurable via inputs** - All strategy parameters are exposed as user inputs
2. **ADX filter with 5 modes** - Traditional, DI Aligned, DI Rising, ADX Rising, Combined
3. **ATR-based exits** - Stop loss, take profit, and trailing stop use ATR multipliers
4. **Re-entry logic** - Trend continuation after profitable exits
5. **Volume filter** - Require volume > MA for entries
6. **Session filter** - Restrict trading to allowed hours

See [strategy/WORKFLOW.md](strategy/WORKFLOW.md) for the interactive generation workflow.
