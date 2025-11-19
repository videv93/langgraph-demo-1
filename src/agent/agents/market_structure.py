"""Market structure analysis agent for identifying support/resistance and key levels."""

import random
from enum import Enum
from typing import Any, TypedDict


class TrendDirection(str, Enum):
    """Market trend direction."""

    UPTREND = "uptrend"
    DOWNTREND = "downtrend"
    SIDEWAYS = "sideways"
    UNKNOWN = "unknown"


class MarketStructureOutput(TypedDict):
    """Output from market structure analysis."""

    analysis_complete: bool
    trend_direction: TrendDirection
    current_price: float
    support_level: float
    resistance_level: float
    market_volatility: str
    key_price_levels: list[float]
    price_history: list[float]
    analysis_timestamp: str


class MarketStructure:
    """Analyze market structure to identify key price levels and trends.

    Performs analysis including:
    - Support and resistance level identification
    - Trend direction determination
    - Volatility assessment
    - Key price level identification
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the market structure agent.

        Args:
            config: Optional configuration with market parameters.
                    Expected keys: instrument, timeframe, lookback_periods, etc.
        """
        self.config = config or {}
        self.instrument = self.config.get("instrument", "ETH-USDT")
        self.timeframe = self.config.get("timeframe", "1H")
        self.lookback_periods = self.config.get("lookback_periods", 100)
        # ETH-USDT reference levels
        self.base_price = self.config.get("base_price", 2500.0)

    def execute(self) -> MarketStructureOutput:
        """Execute market structure analysis.

        Returns:
            MarketStructureOutput with identified structure and levels.
        """
        from datetime import datetime

        # Generate mock price history
        price_history = self._generate_mock_prices()
        current_price = price_history[-1]

        # Analyze trend direction
        trend = self._analyze_trend(price_history)

        # Identify support and resistance levels
        support, resistance = self._identify_support_resistance(price_history)

        # Assess market volatility
        volatility = self._assess_volatility(price_history)

        # Identify key price levels
        key_levels = self._identify_key_levels(support, resistance)

        return {
            "analysis_complete": True,
            "trend_direction": trend,
            "current_price": current_price,
            "support_level": support,
            "resistance_level": resistance,
            "market_volatility": volatility,
            "key_price_levels": key_levels,
            "price_history": price_history,
            "analysis_timestamp": datetime.utcnow().isoformat(),
        }

    def _generate_mock_prices(self) -> list[float]:
        """Generate mock ETH-USDT price history.

        Returns:
            List of historical prices (lookback_periods length).
        """
        prices = [self.base_price]
        random.seed(42)  # For reproducibility

        for _ in range(self.lookback_periods - 1):
            # Generate realistic price movements (±2% per candle)
            change_percent = random.uniform(-2.0, 2.5)  # Slight upward bias
            new_price = prices[-1] * (1 + change_percent / 100.0)
            # Ensure price stays in realistic ETH-USDT range (1500-3500)
            new_price = max(1500.0, min(3500.0, new_price))
            prices.append(round(new_price, 2))

        return prices

    def _analyze_trend(self, price_history: list[float]) -> TrendDirection:
        """Determine the current market trend direction.

        Args:
            price_history: List of historical prices.

        Returns:
            TrendDirection indicating uptrend, downtrend, sideways, or unknown.
        """
        if len(price_history) < 20:
            return TrendDirection.UNKNOWN

        recent = price_history[-20:]
        early = price_history[-40:-20]

        recent_avg = sum(recent) / len(recent)
        early_avg = sum(early) / len(early)

        if recent_avg > early_avg * 1.01:
            return TrendDirection.UPTREND
        elif recent_avg < early_avg * 0.99:
            return TrendDirection.DOWNTREND
        else:
            return TrendDirection.SIDEWAYS

    def _identify_support_resistance(
        self, price_history: list[float]
    ) -> tuple[float, float]:
        """Identify support and resistance price levels.

        Args:
            price_history: List of historical prices.

        Returns:
            Tuple of (support_level, resistance_level).
        """
        if not price_history:
            return self.base_price * 0.95, self.base_price * 1.05

        min_price = min(price_history[-50:]) if len(price_history) >= 50 else min(price_history)
        max_price = max(price_history[-50:]) if len(price_history) >= 50 else max(price_history)

        # Add 2% margin for levels
        support = min_price * 0.98
        resistance = max_price * 1.02

        return round(support, 2), round(resistance, 2)

    def _assess_volatility(self, price_history: list[float]) -> str:
        """Assess current market volatility.

        Args:
            price_history: List of historical prices.

        Returns:
            Volatility assessment: "low", "medium", or "high".
        """
        if len(price_history) < 20:
            return "medium"

        recent_prices = price_history[-20:]
        avg_price = sum(recent_prices) / len(recent_prices)

        # Calculate percentage changes
        changes = []
        for i in range(1, len(recent_prices)):
            pct_change = abs((recent_prices[i] - recent_prices[i - 1]) / recent_prices[i - 1]) * 100
            changes.append(pct_change)

        avg_change = sum(changes) / len(changes) if changes else 0

        if avg_change < 0.8:
            return "low"
        elif avg_change > 1.5:
            return "high"
        else:
            return "medium"

    def _identify_key_levels(self, support: float, resistance: float) -> list[float]:
        """Identify key price levels for trading decisions.

        Args:
            support: Support price level.
            resistance: Resistance price level.

        Returns:
            List of key price levels.
        """
        # Placeholder: in production, calculate Fibonacci retracements,
        # pivot points, and other technical levels
        pivot = (support + resistance) / 2
        key_levels = [support, pivot, resistance]
        return sorted(key_levels)
