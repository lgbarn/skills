# NinjaScript Strategy Signal Code Blocks

This file contains signal-specific code blocks for all 11 entry signals. Each block is designed to replace placeholders in the base template.

---

## Signal Quick Reference

| Signal | WARMUP_BARS | Key Indicators |
|--------|-------------|----------------|
| vwap | 750 | Rolling VWAP queues |
| keltner | 50 | EMA, ATR |
| ema_cross | 30 | Fast EMA, Slow EMA |
| supertrend | 30 | Custom SuperTrend |
| alligator | 30 | SMMA arrays |
| ssl | 30 | SMA High, SMA Low |
| squeeze | 50 | BB, KC, Momentum |
| aroon | 60 | Custom Aroon |
| adx_only | 30 | ADX (use DI from base) |
| stochastic | 30 | Stochastic indicator |
| macd | 30 | MACD or custom SMA-based |

---

## 1. VWAP (Rolling VWAP Band Breakout)

### Metadata
```
STRATEGY_NAME: VWAP
STRATEGY_DESCRIPTION: Rolling VWAP Band Breakout Strategy with trend continuation re-entry logic. Uses rolling VWAP, ADX filter, ATR-based stops.
WARMUP_BARS: 750
```

### SIGNAL_VARIABLES
```csharp
// Rolling VWAP calculation arrays
private Queue<double> tpvQueue;    // Typical price * volume
private Queue<double> volQueue;    // Volume
private Queue<double> tp2vQueue;   // Typical price^2 * volume
private double sumTPV, sumVol, sumTP2V;

// VWAP values
private double vwapValue, upperBand, lowerBand;
private double prevUpperBand, prevLowerBand;
```

### SIGNAL_DEFAULTS
```csharp
// === VWAP Settings ===
VWAPWindow = 720;      // 24 hours at 2-min bars
BandMultiplier = 1.0;  // 1 standard deviation
```

### SIGNAL_INIT
```csharp
// Initialize rolling VWAP queues
tpvQueue = new Queue<double>(VWAPWindow);
volQueue = new Queue<double>(VWAPWindow);
tp2vQueue = new Queue<double>(VWAPWindow);
sumTPV = sumVol = sumTP2V = 0;
```

### SIGNAL_UPDATE
```csharp
// Store previous band values
prevUpperBand = upperBand;
prevLowerBand = lowerBand;

// Update Rolling VWAP
UpdateRollingVWAP();

// Validate VWAP values
if (double.IsNaN(vwapValue) || vwapValue == 0)
    return;
```

### ENTRY_DETECTION
```csharp
// Band breakout detection
bool longBreakout = Close[1] <= prevUpperBand && Close[0] > upperBand;
bool shortBreakout = Close[1] >= prevLowerBand && Close[0] < lowerBand;
bool stillAboveBand = Close[0] > upperBand;
bool stillBelowBand = Close[0] < lowerBand;
```

### REENTRY_CONDITION
```csharp
if (lastExitDirection == 1 && stillAboveBand && hourOk && volumeOk && EnableLongTrades)
    longSignal = true;
if (lastExitDirection == -1 && stillBelowBand && hourOk && volumeOk && EnableShortTrades)
    shortSignal = true;
```

### SIGNAL_CALCULATION_METHODS
```csharp
private void UpdateRollingVWAP()
{
    // Calculate typical price
    double tp = (High[0] + Low[0] + Close[0]) / 3.0;
    double vol = Volume[0] > 0 ? Volume[0] : 1;

    double currentTPV = tp * vol;
    double currentVol = vol;
    double currentTP2V = tp * tp * vol;

    // Add to queues and running sums
    tpvQueue.Enqueue(currentTPV);
    volQueue.Enqueue(currentVol);
    tp2vQueue.Enqueue(currentTP2V);

    sumTPV += currentTPV;
    sumVol += currentVol;
    sumTP2V += currentTP2V;

    // Remove oldest if queue is full
    while (tpvQueue.Count > VWAPWindow)
    {
        sumTPV -= tpvQueue.Dequeue();
        sumVol -= volQueue.Dequeue();
        sumTP2V -= tp2vQueue.Dequeue();
    }

    // Calculate VWAP and bands
    if (sumVol > 0)
    {
        vwapValue = sumTPV / sumVol;
        double variance = Math.Max(sumTP2V / sumVol - vwapValue * vwapValue, 0.0);
        double stDev = Math.Sqrt(variance);
        upperBand = vwapValue + BandMultiplier * stDev;
        lowerBand = vwapValue - BandMultiplier * stDev;
    }
    else
    {
        vwapValue = Close[0];
        upperBand = Close[0];
        lowerBand = Close[0];
    }
}
```

