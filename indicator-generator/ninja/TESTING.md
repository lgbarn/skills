# NinjaScript TDD Guide

Test-Driven Development (TDD) guide for NinjaTrader 8 indicators using NUnit and dotnet test.

---

## Why TDD for NinjaScript?

NinjaScript code cannot be directly unit tested because:
- NinjaTrader's internal instantiation is proprietary
- MSTest/NUnit cannot directly test indicators or strategies
- Objects require the NT harness to be running

**Solution:** Extract business logic into testable helper classes and use dependency injection.

---

## The Helper Class Pattern

### Principle
Keep NinjaScript indicators minimal - only lifecycle methods (`OnStateChange`, `OnBarUpdate`). Extract all calculation logic into separate helper classes that can be tested independently.

### Benefits
- Testable code without running NinjaTrader
- Clear separation of concerns
- Easier refactoring with test protection
- Improved code organization

---

## TDD Workflow

### Red-Green-Refactor Cycle

```
1. RED    - Write a failing test for the desired behavior
2. GREEN  - Write minimal code to make the test pass
3. REFACTOR - Improve code while keeping tests green
```

### When to Write Tests

| Scenario | Action |
|----------|--------|
| New indicator | Write tests for calculations before implementing |
| New feature | Write tests first, then implement |
| Bug fix | Write test that reproduces bug, then fix |
| Refactoring | Ensure tests exist first, then refactor |

---

## Test Project Setup

### 1. Create Test Project

```bash
# Navigate to NinjaTrader bin directory
cd "C:\Users\[username]\Documents\NinjaTrader 8\bin"

# Create NUnit test project
dotnet new nunit -n LB.Indicators.Tests -f net48

# Navigate to project
cd LB.Indicators.Tests
```

### 2. Project Structure

```
NinjaTrader 8/
├── bin/
│   ├── Custom/
│   │   └── Indicators/
│   │       └── LB/
│   │           └── VWAPLB.cs          # Indicator + Helper class
│   └── LB.Indicators.Tests/
│       ├── LB.Indicators.Tests.csproj
│       ├── Helpers/
│       │   └── VWAPHelperTests.cs
│       └── Calculators/
│           └── SessionCalculatorTests.cs
```

### 3. Project File (.csproj)

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net48</TargetFramework>
    <IsPackable>false</IsPackable>
    <LangVersion>latest</LangVersion>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="NUnit" Version="3.14.0" />
    <PackageReference Include="NUnit3TestAdapter" Version="4.5.0" />
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.8.0" />
    <PackageReference Include="Moq" Version="4.20.70" />
  </ItemGroup>

  <ItemGroup>
    <!-- Reference NinjaTrader DLLs if needed for types -->
    <Reference Include="NinjaTrader.Core">
      <HintPath>C:\Program Files (x86)\NinjaTrader 8\bin\NinjaTrader.Core.dll</HintPath>
      <Private>false</Private>
    </Reference>
  </ItemGroup>

  <ItemGroup>
    <!-- Reference your indicator helper classes -->
    <Compile Include="..\Custom\Indicators\LB\**\*Helper.cs" Link="Helpers\%(RecursiveDir)%(Filename)%(Extension)" />
    <Compile Include="..\Custom\Indicators\LB\**\*Calculator.cs" Link="Calculators\%(RecursiveDir)%(Filename)%(Extension)" />
  </ItemGroup>
</Project>
```

---

## Writing Helper Classes

### Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Stateless calculations | `*Calculator` | `VWAPCalculator`, `ATRCalculator` |
| Stateful accumulators | `*Helper` | `VWAPHelper`, `SessionHelper` |
| Session logic | `*SessionCalculator` | `IBSessionCalculator` |

### Placement

Place helper classes in the same file as the indicator, after the indicator class:

```csharp
namespace NinjaTrader.NinjaScript.Indicators.LB
{
    public class VWAPLB : Indicator
    {
        // Indicator code...
    }

    // ═══════════════════════════════════════════════════════════
    // HELPER CLASSES (Testable)
    // ═══════════════════════════════════════════════════════════

    public class VWAPHelper
    {
        // Testable calculation logic...
    }
}
```

### Example: VWAP Helper

```csharp
/// <summary>
/// Testable VWAP calculation helper with standard deviation bands.
/// </summary>
public class VWAPHelper
{
    private double sumPriceVolume;
    private double sumVolume;
    private double sumSquaredPV;

    /// <summary>
    /// Resets accumulators for new session.
    /// </summary>
    public void Reset()
    {
        sumPriceVolume = 0;
        sumVolume = 0;
        sumSquaredPV = 0;
    }

