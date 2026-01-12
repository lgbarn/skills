# NinjaScript C# Indicator Template

Use this template as the starting point for new NinjaTrader 8 indicators.

## Complete Template

```csharp
#region Using declarations
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;
using System.Windows.Media;
using System.Xml.Serialization;
using NinjaTrader.Cbi;
using NinjaTrader.Gui;
using NinjaTrader.Gui.Chart;
using NinjaTrader.Gui.SuperDom;
using NinjaTrader.Gui.Tools;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
using NinjaTrader.Core.FloatingPoint;
using NinjaTrader.NinjaScript.DrawingTools;
#endregion

// Author: Luther Barnum

namespace NinjaTrader.NinjaScript.Indicators.LB
{
    public class [INDICATOR_NAME]LB : Indicator
    {
        #region Variables
        // ═══════════════════════════════════════════════════════════
        // TRACKING VARIABLES
        // ═══════════════════════════════════════════════════════════
        private double sumPriceVolume;
        private double sumVolume;
        private double currentValue;

        // ═══════════════════════════════════════════════════════════
        // SESSION STATE
        // ═══════════════════════════════════════════════════════════
        private DateTime currentSessionDate;
        private DateTime sessionStartTime;
        private DateTime sessionEndTime;
        private bool sessionActive;

        // ═══════════════════════════════════════════════════════════
        // SERIES
        // ═══════════════════════════════════════════════════════════
        private Series<double> valueSeries;

        // ═══════════════════════════════════════════════════════════
        // SECONDARY INDICATORS
        // ═══════════════════════════════════════════════════════════
        private EMA emaIndicator;
        private ATR atrIndicator;

        // ═══════════════════════════════════════════════════════════
        // TIMEZONE
        // ═══════════════════════════════════════════════════════════
        private TimeZoneInfo selectedTimeZone;
        #endregion

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                // ═══════════════════════════════════════════════════════════
                // METADATA
                // ═══════════════════════════════════════════════════════════
                Description = @"[DESCRIPTION]";
                Name = "[INDICATOR_NAME] LB";
                Calculate = Calculate.OnBarClose;
                IsOverlay = true;
                DisplayInDataBox = true;
                DrawOnPricePanel = true;
                DrawHorizontalGridLines = true;
                DrawVerticalGridLines = true;
                PaintPriceMarkers = true;
                ScaleJustification = NinjaTrader.Gui.Chart.ScaleJustification.Right;
                IsSuspendedWhileInactive = true;
                MaximumBarsLookBack = MaximumBarsLookBack.Infinite;

                // ═══════════════════════════════════════════════════════════
                // PLOTS
                // ═══════════════════════════════════════════════════════════
                AddPlot(new Stroke(Brushes.MediumOrchid, 2), PlotStyle.Line, "MainValue");
                AddPlot(new Stroke(Brushes.Lime, 1), PlotStyle.Line, "UpperBand");
                AddPlot(new Stroke(Brushes.Red, 1), PlotStyle.Line, "LowerBand");

                // ═══════════════════════════════════════════════════════════
                // DEFAULT PROPERTY VALUES
                // ═══════════════════════════════════════════════════════════
                EnableFeature1 = true;
                EnableFeature2 = false;
                Period = 14;
                Multiplier = 1.0;
                StartHour = 9;
                StartMinute = 30;
                EndHour = 16;
                EndMinute = 0;
                SessionTimeZone = TimeZoneOption.America_NewYork;
                MainColor = Brushes.MediumOrchid;
                UpperColor = Brushes.Lime;
                LowerColor = Brushes.Red;
            }
            else if (State == State.Configure)
            {
                // ═══════════════════════════════════════════════════════════
                // SECONDARY DATA SERIES (for multi-timeframe)
                // ═══════════════════════════════════════════════════════════
                // AddDataSeries(BarsPeriodType.Week, 1);   // BarsInProgress = 1
                // AddDataSeries(BarsPeriodType.Month, 1);  // BarsInProgress = 2
            }
            else if (State == State.DataLoaded)
            {
                // ═══════════════════════════════════════════════════════════
                // INITIALIZE SERIES
                // ═══════════════════════════════════════════════════════════
                valueSeries = new Series<double>(this, MaximumBarsLookBack.Infinite);

                // ═══════════════════════════════════════════════════════════
                // INITIALIZE SECONDARY INDICATORS
                // ═══════════════════════════════════════════════════════════
                emaIndicator = EMA(Close, Period);
                atrIndicator = ATR(14);

                // ═══════════════════════════════════════════════════════════
                // INITIALIZE TIMEZONE
                // ═══════════════════════════════════════════════════════════
                selectedTimeZone = TimeZoneInfo.FindSystemTimeZoneById(GetWindowsTimeZoneId(SessionTimeZone));
            }
        }

        protected override void OnBarUpdate()
        {
            // ═══════════════════════════════════════════════════════════
            // SECONDARY DATA SERIES HANDLING
            // ═══════════════════════════════════════════════════════════
            // if (BarsInProgress == 1) // Weekly
            // {
            //     // Process weekly data
            //     return;
            // }

            if (BarsInProgress != 0)
                return;

            // ═══════════════════════════════════════════════════════════
            // EARLY RETURN FOR INSUFFICIENT DATA
            // ═══════════════════════════════════════════════════════════
            if (CurrentBar < Period)
                return;

            // ═══════════════════════════════════════════════════════════
            // SESSION DETECTION
            // ═══════════════════════════════════════════════════════════
            DateTime currentBarTime = Times[0][0];
            DateTime currentDate = currentBarTime.Date;

            if (Bars.IsFirstBarOfSession)
            {
                ResetSession();
            }

            if (currentSessionDate != currentDate)
            {
                currentSessionDate = currentDate;
                sessionStartTime = currentDate.AddHours(StartHour).AddMinutes(StartMinute);
                sessionEndTime = currentDate.AddHours(EndHour).AddMinutes(EndMinute);
            }

            // ═══════════════════════════════════════════════════════════
            // SESSION WINDOW CHECK
            // ═══════════════════════════════════════════════════════════
            bool inSessionWindow = currentBarTime >= sessionStartTime && currentBarTime < sessionEndTime;

            if (inSessionWindow && !sessionActive)
            {
                // Session started
                sessionActive = true;
                sumPriceVolume = 0;
                sumVolume = 0;
            }

            // ═══════════════════════════════════════════════════════════
            // MAIN CALCULATION
            // ═══════════════════════════════════════════════════════════
            if (EnableFeature1 && sessionActive)
            {
                double sourcePrice = (High[0] + Low[0] + Close[0]) / 3.0;
                double volume = Volume[0] > 0 ? Volume[0] : 1;

                sumPriceVolume += sourcePrice * volume;
                sumVolume += volume;

                currentValue = sumVolume > 0 ? sumPriceVolume / sumVolume : sourcePrice;

                // Store in series
                valueSeries[0] = currentValue;
            }

            // ═══════════════════════════════════════════════════════════
            // OUTPUT VALUES
            // ═══════════════════════════════════════════════════════════
            if (EnableFeature1)
            {
                Values[0][0] = currentValue;

                if (EnableFeature2)
                {
                    double band = atrIndicator[0] * Multiplier;
                    Values[1][0] = currentValue + band;
                    Values[2][0] = currentValue - band;
                }
                else
                {
                    Values[1][0] = double.NaN;
                    Values[2][0] = double.NaN;
                }
            }
            else
            {
                Values[0][0] = double.NaN;
                Values[1][0] = double.NaN;
                Values[2][0] = double.NaN;
            }
        }

        #region Helper Methods
        private void ResetSession()
        {
            sumPriceVolume = 0;
            sumVolume = 0;
            currentValue = 0;
            sessionActive = false;
        }

        private string GetWindowsTimeZoneId(TimeZoneOption option)
        {
            switch (option)
            {
                case TimeZoneOption.America_NewYork:
                    return "Eastern Standard Time";
                case TimeZoneOption.America_Chicago:
                    return "Central Standard Time";
                case TimeZoneOption.America_LosAngeles:
                    return "Pacific Standard Time";
                case TimeZoneOption.Europe_London:
                    return "GMT Standard Time";
                case TimeZoneOption.Asia_Tokyo:
                    return "Tokyo Standard Time";
                default:
                    return "Eastern Standard Time";
            }
        }
        #endregion

        #region Properties

        // ═══════════════════════════════════════════════════════════
        // FEATURE TOGGLES
        // ═══════════════════════════════════════════════════════════
        [NinjaScriptProperty]
        [Display(Name = "Enable Feature 1", Description = "Enable the main feature",
                 Order = 1, GroupName = "Feature Toggles")]
        public bool EnableFeature1 { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Enable Feature 2", Description = "Enable secondary feature (bands)",
                 Order = 2, GroupName = "Feature Toggles")]
        public bool EnableFeature2 { get; set; }

        // ═══════════════════════════════════════════════════════════
        // PARAMETERS
        // ═══════════════════════════════════════════════════════════
        [NinjaScriptProperty]
        [Range(1, int.MaxValue)]
        [Display(Name = "Period", Description = "Lookback period",
                 Order = 1, GroupName = "Parameters")]
        public int Period { get; set; }

        [NinjaScriptProperty]
        [Range(0.1, 10.0)]
        [Display(Name = "Multiplier", Description = "Band multiplier",
                 Order = 2, GroupName = "Parameters")]
        public double Multiplier { get; set; }

        // ═══════════════════════════════════════════════════════════
        // SESSION SETTINGS
        // ═══════════════════════════════════════════════════════════
        [NinjaScriptProperty]
        [Range(0, 23)]
        [Display(Name = "Start Hour", Order = 1, GroupName = "Session Settings")]
        public int StartHour { get; set; }

        [NinjaScriptProperty]
        [Range(0, 59)]
        [Display(Name = "Start Minute", Order = 2, GroupName = "Session Settings")]
        public int StartMinute { get; set; }

        [NinjaScriptProperty]
        [Range(0, 23)]
        [Display(Name = "End Hour", Order = 3, GroupName = "Session Settings")]
        public int EndHour { get; set; }

        [NinjaScriptProperty]
        [Range(0, 59)]
        [Display(Name = "End Minute", Order = 4, GroupName = "Session Settings")]
        public int EndMinute { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Time Zone", Order = 5, GroupName = "Session Settings")]
        public TimeZoneOption SessionTimeZone { get; set; }

        // ═══════════════════════════════════════════════════════════
        // COLORS
        // ═══════════════════════════════════════════════════════════
        [NinjaScriptProperty]
        [XmlIgnore]
        [Display(Name = "Main Color", Order = 1, GroupName = "Colors")]
        public Brush MainColor { get; set; }

        [Browsable(false)]
        public string MainColorSerializable
        {
            get { return Serialize.BrushToString(MainColor); }
            set { MainColor = Serialize.StringToBrush(value); }
        }

        [NinjaScriptProperty]
        [XmlIgnore]
        [Display(Name = "Upper Band Color", Order = 2, GroupName = "Colors")]
        public Brush UpperColor { get; set; }

        [Browsable(false)]
        public string UpperColorSerializable
        {
            get { return Serialize.BrushToString(UpperColor); }
            set { UpperColor = Serialize.StringToBrush(value); }
        }

        [NinjaScriptProperty]
        [XmlIgnore]
        [Display(Name = "Lower Band Color", Order = 3, GroupName = "Colors")]
        public Brush LowerColor { get; set; }

        [Browsable(false)]
        public string LowerColorSerializable
        {
            get { return Serialize.BrushToString(LowerColor); }
            set { LowerColor = Serialize.StringToBrush(value); }
        }

        // ═══════════════════════════════════════════════════════════
        // OUTPUT SERIES (for other scripts to access)
        // ═══════════════════════════════════════════════════════════
        [Browsable(false)]
        [XmlIgnore]
        public Series<double> MainValue
        {
            get { return Values[0]; }
        }

        [Browsable(false)]
        [XmlIgnore]
        public Series<double> Upper
        {
            get { return Values[1]; }
        }

        [Browsable(false)]
        [XmlIgnore]
        public Series<double> Lower
        {
            get { return Values[2]; }
        }
        #endregion
    }

    // ═══════════════════════════════════════════════════════════
    // ENUMERATIONS
    // ═══════════════════════════════════════════════════════════
    public enum TimeZoneOption
    {
        America_NewYork,
        America_Chicago,
        America_LosAngeles,
        Europe_London,
        Asia_Tokyo
    }
}

#region NinjaScript generated code. Neither change nor remove.
// This section is auto-generated by NinjaTrader
#endregion
```

