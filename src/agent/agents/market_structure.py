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
                    current_price, price_df (pandas DataFrame with OHLC data),
                    min_swing_bars, sr_zone_thickness_pct
        """
        self.config = config or {}
        self.timeframe = self.config.get("timeframe", "4H")
        self.instrument = self.config.get("instrument", "ETH-USDT")
        self.lookback_periods = self.config.get("lookback_periods", 100)
        self.current_price = self.config.get("current_price", 0.0)
        self.price_df = self._build_dataframe()
        self.min_swing_bars = self.config.get("min_swing_bars", 3)
        self.sr_zone_thickness_pct = self.config.get("sr_zone_thickness_pct", 0.5)

    def _build_dataframe(self) -> pd.DataFrame:
        """Build pandas DataFrame from config price data.

        Accepts either a pre-built DataFrame or raw OHLC data and converts it.

        Returns:
            pandas DataFrame with columns: open, high, low, close
        """
        # If price_df already provided, use it
        if "price_df" in self.config and isinstance(self.config["price_df"], pd.DataFrame):
            df = self.config["price_df"].copy()
        else:
            # Build from ohlc_data (legacy support)
            ohlc_data = self.config.get("ohlc_data", [])
            if not ohlc_data:
                return pd.DataFrame(columns=["open", "high", "low", "close"])

            data = []
            for candle in ohlc_data:
                if isinstance(candle, dict):
                    data.append({
                        "open": float(candle.get("open", 0)),
                        "high": float(candle.get("high", 0)),
                        "low": float(candle.get("low", 0)),
                        "close": float(candle.get("close", 0)),
                    })
                elif isinstance(candle, (list, tuple)) and len(candle) >= 4:
                    data.append({
                        "open": float(candle[0]),
                        "high": float(candle[1]),
                        "low": float(candle[2]),
                        "close": float(candle[3]),
                    })

            df = pd.DataFrame(data)

        # Ensure required columns exist
        for col in ["high", "low", "close"]:
            if col not in df.columns:
                df[col] = 0.0

        return df.astype({"open": float, "high": float, "low": float, "close": float})

    def execute(self) -> MarketStructureOutput:
        """Execute market structure analysis.

        Returns:
            MarketStructureOutput with structural framework and current context.
        """
        if self.price_df.empty or self.current_price <= 0:
            return self._empty_output()

        # Detect swing points using scipy
        swing_highs, swing_lows = self._detect_swing_points()

        # Analyze trend structure using YTC swing analysis methodology
        trend_structure = self._analyze_trend_structure()

        # Identify support and resistance zones
        support_zones = self._calculate_zones(swing_lows, "support")
        resistance_zones = self._calculate_zones(swing_highs, "resistance")

        # Get prior session levels
        prior_session = self._get_prior_session_levels()

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

    def _detect_swing_points(self) -> tuple[list[dict], list[dict]]:
        """Detect swing highs and lows using scipy.signal.argrelextrema.

        Returns:
            Tuple of (swing_highs, swing_lows) as list of dicts.
        """
        if len(self.price_df) < self.min_swing_bars * 2 + 1:
            return [], []

        highs_array = self.price_df["high"].values.astype(np.float64)
        lows_array = self.price_df["low"].values.astype(np.float64)

        # Find local maxima and minima
        swing_high_indices = argrelextrema(
            highs_array, np.greater, order=self.min_swing_bars
        )[0]
        swing_low_indices = argrelextrema(
            lows_array, np.less, order=self.min_swing_bars
        )[0]

        swing_highs = [
            {
                "index": int(idx),
                "price": float(highs_array[idx]),
            }
            for idx in swing_high_indices
        ]

        swing_lows = [
            {
                "index": int(idx),
                "price": float(lows_array[idx]),
            }
            for idx in swing_low_indices
        ]

        return swing_highs, swing_lows

    def _analyze_trend_structure(self) -> TrendDirection:
        """Determine trend structure using YTC swing analysis methodology.

        Classifies trend based on swing patterns:
        - Uptrend: Series of higher highs (HH) and higher lows (HL)
        - Downtrend: Series of lower highs (LH) and lower lows (LL)
        - Sideways: No clear directional pattern

        Returns:
            TrendDirection enum value (UPTREND, DOWNTREND, or SIDEWAYS).
        """
        if len(self.price_df) < 5:
            return TrendDirection.SIDEWAYS

        # Detect swing points
        swing_highs, swing_lows = self._detect_swing_points()

        if len(swing_highs) < 2 or len(swing_lows) < 2:
            return TrendDirection.SIDEWAYS

        # Check for uptrend pattern: HH and HL
        uptrend_pattern = False
        downtrend_pattern = False

        # Get last two swing highs and lows
        last_sh = swing_highs[-1]["price"]
        prev_sh = swing_highs[-2]["price"]
        last_sl = swing_lows[-1]["price"]
        prev_sl = swing_lows[-2]["price"]

        # Uptrend: HH and HL
        if last_sh > prev_sh and last_sl > prev_sl:
            uptrend_pattern = True

        # Downtrend: LH and LL
        if last_sh < prev_sh and last_sl < prev_sl:
            downtrend_pattern = True

        # Determine trend direction
        if uptrend_pattern:
            return TrendDirection.UPTREND
        elif downtrend_pattern:
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

            zones.append(
                {
                    "level": round(level, 2),
                    "strength": strength,
                    "type": f"swing_{zone_type[:-1]}",  # swing_support or swing_resistance
                    "touches": touches,
                    "zone_range": [
                        round(level - zone_thickness, 2),
                        round(level + zone_thickness, 2),
                    ],
                }
            )

        return sorted(zones, key=lambda z: z["level"])

    def _count_touches(self, level: float, thickness: float) -> int:
        """Count how many times price touched a zone.

        Args:
            level: Zone center level.
            thickness: Zone half-width.

        Returns:
            Number of touches.
        """
        if self.price_df.empty:
            return 0

        # Vectorized comparison using pandas
        touches = (
            (self.price_df["close"] >= level - thickness) &
            (self.price_df["close"] <= level + thickness)
        ).sum()

        return int(touches)

    def _get_prior_session_levels(self) -> dict[str, float]:
        """Get prior session's high, low, and close.

        Returns:
            Dict with prior_high, prior_low, prior_close.
        """
        if len(self.price_df) < 2:
            return {"high": 0.0, "low": 0.0, "close": 0.0}

        # Use previous candle as "prior session"
        prior = self.price_df.iloc[-2]
        return {
            "high": round(float(prior["high"]), 2),
            "low": round(float(prior["low"]), 2),
            "close": round(float(prior["close"]), 2),
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

    def calculate_indicators(self) -> dict[str, float]:
        """Calculate additional technical indicators using talib.

        Returns:
            Dict with indicator values (RSI, MACD, Bollinger Bands).
        """
        if len(self.price_df) < 14:
            return {}

        close_array = self.price_df["close"].values.astype(np.float64)

        indicators = {}

        # RSI
        rsi = talib.RSI(close_array, timeperiod=14)
        if not np.isnan(rsi[-1]):
            indicators["rsi"] = float(rsi[-1])

        # MACD
        macd, signal, hist = talib.MACD(
            close_array, fastperiod=12, slowperiod=26, signalperiod=9
        )
        if not np.isnan(macd[-1]):
            indicators["macd"] = float(macd[-1])
            indicators["macd_signal"] = float(signal[-1])
            indicators["macd_histogram"] = float(hist[-1])

        # Bollinger Bands
        upper, middle, lower = talib.BBANDS(
            close_array, timeperiod=20, nbdevup=2, nbdevdn=2
        )
        if not np.isnan(upper[-1]):
            indicators["bb_upper"] = float(upper[-1])
            indicators["bb_middle"] = float(middle[-1])
            indicators["bb_lower"] = float(lower[-1])

        return indicators