    /// <summary>
    /// Calculates VWAP and standard deviation for current bar.
    /// </summary>
    /// <param name="high">Bar high price</param>
    /// <param name="low">Bar low price</param>
    /// <param name="close">Bar close price</param>
    /// <param name="volume">Bar volume (uses 1 if zero)</param>
    /// <returns>Tuple of (vwap, standardDeviation)</returns>
    public (double vwap, double stdDev) Calculate(double high, double low, double close, double volume)
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

    /// <summary>
    /// Gets current VWAP value without adding new data.
    /// </summary>
    public double CurrentVWAP => sumVolume > 0 ? sumPriceVolume / sumVolume : 0;
}
```

### Example: Session Calculator

```csharp
/// <summary>
/// Testable session boundary detection.
/// </summary>
public class SessionCalculator
{
    private readonly TimeSpan sessionStart;
    private readonly TimeSpan sessionEnd;

    public SessionCalculator(TimeSpan start, TimeSpan end)
    {
        sessionStart = start;
        sessionEnd = end;
    }

    /// <summary>
    /// Determines if given time is within session window.
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

---

## Writing Tests

### Test Class Structure

```csharp
using NUnit.Framework;
using NinjaTrader.NinjaScript.Indicators.LB;

namespace LB.Indicators.Tests
{
    [TestFixture]
    public class VWAPHelperTests
    {
        private VWAPHelper helper;

        [SetUp]
        public void Setup()
        {
            helper = new VWAPHelper();
        }

        [TearDown]
        public void TearDown()
        {
            helper = null;
        }

        // Tests go here...
    }
}
```

### Test Naming Convention

Use the pattern: `MethodName_Scenario_ExpectedResult`

```csharp
[Test]
public void Calculate_SingleBar_ReturnsTypicalPrice()
{
    // Arrange
    // Act
    var result = helper.Calculate(100, 90, 95, 1000);
    // Assert
    Assert.AreEqual(95, result.vwap, 0.001);
}

[Test]
public void Calculate_ZeroVolume_UsesDefaultVolume()
{
    var result = helper.Calculate(100, 90, 95, 0);
    Assert.AreEqual(95, result.vwap, 0.001);
}

[Test]
public void Reset_AfterCalculations_ClearsAccumulators()
{
    helper.Calculate(100, 90, 95, 1000);
    helper.Reset();
    var result = helper.Calculate(110, 100, 105, 1000);
    Assert.AreEqual(105, result.vwap, 0.001);
}
```

### Testing Edge Cases

Always test these scenarios:

```csharp
// Zero/Null inputs
[Test]
public void Calculate_ZeroVolume_HandlesGracefully()

// Negative values
[Test]
public void Calculate_NegativeVariance_ReturnsZeroStdDev()

// Boundary conditions
[Test]
public void IsInSession_ExactlyAtStart_ReturnsTrue()

[Test]
public void IsInSession_ExactlyAtEnd_ReturnsFalse()

// Overnight sessions
[Test]
public void IsInSession_OvernightSession_HandlesCorrectly()

// Sequence of operations
[Test]
public void Calculate_MultipleBarSequence_AccumulatesCorrectly()
```

### Session Calculator Tests

```csharp
[TestFixture]
public class SessionCalculatorTests
{
    [Test]
    public void IsInSession_WithinWindow_ReturnsTrue()
    {
        var calc = new SessionCalculator(
            new TimeSpan(9, 30, 0),   // 9:30 AM
            new TimeSpan(16, 0, 0)    // 4:00 PM
        );

        var time = new DateTime(2024, 1, 15, 10, 30, 0);
        Assert.IsTrue(calc.IsInSession(time));
    }

    [Test]
    public void IsInSession_OutsideWindow_ReturnsFalse()
    {
        var calc = new SessionCalculator(
            new TimeSpan(9, 30, 0),
            new TimeSpan(16, 0, 0)
        );

        var time = new DateTime(2024, 1, 15, 8, 0, 0);
        Assert.IsFalse(calc.IsInSession(time));
    }

    [Test]
    public void IsInSession_OvernightSession_HandlesCorrectly()
    {
        var calc = new SessionCalculator(
            new TimeSpan(18, 0, 0),   // 6:00 PM
            new TimeSpan(5, 0, 0)     // 5:00 AM next day
        );

        // 8 PM should be in session
        var evening = new DateTime(2024, 1, 15, 20, 0, 0);
        Assert.IsTrue(calc.IsInSession(evening));

        // 2 AM should be in session
        var night = new DateTime(2024, 1, 16, 2, 0, 0);
        Assert.IsTrue(calc.IsInSession(night));

        // 10 AM should be out of session
        var morning = new DateTime(2024, 1, 16, 10, 0, 0);
        Assert.IsFalse(calc.IsInSession(morning));
    }
}
```

---

## Running Tests

### Command Line

```bash
# Run all tests
dotnet test

# Run with verbose output
dotnet test --logger "console;verbosity=detailed"

# Run specific test class
dotnet test --filter "FullyQualifiedName~VWAPHelperTests"

# Run specific test
dotnet test --filter "FullyQualifiedName~Calculate_SingleBar_ReturnsTypicalPrice"
```

### Visual Studio

1. Open Test Explorer: `Test > Test Explorer`
2. Build solution: `Ctrl+Shift+B`
3. Run all tests: `Ctrl+R, A`
4. Run selected: `Ctrl+R, T`

---

## Integrating Helper into Indicator

After tests pass, use the helper in your indicator:

```csharp
public class VWAPLB : Indicator
{
    #region Private Fields
    private VWAPHelper vwapHelper;
    #endregion

    protected override void OnStateChange()
    {
        if (State == State.SetDefaults)
        {
            Description = "VWAP with standard deviation bands";
            Name = "VWAP LB";
            // ...
        }
        else if (State == State.DataLoaded)
        {
            vwapHelper = new VWAPHelper();
        }
    }

    protected override void OnBarUpdate()
    {
        if (Bars.IsFirstBarOfSession)
        {
            vwapHelper.Reset();
        }

        var (vwap, stdDev) = vwapHelper.Calculate(
            High[0], Low[0], Close[0], Volume[0]
        );

        Values[0][0] = vwap;
        Values[1][0] = vwap + stdDev * Multiplier;
        Values[2][0] = vwap - stdDev * Multiplier;
    }
}
```

---

## Refactoring Existing Indicators

When refactoring indicators without tests:

### Step 1: Identify Pure Calculations
Look for code that:
- Performs mathematical operations
- Tracks state across bars
- Makes decisions based on conditions

### Step 2: Extract to Helper Class
Move the calculation logic:

```csharp
// Before (in OnBarUpdate)
double typicalPrice = (High[0] + Low[0] + Close[0]) / 3.0;
sumPV += typicalPrice * Volume[0];
sumV += Volume[0];
double vwap = sumPV / sumV;

// After (helper class)
var result = vwapHelper.Calculate(High[0], Low[0], Close[0], Volume[0]);
Values[0][0] = result.vwap;
```

### Step 3: Write Characterization Tests
Tests that capture current behavior:

```csharp
[Test]
public void Calculate_KnownInputSequence_MatchesExpectedOutput()
{
    // Use real data from NinjaTrader to verify helper matches
    var helper = new VWAPHelper();

    // Bar 1
    var r1 = helper.Calculate(100, 98, 99, 1000);
    Assert.AreEqual(99.0, r1.vwap, 0.001);

    // Bar 2
    var r2 = helper.Calculate(101, 99, 100, 1500);
    Assert.AreEqual(99.6, r2.vwap, 0.1);  // Approximately

    // Continue with known sequence...
}
```

### Step 4: Refactor with Confidence
With tests in place, you can safely:
- Rename variables
- Extract methods
- Optimize calculations
- Fix bugs

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Tests not discovered | Ensure NUnit3TestAdapter is installed |
| DLL not found | Check HintPath in .csproj references |
| Compile errors | Verify .NET Framework version matches |
| Helper not accessible | Ensure helper is `public` class |

### Debug Tips

```csharp
// Add test output for debugging
[Test]
public void DebugTest()
{
    var result = helper.Calculate(100, 90, 95, 1000);
    TestContext.WriteLine($"VWAP: {result.vwap}, StdDev: {result.stdDev}");
    Assert.Pass();
}
```

---

## Best Practices

### Do
- Write tests before implementation (TDD)
- Test edge cases and boundary conditions
- Use descriptive test names
- Keep helper classes focused and single-purpose
- Use dependency injection for flexibility

### Don't
- Test NinjaTrader framework code
- Test trivial getters/setters
- Create complex mock objects for simple tests
- Ignore failing tests
- Skip tests for "simple" code

---

## Resources

- [ScaleInTrading TDD Guide](http://www.scaleintrading.com/blog/nt8-development-2/tdd-and-unit-testing-with-nt8-2)
- [NinjaTDD Framework](https://github.com/adfra/NinjaTDD)
- [NUnit Documentation](https://docs.nunit.org/)
- [dotnet test Documentation](https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-test)
