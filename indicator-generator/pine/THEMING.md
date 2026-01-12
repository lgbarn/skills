# Pine Script Color Theming

Color conventions and theming patterns for TradingView Pine Script indicators.

---

## Theme Toggle

```pine
useLightTheme = input.bool(false, "Light Theme Mode",
    group="Theme",
    tooltip="Enable for light chart backgrounds")
```

---

## Theme-Aware Color Pattern

Use ternary operator to select colors based on theme:

```pine
// Pattern: useLightTheme ? lightThemeColor : darkThemeColor
theme_bullish = useLightTheme ? color.new(#004400, 0) : color.lime
theme_bearish = useLightTheme ? color.new(#990000, 0) : color.red
theme_neutral = useLightTheme ? color.new(#806600, 0) : color.yellow
```

---

## Standard Color Palette

WCAG AA compliant colors for accessibility:

| Purpose | Light Theme | Dark Theme | Notes |
|---------|-------------|------------|-------|
| Bullish strong | `#004400` | `#00FF00` (lime) | WCAG AA |
| Bullish moderate | `#006600` | `#00AA00` | |
| Bearish strong | `#990000` | `#FF0000` (red) | WCAG AA |
| Bearish moderate | `#660000` | `#AA0000` | |
| Neutral | `#806600` | `#FFFF00` (yellow) | |
| VWAP | `#4A148C` | `#CE95D8` (orchid) | WCAG AAA |
| Weekly | `#006363` | `#00FFFF` (cyan) | |
| Monthly | `#0D47A1` | `#1E90FF` (blue) | |
| Text | `#000000` (black) | `#FFFFFF` (white) | |
| Gray | `#404040` | `#808080` | |

---

## Transparency

Use `color.new()` for transparency:

```pine
fillColor = color.new(theme_bullish, 90)  // 90% transparent
labelBg = color.new(color.black, 80)      // 80% transparent
lineColor = color.new(color.blue, 20)     // 20% transparent (mostly opaque)
```

Common transparency values:
- **0** - Fully opaque
- **20** - Subtle transparency for lines
- **50** - Medium transparency
- **80** - High transparency for backgrounds
- **90** - Very transparent for fills
- **100** - Fully transparent (invisible)

---

## Color Variables Naming

Use `theme_` prefix for theme-aware colors:

```pine
// Theme-aware colors
theme_bullish = useLightTheme ? color.new(#004400, 0) : color.lime
theme_bearish = useLightTheme ? color.new(#990000, 0) : color.red
theme_vwap = useLightTheme ? color.new(#4A148C, 0) : color.new(#CE95D8, 0)
theme_band = useLightTheme ? color.new(#4A148C, 70) : color.new(#CE95D8, 70)
theme_text = useLightTheme ? color.black : color.white
theme_background = useLightTheme ? color.new(color.white, 80) : color.new(color.black, 80)
```

---

## Complete Theme Example

```pine
// ═══ THEME SETTINGS ═══
useLightTheme = input.bool(false, "Light Theme Mode", group="Theme")

// ═══ THEME-AWARE COLORS ═══
// Directional colors
theme_bullish = useLightTheme ? color.new(#004400, 0) : color.lime
theme_bearish = useLightTheme ? color.new(#990000, 0) : color.red
theme_neutral = useLightTheme ? color.new(#806600, 0) : color.yellow

// Feature colors
theme_vwap = useLightTheme ? color.new(#4A148C, 0) : color.new(#CE95D8, 0)
theme_vwapBand = useLightTheme ? color.new(#4A148C, 80) : color.new(#CE95D8, 80)
theme_ib = useLightTheme ? color.new(#806600, 0) : color.yellow

// UI colors
theme_text = useLightTheme ? color.black : color.white
theme_labelBg = useLightTheme ? color.new(color.white, 80) : color.new(color.black, 80)
```

---

## Conditional Color Selection

```pine
// Dynamic color based on value comparison
plotColor = close > vwap ? theme_bullish : theme_bearish

// Gradient based on intensity
intensity = math.min(100, math.abs(rsiValue - 50) * 2)
rsiColor = rsiValue > 50 ?
    color.new(theme_bullish, 100 - intensity) :
    color.new(theme_bearish, 100 - intensity)
```
