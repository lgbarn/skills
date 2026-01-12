# Pine Script v6 Indicator Template

Use this template as the starting point for new TradingView indicators.

## Complete Template

```pine
// Released under the Mozilla Public License 2.0 — see https://mozilla.org/MPL/2.0/
// by Luther Barnum - [INDICATOR_NAME]

//@version=6
indicator("[INDICATOR_NAME]", shorttitle="[SHORT_NAME]", overlay=true, max_bars_back=500, max_labels_count=500, max_lines_count=500, max_boxes_count=500)

// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║   IMPORTS                                                                  ║
// ╚═══════════════════════════════════════════════════════════════════════════╝

// Uncomment if using Session Volume Profile
// import jmosullivan/SessionVolumeProfile/12 as SVP
// import jmosullivan/Session/10 as Session

// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║   FEATURE TOGGLES (MASTER)                                                 ║
// ╚═══════════════════════════════════════════════════════════════════════════╝

enableFeature1 = input.bool(true, "Enable Feature 1", group="Feature Toggles", tooltip="Master toggle for Feature 1")
enableFeature2 = input.bool(true, "Enable Feature 2", group="Feature Toggles", tooltip="Master toggle for Feature 2")

// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║   THEME SETTINGS                                                           ║
// ╚═══════════════════════════════════════════════════════════════════════════╝

useLightTheme = input.bool(false, "Light Theme Mode", group="Theme", tooltip="Enable for light chart backgrounds (WCAG AA compliant colors)")

// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║   FEATURE 1 SETTINGS                                                       ║
// ╚═══════════════════════════════════════════════════════════════════════════╝

showFeature1Line = input.bool(true, "Show Line", inline="f1_show", group="Feature 1 Settings")
feature1Period = input.int(14, "Period", minval=1, maxval=500, step=1, group="Feature 1 Settings", tooltip="Lookback period for calculation")
feature1Width = input.int(2, "Width", minval=1, maxval=5, inline="f1_style", group="Feature 1 Settings")
feature1StyleInput = input.string("Solid", "Style", options=["Solid", "Dashed", "Dotted"], inline="f1_style", group="Feature 1 Settings")

// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║   SESSION SETTINGS                                                         ║
// ╚═══════════════════════════════════════════════════════════════════════════╝

sessionTimeZone = input.string("America/New_York", "Time Zone", options=["America/New_York", "America/Chicago", "America/Los_Angeles", "Europe/London", "Asia/Tokyo"], group="Session Settings")
sessionStartHour = input.int(9, "Start Hour", minval=0, maxval=23, inline="session_start", group="Session Settings")
sessionStartMinute = input.int(30, "Min", minval=0, maxval=59, step=5, inline="session_start", group="Session Settings")
sessionEndHour = input.int(16, "End Hour", minval=0, maxval=23, inline="session_end", group="Session Settings")
sessionEndMinute = input.int(0, "Min", minval=0, maxval=59, step=5, inline="session_end", group="Session Settings")

// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║   THEME-AWARE COLOR DEFINITIONS                                            ║
// ╚═══════════════════════════════════════════════════════════════════════════╝

// ─── Base Colors ───
theme_white = useLightTheme ? color.black : color.white
theme_gray = useLightTheme ? color.new(#404040, 0) : color.new(#808080, 0)

// ─── Bullish/Bearish ───
theme_lime = useLightTheme ? color.new(#004400, 0) : color.lime          // WCAG AA
theme_red = useLightTheme ? color.new(#990000, 0) : color.red            // WCAG AA
theme_yellow = useLightTheme ? color.new(#806600, 0) : color.yellow      // WCAG AA

// ─── Feature-Specific Colors ───
theme_feature1 = useLightTheme ? color.new(#4A148C, 0) : color.new(#CE95D8, 0)  // Purple/Orchid
theme_feature2 = useLightTheme ? color.new(#006363, 0) : color.new(#00FFFF, 0)  // Teal/Cyan

// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║   CONSTANTS                                                                ║
// ╚═══════════════════════════════════════════════════════════════════════════╝

MINUTES_PER_DAY = 1440

// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║   HELPER FUNCTIONS                                                         ║
// ╚═══════════════════════════════════════════════════════════════════════════╝

// Convert style string to plot style constant
getPlotStyle(s) =>
    switch s
        "Dashed" => plot.style_linebr
        "Dotted" => plot.style_circles
        => plot.style_line

// Convert style string to line style constant
getLineStyle(s) =>
    switch s
        "Dashed" => line.style_dashed
        "Dotted" => line.style_dotted
        => line.style_solid

// Convert size string to size constant
getSizeConstant(sizeStr) =>
    switch str.lower(sizeStr)
        "tiny"   => size.tiny
        "small"  => size.small
        "normal" => size.normal
        "large"  => size.large
        "huge"   => size.huge
        => size.normal

// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║   CACHED TIME CALCULATIONS                                                 ║
// ╚═══════════════════════════════════════════════════════════════════════════╝

cached_hour = hour(time, sessionTimeZone)
cached_minute = minute(time, sessionTimeZone)
cached_totalMinutes = cached_hour * 60 + cached_minute

// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║   SESSION WINDOW LOGIC                                                     ║
// ╚═══════════════════════════════════════════════════════════════════════════╝

var int session_startMinutes = sessionStartHour * 60 + sessionStartMinute
var int session_endMinutes = sessionEndHour * 60 + sessionEndMinute
var bool session_crossesMidnight = session_endMinutes < session_startMinutes

withinSessionWindow() =>
    if session_crossesMidnight
        cached_totalMinutes >= session_startMinutes or cached_totalMinutes < session_endMinutes
    else
        cached_totalMinutes >= session_startMinutes and cached_totalMinutes < session_endMinutes

isSessionStart() =>
    if session_crossesMidnight
        cached_totalMinutes == session_startMinutes
    else
        cached_totalMinutes >= session_startMinutes and cached_totalMinutes[1] < session_startMinutes

// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║   TYPE DEFINITIONS                                                         ║
// ╚═══════════════════════════════════════════════════════════════════════════╝

// Example: Graphics container for session-based features
type SessionGraphics
    line highLine
    line lowLine
    line midLine
    label highLabel
    label lowLabel
    label midLabel
    box rangeBox

method deleteAll(SessionGraphics g) =>
    line.delete(g.highLine)
    line.delete(g.lowLine)
    line.delete(g.midLine)
    label.delete(g.highLabel)
    label.delete(g.lowLabel)
    label.delete(g.midLabel)
    box.delete(g.rangeBox)

method extendLines(SessionGraphics g) =>
    if not na(g.highLine)
        line.set_x2(g.highLine, bar_index)
    if not na(g.lowLine)
        line.set_x2(g.lowLine, bar_index)
    if not na(g.midLine)
        line.set_x2(g.midLine, bar_index)

// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║   STATE VARIABLES                                                          ║
// ╚═══════════════════════════════════════════════════════════════════════════╝

var float feature1Value = na
var float sessionHigh = na
var float sessionLow = na
var bool sessionActive = false

// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║   MAIN CALCULATION LOGIC                                                   ║
// ╚═══════════════════════════════════════════════════════════════════════════╝

// ─── Session Reset ───
if isSessionStart()
    sessionHigh := high
    sessionLow := low
    sessionActive := true

// ─── Feature 1 Calculation ───
if enableFeature1 and sessionActive
    // Example: Simple moving average
    feature1Value := ta.sma(close, feature1Period)

// ─── Session High/Low Tracking ───
if sessionActive and withinSessionWindow()
    sessionHigh := math.max(sessionHigh, high)
    sessionLow := math.min(sessionLow, low)

// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║   PLOTTING                                                                 ║
// ╚═══════════════════════════════════════════════════════════════════════════╝

// ─── Feature 1 Plot ───
feature1LineStyle = feature1StyleInput == "Dashed" ? plot.style_linebr : feature1StyleInput == "Dotted" ? plot.style_circles : plot.style_line

plot(enableFeature1 and showFeature1Line ? feature1Value : na,
     title="Feature 1",
     color=theme_feature1,
     linewidth=feature1Width,
     style=feature1LineStyle)

// ─── Session High/Low ───
plot(sessionActive ? sessionHigh : na, title="Session High", color=theme_lime, linewidth=1, style=plot.style_linebr)
plot(sessionActive ? sessionLow : na, title="Session Low", color=theme_red, linewidth=1, style=plot.style_linebr)

// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║   ALERTS                                                                   ║
// ╚═══════════════════════════════════════════════════════════════════════════╝

// alertcondition(condition, title="Alert Title", message="Alert message")
```

