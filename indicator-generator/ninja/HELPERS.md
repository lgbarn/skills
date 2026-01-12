# NinjaScript Helper Classes & TDD

Test-Driven Development patterns and helper class architecture for NinjaTrader 8 indicators.

---

## The Helper Class Pattern

NinjaScript code cannot be directly unit tested because it depends on the NinjaTrader platform. Extract business logic into testable helper classes:

```csharp
namespace NinjaTrader.NinjaScript.Indicators.LB
{
    public class VWAPLB : Indicator
    {
        private VWAPHelper vwapHelper;

        protected override void OnStateChange()
        {
            if (State == State.DataLoaded)
                vwapHelper = new VWAPHelper();
        }

        protected override void OnBarUpdate()
        {
            if (Bars.IsFirstBarOfSession)
                vwapHelper.Reset();

            var (vwap, stdDev) = vwapHelper.Calculate(
                High[0], Low[0], Close[0], Volume[0]);

            Values[0][0] = vwap;
        }
    }

    // ═══════════════════════════════════════════════════════════
    // HELPER CLASSES (Testable)
    // ═══════════════════════════════════════════════════════════

    /// <summary>
    /// Testable VWAP calculation helper.
    /// </summary>
    public class VWAPHelper
    {
        private double sumPriceVolume;
        private double sumVolume;
        private double sumSquaredPV;

        public void Reset()
        {
            sumPriceVolume = 0;
            sumVolume = 0;
            sumSquaredPV = 0;
        }

        public (double vwap, double stdDev) Calculate(
            double high, double low, double close, double volume)
        {
            double typicalPrice = (high + low + close) / 3.0;
            double safeVolume = volume > 0 ? volume : 1;

            sumPriceVolume += typicalPrice * safeVolume;
            sumVolume += safeVolume;
            sumSquaredPV += (typicalPrice * typicalPrice) * safeVolume;

            double vwap = sumVolume > 0 ? sumPriceVolume / sumVolume : typicalPrice;
            double variance = sumVolume > 0 ? (sumSquaredPV / sumVolume) - (vwap * vwap) : 0;
            double stdDev = Math.Sqrt(Math.Max(0, variance));

            return (vwap, stdDev);
        }
    }
}
```

---

## Helper Class Naming Conventions

| Type | Pattern | Example | Use Case |
|------|---------|---------|----------|
| Stateless calculations | `*Calculator` | `VWAPCalculator`, `ATRCalculator` | Pure functions, no state |
| Stateful accumulators | `*Helper` | `VWAPHelper`, `SessionHelper` | Tracks running totals |
| Session logic | `*SessionCalculator` | `IBSessionCalculator` | Session-specific state |

---

## Dependency Injection Pattern

Pass bar data as parameters instead of accessing NinjaScript properties directly:

```csharp
// Bad - cannot test
public double CalculateVWAP()
{
    return (High[0] + Low[0] + Close[0]) / 3.0 * Volume[0];
}

// Good - testable
public double CalculateVWAP(double high, double low, double close, double volume)
{
    return (high + low + close) / 3.0 * volume;
}
```

---

## TDD Workflow

```
1. RED    - Write failing test for calculation
2. GREEN  - Implement helper class method
3. REFACTOR - Clean up while tests pass
4. INTEGRATE - Use helper in indicator
5. VERIFY - Run dotnet test
```

---

## Example Test Class

```csharp
using NUnit.Framework;
using NinjaTrader.NinjaScript.Indicators.LB;

namespace LB.Indicators.Tests
{
    [TestFixture]
    public class VWAPHelperTests
    {
        private VWAPHelper _helper;

        [SetUp]
        public void SetUp()
        {
            _helper = new VWAPHelper();
        }

        [Test]
        public void Calculate_SingleBar_ReturnsTypicalPrice()
        {
            // Arrange
            double high = 100.0;
            double low = 98.0;
            double close = 99.0;
            double volume = 1000;
            double expectedVWAP = (100.0 + 98.0 + 99.0) / 3.0;

            // Act
            var (vwap, stdDev) = _helper.Calculate(high, low, close, volume);

            // Assert
            Assert.That(vwap, Is.EqualTo(expectedVWAP).Within(0.0001));
            Assert.That(stdDev, Is.EqualTo(0).Within(0.0001));
        }

        [Test]
        public void Calculate_MultipleBars_WeightsByVolume()
        {
            // Arrange & Act
            _helper.Calculate(100, 100, 100, 1000);  // TP = 100
            var (vwap, _) = _helper.Calculate(110, 110, 110, 2000);  // TP = 110

            // Assert - weighted average: (100*1000 + 110*2000) / 3000 = 106.67
            Assert.That(vwap, Is.EqualTo(106.6667).Within(0.01));
        }

        [Test]
        public void Reset_ClearsAccumulators()
        {
            // Arrange
            _helper.Calculate(100, 100, 100, 1000);

            // Act
            _helper.Reset();
            var (vwap, _) = _helper.Calculate(50, 50, 50, 1000);

            // Assert - after reset, should be just the new bar's TP
            Assert.That(vwap, Is.EqualTo(50).Within(0.0001));
        }

        [Test]
        public void Calculate_ZeroVolume_UsesDefaultVolume()
        {
            // Act
            var (vwap, _) = _helper.Calculate(100, 98, 99, 0);

            // Assert - should still calculate (uses volume = 1)
            Assert.That(vwap, Is.EqualTo(99).Within(0.01));
        }
    }
}
```

