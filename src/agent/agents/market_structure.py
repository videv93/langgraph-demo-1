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
                    Expected keys: instrument, timeframe, lookback_periods,
                    current_price, price_history, market_data, hummingbot_client
        """
        self.config = config or {}
        self.instrument = self.config.get("instrument", "ETH-USDT")
        self.timeframe = self.config.get("timeframe", "4H")
        self.lookback_periods = self.config.get("lookback_periods", 100)
        self.base_price = self.config.get("base_price")
        self.current_price = self.config.get("current_price", 0.0)
        self.price_history = self.config.get("price_history", [])
        self.market_data = self.config.get("market_data", {})
        self.hummingbot_client = self.config.get("hummingbot_client")

    def execute(self) -> MarketStructureOutput:
        """Execute market structure analysis using real price data from Hummingbot.

        Returns:
            MarketStructureOutput with identified structure and levels.
        """
        from datetime import datetime

        # Extract real price history from Hummingbot
        price_history = []
        if self.price_history:
            price_history = [
                float(candle.get("close", 0))
                if isinstance(candle, dict)
                else float(candle)
                for candle in self.price_history
            ]

        # Use real current price from Hummingbot
        current_price = self.current_price if self.current_price > 0 else 0.0

        # Analyze trend direction
        trend = self._analyze_trend(price_history)

        # Identify support and resistance levels
        support, resistance = self._identify_support_resistance(price_history, current_price)

        # Assess market volatility
        volatility = self._assess_volatility(price_history)

        # Identify key price levels
        key_levels = self._identify_key_levels(support, resistance)

        return {
            "analysis_complete": bool(price_history and current_price > 0),
            "trend_direction": trend,
            "current_price": current_price,
            "support_level": support,
            "resistance_level": resistance,
            "market_volatility": volatility,
            "key_price_levels": key_levels,
            "price_history": price_history,
            "analysis_timestamp": datetime.utcnow().isoformat(),
        }

    def _analyze_trend(self, price_history: list[float]) -> TrendDirection:
        """Determine the current market trend direction from price history.

        Args:
            price_history: List of historical prices.

        Returns:
            TrendDirection indicating uptrend, downtrend, sideways, or unknown.
        """
        if len(price_history) < 10:
            return TrendDirection.UNKNOWN

        # Use different timeframes for trend analysis
        short_period = min(10, len(price_history))
        medium_period = min(25, len(price_history))

        # Calculate simple moving averages
        short_avg = sum(price_history[-short_period:]) / short_period
        medium_avg = sum(price_history[-medium_period:]) / medium_period
        
        current_price = price_history[-1]

        # Determine trend based on price position relative to moving averages
        if current_price > short_avg > medium_avg:
            return TrendDirection.UPTREND
        elif current_price < short_avg < medium_avg:
            return TrendDirection.DOWNTREND
        else:
            return TrendDirection.SIDEWAYS

    def _identify_support_resistance(
        self, price_history: list[float], current_price: float = 0.0
    ) -> tuple[float, float]:
        """Identify support and resistance price levels from real price data.

        Args:
            price_history: List of historical prices.
            current_price: Current price for reference.

        Returns:
            Tuple of (support_level, resistance_level).
        """
        if not price_history:
            return 0.0, 0.0

        # Use last 100 candles for more recent support/resistance
        lookback = min(100, len(price_history))
        recent_prices = price_history[-lookback:]
        
        min_price = min(recent_prices)
        max_price = max(recent_prices)

        # Calculate support and resistance with dynamic margins
        price_range = max_price - min_price
        margin = max(0.005, price_range * 0.01)  # At least 0.5% or 1% of range
        
        support = round(min_price - margin, 2)
        resistance = round(max_price + margin, 2)

        return support, resistance

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