### SIGNAL_PROPERTIES
```csharp
[NinjaScriptProperty]
[Range(10, 2000)]
[Display(Name = "VWAP Window (bars)", Order = 1, GroupName = "Signal Settings")]
public int VWAPWindow { get; set; }

[NinjaScriptProperty]
[Range(0.1, 3.0)]
[Display(Name = "Band Multiplier (σ)", Order = 2, GroupName = "Signal Settings")]
public double BandMultiplier { get; set; }
```

---

## 2. Keltner (Keltner Channel Breakout)

### Metadata
```
STRATEGY_NAME: Keltner
STRATEGY_DESCRIPTION: Keltner Channel Breakout Strategy with trend continuation re-entry logic. Uses EMA-based channels with ATR bands.
WARMUP_BARS: 50
```

### SIGNAL_VARIABLES
```csharp
// Keltner Channel indicators
private EMA keltnerEma;
private ATR keltnerAtr;

// Keltner values
private double keltnerMid, keltnerUpper, keltnerLower;
private double prevKeltnerUpper, prevKeltnerLower;
```

### SIGNAL_DEFAULTS
```csharp
// === Keltner Settings ===
KeltnerEMAPeriod = 20;
KeltnerATRMult = 2.75;  // Optimal from backtest
```

### SIGNAL_INIT
```csharp
// Initialize Keltner indicators
keltnerEma = EMA(Close, KeltnerEMAPeriod);
keltnerAtr = ATR(KeltnerEMAPeriod);  // Use same period for ATR
```

### SIGNAL_UPDATE
```csharp
// Store previous values
prevKeltnerUpper = keltnerUpper;
prevKeltnerLower = keltnerLower;

// Calculate Keltner Channel
keltnerMid = keltnerEma[0];
double kc_atr = keltnerAtr[0];
keltnerUpper = keltnerMid + KeltnerATRMult * kc_atr;
keltnerLower = keltnerMid - KeltnerATRMult * kc_atr;
```

### ENTRY_DETECTION
```csharp
// Keltner breakout detection
bool longBreakout = Close[1] <= prevKeltnerUpper && Close[0] > keltnerUpper;
bool shortBreakout = Close[1] >= prevKeltnerLower && Close[0] < keltnerLower;
bool stillAboveBand = Close[0] > keltnerUpper;
bool stillBelowBand = Close[0] < keltnerLower;
```

### REENTRY_CONDITION
```csharp
if (lastExitDirection == 1 && stillAboveBand && hourOk && volumeOk && EnableLongTrades)
    longSignal = true;
if (lastExitDirection == -1 && stillBelowBand && hourOk && volumeOk && EnableShortTrades)
    shortSignal = true;
```

### SIGNAL_CALCULATION_METHODS
```csharp
// Keltner uses built-in indicators, no additional methods needed
```

### SIGNAL_PROPERTIES
```csharp
[NinjaScriptProperty]
[Range(5, 50)]
[Display(Name = "EMA Period", Order = 1, GroupName = "Signal Settings")]
public int KeltnerEMAPeriod { get; set; }

[NinjaScriptProperty]
[Range(0.5, 5.0)]
[Display(Name = "ATR Multiplier", Order = 2, GroupName = "Signal Settings")]
public double KeltnerATRMult { get; set; }
```

---

## 3. EMA Cross (EMA Crossover)

### Metadata
```
STRATEGY_NAME: EMACross
STRATEGY_DESCRIPTION: EMA Crossover Strategy with separation filter and trend continuation re-entry logic. Uses Linda Raschke's 3/8 setup.
WARMUP_BARS: 30
```

### SIGNAL_VARIABLES
```csharp
// EMA indicators
private EMA emaFast;
private EMA emaSlow;

// EMA values
private double fastEma, slowEma, prevFastEma, prevSlowEma;
```

### SIGNAL_DEFAULTS
```csharp
// === EMA Cross Settings ===
EMAFastPeriod = 3;     // Linda Raschke
EMASLowPeriod = 8;     // Linda Raschke
EMASeparationFilter = true;
EMASeparationMin = 0.35;  // Minimum points between EMAs
```

### SIGNAL_INIT
```csharp
// Initialize EMA indicators
emaFast = EMA(Close, EMAFastPeriod);
emaSlow = EMA(Close, EMASLowPeriod);
```

### SIGNAL_UPDATE
```csharp
// Store previous values
prevFastEma = fastEma;
prevSlowEma = slowEma;

// Get current EMA values
fastEma = emaFast[0];
slowEma = emaSlow[0];
```