---

## Running Tests

```bash
# Navigate to test project
cd Ninjatrader/Tests

# Run all tests
dotnet test LB.Indicators.Tests.csproj --verbosity normal

# Run specific test class
dotnet test --filter "FullyQualifiedName~VWAPHelperTests"

# Run specific test
dotnet test --filter "VWAPHelperTests.Calculate_SingleBar_ReturnsTypicalPrice"
```

---

## Test Project Setup

```xml
<!-- LB.Indicators.Tests.csproj -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net48</TargetFramework>
    <IsPackable>false</IsPackable>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="NUnit" Version="3.13.3" />
    <PackageReference Include="NUnit3TestAdapter" Version="4.4.2" />
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.5.0" />
  </ItemGroup>

  <ItemGroup>
    <!-- Reference helper classes from indicator files -->
    <Compile Include="..\Indicators\*LB.cs" LinkBase="Indicators" />
  </ItemGroup>
</Project>
```

---

## Complete Indicator with Helper Pattern

```csharp
using System;
using NinjaTrader.Cbi;
using NinjaTrader.NinjaScript;
using NinjaTrader.NinjaScript.Indicators;

namespace NinjaTrader.NinjaScript.Indicators.LB
{
    public class InitialBalanceLB : Indicator
    {
        private IBHelper ibHelper;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Name = "Initial Balance LB";
                IsOverlay = true;
                AddPlot(Brushes.Gold, "IB High");
                AddPlot(Brushes.Gold, "IB Low");
                AddPlot(Brushes.Gold, "IB Mid");
                Duration = 60;
            }
            else if (State == State.DataLoaded)
            {
                ibHelper = new IBHelper(Duration);
            }
        }

        protected override void OnBarUpdate()
        {
            if (CurrentBar < 1) return;

            DateTime barTime = Times[0][0];
            bool isNewSession = Bars.IsFirstBarOfSession;

            var result = ibHelper.ProcessBar(
                barTime, High[0], Low[0], isNewSession);

            if (result.IsComplete)
            {
                Values[0][0] = result.High;
                Values[1][0] = result.Low;
                Values[2][0] = result.Mid;
            }
        }

        [NinjaScriptProperty]
        [Range(5, 240)]
        [Display(Name = "Duration (min)", GroupName = "IB Settings")]
        public int Duration { get; set; }
    }

    // ═══════════════════════════════════════════════════════════
    // HELPER CLASS (Testable)
    // ═══════════════════════════════════════════════════════════

    public class IBHelper
    {
        private readonly int durationMinutes;
        private DateTime ibStartTime;
        private double ibHigh;
        private double ibLow;
        private bool ibComplete;

        public IBHelper(int durationMinutes)
        {
            this.durationMinutes = durationMinutes;
            Reset();
        }

        public void Reset()
        {
            ibHigh = double.MinValue;
            ibLow = double.MaxValue;
            ibComplete = false;
            ibStartTime = DateTime.MinValue;
        }

        public IBResult ProcessBar(DateTime barTime, double high, double low, bool isNewSession)
        {
            if (isNewSession)
            {
                Reset();
                ibStartTime = barTime;
                ibHigh = high;
                ibLow = low;
            }

            if (!ibComplete && ibStartTime != DateTime.MinValue)
            {
                var elapsed = (barTime - ibStartTime).TotalMinutes;

                if (elapsed < durationMinutes)
                {
                    ibHigh = Math.Max(ibHigh, high);
                    ibLow = Math.Min(ibLow, low);
                }
                else
                {
                    ibComplete = true;
                }
            }

            return new IBResult
            {
                IsComplete = ibComplete,
                High = ibComplete ? ibHigh : double.NaN,
                Low = ibComplete ? ibLow : double.NaN,
                Mid = ibComplete ? (ibHigh + ibLow) / 2 : double.NaN
            };
        }
    }

    public struct IBResult
    {
        public bool IsComplete;
        public double High;
        public double Low;
        public double Mid;
    }
}
```
