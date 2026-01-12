# NinjaScript C# Strategy Template

Use this template as the starting point for new NinjaTrader 8 strategies with entry signals, ADX filtering, ATR-based exits, and re-entry logic.

---

## Complete Template

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
// {{STRATEGY_NAME}} Strategy with Re-entry Logic
// {{STRATEGY_DESCRIPTION}}

namespace NinjaTrader.NinjaScript.Strategies.LB
{
    public class {{STRATEGY_NAME}}StrategyLB : Strategy
    {
        #region Variables

        // ═══════════════════════════════════════════════════════════
        // CORE INDICATORS
        // ═══════════════════════════════════════════════════════════
        private ATR atrIndicator;
        private ADX adxIndicator;
        private EMA volumeEma;

        // ═══════════════════════════════════════════════════════════
        // SIGNAL-SPECIFIC VARIABLES
        // ═══════════════════════════════════════════════════════════
        {{SIGNAL_VARIABLES}}

        // ═══════════════════════════════════════════════════════════
        // ADX COMPONENTS (for mode checking)
        // ═══════════════════════════════════════════════════════════
        private double plusDI, minusDI, prevPlusDI, prevMinusDI;
        private double prevADX;

        // ═══════════════════════════════════════════════════════════
        // POSITION MANAGEMENT
        // ═══════════════════════════════════════════════════════════
        private double entryPrice;
        private double stopLoss;
        private double takeProfit;
        private double highWaterMark;
        private double lowWaterMark;
        private bool trailActive;
        private double trailTriggerPrice;
        private double trailDistancePoints;

        // ═══════════════════════════════════════════════════════════
        // RE-ENTRY TRACKING
        // ═══════════════════════════════════════════════════════════
        private int lastExitBar;
        private bool lastExitProfitable;
        private int lastExitDirection;  // 1 = long, -1 = short
        private int reentryCount;

        // ═══════════════════════════════════════════════════════════
        // SIGNAL NAMES
        // ═══════════════════════════════════════════════════════════
        private const string LONG_SIGNAL = "{{STRATEGY_NAME}}Long";
        private const string SHORT_SIGNAL = "{{STRATEGY_NAME}}Short";

        // ═══════════════════════════════════════════════════════════
        // SESSION MANAGEMENT
        // ═══════════════════════════════════════════════════════════
        private HashSet<int> allowedHours;

        #endregion

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                // ═══════════════════════════════════════════════════════════
                // STRATEGY IDENTIFICATION
                // ═══════════════════════════════════════════════════════════
                Description = @"{{STRATEGY_DESCRIPTION}}";
                Name = "{{STRATEGY_NAME}}StrategyLB";

                // ═══════════════════════════════════════════════════════════
                // CALCULATION SETTINGS
                // ═══════════════════════════════════════════════════════════
                Calculate = Calculate.OnBarClose;
                EntriesPerDirection = 1;
                EntryHandling = EntryHandling.AllEntries;
                IsExitOnSessionCloseStrategy = true;
                ExitOnSessionCloseSeconds = 30;
                IsFillLimitOnTouch = false;
                MaximumBarsLookBack = MaximumBarsLookBack.TwoHundredFiftySix;
                OrderFillResolution = OrderFillResolution.Standard;
                Slippage = 1;
                StartBehavior = StartBehavior.WaitUntilFlat;
                TimeInForce = TimeInForce.Gtc;
                TraceOrders = false;
                RealtimeErrorHandling = RealtimeErrorHandling.StopCancelClose;
                StopTargetHandling = StopTargetHandling.PerEntryExecution;
                BarsRequiredToTrade = {{WARMUP_BARS}};
                IsInstantiatedOnEachOptimizationIteration = true;

                // ═══════════════════════════════════════════════════════════
                // FEATURE TOGGLES
                // ═══════════════════════════════════════════════════════════
                EnableLongTrades = true;
                EnableShortTrades = true;
                EnableReentry = true;
                UseVolumeFilter = true;
                UseSessionFilter = true;

                // ═══════════════════════════════════════════════════════════
                // SIGNAL SETTINGS
                // ═══════════════════════════════════════════════════════════
                {{SIGNAL_DEFAULTS}}

                // ═══════════════════════════════════════════════════════════
                // ADX FILTER SETTINGS
                // ═══════════════════════════════════════════════════════════
                UseADXFilter = true;
                ADXThreshold = 35;
                ADXPeriod = 14;
                ADXMode = ADXFilterMode.DIRising;