### ENTRY_DETECTION
```csharp
// EMA crossover detection
double separation = Math.Abs(fastEma - slowEma);
bool separationOk = !EMASeparationFilter || separation >= EMASeparationMin;

bool longBreakout = prevFastEma <= prevSlowEma && fastEma > slowEma && separationOk;
bool shortBreakout = prevSlowEma <= prevFastEma && slowEma > fastEma && separationOk;
bool stillAboveBand = fastEma > slowEma;  // Fast still above slow
bool stillBelowBand = fastEma < slowEma;  // Fast still below slow
```

### REENTRY_CONDITION
```csharp
if (lastExitDirection == 1 && stillAboveBand && hourOk && volumeOk && EnableLongTrades)
    longSignal = true;
if (lastExitDirection == -1 && stillBelowBand && hourOk && volumeOk && EnableShortTrades)
    shortSignal = true;
```

### SIGNAL_CALCULATION_METHODS
```csharp
// EMA uses built-in indicators, no additional methods needed
```

### SIGNAL_PROPERTIES
```csharp
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
```

---

## 4. SuperTrend

### Metadata
```
STRATEGY_NAME: SuperTrend
STRATEGY_DESCRIPTION: SuperTrend Direction Flip Strategy with trend continuation re-entry logic. Uses ATR-based dynamic support/resistance.
WARMUP_BARS: 30
```

### SIGNAL_VARIABLES
```csharp
// SuperTrend calculation
private ATR stAtr;
private double superTrendValue;
private int superTrendDir;      // 1 = up, -1 = down
private int prevSuperTrendDir;
private double upperBandST, lowerBandST;
private double prevUpperBandST, prevLowerBandST;
```

### SIGNAL_DEFAULTS
```csharp
// === SuperTrend Settings ===
SuperTrendPeriod = 10;
SuperTrendMult = 3.0;
```

### SIGNAL_INIT
```csharp
// Initialize SuperTrend ATR
stAtr = ATR(SuperTrendPeriod);
superTrendDir = 1;
prevSuperTrendDir = 1;
```

### SIGNAL_UPDATE
```csharp
// Store previous direction
prevSuperTrendDir = superTrendDir;
prevUpperBandST = upperBandST;
prevLowerBandST = lowerBandST;

// Calculate SuperTrend
CalculateSuperTrend();
```

### ENTRY_DETECTION
```csharp
// SuperTrend direction flip detection
bool longBreakout = prevSuperTrendDir == -1 && superTrendDir == 1;
bool shortBreakout = prevSuperTrendDir == 1 && superTrendDir == -1;
bool stillAboveBand = superTrendDir == 1;
bool stillBelowBand = superTrendDir == -1;
```

### REENTRY_CONDITION
```csharp
if (lastExitDirection == 1 && stillAboveBand && hourOk && volumeOk && EnableLongTrades)
    longSignal = true;
if (lastExitDirection == -1 && stillBelowBand && hourOk && volumeOk && EnableShortTrades)
    shortSignal = true;
```

### SIGNAL_CALCULATION_METHODS
```csharp
private void CalculateSuperTrend()
{
    double hl2 = (High[0] + Low[0]) / 2.0;
    double atrValue = stAtr[0];

    // Calculate basic bands
    double basicUpper = hl2 + SuperTrendMult * atrValue;
    double basicLower = hl2 - SuperTrendMult * atrValue;

    // Final upper band (can only decrease in downtrend)
    if (basicUpper < prevUpperBandST || Close[1] > prevUpperBandST)
        upperBandST = basicUpper;
    else
        upperBandST = prevUpperBandST;

    // Final lower band (can only increase in uptrend)
    if (basicLower > prevLowerBandST || Close[1] < prevLowerBandST)
        lowerBandST = basicLower;
    else
        lowerBandST = prevLowerBandST;

    // Determine direction
    if (prevSuperTrendDir == 1)
    {
        superTrendDir = Close[0] >= lowerBandST ? 1 : -1;
    }
    else
    {
        superTrendDir = Close[0] <= upperBandST ? -1 : 1;
    }

    // Set SuperTrend value based on direction
    superTrendValue = superTrendDir == 1 ? lowerBandST : upperBandST;
}
```

### SIGNAL_PROPERTIES
```csharp
[NinjaScriptProperty]
[Range(5, 30)]
[Display(Name = "SuperTrend Period", Order = 1, GroupName = "Signal Settings")]
public int SuperTrendPeriod { get; set; }

[NinjaScriptProperty]
[Range(1.0, 5.0)]
[Display(Name = "SuperTrend Multiplier", Order = 2, GroupName = "Signal Settings")]
public double SuperTrendMult { get; set; }
```

---

## 5. Alligator (Williams Alligator)

