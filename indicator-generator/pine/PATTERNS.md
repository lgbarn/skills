# Pine Script Patterns Reference

Detailed conventions and patterns for TradingView Pine Script v5/v6 indicators.

## Quick Navigation

| Topic | File | Description |
|-------|------|-------------|
| Inputs | [INPUTS.md](INPUTS.md) | Input organization, tooltips, grouping patterns |
| Theming | [THEMING.md](THEMING.md) | Color theming, light/dark mode, color palette |
| State | [STATE.md](STATE.md) | var vs varip, arrays, maps, custom types |
| Functions | [FUNCTIONS.md](FUNCTIONS.md) | Function documentation, session handling |
| Performance | [PERFORMANCE.md](PERFORMANCE.md) | Optimization, bar states, calculations, resource limits |

---

## Critical Rules (Quick Reference)

### Line Continuation / Wrapping

**Critical**: Continuation lines must follow specific indentation rules.

| Context | Rule |
|---------|------|
| Global scope | Continuation indent must NOT be a multiple of 4 (use 1, 2, 3, 5, 6, 7, etc. spaces) |
| Inside parentheses | No restriction - any indentation is allowed |
| Inside local blocks | Must use MORE than 4 spaces, and NOT a multiple of 4 (use 5, 6, 7, 9, 10, etc.) |

**Correct - Global scope (2 spaces):**
```pine
a = open + high +
  low + close
```

**Incorrect - Global scope (4 spaces - will error):**
```pine
a = open + high +
    low + close  // ERROR: 4-space indent interpreted as local block
```

**Correct - Inside parentheses (any indent OK):**
```pine
plot(
    series = close,
    title = "Close",
    color = color.blue
)
```

---

### Spacing Conventions

**Source**: [TradingView Style Guide](https://www.tradingview.com/pine-script-docs/writing/style-guide/)

- Space on both sides of all operators (except unary)
- Space after commas
- Space around named arguments

```pine
// GOOD
int a = close > open ? 1 : -1
float b = -1.5  // Unary minus - no space
plot(close, color = color.red)

// BAD
int a=close>open?1:-1
plot(close,color=color.red)
```

---

### Script Organization Order

**Source**: [TradingView Style Guide](https://www.tradingview.com/pine-script-docs/writing/style-guide/)

1. **`<license>`** - MPL 2.0 header comment
2. **`<version>`** - `//@version=6`
3. **`<declaration_statement>`** - `indicator()` / `strategy()` / `library()`
4. **`<import_statements>`** - Library imports
5. **`<constant_declarations>`** - SNAKE_CASE constants
6. **`<inputs>`** - All inputs grouped together
7. **`<function_declarations>`** - User-defined functions
8. **`<calculations>`** - Core logic
9. **`<strategy_calls>`** - Strategy orders (strategies only)
10. **`<visuals>`** - Plots, drawings, colors
11. **`<alerts>`** - Alert conditions

---

### Constants Declaration

**Source**: [TradingView Style Guide](https://www.tradingview.com/pine-script-docs/writing/style-guide/)

- Use `SNAKE_CASE` for all constants
- **Do NOT use `var` for constants** - it incurs a performance penalty

```pine
// GOOD - const keyword, no var
const int MS_IN_DAY = 1000 * 60 * 60 * 24
const color BULL_COLOR = #00FF00
const string RST_SESSION = "At the beginning of the regular session"

// BAD - var adds overhead for constants
var int MS_IN_DAY = 1000 * 60 * 60 * 24
```

---

### Section Dividers

**Major Sections:**
```pine
// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║   SECTION TITLE IN CAPS                                                    ║
// ╚═══════════════════════════════════════════════════════════════════════════╝
```

**Minor Subsections:**
```pine
// ─── Subsection Title ───
```

---

### Naming Conventions

**Source**: [TradingView Style Guide](https://www.tradingview.com/pine-script-docs/writing/style-guide/)

Always declare variable types explicitly:

```pine
// GOOD - explicit types
float vwapValue = 0.0
int barCount = 0
bool sessionActive = false
color plotColor = color.blue
string labelText = "VWAP"
```

**Prefixes:**
| Prefix | Usage | Example |
|--------|-------|---------|
| `enable*` | Master feature toggle | `enableVWAP` |
| `show*` | Display toggle | `showBands` |
| `cached_*` | Pre-computed values | `cached_totalMinutes` |
| `theme_*` | Theme-aware colors | `theme_bullish` |
| `prev_*` | Previous value | `prev_close` |
| `sum*` | Cumulative sum | `sumPriceVolume` |

**Suffixes:**
| Suffix | Usage | Example |
|--------|-------|---------|
| `*Color` | Color variable | `vwapColor` |
| `*Width` | Line width | `lineWidth` |
| `*Style` | Line/plot style | `lineStyle` |
| `*Input` | Raw input value | `styleInput` |
| `*_line` | Line object | `high_line` |
| `*_label` | Label object | `high_label` |
| `*_box` | Box object | `range_box` |

---

### File Naming

| Type | Pattern | Example |
|------|---------|---------|
| Branded | `LB_*.pine` | `LB_VWAP.pine` |
| Pro/Composite | `*_Pro.pine` | `VWAP_Pro.pine` |
| Base variant | lowercase | `vwap.pine` |

---

## Detailed Documentation

For comprehensive patterns and examples, see the linked files:

- **[INPUTS.md](INPUTS.md)** - Input organization, tooltip best practices, input patterns by type
- **[THEMING.md](THEMING.md)** - Theme toggle, color palette, transparency, conditional colors
- **[STATE.md](STATE.md)** - var vs varip, arrays, maps, custom types with methods
- **[FUNCTIONS.md](FUNCTIONS.md)** - Function annotations, session handling, helper patterns
- **[PERFORMANCE.md](PERFORMANCE.md)** - Bar states, optimization, calculations, resource limits
