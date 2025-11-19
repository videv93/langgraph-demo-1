"""Strength and weakness analysis agent for identifying momentum and divergences."""

from typing import Any, TypedDict


class StrengthWeaknessOutput(TypedDict):
    """Output from strength and weakness analysis."""

    analysis_complete: bool
    momentum_direction: str  # "strong_up", "moderate_up", "weak", "moderate_down", "strong_down"
    rsi_value: float
    macd_signal: str  # "bullish_cross", "bearish_cross", "no_signal"
    divergence_detected: bool
    divergence_type: str  # "bullish", "bearish", or "none"
    overall_strength: str  # "strong", "moderate", "weak"
    trading_probability: float  # 0-100
    analysis_timestamp: str


class StrengthWeakness:
    """Analyze market strength and weakness using momentum indicators.

    Performs analysis including:
    - RSI (Relative Strength Index) calculation
    - MACD (Moving Average Convergence Divergence) analysis
    - Divergence detection (bullish/bearish)
    - Momentum assessment
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the strength and weakness agent.

        Args:
            config: Optional configuration with price and indicator parameters.
                    Expected keys: price_history, moving_averages, entry_bias, etc.
        """
        self.config = config or {}
        self.price_history = self.config.get("price_history", [])
        self.entry_bias = self.config.get("entry_bias", "neutral")
        self.current_price = self.config.get("current_price", 0.0)

    def execute(self) -> StrengthWeaknessOutput:
        """Execute strength and weakness analysis.

        Returns:
            StrengthWeaknessOutput with momentum and divergence data.
        """
        from datetime import datetime

        # Calculate RSI
        rsi = self._calculate_rsi(14)

        # Analyze MACD
        macd_signal = self._analyze_macd()

        # Detect divergences
        divergence_detected, divergence_type = self._detect_divergences(rsi)

        # Assess overall momentum
        momentum = self._assess_momentum(rsi, macd_signal)

        # Determine overall strength
        overall_strength = self._determine_overall_strength(rsi, momentum, divergence_detected)

        # Calculate trading probability
        trading_prob = self._calculate_trading_probability(
            rsi, momentum, divergence_detected, divergence_type
        )

        return {
            "analysis_complete": True,
            "momentum_direction": momentum,
            "rsi_value": round(rsi, 2),
            "macd_signal": macd_signal,
            "divergence_detected": divergence_detected,
            "divergence_type": divergence_type,
            "overall_strength": overall_strength,
            "trading_probability": round(trading_prob, 1),
            "analysis_timestamp": datetime.utcnow().isoformat(),
        }

    def _calculate_rsi(self, period: int = 14) -> float:
        """Calculate Relative Strength Index.

        Args:
            period: RSI period (default 14).

        Returns:
            RSI value (0-100).
        """
        if len(self.price_history) < period + 1:
            return 50.0  # Neutral when insufficient data

        # Calculate gains and losses
        deltas = []
        for i in range(1, len(self.price_history)):
            delta = self.price_history[i] - self.price_history[i - 1]
            deltas.append(delta)

        recent_deltas = deltas[-period:]
        gains = sum(max(d, 0) for d in recent_deltas)
        losses = sum(abs(min(d, 0)) for d in recent_deltas)

        if losses == 0:
            return 100.0 if gains > 0 else 50.0

        rs = gains / losses
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _analyze_macd(self) -> str:
        """Analyze MACD (Moving Average Convergence Divergence).

        Returns:
            MACD signal: "bullish_cross", "bearish_cross", or "no_signal".
        """
        if len(self.price_history) < 26:
            return "no_signal"

        # Calculate EMAs
        ema_12 = self._calculate_ema(12)
        ema_26 = self._calculate_ema(26)

        # Simple MACD line
        macd_line = ema_12 - ema_26

        # Check previous candle (need at least 27 prices)
        if len(self.price_history) < 27:
            return "no_signal"

        # Simplified: check if MACD crossed signal line
        # Bullish: positive and increasing
        # Bearish: negative and decreasing
        if macd_line > 0:
            return "bullish_cross"
        elif macd_line < 0:
            return "bearish_cross"
        else:
            return "no_signal"

    def _calculate_ema(self, period: int) -> float:
        """Calculate Exponential Moving Average.

        Args:
            period: EMA period.

        Returns:
            EMA value.
        """
        if len(self.price_history) < period:
            return sum(self.price_history) / len(self.price_history)

        multiplier = 2 / (period + 1)
        ema = sum(self.price_history[:period]) / period

        for price in self.price_history[period:]:
            ema = price * multiplier + ema * (1 - multiplier)

        return ema

    def _detect_divergences(self, rsi: float) -> tuple[bool, str]:
        """Detect bullish or bearish divergences.

        Args:
            rsi: Current RSI value.

        Returns:
            Tuple of (divergence_detected, divergence_type).
        """
        if len(self.price_history) < 20:
            return False, "none"

        # Simplified divergence detection
        recent_prices = self.price_history[-10:]
        prior_prices = self.price_history[-20:-10]

        recent_high = max(recent_prices)
        prior_high = max(prior_prices)

        # Bullish divergence: price lower, but RSI higher (strength building)
        if recent_high < prior_high and rsi > 50:
            return True, "bullish"

        # Bearish divergence: price higher, but RSI lower (weakness building)
        if recent_high > prior_high and rsi < 50:
            return True, "bearish"

        return False, "none"

    def _assess_momentum(self, rsi: float, macd_signal: str) -> str:
        """Assess overall market momentum.

        Args:
            rsi: Current RSI value.
            macd_signal: MACD analysis result.

        Returns:
            Momentum description.
        """
        momentum_score = 0

        # RSI contribution (0-40 points)
        if rsi > 70:
            momentum_score += 40  # Overbought, strong up
        elif rsi > 60:
            momentum_score += 30  # Strong up
        elif rsi > 50:
            momentum_score += 20  # Moderate up
        elif rsi > 40:
            momentum_score += 10  # Weak up
        elif rsi > 30:
            momentum_score -= 10  # Weak down
        elif rsi > 20:
            momentum_score -= 30  # Strong down
        else:
            momentum_score -= 40  # Oversold, strong down

        # MACD contribution (0-30 points)
        if macd_signal == "bullish_cross":
            momentum_score += 30
        elif macd_signal == "bearish_cross":
            momentum_score -= 30

        # Categorize
        if momentum_score >= 40:
            return "strong_up"
        elif momentum_score >= 20:
            return "moderate_up"
        elif momentum_score >= -20:
            return "weak"
        elif momentum_score >= -40:
            return "moderate_down"
        else:
            return "strong_down"

    def _determine_overall_strength(
        self, rsi: float, momentum: str, divergence_detected: bool
    ) -> str:
        """Determine overall market strength.

        Args:
            rsi: Current RSI value.
            momentum: Momentum direction.
            divergence_detected: Whether divergence is detected.

        Returns:
            Overall strength assessment.
        """
        # Penalize if divergence detected (warning signal)
        if divergence_detected:
            return "weak"

        # Assess based on momentum and RSI extremes
        if momentum.startswith("strong"):
            return "strong"
        elif momentum.startswith("moderate"):
            return "moderate"
        else:
            return "weak"

    def _calculate_trading_probability(
        self, rsi: float, momentum: str, divergence_detected: bool, divergence_type: str
    ) -> float:
        """Calculate probability of successful trade based on strength.

        Args:
            rsi: Current RSI value.
            momentum: Momentum direction.
            divergence_detected: Whether divergence is detected.
            divergence_type: Type of divergence (if detected).

        Returns:
            Trading probability (0-100).
        """
        probability = 50.0  # Base probability

        # Momentum contribution
        if momentum == "strong_up":
            probability += 20
        elif momentum == "moderate_up":
            probability += 10
        elif momentum == "weak":
            probability += 0
        elif momentum == "moderate_down":
            probability -= 10
        elif momentum == "strong_down":
            probability -= 20

        # RSI contribution
        if rsi > 70:
            probability -= 5  # Overbought
        elif rsi < 30:
            probability -= 5  # Oversold
        else:
            probability += 5

        # Divergence impact
        if divergence_detected:
            if divergence_type == "bullish":
                probability += 10  # Bullish divergence is positive
            elif divergence_type == "bearish":
                probability -= 10  # Bearish divergence is negative

        return max(0, min(100, probability))
