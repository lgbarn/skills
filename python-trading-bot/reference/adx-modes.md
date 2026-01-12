# ADX Filter Modes

ADX (Average Directional Index) filter configuration and implementation.

---

## ADX Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `adx_enabled` | bool | true | - | Enable ADX filter for entries |
| `adx_period` | int | 14 | 5-30 | ADX calculation period |
| `di_period` | int | 14 | 5-30 | DI calculation period |
| `adx_threshold` | float | 35 | 10-50 | Minimum ADX for entry |
| `adx_mode` | str | "di_rising" | see below | Filter mode |

---

## ADX Modes

| Mode | Logic | Use Case |
|------|-------|----------|
| `traditional` | ADX > threshold | Simplest, most signals |
| `di_aligned` | + DIs aligned with trade direction | Confirms trend direction |
| `di_rising` | + Dominant DI is rising | **Recommended** - confirms momentum |
| `adx_rising` | + ADX itself is rising | Trend strengthening |
| `combined` | All of the above | Most selective, fewest signals |

---

## Implementation

```python
def check_adx_condition(bar, prev_bar, direction, config):
    if bar["adx"] <= config["adx_threshold"]:
        return False

    if config["adx_mode"] == "traditional":
        return True

    elif config["adx_mode"] == "di_aligned":
        if direction == 1:  # Long
            return bar["plus_di"] > bar["minus_di"]
        else:  # Short
            return bar["minus_di"] > bar["plus_di"]

    elif config["adx_mode"] == "di_rising":
        if direction == 1:  # Long
            return bar["plus_di"] > prev_bar["plus_di"]
        else:  # Short
            return bar["minus_di"] > prev_bar["minus_di"]

    elif config["adx_mode"] == "adx_rising":
        return bar["adx"] > prev_bar["adx"]

    elif config["adx_mode"] == "combined":
        adx_rising = bar["adx"] > prev_bar["adx"]
        if direction == 1:
            di_aligned = bar["plus_di"] > bar["minus_di"]
        else:
            di_aligned = bar["minus_di"] > bar["plus_di"]
        return di_aligned and adx_rising
```

---

## See Also

- [templates/indicators/CORE_INDICATORS.md](../templates/indicators/CORE_INDICATORS.md) - ADX calculation details
- [docs/architecture-dataflow.md](../docs/architecture-dataflow.md) - ADX filter in entry flow