## Template Sections

### 1. Using Declarations
- Standard NinjaTrader imports
- Add SharpDX for custom rendering if needed

### 2. Namespace
- Use `NinjaTrader.NinjaScript.Indicators.LB`
- Class name: `[Name]LB : Indicator`

### 3. Variables Region
- Tracking variables (sums, counts)
- Session state
- Series declarations
- Secondary indicator references
- Timezone info

### 4. OnStateChange()

**State.SetDefaults:**
- Metadata (Description, Name)
- Calculate mode
- Visual settings
- Plot definitions
- Default property values

**State.Configure:**
- Add secondary data series

**State.DataLoaded:**
- Initialize Series objects
- Create secondary indicators
- Set up timezone

### 5. OnBarUpdate()
- Secondary series handling (early returns)
- Insufficient data check
- Session detection
- Main calculations
- Output assignment

### 6. Helper Methods
- Reset functions
- Conversion utilities
- Timezone mapping

### 7. Properties Region
- Feature toggles (GroupName = "Feature Toggles")
- Parameters (GroupName = "Parameters")
- Session settings (GroupName = "Session Settings")
- Colors with serialization
- Output series (Browsable(false))

### 8. Enumerations
- Custom enum types for dropdowns

### 9. Generated Code Region
- Auto-generated caching code (DO NOT MODIFY)