### Metadata
```
STRATEGY_NAME: Alligator
STRATEGY_DESCRIPTION: Williams Alligator Alignment Strategy with trend continuation re-entry logic. Uses SMMA with offsets for trend confirmation.
WARMUP_BARS: 30
```

### SIGNAL_VARIABLES
```csharp
// Alligator SMMA values
private double[] jawBuffer;
private double[] teethBuffer;
private double[] lipsBuffer;
private double jaw, teeth, lips;
private double prevJaw, prevTeeth, prevLips;
private bool alignedUp, alignedDown, prevAlignedUp, prevAlignedDown;
```

### SIGNAL_DEFAULTS
```csharp
// === Alligator Settings ===
AlligatorJawPeriod = 13;
AlligatorJawOffset = 8;
AlligatorTeethPeriod = 8;
AlligatorTeethOffset = 5;
AlligatorLipsPeriod = 5;
AlligatorLipsOffset = 3;
```

### SIGNAL_INIT
```csharp
// Initialize Alligator buffers
int maxOffset = Math.Max(AlligatorJawOffset, Math.Max(AlligatorTeethOffset, AlligatorLipsOffset));
jawBuffer = new double[maxOffset + 1];
teethBuffer = new double[maxOffset + 1];
lipsBuffer = new double[maxOffset + 1];
```

### SIGNAL_UPDATE
```csharp
// Store previous alignment
prevAlignedUp = alignedUp;
prevAlignedDown = alignedDown;
prevJaw = jaw;
prevTeeth = teeth;
prevLips = lips;

// Calculate Alligator
CalculateAlligator();

// Check alignment
alignedUp = lips > teeth && teeth > jaw;
alignedDown = lips < teeth && teeth < jaw;
```

### ENTRY_DETECTION
```csharp
// Alligator alignment detection
bool longBreakout = !prevAlignedUp && alignedUp;
bool shortBreakout = !prevAlignedDown && alignedDown;
bool stillAboveBand = alignedUp;
bool stillBelowBand = alignedDown;
```

### REENTRY_CONDITION
```csharp
if (lastExitDirection == 1 && stillAboveBand && hourOk && volumeOk && EnableLongTrades)
    longSignal = true;
if (lastExitDirection == -1 && stillBelowBand && hourOk && volumeOk && EnableShortTrades)
    shortSignal = true;
```

### SIGNAL_CALCULATION_METHODS
```csharp
private void CalculateAlligator()
{
    // SMMA calculation (Smoothed Moving Average = Wilder's smoothing)
    double median = (High[0] + Low[0]) / 2.0;

    // Calculate SMMA for each line
    jaw = CalculateSMMA(AlligatorJawPeriod, median, jaw);
    teeth = CalculateSMMA(AlligatorTeethPeriod, median, teeth);
    lips = CalculateSMMA(AlligatorLipsPeriod, median, lips);

    // Note: Offsets are applied when comparing values
    // In real-time, we'd shift the display, but for entry detection
    // we compare the current calculated values
}

private double CalculateSMMA(int period, double value, double prevSmma)
{
    if (CurrentBar < period)
    {
        // Simple average for warmup
        double sum = 0;
        for (int i = 0; i < Math.Min(CurrentBar + 1, period); i++)
            sum += (High[i] + Low[i]) / 2.0;
        return sum / Math.Min(CurrentBar + 1, period);
    }

    // SMMA = (prevSMMA * (period - 1) + value) / period
    return (prevSmma * (period - 1) + value) / period;
}
```

### SIGNAL_PROPERTIES
```csharp
[NinjaScriptProperty]
[Range(5, 30)]
[Display(Name = "Jaw Period", Order = 1, GroupName = "Signal Settings")]
public int AlligatorJawPeriod { get; set; }

[NinjaScriptProperty]
[Range(1, 15)]
[Display(Name = "Jaw Offset", Order = 2, GroupName = "Signal Settings")]
public int AlligatorJawOffset { get; set; }

[NinjaScriptProperty]
[Range(3, 20)]
[Display(Name = "Teeth Period", Order = 3, GroupName = "Signal Settings")]
public int AlligatorTeethPeriod { get; set; }

[NinjaScriptProperty]
[Range(1, 10)]
[Display(Name = "Teeth Offset", Order = 4, GroupName = "Signal Settings")]
public int AlligatorTeethOffset { get; set; }

[NinjaScriptProperty]
[Range(2, 15)]
[Display(Name = "Lips Period", Order = 5, GroupName = "Signal Settings")]
public int AlligatorLipsPeriod { get; set; }

[NinjaScriptProperty]
[Range(1, 8)]
[Display(Name = "Lips Offset", Order = 6, GroupName = "Signal Settings")]
public int AlligatorLipsOffset { get; set; }
```