                // ═══════════════════════════════════════════════════════════
                // EXIT SETTINGS (ATR-based)
                // ═══════════════════════════════════════════════════════════
                ATRPeriod = 14;
                StopLossATR = 3.0;
                TakeProfitATR = 3.0;
                TrailTriggerATR = 0.15;
                TrailDistanceATR = 0.15;

                // ═══════════════════════════════════════════════════════════
                // VOLUME FILTER
                // ═══════════════════════════════════════════════════════════
                VolumeMAPeriod = 20;

                // ═══════════════════════════════════════════════════════════
                // RE-ENTRY SETTINGS
                // ═══════════════════════════════════════════════════════════
                ReentryWaitBars = 3;
                ReentryADXMin = 40;
                MaxReentries = 10;

                // ═══════════════════════════════════════════════════════════
                // SESSION HOURS (ET)
                // ═══════════════════════════════════════════════════════════
                Hour9 = true;
                Hour10 = true;
                Hour11 = true;
                Hour12 = true;
                Hour13 = true;
                Hour14 = true;
                Hour15 = true;
                Hour16 = true;
                Hour18 = true;
                Hour19 = true;
                Hour20 = true;
            }
            else if (State == State.Configure)
            {
                // No fixed stop/target - we manage exits manually
            }
            else if (State == State.DataLoaded)
            {
                // ═══════════════════════════════════════════════════════════
                // INITIALIZE CORE INDICATORS
                // ═══════════════════════════════════════════════════════════
                atrIndicator = ATR(ATRPeriod);
                adxIndicator = ADX(ADXPeriod);
                volumeEma = EMA(Volume, VolumeMAPeriod);

                AddChartIndicator(atrIndicator);
                AddChartIndicator(adxIndicator);

                // ═══════════════════════════════════════════════════════════
                // INITIALIZE SIGNAL-SPECIFIC INDICATORS
                // ═══════════════════════════════════════════════════════════
                {{SIGNAL_INIT}}

                // ═══════════════════════════════════════════════════════════
                // BUILD ALLOWED HOURS SET
                // ═══════════════════════════════════════════════════════════
                allowedHours = new HashSet<int>();
                if (Hour9) allowedHours.Add(9);
                if (Hour10) allowedHours.Add(10);
                if (Hour11) allowedHours.Add(11);
                if (Hour12) allowedHours.Add(12);
                if (Hour13) allowedHours.Add(13);
                if (Hour14) allowedHours.Add(14);
                if (Hour15) allowedHours.Add(15);
                if (Hour16) allowedHours.Add(16);
                if (Hour18) allowedHours.Add(18);
                if (Hour19) allowedHours.Add(19);
                if (Hour20) allowedHours.Add(20);

                // ═══════════════════════════════════════════════════════════
                // INITIALIZE STATE
                // ═══════════════════════════════════════════════════════════
                lastExitBar = -999;
                lastExitProfitable = false;
                lastExitDirection = 0;
                reentryCount = 0;
            }
        }

        protected override void OnBarUpdate()
        {
            // ═══════════════════════════════════════════════════════════
            // PRIMARY BARS SERIES ONLY
            // ═══════════════════════════════════════════════════════════
            if (BarsInProgress != 0)
                return;

            // ═══════════════════════════════════════════════════════════
            // WARMUP CHECK
            // ═══════════════════════════════════════════════════════════
            if (CurrentBar < BarsRequiredToTrade)
                return;

            // ═══════════════════════════════════════════════════════════
            // UPDATE SIGNAL-SPECIFIC CALCULATIONS
            // ═══════════════════════════════════════════════════════════
            {{SIGNAL_UPDATE}}

            // ═══════════════════════════════════════════════════════════
            // GET INDICATOR VALUES
            // ═══════════════════════════════════════════════════════════
            double atr = atrIndicator[0];
            double adx = adxIndicator[0];
            prevADX = adxIndicator[1];

            // Calculate DI components manually (ADX indicator provides ADX value only)
            CalculateDI();

            double vol = Volume[0];
            double volMa = volumeEma[0];

            // ═══════════════════════════════════════════════════════════
            // APPLY FILTERS
            // ═══════════════════════════════════════════════════════════
            bool adxOk = !UseADXFilter || CheckADXCondition(adx, true);
            bool adxOkShort = !UseADXFilter || CheckADXCondition(adx, false);
            bool volumeOk = !UseVolumeFilter || vol > volMa;
            bool hourOk = !UseSessionFilter || IsAllowedHour();

            // ═══════════════════════════════════════════════════════════
            // DETECT ENTRY SIGNALS
            // ═══════════════════════════════════════════════════════════
            {{ENTRY_DETECTION}}

            // ═══════════════════════════════════════════════════════════
            // POSITION MANAGEMENT
            // ═══════════════════════════════════════════════════════════
            if (Position.MarketPosition == MarketPosition.Long)
            {
                ManageLongPosition(atr);
            }
            else if (Position.MarketPosition == MarketPosition.Short)
            {
                ManageShortPosition(atr);
            }
            else // Flat
            {
                // ═══════════════════════════════════════════════════════════
                // ENTRY LOGIC
                // ═══════════════════════════════════════════════════════════
                double slPoints = atr * StopLossATR;
                double tpPoints = atr * TakeProfitATR;

                bool longSignal = longBreakout && adxOk && volumeOk && hourOk && EnableLongTrades;
                bool shortSignal = shortBreakout && adxOkShort && volumeOk && hourOk && EnableShortTrades;

                // ═══════════════════════════════════════════════════════════
                // CHECK FOR RE-ENTRY
                // ═══════════════════════════════════════════════════════════
                bool reentryAllowed = EnableReentry &&
                    lastExitProfitable &&
                    (CurrentBar - lastExitBar) >= ReentryWaitBars &&
                    reentryCount < MaxReentries &&
                    adx > ReentryADXMin;

                if (reentryAllowed)
                {
                    {{REENTRY_CONDITION}}
                }

                // Reset reentry count on fresh breakout
                if ((longBreakout || shortBreakout) && !reentryAllowed)
                    reentryCount = 0;

                // ═══════════════════════════════════════════════════════════
                // EXECUTE ENTRIES
                // ═══════════════════════════════════════════════════════════
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

                    if (reentryAllowed && lastExitDirection == 1)
                        reentryCount++;

                    DrawEntryMarker(true);
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

                    if (reentryAllowed && lastExitDirection == -1)
                        reentryCount++;

                    DrawEntryMarker(false);
                }
            }
        }

        #region Signal Calculation
        {{SIGNAL_CALCULATION_METHODS}}
        #endregion

        #region ADX Filter

        private void CalculateDI()
        {
            if (CurrentBar < ADXPeriod + 1)
            {
                plusDI = minusDI = prevPlusDI = prevMinusDI = 0;
                return;
            }

            // Store previous values
            prevPlusDI = plusDI;
            prevMinusDI = minusDI;

            // Calculate True Range components
            double trueRange = Math.Max(High[0] - Low[0],
                Math.Max(Math.Abs(High[0] - Close[1]),
                         Math.Abs(Low[0] - Close[1])));

            // Calculate +DM and -DM
            double plusDM = High[0] - High[1] > Low[1] - Low[0] ?
                Math.Max(High[0] - High[1], 0) : 0;
            double minusDM = Low[1] - Low[0] > High[0] - High[1] ?
                Math.Max(Low[1] - Low[0], 0) : 0;

            // Smooth using Wilder's method (simplified)
            double smoothedTR = 0, smoothedPlusDM = 0, smoothedMinusDM = 0;
            for (int i = 0; i < ADXPeriod; i++)
            {
                double tr = Math.Max(High[i] - Low[i],
                    Math.Max(Math.Abs(High[i] - (i + 1 < CurrentBar ? Close[i + 1] : Close[i])),
                             Math.Abs(Low[i] - (i + 1 < CurrentBar ? Close[i + 1] : Close[i]))));
                smoothedTR += tr;

                double pDM = High[i] - (i + 1 < CurrentBar ? High[i + 1] : High[i]) >
                             (i + 1 < CurrentBar ? Low[i + 1] : Low[i]) - Low[i] ?
                    Math.Max(High[i] - (i + 1 < CurrentBar ? High[i + 1] : High[i]), 0) : 0;
                double mDM = (i + 1 < CurrentBar ? Low[i + 1] : Low[i]) - Low[i] >
                             High[i] - (i + 1 < CurrentBar ? High[i + 1] : High[i]) ?
                    Math.Max((i + 1 < CurrentBar ? Low[i + 1] : Low[i]) - Low[i], 0) : 0;
                smoothedPlusDM += pDM;
                smoothedMinusDM += mDM;
            }

            plusDI = smoothedTR > 0 ? 100 * smoothedPlusDM / smoothedTR : 0;
            minusDI = smoothedTR > 0 ? 100 * smoothedMinusDM / smoothedTR : 0;
        }

        private bool CheckADXCondition(double adx, bool isLong)
        {
            if (adx <= ADXThreshold)
                return false;

            switch (ADXMode)
            {
                case ADXFilterMode.Traditional:
                    return true;

                case ADXFilterMode.DIAligned:
                    return isLong ? plusDI > minusDI : minusDI > plusDI;

                case ADXFilterMode.DIRising:
                    double dominantDI = isLong ? plusDI : minusDI;
                    double prevDominantDI = isLong ? prevPlusDI : prevMinusDI;
                    return dominantDI > prevDominantDI;

                case ADXFilterMode.ADXRising:
                    return adx > prevADX;

                case ADXFilterMode.Combined:
                    bool aligned = isLong ? plusDI > minusDI : minusDI > plusDI;
                    double domDI = isLong ? plusDI : minusDI;
                    double prevDomDI = isLong ? prevPlusDI : prevMinusDI;
                    return aligned && domDI > prevDomDI && adx > prevADX;

                default:
                    return true;
            }
        }

        #endregion

        #region Position Management

        private void ManageLongPosition(double atr)
        {
            // Update high water mark
            if (High[0] > highWaterMark)
                highWaterMark = High[0];

            // Check trail activation
            if (!trailActive && highWaterMark >= trailTriggerPrice)
                trailActive = true;

            // Update trailing stop
            if (trailActive)
            {
                double newStop = highWaterMark - trailDistancePoints;
                if (newStop > stopLoss)
                    stopLoss = newStop;
            }

            // Check exits (priority: Trail > SL > TP)
            if (trailActive && Low[0] <= stopLoss)
            {
                double exitPnl = stopLoss - entryPrice;
                ExitLong(LONG_SIGNAL, "Trail");
                RecordExit(1, exitPnl > 0);
            }
            else if (Low[0] <= stopLoss)
            {
                ExitLong(LONG_SIGNAL, "SL");
                RecordExit(1, false);
            }
            else if (High[0] >= takeProfit)
            {
                ExitLong(LONG_SIGNAL, "TP");
                RecordExit(1, true);
            }
        }

        private void ManageShortPosition(double atr)
        {
            // Update low water mark
            if (Low[0] < lowWaterMark)
                lowWaterMark = Low[0];

            // Check trail activation
            if (!trailActive && lowWaterMark <= trailTriggerPrice)
                trailActive = true;

            // Update trailing stop
            if (trailActive)
            {
                double newStop = lowWaterMark + trailDistancePoints;
                if (newStop < stopLoss)
                    stopLoss = newStop;
            }

            // Check exits (priority: Trail > SL > TP)
            if (trailActive && High[0] >= stopLoss)
            {
                double exitPnl = entryPrice - stopLoss;
                ExitShort(SHORT_SIGNAL, "Trail");
                RecordExit(-1, exitPnl > 0);
            }
            else if (High[0] >= stopLoss)
            {
                ExitShort(SHORT_SIGNAL, "SL");
                RecordExit(-1, false);
            }
            else if (Low[0] <= takeProfit)
            {
                ExitShort(SHORT_SIGNAL, "TP");
                RecordExit(-1, true);
            }
        }

        private void RecordExit(int direction, bool profitable)
        {
            lastExitBar = CurrentBar;
            lastExitProfitable = profitable;
            lastExitDirection = direction;
        }

        #endregion

        #region Helper Methods

        private bool IsAllowedHour()
        {
            int hour = Time[0].Hour;
            return allowedHours.Contains(hour);
        }

        private void DrawEntryMarker(bool isLong)
        {
            if (State == State.Realtime)
            {
                if (isLong)
                    Draw.ArrowUp(this, "Entry" + CurrentBar, false, 0, Low[0] - 2 * TickSize, Brushes.Green);
                else
                    Draw.ArrowDown(this, "Entry" + CurrentBar, false, 0, High[0] + 2 * TickSize, Brushes.Red);
            }
        }

        #endregion

        #region Properties

        // ═══════════════════════════════════════════════════════════
        // FEATURE TOGGLES
        // ═══════════════════════════════════════════════════════════

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

        // ═══════════════════════════════════════════════════════════
        // SIGNAL SETTINGS
        // ═══════════════════════════════════════════════════════════

        {{SIGNAL_PROPERTIES}}

        // ═══════════════════════════════════════════════════════════
        // ADX FILTER
        // ═══════════════════════════════════════════════════════════

        [NinjaScriptProperty]
        [Display(Name = "Use ADX Filter", Order = 1, GroupName = "ADX Filter")]
        public bool UseADXFilter { get; set; }

        [NinjaScriptProperty]
        [Range(10, 60)]
        [Display(Name = "ADX Threshold", Order = 2, GroupName = "ADX Filter")]
        public int ADXThreshold { get; set; }

        [NinjaScriptProperty]
        [Range(5, 30)]
        [Display(Name = "ADX Period", Order = 3, GroupName = "ADX Filter")]
        public int ADXPeriod { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "ADX Mode", Order = 4, GroupName = "ADX Filter")]
        public ADXFilterMode ADXMode { get; set; }

        // ═══════════════════════════════════════════════════════════
        // EXIT SETTINGS
        // ═══════════════════════════════════════════════════════════

        [NinjaScriptProperty]
        [Range(5, 30)]
        [Display(Name = "ATR Period", Order = 1, GroupName = "Exit Settings")]
        public int ATRPeriod { get; set; }

        [NinjaScriptProperty]
        [Range(0.5, 10.0)]
        [Display(Name = "Stop Loss (ATR×)", Order = 2, GroupName = "Exit Settings")]
        public double StopLossATR { get; set; }

        [NinjaScriptProperty]
        [Range(0.5, 10.0)]
        [Display(Name = "Take Profit (ATR×)", Order = 3, GroupName = "Exit Settings")]
        public double TakeProfitATR { get; set; }

        [NinjaScriptProperty]
        [Range(0.05, 2.0)]
        [Display(Name = "Trail Trigger (ATR×)", Order = 4, GroupName = "Exit Settings")]
        public double TrailTriggerATR { get; set; }

        [NinjaScriptProperty]
        [Range(0.05, 2.0)]
        [Display(Name = "Trail Distance (ATR×)", Order = 5, GroupName = "Exit Settings")]
        public double TrailDistanceATR { get; set; }

        // ═══════════════════════════════════════════════════════════
        // VOLUME FILTER
        // ═══════════════════════════════════════════════════════════

        [NinjaScriptProperty]
        [Range(5, 50)]
        [Display(Name = "Volume MA Period", Order = 1, GroupName = "Volume Filter")]
        public int VolumeMAPeriod { get; set; }

        // ═══════════════════════════════════════════════════════════
        // RE-ENTRY SETTINGS
        // ═══════════════════════════════════════════════════════════

        [NinjaScriptProperty]
        [Range(1, 20)]
        [Display(Name = "Wait Bars", Order = 1, GroupName = "Re-entry Settings")]
        public int ReentryWaitBars { get; set; }

        [NinjaScriptProperty]
        [Range(20, 70)]
        [Display(Name = "Re-entry ADX Min", Order = 2, GroupName = "Re-entry Settings")]
        public int ReentryADXMin { get; set; }

        [NinjaScriptProperty]
        [Range(1, 50)]
        [Display(Name = "Max Re-entries", Order = 3, GroupName = "Re-entry Settings")]
        public int MaxReentries { get; set; }

        // ═══════════════════════════════════════════════════════════
        // SESSION HOURS
        // ═══════════════════════════════════════════════════════════

        [NinjaScriptProperty]
        [Display(Name = "9 AM", Order = 1, GroupName = "Session Hours")]
        public bool Hour9 { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "10 AM", Order = 2, GroupName = "Session Hours")]
        public bool Hour10 { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "11 AM", Order = 3, GroupName = "Session Hours")]
        public bool Hour11 { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "12 PM", Order = 4, GroupName = "Session Hours")]
        public bool Hour12 { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "1 PM", Order = 5, GroupName = "Session Hours")]
        public bool Hour13 { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "2 PM", Order = 6, GroupName = "Session Hours")]
        public bool Hour14 { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "3 PM", Order = 7, GroupName = "Session Hours")]
        public bool Hour15 { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "4 PM", Order = 8, GroupName = "Session Hours")]
        public bool Hour16 { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "6 PM", Order = 9, GroupName = "Session Hours")]
        public bool Hour18 { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "7 PM", Order = 10, GroupName = "Session Hours")]
        public bool Hour19 { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "8 PM", Order = 11, GroupName = "Session Hours")]
        public bool Hour20 { get; set; }

        #endregion
    }

    // ═══════════════════════════════════════════════════════════
    // ENUMERATIONS
    // ═══════════════════════════════════════════════════════════

    public enum ADXFilterMode
    {
        [Display(Name = "Traditional (ADX > threshold)")]
        Traditional,

        [Display(Name = "DI Aligned (DI confirms direction)")]
        DIAligned,

        [Display(Name = "DI Rising (Dominant DI rising)")]
        DIRising,

        [Display(Name = "ADX Rising (ADX itself rising)")]
        ADXRising,

        [Display(Name = "Combined (All conditions)")]
        Combined
    }
}
```

---

## Template Placeholders

Replace these placeholders when generating a strategy:

| Placeholder | Description |
|-------------|-------------|
| `{{STRATEGY_NAME}}` | Strategy name (e.g., "Keltner", "VWAP", "EMACross") |
| `{{STRATEGY_DESCRIPTION}}` | User-facing description |
| `{{WARMUP_BARS}}` | BarsRequiredToTrade value (signal-dependent) |
| `{{SIGNAL_VARIABLES}}` | Signal-specific variable declarations |
| `{{SIGNAL_DEFAULTS}}` | Signal-specific default property values |
| `{{SIGNAL_INIT}}` | Signal-specific indicator initialization |
| `{{SIGNAL_UPDATE}}` | Signal-specific per-bar calculations |
| `{{ENTRY_DETECTION}}` | Entry signal detection logic |
| `{{REENTRY_CONDITION}}` | Re-entry condition check |
| `{{SIGNAL_CALCULATION_METHODS}}` | Helper methods for signal calculation |
| `{{SIGNAL_PROPERTIES}}` | Signal-specific property definitions |

---

## Template Sections

### 1. Using Declarations
Standard NinjaTrader imports for strategies.

### 2. Variables Region
- Core indicators (ATR, ADX, Volume EMA)
- Signal-specific variables
- ADX components for mode checking
- Position management state
- Re-entry tracking
- Session management

### 3. OnStateChange()

**State.SetDefaults:**
- Strategy metadata
- Calculation settings (OnBarClose, entries, slippage, etc.)
- Feature toggles
- Signal-specific defaults
- ADX filter settings
- Exit settings (ATR-based)
- Re-entry settings
- Session hours

**State.Configure:**
- No action (manual exit management)

**State.DataLoaded:**
- Initialize core indicators
- Initialize signal-specific indicators
- Build allowed hours set
- Reset state variables

### 4. OnBarUpdate()
- Primary bars check
- Warmup check
- Signal-specific calculations
- Get indicator values
- Apply filters (ADX, volume, session)
- Detect entry signals
- Position management
- Entry execution

### 5. ADX Filter Region
- `CalculateDI()` - Calculate +DI and -DI values
- `CheckADXCondition()` - Apply filter based on mode

### 6. Position Management Region
- `ManageLongPosition()` - Trail, SL, TP exits
- `ManageShortPosition()` - Trail, SL, TP exits
- `RecordExit()` - Track exit for re-entry logic

### 7. Helper Methods
- `IsAllowedHour()` - Session filter check
- `DrawEntryMarker()` - Visual entry markers

### 8. Properties Region
Organized into groups:
- Feature Toggles
- Signal Settings (signal-specific)
- ADX Filter
- Exit Settings
- Volume Filter
- Re-entry Settings
- Session Hours

### 9. Enumerations
- `ADXFilterMode` - 5 modes for ADX filtering

---

## ADX Filter Modes

| Mode | Description |
|------|-------------|
| **Traditional** | ADX > threshold only |
| **DIAligned** | + ADX > threshold AND DIs aligned with direction |
| **DIRising** | + ADX > threshold AND dominant DI is rising (RECOMMENDED) |
| **ADXRising** | + ADX > threshold AND ADX itself is rising |
| **Combined** | All conditions must be true |

---

## Exit Priority Order

Conservative backtesting standard:
1. **Trailing Stop** (if active AND hit)
2. **Stop Loss** (hard protective stop)
3. **Take Profit** (profit target)

---

## Re-entry Logic Requirements

1. `EnableReentry` must be true
2. Previous exit must be profitable
3. Wait `ReentryWaitBars` bars after exit
4. Current re-entries < `MaxReentries`
5. ADX > `ReentryADXMin` (higher than initial entry)
6. Price still beyond original signal level (signal-specific)

---

## Naming Convention

- File: `{{STRATEGY_NAME}}StrategyLB.cs`
- Class: `{{STRATEGY_NAME}}StrategyLB`
- Signal names: `{{STRATEGY_NAME}}Long`, `{{STRATEGY_NAME}}Short`