---

## Helper Class Template (TDD)

Add testable helper classes after the indicator class but within the namespace. See [TESTING.md](TESTING.md) for complete TDD guide.

```csharp
    // ═══════════════════════════════════════════════════════════
    // HELPER CLASSES (Testable)
    // ═══════════════════════════════════════════════════════════

    /// <summary>
    /// Testable calculation helper for [INDICATOR_NAME].
    /// All business logic should be implemented here for unit testing.
    /// </summary>
    public class [INDICATOR_NAME]Helper
    {
        #region Private Fields
        private double sumPriceVolume;
        private double sumVolume;
        private double sumSquaredPV;
        #endregion

        #region Public Methods
        /// <summary>
        /// Resets all accumulators for new session.
        /// </summary>
        public void Reset()
        {
            sumPriceVolume = 0;
            sumVolume = 0;
            sumSquaredPV = 0;
        }

        /// <summary>
        /// Calculates the indicator value for current bar.
        /// </summary>
        /// <param name="high">Bar high price</param>
        /// <param name="low">Bar low price</param>
        /// <param name="close">Bar close price</param>
        /// <param name="volume">Bar volume (defaults to 1 if zero)</param>
        /// <returns>Calculated value</returns>
        public double Calculate(double high, double low, double close, double volume)
        {
            double typicalPrice = (high + low + close) / 3.0;
            double safeVolume = volume > 0 ? volume : 1;

            sumPriceVolume += typicalPrice * safeVolume;
            sumVolume += safeVolume;

            return sumVolume > 0 ? sumPriceVolume / sumVolume : typicalPrice;
        }

        /// <summary>
        /// Calculates value with standard deviation.
        /// </summary>
        /// <returns>Tuple of (value, standardDeviation)</returns>
        public (double value, double stdDev) CalculateWithStdDev(
            double high, double low, double close, double volume)
        {
            double typicalPrice = (high + low + close) / 3.0;
            double safeVolume = volume > 0 ? volume : 1;

            sumPriceVolume += typicalPrice * safeVolume;
            sumVolume += safeVolume;
            sumSquaredPV += (typicalPrice * typicalPrice) * safeVolume;

            double value = sumVolume > 0 ? sumPriceVolume / sumVolume : typicalPrice;
            double variance = sumVolume > 0 ? (sumSquaredPV / sumVolume) - (value * value) : 0;
            double stdDev = Math.Sqrt(Math.Max(0, variance));

            return (value, stdDev);
        }
        #endregion

        #region Properties
        /// <summary>
        /// Gets current accumulated value without adding new data.
        /// </summary>
        public double CurrentValue => sumVolume > 0 ? sumPriceVolume / sumVolume : 0;

        /// <summary>
        /// Gets total volume accumulated.
        /// </summary>
        public double TotalVolume => sumVolume;
        #endregion
    }

    /// <summary>
    /// Session boundary detection calculator.
    /// </summary>
    public class SessionCalculator
    {
        private readonly TimeSpan sessionStart;
        private readonly TimeSpan sessionEnd;

        public SessionCalculator(int startHour, int startMinute, int endHour, int endMinute)
        {
            sessionStart = new TimeSpan(startHour, startMinute, 0);
            sessionEnd = new TimeSpan(endHour, endMinute, 0);
        }

        /// <summary>
        /// Determines if given time is within session window.
        /// Handles overnight sessions correctly.
        /// </summary>
        public bool IsInSession(DateTime time)
        {
            TimeSpan currentTime = time.TimeOfDay;

            // Handle overnight sessions (end < start)
            if (sessionEnd < sessionStart)
            {
                return currentTime >= sessionStart || currentTime < sessionEnd;
            }

            return currentTime >= sessionStart && currentTime < sessionEnd;
        }

        /// <summary>
        /// Determines if this is the first bar of a new session.
        /// </summary>
        public bool IsSessionStart(DateTime currentTime, DateTime previousTime)
        {
            return IsInSession(currentTime) && !IsInSession(previousTime);
        }
    }
```