---

## 6. SSL Channel

### Metadata
```
STRATEGY_NAME: SSL
STRATEGY_DESCRIPTION: SSL Channel Direction Flip Strategy with trend continuation re-entry logic. Uses SMA-based dynamic support/resistance.
WARMUP_BARS: 30
```

### SIGNAL_VARIABLES
```csharp
// SSL Channel
private SMA smaHigh;
private SMA smaLow;
private int sslDir, prevSslDir;
private double sslUp, sslDown;
```

### SIGNAL_DEFAULTS
```csharp
// === SSL Settings ===
SSLPeriod = 10;
```

### SIGNAL_INIT
```csharp
// Initialize SSL indicators
smaHigh = SMA(High, SSLPeriod);
smaLow = SMA(Low, SSLPeriod);
sslDir = 1;
prevSslDir = 1;
```

### SIGNAL_UPDATE
```csharp
// Store previous direction
prevSslDir = sslDir;

// Calculate SSL Channel
sslUp = smaHigh[0];
sslDown = smaLow[0];

// Determine direction based on close position
if (Close[0] > sslUp)
    sslDir = 1;
else if (Close[0] < sslDown)
    sslDir = -1;
// else maintain previous direction
```

### ENTRY_DETECTION
```csharp
// SSL direction flip detection
bool longBreakout = prevSslDir == -1 && sslDir == 1;
bool shortBreakout = prevSslDir == 1 && sslDir == -1;
bool stillAboveBand = sslDir == 1;
bool stillBelowBand = sslDir == -1;
```

### REENTRY_CONDITION
```csharp
if (lastExitDirection == 1 && stillAboveBand && hourOk && volumeOk && EnableLongTrades)
    longSignal = true;
if (lastExitDirection == -1 && stillBelowBand && hourOk && volumeOk && EnableShortTrades)
    shortSignal = true;
```

### SIGNAL_CALCULATION_METHODS
```csharp
// SSL uses built-in SMA indicators, no additional methods needed
```

### SIGNAL_PROPERTIES
```csharp
[NinjaScriptProperty]
[Range(5, 30)]
[Display(Name = "SSL Period", Order = 1, GroupName = "Signal Settings")]
public int SSLPeriod { get; set; }
```

---

## 7. Squeeze (TTM Squeeze)

### Metadata
```
STRATEGY_NAME: Squeeze
STRATEGY_DESCRIPTION: TTM Squeeze Release Strategy with momentum direction. Fires when Bollinger Bands exit Keltner Channels.
WARMUP_BARS: 50
```

### SIGNAL_VARIABLES
```csharp
// Squeeze indicators
private Bollinger bb;
private ATR kcAtr;
private EMA kcEma;
private Momentum mom;

// Squeeze state
private bool squeezeOn, prevSqueezeOn;
private double momentum, prevMomentum;
```

### SIGNAL_DEFAULTS
```csharp
// === Squeeze Settings ===
SqueezeBBPeriod = 20;
SqueezeBBMult = 2.0;
SqueezeKCPeriod = 20;
SqueezeKCMult = 1.5;
SqueezeMomentumPeriod = 12;
```

### SIGNAL_INIT
```csharp
// Initialize Squeeze indicators
bb = Bollinger(Close, SqueezeBBMult, SqueezeBBPeriod);
kcAtr = ATR(SqueezeKCPeriod);
kcEma = EMA(Close, SqueezeKCPeriod);
mom = Momentum(Close, SqueezeMomentumPeriod);

squeezeOn = false;
prevSqueezeOn = false;
```

### SIGNAL_UPDATE
```csharp
// Store previous values
prevSqueezeOn = squeezeOn;
prevMomentum = momentum;

// Calculate Keltner Channel bands
double kcUpper = kcEma[0] + SqueezeKCMult * kcAtr[0];
double kcLower = kcEma[0] - SqueezeKCMult * kcAtr[0];

// Get Bollinger Bands
double bbUpper = bb.Upper[0];
double bbLower = bb.Lower[0];

// Squeeze is ON when BB inside KC
squeezeOn = bbLower > kcLower && bbUpper < kcUpper;

// Get momentum
momentum = mom[0];
```

### ENTRY_DETECTION
```csharp
// Squeeze release detection (was on, now off)
bool squeezeFired = prevSqueezeOn && !squeezeOn;

bool longBreakout = squeezeFired && momentum > 0;
bool shortBreakout = squeezeFired && momentum < 0;
bool stillAboveBand = momentum > 0;   // Momentum still positive
bool stillBelowBand = momentum < 0;   // Momentum still negative
```

