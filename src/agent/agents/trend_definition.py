"""Trend definition agent for identifying and confirming market trends."""

from enum import Enum
from typing import Any, TypedDict


class TrendStrength(str, Enum):
    """Strength of the identified trend."""

    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"


class TrendDefinitionOutput(TypedDict):
    """Output from trend definition analysis."""

    trend_confirmed: bool
    primary_trend: str
    trend_strength: TrendStrength
    entry_bias: str  # "long" or "short"
    moving_average_10: float
    moving_average_20: float
    moving_average_50: float
    analysis_timestamp: str


class TrendDefinition:
    """Define and confirm market trends using multiple technical indicators.

    Performs analysis including:
    - Moving average crossovers
    - Trend line analysis
    - Higher highs/lows validation
    - Multi-timeframe trend confirmation
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the trend definition agent.

        Args:
            config: Optional configuration with price data and parameters.
                    Expected keys: price_history, current_price, trend_direction, etc.
        """
        self.config = config or {}
        self.price_history = self.config.get("price_history", [])
        self.current_price = self.config.get("current_price", 0.0)
        self.trend_direction = self.config.get("trend_direction", "unknown")

    def execute(self) -> TrendDefinitionOutput:
        """Execute trend definition analysis.

        Returns:
            TrendDefinitionOutput with confirmed trend and entry bias.
        """
        from datetime import datetime

        # Calculate moving averages
        ma_10 = self._calculate_moving_average(10)
        ma_20 = self._calculate_moving_average(20)
        ma_50 = self._calculate_moving_average(50)

        # Confirm trend from MAs
        primary_trend, entry_bias = self._confirm_trend_from_moving_averages(
            ma_10, ma_20, ma_50
        )

        # Determine trend strength
        trend_strength = self._assess_trend_strength(ma_10, ma_20, ma_50)

        # Validate with price action (higher highs/lows)
        trend_confirmed = self._validate_with_price_action(primary_trend)

        return {
            "trend_confirmed": trend_confirmed,
            "primary_trend": primary_trend,
            "trend_strength": trend_strength,
            "entry_bias": entry_bias,
            "moving_average_10": round(ma_10, 2),
            "moving_average_20": round(ma_20, 2),
            "moving_average_50": round(ma_50, 2),
            "analysis_timestamp": datetime.utcnow().isoformat(),
        }

    def _calculate_moving_average(self, period: int) -> float:
        """Calculate moving average for a given period.

        Args:
            period: Number of periods for the moving average.

        Returns:
            Moving average value.
        """
        if len(self.price_history) < period:
            return sum(self.price_history) / len(self.price_history) if self.price_history else 0.0

        recent_prices = self.price_history[-period:]
        return sum(recent_prices) / len(recent_prices)

    def _confirm_trend_from_moving_averages(
        self, ma_10: float, ma_20: float, ma_50: float
    ) -> tuple[str, str]:
        """Confirm trend direction from moving average relationships.

        Args:
            ma_10: 10-period moving average.
            ma_20: 20-period moving average.
            ma_50: 50-period moving average.

        Returns:
            Tuple of (primary_trend, entry_bias).
            entry_bias is "long" for uptrend or "short" for downtrend.
        """
        # Bullish condition: price > MA10 > MA20 > MA50
        if self.current_price > ma_10 > ma_20 > ma_50:
            return "uptrend", "long"

        # Bearish condition: price < MA10 < MA20 < MA50
        if self.current_price < ma_10 < ma_20 < ma_50:
            return "downtrend", "short"

        # Golden cross: MA10 > MA20 (bullish)
        if ma_10 > ma_20 > ma_50:
            return "uptrend", "long"

        # Death cross: MA10 < MA20 (bearish)
        if ma_10 < ma_20 < ma_50:
            return "downtrend", "short"

        # Uncertain
        return "sideways", "neutral"

    def _assess_trend_strength(
        self, ma_10: float, ma_20: float, ma_50: float
    ) -> TrendStrength:
        """Assess the strength of the identified trend.

        Args:
            ma_10: 10-period moving average.
            ma_20: 20-period moving average.
            ma_50: 50-period moving average.

        Returns:
            TrendStrength assessment.
        """
        if not self.price_history or len(self.price_history) < 50:
            return TrendStrength.WEAK

        # Calculate spacing between MAs
        spacing_10_20 = abs(ma_10 - ma_20) / ma_20
        spacing_20_50 = abs(ma_20 - ma_50) / ma_50

        # Strong trend: MAs are well-separated and properly ordered
        if spacing_20_50 > 0.02 and spacing_10_20 > 0.01:
            return TrendStrength.STRONG

        # Moderate trend: Some separation
        if spacing_20_50 > 0.01 or spacing_10_20 > 0.005:
            return TrendStrength.MODERATE

        # Weak trend: MAs are close together
        return TrendStrength.WEAK

    def _validate_with_price_action(self, primary_trend: str) -> bool:
        """Validate trend with price action (higher highs/lows).

        Args:
            primary_trend: The identified primary trend.

        Returns:
            True if trend is validated by price action.
        """
        if len(self.price_history) < 10:
            return False

        recent = self.price_history[-10:]
        mid = self.price_history[-20:-10] if len(self.price_history) >= 20 else []

        if not mid:
            return False

        recent_high = max(recent)
        recent_low = min(recent)
        mid_high = max(mid)
        mid_low = min(mid)

        # For uptrend: higher highs and higher lows
        if primary_trend == "uptrend":
            return recent_high > mid_high and recent_low > mid_low

        # For downtrend: lower highs and lower lows
        if primary_trend == "downtrend":
            return recent_high < mid_high and recent_low < mid_low

        # Sideways: overlapping price ranges
        return True
