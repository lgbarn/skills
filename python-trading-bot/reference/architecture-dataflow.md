# Data Flow & Logic

Bar processing, entry/exit flows, and position state management.

---

## Bar Processing Flow

```
1. WebSocket receives raw bar data
   └─▶ {timestamp, open, high, low, close, volume}

2. Convert to standard bar format
   └─▶ Add hour, date extracted from timestamp

3. Append to bars list
   └─▶ self.bars.append(bar)

4. Check warmup
   └─▶ Need minimum bars for indicators

5. Update indicators
   └─▶ indicators.update(self.bars)

6. Get enriched bar
   └─▶ curr = indicators.get_bar(idx)
   └─▶ {close, atr, adx, plus_di, minus_di, vol_ma, ...signal indicators}

7. Check daily reset
   └─▶ risk_manager.check_new_day()

8. Process position
   └─▶ If flat: check entries
   └─▶ If in position: check exits
```

---

## Entry Flow

```
1. Session filter
   └─▶ Skip if outside allowed hours

2. Volume filter
   └─▶ Skip if volume < vol_ma

3. Calculate exit levels
   └─▶ sl_pts = atr * sl_atr_mult
   └─▶ tp_pts = atr * tp_atr_mult

4. Check signal
   └─▶ Signal-specific detection (crossover, breakout, etc.)

5. Check re-entry
   └─▶ If last exit profitable + 3 bars + ADX > 40

6. ADX filter (skip for re-entry)
   └─▶ ADX > threshold + mode-specific condition

7. Execute entry
   └─▶ Apply slippage
   └─▶ Set SL/TP levels
   └─▶ Send to TradersPost
```

---

## Exit Flow

```
1. Update HWM/LWM
   └─▶ Track high water mark (longs) / low water mark (shorts)

2. Check trailing activation
   └─▶ If profit >= trail_trigger_atr * ATR
   └─▶ Activate trailing stop

3. Update trailing stop
   └─▶ Trail follows HWM/LWM at distance

4. Check exits (priority order)
   └─▶ 1. Trailing stop (if active)
   └─▶ 2. Stop loss
   └─▶ 3. Take profit

5. Execute exit
   └─▶ Apply slippage
   └─▶ Calculate P&L
   └─▶ Update risk manager
   └─▶ Send to TradersPost
   └─▶ Track for re-entry
```

---

## Signal Detection

All signals use **edge detection** (not level):

```python
# WRONG: Level-based (fires every bar above level)
if close > upper:
    long_signal = True

# CORRECT: Edge-based (fires only on crossover)
if prev_close <= prev_upper and close > upper:
    long_signal = True
```

This prevents multiple entries while price stays above/below threshold.

---

## ADX Filter Modes

```python
def _check_adx(curr, prev, direction):
    if adx <= threshold:
        return False  # Base condition

    if mode == "traditional":
        return True  # Just ADX > threshold

    elif mode == "di_aligned":
        # DIs aligned with trade direction
        if direction == 1:
            return plus_di > minus_di
        else:
            return minus_di > plus_di

    elif mode == "di_rising":
        # Dominant DI is rising (RECOMMENDED)
        if direction == 1:
            return curr_plus_di > prev_plus_di
        else:
            return curr_minus_di > prev_minus_di

    elif mode == "adx_rising":
        return curr_adx > prev_adx

    elif mode == "combined":
        # All conditions
        return di_aligned and adx_rising
```

---

## Position State Machine

```
                    ┌──────────────┐
                    │     FLAT     │
                    │   pos = 0    │
                    └──────┬───────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               │               ▼
    ┌──────────────┐       │        ┌──────────────┐
    │     LONG     │       │        │    SHORT     │
    │   pos = 1    │◀──────┘───────▶│   pos = -1   │
    └──────┬───────┘                └──────┬───────┘
           │                               │
           │         Exit (SL/TP/Trail)    │
           │                               │
           └───────────────┬───────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │     FLAT     │
                    │   pos = 0    │
                    │              │
                    │ Track for    │
                    │ re-entry     │
                    └──────────────┘
```

---

## Error Handling

### WebSocket Reconnection

```python
async def _handle_messages():
    while self._running:
        try:
            msg = await ws.receive()
            # Process message
        except:
            await self._reconnect()

async def _reconnect():
    await asyncio.sleep(5)
    await self._connect_websocket()
```

### Graceful Shutdown

```python
def shutdown_handler():
    asyncio.create_task(bot.stop())

for sig in (SIGINT, SIGTERM):
    loop.add_signal_handler(sig, shutdown_handler)

async def stop():
    self._running = False
    if self.position != 0:
        await self._exit_position("Shutdown")
    await self.tradovate.disconnect()
```

---

## See Also

- [COMPONENTS.md](COMPONENTS.md) - Component details
- [../ARCHITECTURE.md](../ARCHITECTURE.md) - Architecture overview
- [../adx-modes.md](../adx-modes.md) - ADX filter configuration