### REENTRY_CONDITION
```csharp
if (lastExitDirection == 1 && stillAboveBand && hourOk && volumeOk && EnableLongTrades)
    longSignal = true;
if (lastExitDirection == -1 && stillBelowBand && hourOk && volumeOk && EnableShortTrades)
    shortSignal = true;
```

### SIGNAL_CALCULATION_METHODS
```csharp
// Squeeze uses built-in indicators, no additional methods needed
```

### SIGNAL_PROPERTIES
```csharp
[NinjaScriptProperty]
[Range(10, 30)]
[Display(Name = "BB Period", Order = 1, GroupName = "Signal Settings")]
public int SqueezeBBPeriod { get; set; }

[NinjaScriptProperty]
[Range(1.0, 3.0)]
[Display(Name = "BB Multiplier", Order = 2, GroupName = "Signal Settings")]
public double SqueezeBBMult { get; set; }

[NinjaScriptProperty]
[Range(10, 30)]
[Display(Name = "KC Period", Order = 3, GroupName = "Signal Settings")]
public int SqueezeKCPeriod { get; set; }

[NinjaScriptProperty]
[Range(0.5, 3.0)]
[Display(Name = "KC Multiplier", Order = 4, GroupName = "Signal Settings")]
public double SqueezeKCMult { get; set; }

[NinjaScriptProperty]
[Range(5, 20)]
[Display(Name = "Momentum Period", Order = 5, GroupName = "Signal Settings")]
public int SqueezeMomentumPeriod { get; set; }
```

---

## 8. Aroon

### Metadata
```
STRATEGY_NAME: Aroon
STRATEGY_DESCRIPTION: Aroon Crossover Strategy with trend continuation re-entry logic. Measures bars since highest high / lowest low.
WARMUP_BARS: 60
```

### SIGNAL_VARIABLES
```csharp
// Aroon values
private double aroonUp, aroonDown;
private double prevAroonUp, prevAroonDown;
```

### SIGNAL_DEFAULTS
```csharp
// === Aroon Settings ===
AroonPeriod = 50;  // Optimal from backtest
```

### SIGNAL_INIT
```csharp
// Aroon uses custom calculation, no indicators to initialize
aroonUp = aroonDown = 0;
prevAroonUp = prevAroonDown = 0;
```

### SIGNAL_UPDATE
```csharp
// Store previous values
prevAroonUp = aroonUp;
prevAroonDown = aroonDown;

// Calculate Aroon
CalculateAroon();
```

### ENTRY_DETECTION
```csharp
// Aroon crossover detection
bool longBreakout = prevAroonUp <= prevAroonDown && aroonUp > aroonDown;
bool shortBreakout = prevAroonDown <= prevAroonUp && aroonDown > aroonUp;
bool stillAboveBand = aroonUp > aroonDown;
bool stillBelowBand = aroonDown > aroonUp;
```

### REENTRY_CONDITION
```csharp
if (lastExitDirection == 1 && stillAboveBand && hourOk && volumeOk && EnableLongTrades)
    longSignal = true;
if (lastExitDirection == -1 && stillBelowBand && hourOk && volumeOk && EnableShortTrades)
    shortSignal = true;
```

### SIGNAL_CALCULATION_METHODS
```csharp
private void CalculateAroon()
{
    if (CurrentBar < AroonPeriod)
    {
        aroonUp = aroonDown = 50;
        return;
    }

    // Find bars since highest high and lowest low
    int barsSinceHigh = 0;
    int barsSinceLow = 0;
    double highestHigh = High[0];
    double lowestLow = Low[0];

    for (int i = 0; i <= AroonPeriod; i++)
    {
        if (High[i] >= highestHigh)
        {
            highestHigh = High[i];
            barsSinceHigh = i;
        }
        if (Low[i] <= lowestLow)
        {
            lowestLow = Low[i];
            barsSinceLow = i;
        }
    }

    // Calculate Aroon values
    aroonUp = 100.0 * (AroonPeriod - barsSinceHigh) / AroonPeriod;
    aroonDown = 100.0 * (AroonPeriod - barsSinceLow) / AroonPeriod;
}
```

### SIGNAL_PROPERTIES
```csharp
[NinjaScriptProperty]
[Range(10, 100)]
[Display(Name = "Aroon Period", Order = 1, GroupName = "Signal Settings")]
public int AroonPeriod { get; set; }
```

---

## 9. ADX Only (+DI/-DI Crossover)

### Metadata
```
STRATEGY_NAME: ADXOnly
STRATEGY_DESCRIPTION: DI Crossover Strategy. Uses +DI/-DI crossover from ADX calculation for trend entries.
WARMUP_BARS: 30
```