### Integrating Helper in Indicator

Update the indicator to use the helper class:

```csharp
#region Variables
private [INDICATOR_NAME]Helper helper;
private SessionCalculator sessionCalc;
#endregion

// In State.DataLoaded:
helper = new [INDICATOR_NAME]Helper();
sessionCalc = new SessionCalculator(StartHour, StartMinute, EndHour, EndMinute);

// In OnBarUpdate:
if (Bars.IsFirstBarOfSession)
{
    helper.Reset();
}

var (value, stdDev) = helper.CalculateWithStdDev(
    High[0], Low[0], Close[0], Volume[0]);

Values[0][0] = value;
Values[1][0] = value + stdDev * Multiplier;
Values[2][0] = value - stdDev * Multiplier;
```

---

## Test Class Template

Create corresponding test file in test project:

```csharp
using NUnit.Framework;
using NinjaTrader.NinjaScript.Indicators.LB;

namespace LB.Indicators.Tests
{
    [TestFixture]
    public class [INDICATOR_NAME]HelperTests
    {
        private [INDICATOR_NAME]Helper helper;

        [SetUp]
        public void Setup()
        {
            helper = new [INDICATOR_NAME]Helper();
        }

        [TearDown]
        public void TearDown()
        {
            helper = null;
        }

        [Test]
        public void Calculate_SingleBar_ReturnsTypicalPrice()
        {
            // Arrange
            double high = 100, low = 90, close = 95, volume = 1000;

            // Act
            double result = helper.Calculate(high, low, close, volume);

            // Assert
            Assert.AreEqual(95.0, result, 0.001);
        }

        [Test]
        public void Calculate_ZeroVolume_UsesDefaultVolume()
        {
            double result = helper.Calculate(100, 90, 95, 0);
            Assert.AreEqual(95.0, result, 0.001);
        }

        [Test]
        public void Reset_ClearsAccumulators()
        {
            helper.Calculate(100, 90, 95, 1000);
            helper.Reset();
            Assert.AreEqual(0, helper.TotalVolume);
        }

        [Test]
        public void CalculateWithStdDev_SingleBar_ReturnsZeroStdDev()
        {
            var (value, stdDev) = helper.CalculateWithStdDev(100, 90, 95, 1000);
            Assert.AreEqual(95.0, value, 0.001);
            Assert.AreEqual(0, stdDev, 0.001);
        }
    }

    [TestFixture]
    public class SessionCalculatorTests
    {
        [Test]
        public void IsInSession_WithinWindow_ReturnsTrue()
        {
            var calc = new SessionCalculator(9, 30, 16, 0);
            var time = new DateTime(2024, 1, 15, 10, 30, 0);
            Assert.IsTrue(calc.IsInSession(time));
        }

        [Test]
        public void IsInSession_OutsideWindow_ReturnsFalse()
        {
            var calc = new SessionCalculator(9, 30, 16, 0);
            var time = new DateTime(2024, 1, 15, 8, 0, 0);
            Assert.IsFalse(calc.IsInSession(time));
        }

        [Test]
        public void IsInSession_OvernightSession_HandlesCorrectly()
        {
            var calc = new SessionCalculator(18, 0, 5, 0);  // 6 PM to 5 AM

            // 8 PM should be in session
            Assert.IsTrue(calc.IsInSession(new DateTime(2024, 1, 15, 20, 0, 0)));

            // 2 AM should be in session
            Assert.IsTrue(calc.IsInSession(new DateTime(2024, 1, 16, 2, 0, 0)));

            // 10 AM should be out of session
            Assert.IsFalse(calc.IsInSession(new DateTime(2024, 1, 16, 10, 0, 0)));
        }
    }
}
```
