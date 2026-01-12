---
name: indicator-generator
description: Create, modify, debug, and convert trading indicators AND STRATEGIES for TradingView (Pine Script v5/v6) and NinjaTrader 8 (NinjaScript C#). Use when writing indicators, strategies, adding features, refactoring, converting between platforms, or debugging. Follows Luther Barnum's coding standards. Triggers: "create indicator", "create strategy", "strategy for", "Pine Script", "NinjaScript", "convert to", "add feature", "VWAP", "keltner strategy", "ema cross strategy", "generate strategy from backtest".
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(dotnet:*, npm:*)
---

# Trading Indicator & Strategy Generator

Generate professional trading indicators and automated strategies following Luther Barnum's coding standards for TradingView (Pine Script) and NinjaTrader 8 (NinjaScript C#).

## Quick Start

### For Indicators
1. **Identify the target platform(s)**
2. **Reference the platform-specific template and patterns**
3. **Apply common conventions** (author attribution, feature toggles, theming)
4. **Follow indicator type patterns** based on what you're building

### For Strategies
1. **Run `/strategy:new`** or describe the strategy you want
2. **Answer interactive prompts** about signal, parameters, and features
3. **Receive generated code** for your target platform (Pine Script or NinjaScript)

See [strategy/WORKFLOW.md](strategy/WORKFLOW.md) for the full interactive workflow.

---

## When to Use This Skill

**Use this skill when:**
- Creating a new indicator from scratch
- **Generating automated trading strategies** from backtested configurations
- Adding features to an existing indicator or strategy
- Converting indicators/strategies between platforms
- Refactoring code for performance or organization
- Debugging indicator/strategy calculation issues
- Understanding platform-specific patterns and conventions

**Do NOT use for:**
- CI/CD configuration (use ci-cd-setup skill)
- General code review unrelated to trading
- Non-trading-related code or scripts
- Tradovate strategies (indicators only for Tradovate)

---

## Critical Rules (Quick Reference)

### Pine Script - Must Know

| Rule | Details |
|------|---------|
| **Line continuation** | Continuation indent must NOT be multiples of 4 (except inside parentheses) |
| **Constants** | Use `SNAKE_CASE`, do NOT use `var` for constants (performance penalty) |
| **Explicit typing** | Always declare variable types: `float vwapValue = 0.0` |
| **var vs varip** | `var` = persists historically, `varip` = realtime only |
| **Math stability** | Clamp variance before sqrt: `math.sqrt(math.max(0, variance))` |
| **Array safety** | Always check bounds before array access |
| **Tooltips** | Every input should have a descriptive tooltip |

See [pine/PATTERNS.md](pine/PATTERNS.md) for complete patterns.

### NinjaScript - Must Know

| Rule | Details |
|------|---------|
| **TDD required** | Write tests first for all calculations using helper classes |
| **Helper classes** | Extract logic to testable `*Helper`/`*Calculator` classes |
| **Test runner** | Use `dotnet test` with NUnit to run tests |
| **Region organization** | Use `#region` blocks: Variables, OnStateChange, OnBarUpdate, Properties |
| **Guard clauses** | Start OnBarUpdate with guards: `if (CurrentBar < Period) return;` |
| **Plot indexing** | Document plot indices: `// VWAP plots (0-4)` |
| **Error handling** | Use try/catch for timezone conversion, null checks for indicators |
| **MTF series** | Check `CurrentBars[n] > 0` before accessing secondary series |

See [ninja/PATTERNS.md](ninja/PATTERNS.md) for patterns and [ninja/TESTING.md](ninja/TESTING.md) for TDD guide.

### Tradovate - Must Know

| Rule | Details |
|------|---------|
| **Graphics ScaleBound** | Use `du()` for domain units, `px()` for pixels, `op()` to combine |
| **Last bar graphics** | Only render graphics on `d.isLast()` |
| **Validation** | Use `validate(obj)` for parameter relationship checks |
| **Calculator reuse** | Create calculators once in `init()`, reuse in `map()` |
| **History access** | Cache `history.prior()` result, don't call multiple times |

See [tradovate/PATTERNS.md](tradovate/PATTERNS.md) for complete patterns.

### All Platforms - Mathematical Stability

```
// Always guard against:
- Division by zero: `sumV > 0 ? sumPV / sumV : defaultValue`
- Negative sqrt: `Math.sqrt(Math.max(0, variance))`
- Array out of bounds: Check size before access
- NaN/Infinity: Validate data before calculations
```

---

## Additional Resources

| Resource | Description |
|----------|-------------|
| [DEBUGGING.md](DEBUGGING.md) | Cross-platform debugging strategies |
| [EXAMPLES.md](EXAMPLES.md) | Complete examples for each indicator type |

---

## Strategy Generation

Generate automated trading strategies from backtested configurations for Pine Script and NinjaScript.

### Commands

| Command | Description |
|---------|-------------|
| `/strategy:new` | Start interactive strategy builder |
| `/strategy:new <signal>` | Start with signal pre-selected |
| `/strategy:pine <signal>` | Generate Pine Script strategy |
| `/strategy:ninja <signal>` | Generate NinjaScript strategy |
| `/strategy:list` | Show all signals with backtest metrics |

### Available Entry Signals (11)

| Signal | Description | Profit Factor | Win Rate |
|--------|-------------|---------------|----------|
| **keltner** | Keltner Channel breakout | 10.04 | 87.8% |
| **ema_cross** | EMA crossover with separation | 6.23 | 82.7% |
| **vwap** | Rolling VWAP band breakout | 5.20 | 85.3% |
| **supertrend** | SuperTrend direction flip | 4.41 | 82.5% |
| **alligator** | Williams Alligator alignment | 4.16 | 83.5% |
| ssl | SSL Channel direction flip | 4.08 | 79.8% |
| squeeze | TTM Squeeze release | 3.88 | 82.0% |
| aroon | Aroon crossover | 3.46 | 81.4% |
| adx_only | +DI/-DI crossover | 3.37 | 80.7% |
| stochastic | Stochastic %K/%D crossover | - | - |
| macd | MACD line/signal crossover | - | - |

*Metrics from 219-day NQ futures backtest with ADX di_rising, threshold 35.*

### Strategy Features (All Configurable)

- **Entry Signals**: All 11 backtested signals supported
- **ADX Filter**: 5 modes (traditional, di_aligned, di_rising, adx_rising, combined)
- **ATR-based Exits**: Stop loss, take profit, trailing stop
- **Re-entry Logic**: Trend continuation after profitable exits
- **Volume Filter**: Require volume > MA
- **Session Filter**: Trading hour restrictions

### Strategy References

| Resource | Description |
|----------|-------------|
| [strategy/WORKFLOW.md](strategy/WORKFLOW.md) | Interactive prompt workflow |
| [strategy/SIGNALS.md](strategy/SIGNALS.md) | Detailed signal documentation |
| [strategy/CONFIG.md](strategy/CONFIG.md) | Parameter reference |
| [strategy/pine/TEMPLATE.md](strategy/pine/TEMPLATE.md) | Pine Script strategy template |
| [strategy/ninja/TEMPLATE.md](strategy/ninja/TEMPLATE.md) | NinjaScript strategy template |

### Example Usage

```
User: Create a keltner strategy for Pine Script
Assistant: [Runs interactive workflow]
  - Signal: keltner (EMA=20, ATR Mult=2.75)
  - ADX: threshold=35, mode=di_rising
  - Exits: SL=3.0×ATR, TP=3.0×ATR, Trail=0.15×ATR
  - Features: Re-entry, Volume Filter, Session Filter
  - Platform: Pine Script v6

[Generates LB_Keltner_Strategy.pine]
```

---

## Platform References

| Platform | Template | Patterns | File Naming |
|----------|----------|----------|-------------|
| TradingView | [pine/TEMPLATE.md](pine/TEMPLATE.md) | [pine/PATTERNS.md](pine/PATTERNS.md) | `LB_*.pine` or `*_Pro.pine` |
| NinjaTrader 8 | [ninja/TEMPLATE.md](ninja/TEMPLATE.md) | [ninja/PATTERNS.md](ninja/PATTERNS.md) | `*LB.cs` or `*_Pro.cs` |
| Tradovate | [tradovate/TEMPLATE.md](tradovate/TEMPLATE.md) | [tradovate/PATTERNS.md](tradovate/PATTERNS.md) | `*LB.js` or `*ProLB.js` |

## Cross-Platform Examples

See [EXAMPLES.md](EXAMPLES.md) for complete examples of each indicator type across all platforms.

---

## Common Conventions (All Platforms)

### Author Attribution
- **Pine:** `// by Luther Barnum - [Indicator Name]`
- **Ninja:** `// Author: Luther Barnum` in file header
- **Tradovate:** `tags: ["Luther Barnum"]` in module.exports

### Feature Toggles
All indicators use master enable/disable booleans in a "Feature Toggles" group:

```pine
// Pine Script
enableVWAP = input.bool(true, "Enable VWAP", group="Feature Toggles")
```

```csharp
// NinjaScript
[Display(Name = "Enable VWAP", GroupName = "Feature Toggles", Order = 1)]
public bool EnableVWAP { get; set; }
```

```javascript
// Tradovate
params: {
  enableVWAP: predef.paramSpecs.bool(true),
}
```

### Session Handling
- Default timezone: America/New_York (Eastern)
- Support RTH (Regular Trading Hours) and ETH (Extended)
- Handle midnight-crossing sessions
- Detect session start/end boundaries

### Color Palette
Consistent colors across platforms:

| Purpose | Light Theme | Dark Theme |
|---------|-------------|------------|
| Bullish | Dark green (#004400) | Lime (#00FF00) |
| Bearish | Dark red (#990000) | Red (#FF0000) |
| Neutral | Gold (#FFD700) | Yellow (#FFFF00) |
| VWAP | Purple (#4A148C) | Orchid (#CE95D8) |
| Weekly | Teal (#006363) | Cyan (#00FFFF) |
| Monthly | Navy (#0D47A1) | Blue (#1E90FF) |

### Naming Conventions
- **Variables:** camelCase (`vwapValue`, `ibHigh`, `sumPriceVolume`)
- **Prefixes:** `show*`, `enable*`, `prev*`, `cached_*`, `theme_*`
- **Suffixes:** `*Color`, `*Width`, `*Style`, `*_line`, `*_label`

---

## Indicator Types

### 1. VWAP Variants
Features: Daily/Weekly/Monthly VWAP, SD bands, anchored start times, MTF dashboard

Key calculations:
- Cumulative TPV (Typical Price × Volume)
- Standard deviation bands
- Session reset logic

### 2. Session-Based (IB, Opening Range)
Features: Time window detection, high/low tracking, extension levels, labels

Key calculations:
- Session start/end detection
- Running high/low within window
- Extension multipliers (0.5x, 1x, 1.5x, 2x)

### 3. Oscillators (RSI, ADX, Stochastic)
Features: Bounded values, overbought/oversold zones, signal crossovers

Key calculations:
- Period-based lookback
- Smoothing (EMA, SMA)
- Zone thresholds

### 4. Multi-Feature Composites (Pro Indicators)
Features: Multiple toggleable components, unified settings, dashboard

Architecture:
- Master feature toggles
- Modular calculation sections
- Combined plot management
- Performance optimization

---

## Workflow

### Creating a New Indicator

1. Start with the platform TEMPLATE.md
2. Replace placeholder values:
   - `[INDICATOR_NAME]` → Your indicator name
   - `[SHORT_NAME]` → Abbreviated name
   - `[DESCRIPTION]` → User-facing description
3. Add inputs following PATTERNS.md grouping conventions
4. Implement calculations in the appropriate lifecycle method
5. Add plots/drawing objects
6. Test on platform

### NinjaScript TDD Workflow

For NinjaTrader indicators, follow TDD (Test-Driven Development):

1. **Write tests first** for calculation logic
   ```bash
   dotnet new nunit -n LB.Indicators.Tests -f net48
   ```

2. **Create helper class** with testable methods
   - Extract calculations to `*Helper` or `*Calculator` classes
   - Use dependency injection (pass bar data as parameters)

3. **Run tests** to verify (red-green-refactor)
   ```bash
   dotnet test
   ```

4. **Integrate helper** into indicator
   - Keep indicator thin (lifecycle methods only)
   - Call helper methods from OnBarUpdate

5. **Verify all tests pass** before completion

See [ninja/TESTING.md](ninja/TESTING.md) for complete guide.

### Adding Features to Existing Indicator

1. Add feature toggle in "Feature Toggles" group
2. Add feature-specific inputs in dedicated group
3. Add calculation variables
4. Implement calculation logic (guarded by toggle)
5. Add conditional plots/graphics
6. Update any dashboards

**For NinjaScript:** Write tests for new feature calculations first, then implement in helper class.

### Refactoring Existing NinjaScript Indicator

When refactoring indicators that lack tests:

1. **Identify pure calculations** - VWAP, standard deviation, session detection
2. **Write characterization tests** - Capture current behavior
3. **Extract to helper class** - Move logic out of OnBarUpdate
4. **Refactor with test protection** - Tests prevent regressions
5. **Run `dotnet test`** - Verify all tests pass

### Converting Between Platforms

1. Read source indicator thoroughly
2. Map inputs to target platform conventions
3. Translate calculation logic (watch for API differences)
4. Adapt plotting/drawing to target platform
5. Apply target platform naming conventions
6. Test thoroughly on target platform

---

## Best Practices

### Performance
- Cache repeated calculations (especially time conversions)
- Use `var` (Pine) or class fields (Ninja/Tradovate) for persistent state
- Avoid recalculating on every bar what only changes on session change
- Only render graphics on last bar when possible

### User Experience
- Group related inputs logically
- Provide tooltips explaining each input
- Use sensible defaults matching common use cases
- Support both light and dark themes

### Code Quality
- Use section dividers for organization
- Follow platform-specific naming conventions
- Comment complex calculations
- Keep functions focused and reusable