### SIGNAL_VARIABLES
```csharp
// ADX Only uses the base template's DI calculation
// No additional variables needed
```

### SIGNAL_DEFAULTS
```csharp
// Uses base ADX settings
// No additional defaults
```

### SIGNAL_INIT
```csharp
// Uses base ADX indicator
// No additional initialization
```

### SIGNAL_UPDATE
```csharp
// DI values are calculated in base template's CalculateDI()
// No additional update needed
```

### ENTRY_DETECTION
```csharp
// DI crossover detection (uses base template's plusDI, minusDI, prevPlusDI, prevMinusDI)
bool longBreakout = prevPlusDI <= prevMinusDI && plusDI > minusDI;
bool shortBreakout = prevMinusDI <= prevPlusDI && minusDI > plusDI;
bool stillAboveBand = plusDI > minusDI;
bool stillBelowBand = minusDI > plusDI;
```

### REENTRY_CONDITION
```csharp
if (lastExitDirection == 1 && stillAboveBand && hourOk && volumeOk && EnableLongTrades)
    longSignal = true;
if (lastExitDirection == -1 && stillBelowBand && hourOk && volumeOk && EnableShortTrades)
    shortSignal = true;
```

### SIGNAL_CALCULATION_METHODS
```csharp
// Uses base template's CalculateDI() method
// No additional methods needed
```

### SIGNAL_PROPERTIES
```csharp
// Uses base ADX properties (ADXPeriod, ADXThreshold)
// No additional properties needed
```

---

## 10. Stochastic (Linda Raschke Style)

### Metadata
```
STRATEGY_NAME: Stochastic
STRATEGY_DESCRIPTION: Stochastic %K/%D Crossover Strategy with Linda Raschke's 7-16 setup. Uses oversold/overbought zone entries.
WARMUP_BARS: 30
```

### SIGNAL_VARIABLES
```csharp
// Stochastic indicator
private Stochastics stoch;
private double stochK, stochD, prevStochK, prevStochD;
```

### SIGNAL_DEFAULTS
```csharp
// === Stochastic Settings (Linda Raschke) ===
StochKPeriod = 7;
StochKSlowing = 4;
StochDPeriod = 16;
StochOverbought = 80;
StochOversold = 20;
```

### SIGNAL_INIT
```csharp
// Initialize Stochastic indicator
stoch = Stochastics(StochDPeriod, StochKPeriod, StochKSlowing);
```

### SIGNAL_UPDATE
```csharp
// Store previous values
prevStochK = stochK;
prevStochD = stochD;

// Get current values
stochK = stoch.K[0];
stochD = stoch.D[0];
```

### ENTRY_DETECTION
```csharp
// Stochastic crossover detection
bool longBreakout = prevStochK <= prevStochD && stochK > stochD &&
                    (prevStochK < StochOversold || stochK < 50);
bool shortBreakout = prevStochK >= prevStochD && stochK < stochD &&
                     (prevStochK > StochOverbought || stochK > 50);
bool stillAboveBand = stochK > stochD;
bool stillBelowBand = stochK < stochD;
```

### REENTRY_CONDITION
```csharp
if (lastExitDirection == 1 && stillAboveBand && hourOk && volumeOk && EnableLongTrades)
    longSignal = true;
if (lastExitDirection == -1 && stillBelowBand && hourOk && volumeOk && EnableShortTrades)
    shortSignal = true;
```

### SIGNAL_CALCULATION_METHODS
```csharp
// Stochastic uses built-in indicator, no additional methods needed
```

### SIGNAL_PROPERTIES
```csharp
[NinjaScriptProperty]
[Range(3, 21)]
[Display(Name = "%K Period", Order = 1, GroupName = "Signal Settings")]
public int StochKPeriod { get; set; }

[NinjaScriptProperty]
[Range(1, 10)]
[Display(Name = "%K Slowing", Order = 2, GroupName = "Signal Settings")]
public int StochKSlowing { get; set; }

[NinjaScriptProperty]
[Range(3, 30)]
[Display(Name = "%D Period", Order = 3, GroupName = "Signal Settings")]
public int StochDPeriod { get; set; }

[NinjaScriptProperty]
[Range(60, 95)]
[Display(Name = "Overbought", Order = 4, GroupName = "Signal Settings")]
public int StochOverbought { get; set; }

[NinjaScriptProperty]
[Range(5, 40)]
[Display(Name = "Oversold", Order = 5, GroupName = "Signal Settings")]
public int StochOversold { get; set; }
```

---

## 11. MACD (Linda Raschke Style)

