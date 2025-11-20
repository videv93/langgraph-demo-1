"""Market structure analysis agent for identifying support/resistance and key levels."""

from datetime import datetime
from enum import Enum
from typing import Any, TypedDict
import numpy as np
import pandas as pd
import talib
from scipy.signal import argrelextrema


class TrendDirection(str, Enum):
    """Market trend direction."""

    UPTREND = "uptrend"
    DOWNTREND = "downtrend"
    SIDEWAYS = "sideways"


class SRZone(TypedDict):
    """Support/Resistance zone definition."""

    level: float
    strength: int
    type: str
    touches: int
    zone_range: list[float]


class StructuralFramework(TypedDict):
    """Market structural framework."""

    trend_structure: TrendDirection
    resistance_zones: list[SRZone]
    support_zones: list[SRZone]
    prior_session: dict[str, float]


class CurrentContext(TypedDict):
    """Current price context relative to structure."""

    price_location: str
    nearest_resistance: float
    nearest_support: float
    distance_to_resistance_pct: float
    distance_to_support_pct: float


class MarketStructureOutput(TypedDict):
    """Output from market structure analysis."""

    analysis_complete: bool
    structural_framework: StructuralFramework
    current_context: CurrentContext
    analysis_timestamp: str


class MarketStructure:
    """Analyze market structure to identify support/resistance zones and trends.

    Implements YTC's multiple timeframe analysis approach with:
    - Swing point detection using scipy.signal.argrelextrema
    - Support/resistance zone identification with strength scoring
    - Trend structure classification
    - Prior session level tracking
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the market structure agent.

        Args:
            config: Optional configuration with market parameters.
                    Expected keys: instrument, timeframe, lookback_periods,
                    current_price, ohlc_data, min_swing_bars, sr_zone_thickness_pct
        """
        self.config = config or {}
        self.instrument = self.config.get("instrument", "ETH-USDT")
        self.timeframe = self.config.get("timeframe", "30m")
        self.lookback_periods = self.config.get("lookback_periods", 100)
        self.current_price = self.config.get("current_price", 0.0)
        self.ohlc_data = self.config.get("ohlc_data", [])
        self.min_swing_bars = self.config.get("min_swing_bars", 3)
        self.sr_zone_thickness_pct = self.config.get("sr_zone_thickness_pct", 0.5)

    def execute(self) -> MarketStructureOutput:
        """Execute market structure analysis.

        Returns:
            MarketStructureOutput with structural framework and current context.
        """
        # Extract price data from OHLC
        highs, lows, closes = self._extract_price_data()

        if not closes or self.current_price <= 0:
            return self._empty_output()

        # Detect swing points using scipy
        swing_highs, swing_lows = self._detect_swing_points(highs, lows)

        # Analyze trend structure
        trend_structure = self._analyze_trend_structure(closes)

        # Identify support and resistance zones
        support_zones = self._calculate_zones(swing_lows, "support")
        resistance_zones = self._calculate_zones(swing_highs, "resistance")

        # Get prior session levels
        prior_session = self._get_prior_session_levels(highs, lows, closes)

        # Calculate current context
        current_context = self._calculate_current_context(
            support_zones, resistance_zones
        )

        return {
            "analysis_complete": True,
            "structural_framework": {
                "trend_structure": trend_structure,
                "resistance_zones": resistance_zones,
                "support_zones": support_zones,
                "prior_session": prior_session,
            },
            "current_context": current_context,
            "analysis_timestamp": datetime.utcnow().isoformat(),
        }

    def _extract_price_data(self) -> tuple[list[float], list[float], list[float]]:
        """Extract OHLC data from config.

        Returns:
            Tuple of (highs, lows, closes) as float lists.
        """
        highs = []
        lows = []
        closes = []

        for candle in self.ohlc_data:
            if isinstance(candle, dict):
                highs.append(float(candle.get("high", 0)))
                lows.append(float(candle.get("low", 0)))
                closes.append(float(candle.get("close", 0)))
            else:
                # Handle array-like structure [o, h, l, c, v]
                if len(candle) >= 4:
                    highs.append(float(candle[1]))
                    lows.append(float(candle[2]))
                    closes.append(float(candle[3]))

        return highs, lows, closes

    def _detect_swing_points(
        self, highs: list[float], lows: list[float]
    ) -> tuple[list[dict], list[dict]]:
        """Detect swing highs and lows using scipy.signal.argrelextrema.

        Args:
            highs: List of high prices.
            lows: List of low prices.

        Returns:
            Tuple of (swing_highs, swing_lows) as list of dicts.
        """
        if len(highs) < self.min_swing_bars * 2 + 1:
            return [], []

        highs_array = np.array(highs)
        lows_array = np.array(lows)

        # Find local maxima and minima
        swing_high_indices = argrelextrema(highs_array, np.greater, order=self.min_swing_bars)[0]
        swing_low_indices = argrelextrema(lows_array, np.less, order=self.min_swing_bars)[0]

        swing_highs = [
            {
                "index": int(idx),
                "price": float(highs[idx]),
            }
            for idx in swing_high_indices
        ]

        swing_lows = [
            {
                "index": int(idx),
                "price": float(lows[idx]),
            }
            for idx in swing_low_indices
        ]

        return swing_highs, swing_lows

    def _analyze_trend_structure(self, closes: list[float]) -> TrendDirection:
        """Determine trend structure from price action using talib SMA.

        Args:
            closes: List of closing prices.

        Returns:
            TrendDirection enum value.
        """
        if len(closes) < 25:
            return TrendDirection.SIDEWAYS

        close_array = np.array(closes, dtype=np.float64)

        # Calculate moving averages using talib
        short_ma = talib.SMA(close_array, timeperiod=10)
        medium_ma = talib.SMA(close_array, timeperiod=25)

        current = closes[-1]
        short_ma_current = short_ma[-1]
        medium_ma_current = medium_ma[-1]

        if current > short_ma_current > medium_ma_current:
            return TrendDirection.UPTREND
        elif current < short_ma_current < medium_ma_current:
            return TrendDirection.DOWNTREND
        else:
            return TrendDirection.SIDEWAYS

    def _calculate_zones(
        self, swing_points: list[dict], zone_type: str
    ) -> list[SRZone]:
        """Calculate support/resistance zones from swing points.

        Args:
            swing_points: List of swing point dicts.
            zone_type: "support" or "resistance".

        Returns:
            List of SRZone dicts with strength scoring.
        """
        if not swing_points:
            return []

        zones = []
        for point in swing_points[-5:]:  # Use last 5 swing points
            level = point["price"]
            zone_thickness = level * (self.sr_zone_thickness_pct / 100)

            # Calculate strength based on price proximity
            touches = self._count_touches(level, zone_thickness)
            strength = min(10, 3 + touches)  # Base 3, +1 per touch, max 10

            zones.append({
                "level": round(level, 2),
                "strength": strength,
                "type": f"swing_{zone_type[:-1]}",  # swing_support or swing_resistance
                "touches": touches,
                "zone_range": [
                    round(level - zone_thickness, 2),
                    round(level + zone_thickness, 2),
                ],
            })

        return sorted(zones, key=lambda z: z["level"])

    def _count_touches(self, level: float, thickness: float) -> int:
        """Count how many times price touched a zone using pandas.

        Args:
            level: Zone center level.
            thickness: Zone half-width.

        Returns:
            Number of touches.
        """
        if not self.ohlc_data:
            return 0

        closes = [
            float(c.get("close", 0) if isinstance(c, dict) else c[3])
            for c in self.ohlc_data
        ]

        # Convert to pandas Series for vectorized comparison
        close_series = pd.Series(closes)
        touches = ((close_series >= level - thickness) & 
                   (close_series <= level + thickness)).sum()

        return int(touches)

    def _get_prior_session_levels(
        self, highs: list[float], lows: list[float], closes: list[float]
    ) -> dict[str, float]:
        """Get prior session's high, low, and close.

        Args:
            highs: List of high prices.
            lows: List of low prices.
            closes: List of close prices.

        Returns:
            Dict with prior_high, prior_low, prior_close.
        """
        if len(closes) < 2:
            return {"high": 0.0, "low": 0.0, "close": 0.0}

        # Use previous candle as "prior session"
        return {
            "high": round(highs[-2], 2) if len(highs) >= 2 else 0.0,
            "low": round(lows[-2], 2) if len(lows) >= 2 else 0.0,
            "close": round(closes[-2], 2) if len(closes) >= 2 else 0.0,
        }

    def _calculate_current_context(
        self, support_zones: list[SRZone], resistance_zones: list[SRZone]
    ) -> CurrentContext:
        """Calculate current price context relative to structure.

        Args:
            support_zones: List of support zones.
            resistance_zones: List of resistance zones.

        Returns:
            CurrentContext dict with price location and distances.
        """
        nearest_support = support_zones[-1]["level"] if support_zones else 0.0
        nearest_resistance = resistance_zones[0]["level"] if resistance_zones else 0.0

        dist_to_resist_pct = (
            ((nearest_resistance - self.current_price) / self.current_price * 100)
            if self.current_price > 0 and nearest_resistance > 0
            else 0.0
        )

        dist_to_support_pct = (
            ((self.current_price - nearest_support) / self.current_price * 100)
            if self.current_price > 0 and nearest_support > 0
            else 0.0
        )

        # Determine price location
        if nearest_resistance > 0 and self.current_price >= nearest_resistance * 0.99:
            price_location = "at_resistance"
        elif nearest_support > 0 and self.current_price <= nearest_support * 1.01:
            price_location = "at_support"
        elif nearest_support > 0 and nearest_resistance > 0:
            price_location = "in_range"
        else:
            price_location = "breakout"

        return {
            "price_location": price_location,
            "nearest_resistance": round(nearest_resistance, 2),
            "nearest_support": round(nearest_support, 2),
            "distance_to_resistance_pct": round(dist_to_resist_pct, 2),
            "distance_to_support_pct": round(dist_to_support_pct, 2),
        }

    def _empty_output(self) -> MarketStructureOutput:
        """Return empty output when analysis cannot be completed.

        Returns:
            MarketStructureOutput with empty/default values.
        """
        return {
            "analysis_complete": False,
            "structural_framework": {
                "trend_structure": TrendDirection.SIDEWAYS,
                "resistance_zones": [],
                "support_zones": [],
                "prior_session": {"high": 0.0, "low": 0.0, "close": 0.0},
            },
            "current_context": {
                "price_location": "unknown",
                "nearest_resistance": 0.0,
                "nearest_support": 0.0,
                "distance_to_resistance_pct": 0.0,
                "distance_to_support_pct": 0.0,
            },
            "analysis_timestamp": datetime.utcnow().isoformat(),
        }

    def calculate_indicators(self, closes: list[float]) -> dict[str, float]:
        """Calculate additional technical indicators using talib.

        Args:
            closes: List of closing prices.

        Returns:
            Dict with indicator values (RSI, MACD, Bollinger Bands).
        """
        if len(closes) < 14:
            return {}

        close_array = np.array(closes, dtype=np.float64)

        indicators = {}

        # RSI
        rsi = talib.RSI(close_array, timeperiod=14)
        if not np.isnan(rsi[-1]):
            indicators["rsi"] = float(rsi[-1])

        # MACD
        macd, signal, hist = talib.MACD(close_array, fastperiod=12, slowperiod=26, signalperiod=9)
        if not np.isnan(macd[-1]):
            indicators["macd"] = float(macd[-1])
            indicators["macd_signal"] = float(signal[-1])
            indicators["macd_histogram"] = float(hist[-1])

        # Bollinger Bands
        upper, middle, lower = talib.BBANDS(close_array, timeperiod=20, nbdevup=2, nbdevdn=2)
        if not np.isnan(upper[-1]):
            indicators["bb_upper"] = float(upper[-1])
            indicators["bb_middle"] = float(middle[-1])
            indicators["bb_lower"] = float(lower[-1])

        return indicators