## Template Sections

### 1. Header
- License comment (MPL 2.0)
- Author attribution
- Version declaration (`@version=6`)
- Indicator definition with resource limits

### 2. Imports
- External libraries (SessionVolumeProfile, etc.)
- Only include if actually used

### 3. Feature Toggles
- Master enable/disable for each major feature
- All in "Feature Toggles" group
- Order by importance

### 4. Theme Settings
- Light/dark theme toggle
- Accessibility-focused

### 5. Feature-Specific Settings
- Grouped by feature name
- Use `inline=` for related inputs
- Include tooltips

### 6. Session Settings
- Timezone selection
- Start/end times
- Midnight-crossing support

### 7. Theme Colors
- All colors use ternary operator
- Document WCAG contrast ratios
- Group by purpose (bullish/bearish/feature)

### 8. Constants
- Magic numbers as named constants
- Performance optimizations

### 9. Helper Functions
- Style converters
- Size converters
- Reusable calculations

### 10. Cached Calculations
- Time conversions (compute once per bar)
- Expensive calculations

### 11. Session Logic
- Window detection functions
- Midnight-crossing handling
- Session start detection

### 12. Type Definitions
- Custom types for related graphics
- Methods for bulk operations

### 13. State Variables
- `var` keyword for persistence
- Organized by feature

### 14. Main Calculation
- Session reset logic
- Feature calculations
- Tracking updates

### 15. Plotting
- Conditional display
- Theme-aware colors
- Proper line styles

### 16. Alerts
- Condition-based alerts
- Descriptive messages