### Metadata
```
STRATEGY_NAME: MACD
STRATEGY_DESCRIPTION: MACD Line/Signal Crossover Strategy with Linda Raschke's 3-10-16 SMA-based setup.
WARMUP_BARS: 30
```

### SIGNAL_VARIABLES
```csharp
// MACD components (SMA-based for Linda Raschke style)
private SMA macdFastSma;
private SMA macdSlowSma;
private SMA macdSignalSma;
private double macdLine, macdSignal, prevMacdLine, prevMacdSignal;

// Note: If using standard EMA-based MACD, use NinjaTrader's built-in MACD indicator
private bool useSmaBasedMacd = true;
```

### SIGNAL_DEFAULTS
```csharp
// === MACD Settings (Linda Raschke) ===
MACDFastPeriod = 3;
MACDSlowPeriod = 10;
MACDSignalPeriod = 16;
MACDUseSMA = true;  // Linda Raschke uses SMA
```

### SIGNAL_INIT
```csharp
// Initialize MACD (SMA-based for Linda Raschke)
if (MACDUseSMA)
{
    macdFastSma = SMA(Close, MACDFastPeriod);
    macdSlowSma = SMA(Close, MACDSlowPeriod);
    // Signal line is SMA of MACD line - we'll calculate manually
}
else
{
    // Use built-in EMA-based MACD
    // MACD macdIndicator = MACD(Close, MACDFastPeriod, MACDSlowPeriod, MACDSignalPeriod);
}

useSmaBasedMacd = MACDUseSMA;
```

### SIGNAL_UPDATE
```csharp
// Store previous values
prevMacdLine = macdLine;
prevMacdSignal = macdSignal;

// Calculate MACD
if (useSmaBasedMacd)
{
    macdLine = macdFastSma[0] - macdSlowSma[0];

    // Calculate signal line as SMA of MACD line
    // Simplified: use running average
    if (CurrentBar < MACDSignalPeriod)
    {
        macdSignal = macdLine;
    }
    else
    {
        // Approximate SMA of MACD line
        double sum = 0;
        for (int i = 0; i < MACDSignalPeriod && i < CurrentBar; i++)
        {
            double ml = macdFastSma[i] - macdSlowSma[i];
            sum += ml;
        }
        macdSignal = sum / Math.Min(MACDSignalPeriod, CurrentBar);
    }
}
```

### ENTRY_DETECTION
```csharp
// MACD crossover detection
bool longBreakout = prevMacdLine <= prevMacdSignal && macdLine > macdSignal;
bool shortBreakout = prevMacdLine >= prevMacdSignal && macdLine < macdSignal;
bool stillAboveBand = macdLine > macdSignal;
bool stillBelowBand = macdLine < macdSignal;
```

### REENTRY_CONDITION
```csharp
if (lastExitDirection == 1 && stillAboveBand && hourOk && volumeOk && EnableLongTrades)
    longSignal = true;
if (lastExitDirection == -1 && stillBelowBand && hourOk && volumeOk && EnableShortTrades)
    shortSignal = true;
```

### SIGNAL_CALCULATION_METHODS
```csharp
// MACD calculation is done in SIGNAL_UPDATE section
// No additional methods needed for SMA-based approach
```

### SIGNAL_PROPERTIES
```csharp
[NinjaScriptProperty]
[Range(2, 20)]
[Display(Name = "Fast Period", Order = 1, GroupName = "Signal Settings")]
public int MACDFastPeriod { get; set; }

[NinjaScriptProperty]
[Range(5, 50)]
[Display(Name = "Slow Period", Order = 2, GroupName = "Signal Settings")]
public int MACDSlowPeriod { get; set; }

[NinjaScriptProperty]
[Range(5, 30)]
[Display(Name = "Signal Period", Order = 3, GroupName = "Signal Settings")]
public int MACDSignalPeriod { get; set; }

[NinjaScriptProperty]
[Display(Name = "Use SMA (Linda Raschke)", Order = 4, GroupName = "Signal Settings")]
public bool MACDUseSMA { get; set; }
```

---

## Assembly Notes

When generating a complete strategy:

1. **Select signal** from this file
2. **Copy template** from TEMPLATE.md
3. **Replace placeholders** with signal-specific code blocks
4. **Test compilation** in NinjaTrader 8 IDE
5. **Verify defaults** match backtest.py CONFIG

### Common Adjustments

- **Additional using statements**: Add `using System.Collections.Generic;` for Queue-based signals
- **Property order**: Adjust `Order` attribute values for logical grouping
- **Range attributes**: Match validation ranges to backtest.py CONFIG
- **Warmup bars**: Set BarsRequiredToTrade based on signal's indicator periods
