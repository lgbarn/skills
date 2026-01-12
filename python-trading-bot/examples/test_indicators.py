"""
Indicator Unit Tests Example

Example unit tests for trading indicator calculations.
Uses pytest framework for clean, readable test structure.

Author: Luther Barnum
"""

import pytest
import numpy as np
from datetime import datetime, timedelta
from typing import List


# Mock Indicators class (simplified version)
class Indicators:
    """Example indicator calculation class."""

    def __init__(self, config):
        self.config = config
        self.bars: List[dict] = []

    def update(self, bars: List[dict]):
        """Calculate all indicators for given bars."""
        self.bars = bars

        # Calculate indicators
        ema = self._calculate_ema(self.config.ema_period)
        atr = self._calculate_atr(self.config.atr_period)
        adx = self._calculate_adx(self.config.adx_period)
        keltner_upper, keltner_middle, keltner_lower = self._calculate_keltner(
            self.config.keltner_period, self.config.keltner_mult
        )

        # Add to bars
        for i, bar in enumerate(self.bars):
            bar["ema"] = ema[i]
            bar["atr"] = atr[i]
            bar["adx"] = adx[i]
            bar["upper_band"] = keltner_upper[i]
            bar["middle_band"] = keltner_middle[i]
            bar["lower_band"] = keltner_lower[i]

    def get_bar(self, idx: int) -> dict:
        """Get bar with indicators at index."""
        return self.bars[idx]

    def _calculate_ema(self, period: int) -> np.ndarray:
        """Calculate Exponential Moving Average."""
        closes = np.array([b["close"] for b in self.bars])
        ema = np.zeros_like(closes)

        # Initialize with SMA
        ema[period - 1] = np.mean(closes[:period])

        # Calculate EMA
        multiplier = 2 / (period + 1)
        for i in range(period, len(closes)):
            ema[i] = (closes[i] * multiplier) + (ema[i - 1] * (1 - multiplier))

        # Pad beginning with NaN
        ema[: period - 1] = np.nan

        return ema

    def _calculate_atr(self, period: int = 14) -> np.ndarray:
        """Calculate Average True Range."""
        highs = np.array([b["high"] for b in self.bars])
        lows = np.array([b["low"] for b in self.bars])
        closes = np.array([b["close"] for b in self.bars])

        # True Range
        high_low = highs - lows
        high_close = np.abs(highs - np.roll(closes, 1))
        low_close = np.abs(lows - np.roll(closes, 1))

        true_range = np.maximum(high_low, np.maximum(high_close, low_close))

        # Average True Range (smoothed)
        atr = np.zeros_like(true_range)
        atr[period - 1] = np.mean(true_range[:period])

        for i in range(period, len(true_range)):
            atr[i] = (atr[i - 1] * (period - 1) + true_range[i]) / period

        # Pad beginning
        atr[: period - 1] = np.nan

        return atr

    def _calculate_adx(self, period: int = 14) -> np.ndarray:
        """Calculate Average Directional Index."""
        highs = np.array([b["high"] for b in self.bars])
        lows = np.array([b["low"] for b in self.bars])
        closes = np.array([b["close"] for b in self.bars])

        # True Range
        high_low = highs - lows
        high_close = np.abs(highs - np.roll(closes, 1))
        low_close = np.abs(lows - np.roll(closes, 1))
        tr = np.maximum(high_low, np.maximum(high_close, low_close))

        # Directional Movement
        up_move = highs - np.roll(highs, 1)
        down_move = np.roll(lows, 1) - lows

        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)

        # Smoothed ATR and DM
        atr = np.zeros_like(tr)
        atr[period] = np.mean(tr[: period + 1])

        for i in range(period + 1, len(tr)):
            atr[i] = (atr[i - 1] * (period - 1) + tr[i]) / period

        # Calculate DI
        plus_di = 100 * (plus_dm / (atr + 1e-10))
        minus_di = 100 * (minus_dm / (atr + 1e-10))

        # Calculate DX
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di + 1e-10)

        # Calculate ADX
        adx = np.zeros_like(dx)
        adx[period * 2] = np.mean(dx[period : period * 2 + 1])

        for i in range(period * 2 + 1, len(dx)):
            adx[i] = (adx[i - 1] * (period - 1) + dx[i]) / period

        # Pad beginning
        adx[: period * 2] = 0

        return adx

    def _calculate_keltner(
        self, ema_period: int, atr_mult: float
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Calculate Keltner Channels."""
        ema = self._calculate_ema(ema_period)
        atr = self._calculate_atr(14)  # Standard ATR period

        upper = ema + (atr * atr_mult)
        lower = ema - (atr * atr_mult)

        return upper, ema, lower


# Mock config
class MockConfig:
    ema_period = 20
    atr_period = 14
    adx_period = 14
    keltner_period = 20
    keltner_mult = 2.5


# Pytest Fixtures
@pytest.fixture
def config():
    """Basic config for testing."""
    return MockConfig()


@pytest.fixture
def indicators(config):
    """Indicators instance."""
    return Indicators(config)


@pytest.fixture
def sample_bars():
    """Generate sample bar data for testing."""
    bars = []
    for i in range(100):
        # Simple sine wave price action
        price = 18500 + np.sin(i / 10) * 100
        bars.append(
            {
                "timestamp": datetime(2024, 1, 1) + timedelta(minutes=i * 2),
                "open": price,
                "high": price + 10,
                "low": price - 10,
                "close": price,
                "volume": 1000 + i * 10,
            }
        )
    return bars


@pytest.fixture
def trending_bars():
    """Generate trending market data."""
    bars = []
    for i in range(100):
        price = 18500 + i * 5  # Uptrend
        bars.append(
            {
                "timestamp": datetime(2024, 1, 1) + timedelta(minutes=i * 2),
                "open": price,
                "high": price + 10,
                "low": price - 5,
                "close": price + 2,
                "volume": 1000,
            }
        )
    return bars


@pytest.fixture
def ranging_bars():
    """Generate ranging market data."""
    bars = []
    for i in range(100):
        price = 18500 + (i % 20 - 10) * 5  # Oscillating
        bars.append(
            {
                "timestamp": datetime(2024, 1, 1) + timedelta(minutes=i * 2),
                "open": price,
                "high": price + 5,
                "low": price - 5,
                "close": price,
                "volume": 1000,
            }
        )
    return bars


# Unit Tests
@pytest.mark.unit
class TestEMA:
    """Test EMA calculation."""

    def test_ema_length(self, indicators, sample_bars):
        """Test EMA array has correct length."""
        indicators.bars = sample_bars
        ema = indicators._calculate_ema(period=20)

        assert len(ema) == len(sample_bars)

    def test_ema_warmup_period(self, indicators, sample_bars):
        """Test EMA is NaN during warmup period."""
        indicators.bars = sample_bars
        ema = indicators._calculate_ema(period=20)

        # First 19 values should be NaN
        assert all(np.isnan(ema[:19]))

        # 20th value and beyond should not be NaN
        assert all(~np.isnan(ema[20:]))

    def test_ema_uptrend_values(self, indicators, trending_bars):
        """Test EMA increases in uptrend."""
        indicators.bars = trending_bars
        ema = indicators._calculate_ema(period=20)

        # EMA should be increasing in uptrend
        # Check last 20 values
        assert ema[-1] > ema[-20]

    def test_ema_calculation_accuracy(self, indicators):
        """Test EMA calculation against known values."""
        # Simple test case with known EMA values
        test_bars = [
            {"close": 10, "high": 11, "low": 9, "timestamp": datetime(2024, 1, 1)},
            {"close": 11, "high": 12, "low": 10, "timestamp": datetime(2024, 1, 2)},
            {"close": 12, "high": 13, "low": 11, "timestamp": datetime(2024, 1, 3)},
            {"close": 11, "high": 12, "low": 10, "timestamp": datetime(2024, 1, 4)},
            {"close": 10, "high": 11, "low": 9, "timestamp": datetime(2024, 1, 5)},
        ]

        indicators.bars = test_bars
        ema = indicators._calculate_ema(period=3)

        # After warmup, EMA should be reasonable
        assert ema[2] > 0  # First valid EMA
        assert abs(ema[2] - 11.0) < 1.0  # Approximate SMA for first value


@pytest.mark.unit
class TestATR:
    """Test ATR calculation."""

    def test_atr_positive(self, indicators, sample_bars):
        """Test ATR is always positive."""
        indicators.bars = sample_bars
        atr = indicators._calculate_atr(period=14)

        # ATR should be positive after warmup
        assert all(atr[14:] > 0)

    def test_atr_length(self, indicators, sample_bars):
        """Test ATR array has correct length."""
        indicators.bars = sample_bars
        atr = indicators._calculate_atr(period=14)

        assert len(atr) == len(sample_bars)

    def test_atr_volatile_market(self, indicators):
        """Test ATR increases in volatile market."""
        # Create high volatility bars
        volatile_bars = []
        for i in range(50):
            price = 18500 + np.random.randint(-50, 50)
            volatile_bars.append(
                {
                    "timestamp": datetime(2024, 1, 1) + timedelta(minutes=i * 2),
                    "open": price,
                    "high": price + 30,
                    "low": price - 30,
                    "close": price + 10,
                    "volume": 1000,
                }
            )

        indicators.bars = volatile_bars
        atr_volatile = indicators._calculate_atr(period=14)

        # Create low volatility bars
        calm_bars = []
        for i in range(50):
            price = 18500
            calm_bars.append(
                {
                    "timestamp": datetime(2024, 1, 1) + timedelta(minutes=i * 2),
                    "open": price,
                    "high": price + 2,
                    "low": price - 2,
                    "close": price + 1,
                    "volume": 1000,
                }
            )

        indicators.bars = calm_bars
        atr_calm = indicators._calculate_atr(period=14)

        # Volatile ATR should be higher
        assert atr_volatile[-1] > atr_calm[-1]


@pytest.mark.unit
class TestADX:
    """Test ADX calculation."""

    def test_adx_range(self, indicators, sample_bars):
        """Test ADX is between 0 and 100."""
        indicators.bars = sample_bars
        adx = indicators._calculate_adx(period=14)

        # ADX should be 0-100 after warmup
        valid_adx = adx[28:]  # After 2 * period
        assert all(valid_adx >= 0)
        assert all(valid_adx <= 100)

    def test_adx_trending_market(self, indicators, trending_bars):
        """Test ADX is high in strong trend."""
        indicators.bars = trending_bars
        adx = indicators._calculate_adx(period=14)

        # ADX should be elevated in strong trend
        # Last 10 values should average > 25
        assert np.mean(adx[-10:]) > 25

    def test_adx_ranging_market(self, indicators, ranging_bars):
        """Test ADX is low in ranging market."""
        indicators.bars = ranging_bars
        adx = indicators._calculate_adx(period=14)

        # ADX should be lower in range
        # Last 10 values should average < 30
        assert np.mean(adx[-10:]) < 30


@pytest.mark.unit
class TestKeltner:
    """Test Keltner Channels calculation."""

    def test_keltner_band_relationship(self, indicators, sample_bars):
        """Test upper > middle > lower."""
        indicators.bars = sample_bars
        indicators.update(sample_bars)

        curr = indicators.get_bar(-1)

        assert curr["upper_band"] > curr["middle_band"]
        assert curr["middle_band"] > curr["lower_band"]

    def test_keltner_width_scales_with_atr(self, indicators):
        """Test band width increases with ATR."""
        # High ATR bars
        high_atr_bars = []
        for i in range(50):
            price = 18500 + np.random.randint(-100, 100)
            high_atr_bars.append(
                {
                    "timestamp": datetime(2024, 1, 1) + timedelta(minutes=i * 2),
                    "open": price,
                    "high": price + 50,
                    "low": price - 50,
                    "close": price,
                    "volume": 1000,
                }
            )

        indicators.bars = high_atr_bars
        indicators.update(high_atr_bars)
        curr_high_atr = indicators.get_bar(-1)
        width_high_atr = curr_high_atr["upper_band"] - curr_high_atr["lower_band"]

        # Low ATR bars
        low_atr_bars = []
        for i in range(50):
            price = 18500
            low_atr_bars.append(
                {
                    "timestamp": datetime(2024, 1, 1) + timedelta(minutes=i * 2),
                    "open": price,
                    "high": price + 2,
                    "low": price - 2,
                    "close": price,
                    "volume": 1000,
                }
            )

        indicators.bars = low_atr_bars
        indicators.update(low_atr_bars)
        curr_low_atr = indicators.get_bar(-1)
        width_low_atr = curr_low_atr["upper_band"] - curr_low_atr["lower_band"]

        # High ATR should have wider bands
        assert width_high_atr > width_low_atr


@pytest.mark.integration
class TestIndicatorUpdate:
    """Test full indicator update process."""

    def test_update_all_indicators(self, indicators, sample_bars):
        """Test all indicators calculated correctly."""
        indicators.update(sample_bars)

        curr = indicators.get_bar(-1)

        # All indicators should be present
        assert "ema" in curr
        assert "atr" in curr
        assert "adx" in curr
        assert "upper_band" in curr
        assert "middle_band" in curr
        assert "lower_band" in curr

        # All should be valid numbers (not NaN)
        assert not np.isnan(curr["ema"])
        assert not np.isnan(curr["atr"])
        assert not np.isnan(curr["adx"])

    def test_update_idempotent(self, indicators, sample_bars):
        """Test multiple updates produce same results."""
        indicators.update(sample_bars)
        first = indicators.get_bar(-1).copy()

        # Update again
        indicators.update(sample_bars)
        second = indicators.get_bar(-1)

        # Results should be identical
        assert first["ema"] == second["ema"]
        assert first["atr"] == second["atr"]
        assert first["adx"] == second["adx"]


# Run tests with coverage
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=.", "--cov-report=html"])
