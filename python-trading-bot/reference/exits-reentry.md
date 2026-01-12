# Exit Settings & Re-entry Logic

Stop loss, take profit, trailing stops, and re-entry configuration.

---

## Stop Loss / Take Profit

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `atr_period` | int | 14 | 5-30 | ATR calculation period |
| `sl_atr_mult` | float | 3.0 | 1.0-10.0 | Stop loss = entry ± (ATR × mult) |
| `tp_atr_mult` | float | 3.0 | 1.0-10.0 | Take profit = entry ± (ATR × mult) |

---

## Trailing Stop

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `trail_enabled` | bool | true | - | Enable trailing stops |
| `trail_trigger_atr` | float | 0.15 | 0.05-1.0 | Profit to activate trail (ATR mult) |
| `trail_distance_atr` | float | 0.15 | 0.05-1.0 | Trail distance from HWM/LWM |

**Trailing Stop Logic:**
```python
# Trailing activates when profit >= trigger
if pos == 1:  # Long
    profit = high - entry
    if profit >= trail_trigger:
        trail_on = True
        # Trail follows high water mark
        stop = hwm - trail_distance

elif pos == -1:  # Short
    profit = entry - low
    if profit >= trail_trigger:
        trail_on = True
        # Trail follows low water mark
        stop = lwm + trail_distance
```

---

## Exit Priority Order

When multiple exit conditions are met on the same bar:

1. **Trailing Stop** (if active AND hit)
2. **Stop Loss** (hard protective stop)
3. **Take Profit** (profit target)

This conservative approach assumes the worst outcome when both SL and TP could be hit.

---

## Re-entry Settings

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `reentry_enabled` | bool | true | - | Allow trend continuation re-entries |
| `reentry_bars_wait` | int | 3 | 1-10 | Bars to wait after exit |
| `reentry_adx_min` | float | 40 | 30-60 | Higher ADX required for re-entry |
| `max_reentries` | int | 10 | 1-20 | Max re-entries per trend direction |

**Re-entry Logic:**
```python
# Only after profitable exits
if last_exit_profitable:
    bars_since_exit = current_bar - last_exit_bar

    if bars_since_exit >= reentry_bars_wait:
        if reentry_count < max_reentries:
            if adx > reentry_adx_min:
                # Check if still in trend (signal-specific)
                if last_exit_direction == 1:
                    # Long re-entry check
                    pass
                elif last_exit_direction == -1:
                    # Short re-entry check
                    pass
```

---

## See Also

- [docs/architecture-dataflow.md](../docs/architecture-dataflow.md) - Exit flow diagram
- [signal-keltner.md](signal-keltner.md#re-entry-logic) - Signal-specific re-entry conditions
