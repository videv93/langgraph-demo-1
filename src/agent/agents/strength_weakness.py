"""Strength & Weakness Analysis Agent - YTC Price Action Analysis.

Analyzes price movement strength and weakness using YTC methodology:
- Momentum (bar acceleration, close position, wick analysis)
- Projection (swing extension ratios)
- Depth (pullback retracement percentages)
"""

from typing import Any, TypedDict


class MomentumAnalysis(TypedDict, total=False):
    """Momentum component analysis."""

    score: float  # 0-100
    rating: str  # "strong" | "moderate" | "weak"
    description: str
    bars_in_direction: int
    average_body_size: float
    close_quality: str  # "strong" | "moderate" | "weak"


class ProjectionAnalysis(TypedDict, total=False):
    """Projection component analysis."""

    score: float  # 0-100
    ratio: float  # current/prior swing distance
    rating: str  # "extending" | "normal" | "contracting"
    description: str
    prior_swing_distance: float
    current_projection: float


class DepthAnalysis(TypedDict, total=False):
    """Depth component analysis (pullback retracement)."""

    score: float  # 0-100
    retracement_ratio: float  # 0-1.0+
    retracement_percentage: float  # e.g., 61.8
    rating: str  # "shallow" | "normal" | "deep" | "full_reversal"
    description: str


class StrengthAnalysis(TypedDict, total=False):
    """Overall strength analysis."""

    momentum: MomentumAnalysis
    projection: ProjectionAnalysis
    depth: DepthAnalysis
    combined_score: float  # 0-100
    overall_strength_rating: str  # "strong" | "moderate" | "weak" | "reversal_warning"


class WeaknessSignals(TypedDict, total=False):
    """Weakness signal detection."""

    rejection_bars_detected: bool
    momentum_divergence: bool
    projection_failure: bool
    deep_pullback: bool
    reversal_warning: bool


class SetupApplicability(TypedDict, total=False):
    """Setup type applicability based on strength/weakness."""

    good_for_continuation_setups: bool  # BPB, PB, CPB
    good_for_reversal_setups: bool  # TST, BOF
    fade_weakness_opportunity: bool
    expected_action: str


class StrengthWeaknessOutput(TypedDict, total=False):
    """Output from strength and weakness analysis."""

    analysis_complete: bool
    strength_analysis: StrengthAnalysis
    weakness_signals: WeaknessSignals
    setup_applicability: SetupApplicability


class StrengthWeakness:
    """YTC Strength & Weakness Analysis Agent.

    Analyzes price movement strength and weakness using three components:
    - Momentum: Bar acceleration, close position, wick quality (40% weight)
    - Projection: Swing extension ratios (30% weight)
    - Depth: Pullback retracement percentages (30% weight)

    Overall Score = (Momentum × 0.40) + (Projection × 0.30) + (Depth × 0.30)
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize strength and weakness agent.

        Args:
            config: Configuration with trend data, bar data, and swing information.
                   Expected keys: trend_data, bar_data, support_resistance
        """
        self.config = config or {}
        self._extract_config()

    def _extract_config(self) -> None:
        """Extract configuration parameters."""
        # Trend data
        trend_data = self.config.get("trend_data", {})
        self.trend_direction = trend_data.get("direction", "up")  # "up" | "down"
        self.current_swing = trend_data.get("current_swing", {})
        self.prior_swings = trend_data.get("prior_swings", [])

        # Bar data
        bar_data = self.config.get("bar_data", {})
        self.bars = bar_data.get("current_bars", [])
        self.lookback_bars = bar_data.get("lookback_bars", 20)

        # Support/Resistance
        sr_data = self.config.get("support_resistance", {})
        self.approaching_sr_level = sr_data.get("approaching_sr_level")
        self.level_type = sr_data.get("level_type", "none")

    def execute(self) -> StrengthWeaknessOutput:
        """Execute strength and weakness analysis.

        Returns:
            StrengthWeaknessOutput with momentum, projection, depth analysis.
        """
        # Step 1: Analyze momentum (bar acceleration, close position, wicks)
        momentum_analysis = self._analyze_momentum()

        # Step 2: Analyze projection (swing extension ratios)
        projection_analysis = self._analyze_projection()

        # Step 3: Analyze depth (pullback retracement)
        depth_analysis = self._analyze_depth()

        # Step 4: Calculate combined strength score
        combined_score = self._calculate_combined_score(
            momentum_analysis["score"], projection_analysis["score"], depth_analysis["score"]
        )

        # Step 5: Determine overall strength rating
        overall_rating = self._determine_strength_rating(combined_score)

        # Step 6: Detect weakness signals
        weakness_signals = self._detect_weakness_signals(
            momentum_analysis, projection_analysis, depth_analysis
        )

        # Step 7: Assess setup applicability
        setup_applicability = self._assess_setup_applicability(
            combined_score, weakness_signals, overall_rating
        )

        return {
            "analysis_complete": True,
            "strength_analysis": {
                "momentum": momentum_analysis,
                "projection": projection_analysis,
                "depth": depth_analysis,
                "combined_score": round(combined_score, 1),
                "overall_strength_rating": overall_rating,
            },
            "weakness_signals": weakness_signals,
            "setup_applicability": setup_applicability,
        }

    def _analyze_momentum(self) -> MomentumAnalysis:
        """Analyze momentum using bar acceleration and close position.

        Momentum Score = (Bar Size + Consecutive Bars + Acceleration) / 3

        Returns:
            MomentumAnalysis with score, rating, and details.
        """
        if not self.bars:
            return {
                "score": 50.0,
                "rating": "moderate",
                "description": "Insufficient bar data",
                "bars_in_direction": 0,
                "average_body_size": 0.0,
                "close_quality": "weak",
            }

        # Calculate bar metrics
        bar_sizes = []
        consecutive_bars = 0
        close_quality = self._assess_close_quality()

        for i, bar in enumerate(self.bars):
            body_size = abs(bar.get("body_size", 0))
            bar_sizes.append(body_size)

            # Count consecutive bars in trend direction
            if self._bar_in_trend_direction(bar):
                consecutive_bars += 1
            else:
                consecutive_bars = 0

        # Bar size score
        avg_body = sum(bar_sizes) / len(bar_sizes) if bar_sizes else 0
        historical_avg = sum(bar_sizes) / len(bar_sizes) if bar_sizes else 1.0
        bar_size_score = min(100.0, (avg_body / historical_avg) * 100) if historical_avg > 0 else 50.0

        # Consecutive bars score
        consecutive_score = min(100.0, (consecutive_bars / max(len(self.bars), 1)) * 100)

        # Acceleration score
        acceleration_score = self._calculate_acceleration_score()

        # Combined momentum score
        momentum_score = (bar_size_score + consecutive_score + acceleration_score) / 3

        # Determine rating
        if momentum_score >= 70:
            rating = "strong"
        elif momentum_score >= 40:
            rating = "moderate"
        else:
            rating = "weak"

        # Description
        description = self._describe_momentum(momentum_score, consecutive_bars, close_quality)

        return {
            "score": round(momentum_score, 1),
            "rating": rating,
            "description": description,
            "bars_in_direction": consecutive_bars,
            "average_body_size": round(avg_body, 4),
            "close_quality": close_quality,
        }

    def _bar_in_trend_direction(self, bar: dict[str, Any]) -> bool:
        """Check if bar moved in trend direction.

        Args:
            bar: Price bar data.

        Returns:
            True if bar moved in trend direction.
        """
        if self.trend_direction == "up":
            # Bullish: close > open
            return bar.get("close", 0) > bar.get("open", 0)
        else:
            # Bearish: close < open
            return bar.get("close", 0) < bar.get("open", 0)

    def _assess_close_quality(self) -> str:
        """Assess close position quality relative to bar range.

        Returns:
            "strong" | "moderate" | "weak"
        """
        if not self.bars:
            return "weak"

        strong_closes = 0

        for bar in self.bars[-5:]:  # Last 5 bars
            close_position = bar.get("close_position", "mid")  # "high" | "mid" | "low"

            if self.trend_direction == "up" and close_position == "high":
                strong_closes += 1
            elif self.trend_direction == "down" and close_position == "low":
                strong_closes += 1

        ratio = strong_closes / min(5, len(self.bars))

        if ratio >= 0.6:
            return "strong"
        elif ratio >= 0.3:
            return "moderate"
        else:
            return "weak"

    def _calculate_acceleration_score(self) -> float:
        """Calculate bar acceleration score.

        Compares recent bar sizes to prior bars.

        Returns:
            Score 0-100.
        """
        if len(self.bars) < 2:
            return 50.0

        recent_avg = sum(
            b.get("body_size", 0) for b in self.bars[-3:]
        ) / min(3, len(self.bars))
        prior_avg = sum(
            b.get("body_size", 0) for b in self.bars[-6:-3]
        ) / min(3, len(self.bars) - 3) if len(self.bars) >= 6 else recent_avg

        if prior_avg == 0:
            return 50.0

        acceleration = (recent_avg / prior_avg) * 100
        return min(100.0, max(0.0, acceleration))

    def _describe_momentum(
        self, score: float, consecutive_bars: int, close_quality: str
    ) -> str:
        """Build momentum description string.

        Args:
            score: Momentum score.
            consecutive_bars: Count of bars in trend direction.
            close_quality: Quality of closes.

        Returns:
            Description string.
        """
        if score >= 70:
            return f"Strong {self.trend_direction} momentum, {consecutive_bars} consecutive bars, {close_quality} closes"
        elif score >= 40:
            return f"Moderate momentum, {consecutive_bars} bars in direction, {close_quality} closes"
        else:
            return f"Weak momentum, limited bars in direction, {close_quality} closes"

    def _analyze_projection(self) -> ProjectionAnalysis:
        """Analyze projection using swing extension ratios.

        Projection Score = Ratio × 100
        - Ratio > 1.2 = 80-100 (strong extension)
        - Ratio 0.8-1.2 = 40-70 (normal)
        - Ratio < 0.8 = 0-40 (contraction)

        Returns:
            ProjectionAnalysis with score, ratio, and rating.
        """
        if not self.prior_swings:
            return {
                "score": 50.0,
                "ratio": 1.0,
                "rating": "normal",
                "description": "Insufficient swing data",
                "prior_swing_distance": 0.0,
                "current_projection": 0.0,
            }

        # Get current swing distance
        current_swing = self.current_swing
        current_price = self.bars[-1].get("close", 0) if self.bars else 0

        # Calculate current projection distance
        swing_price = current_swing.get("price", 0)
        current_distance = abs(current_price - swing_price)

        # Get average prior swing distance
        prior_distances = [s.get("distance", 0) for s in self.prior_swings[-3:]]
        avg_prior_distance = (
            sum(prior_distances) / len(prior_distances) if prior_distances else 1.0
        )

        # Calculate ratio
        if avg_prior_distance == 0:
            ratio = 1.0
        else:
            ratio = current_distance / avg_prior_distance

        # Calculate score
        if ratio > 1.2:
            score = min(100.0, ratio * 100 / 1.5)  # Cap at 100
            rating = "extending"
        elif ratio >= 0.8:
            score = (ratio / 1.2) * 70 + 30  # Scale to 40-70
            rating = "normal"
        else:
            score = ratio * 50  # Scale to 0-40
            rating = "contracting"

        # Description
        description = self._describe_projection(ratio, rating)

        return {
            "score": round(score, 1),
            "ratio": round(ratio, 2),
            "rating": rating,
            "description": description,
            "prior_swing_distance": round(avg_prior_distance, 4),
            "current_projection": round(current_distance, 4),
        }

    def _describe_projection(self, ratio: float, rating: str) -> str:
        """Build projection description string.

        Args:
            ratio: Projection ratio.
            rating: Rating (extending/normal/contracting).

        Returns:
            Description string.
        """
        if rating == "extending":
            return f"Strong extension: current swing {ratio:.2f}x prior swings"
        elif rating == "normal":
            return f"Normal projection: current swing {ratio:.2f}x prior swings"
        else:
            return f"Contraction: current swing only {ratio:.2f}x prior swings, exhaustion risk"

    def _analyze_depth(self) -> DepthAnalysis:
        """Analyze depth using pullback retracement percentages.

        Depth Score = 100 - (retracement_ratio × 100)
        - Retracement < 38.2% = 70-100 (shallow = strength)
        - Retracement 38.2-61.8% = 40-70 (normal)
        - Retracement > 61.8% = 0-40 (deep = weakness)

        Returns:
            DepthAnalysis with score and retracement metrics.
        """
        # Calculate pullback depth (only if we have pullback structure)
        pullback_depth = self._calculate_pullback_depth()

        if pullback_depth is None:
            return {
                "score": 50.0,
                "retracement_ratio": 0.5,
                "retracement_percentage": 50.0,
                "rating": "normal",
                "description": "Normal pullback depth",
            }

        # Convert depth to retracement ratio (0-1.0+)
        retracement_ratio = pullback_depth
        retracement_pct = retracement_ratio * 100

        # Calculate score
        if retracement_ratio < 0.382:
            score = min(100.0, (1 - retracement_ratio / 0.382) * 70 + 30)
            rating = "shallow"
        elif retracement_ratio <= 0.618:
            # Normal range
            score = ((0.618 - retracement_ratio) / 0.236) * 30 + 40
            rating = "normal"
        elif retracement_ratio < 1.0:
            score = (1 - retracement_ratio) * 40
            rating = "deep"
        else:
            score = 0.0
            rating = "full_reversal"

        # Description
        description = self._describe_depth(retracement_pct, rating)

        return {
            "score": round(score, 1),
            "retracement_ratio": round(retracement_ratio, 3),
            "retracement_percentage": round(retracement_pct, 1),
            "rating": rating,
            "description": description,
        }

    def _calculate_pullback_depth(self) -> float | None:
        """Calculate pullback retracement as ratio of prior swing.

        Returns:
            Retracement ratio (0-1.0+) or None if no pullback detected.
        """
        if len(self.bars) < 3 or not self.prior_swings:
            return None

        # Identify if we're in a pullback (moving against trend)
        pullback_start_price = None
        pullback_extreme = None

        if self.trend_direction == "up":
            # In uptrend, pullback is downward move
            pullback_extreme = min(b.get("low", float("inf")) for b in self.bars[-5:])
        else:
            # In downtrend, pullback is upward move
            pullback_extreme = max(b.get("high", float("-inf")) for b in self.bars[-5:])

        # Get swing reference points
        if not self.prior_swings:
            return None

        last_swing = self.prior_swings[-1]
        swing_distance = last_swing.get("distance", 0)

        if swing_distance == 0:
            return None

        # Calculate actual pullback depth
        if self.trend_direction == "up":
            swing_high = last_swing.get("price", 0)
            pullback_depth = (swing_high - pullback_extreme) / swing_distance
        else:
            swing_low = last_swing.get("price", 0)
            pullback_depth = (pullback_extreme - swing_low) / swing_distance

        return max(0.0, min(pullback_depth, 2.0))  # Cap at 2.0 for reversals

    def _describe_depth(self, retracement_pct: float, rating: str) -> str:
        """Build depth description string.

        Args:
            retracement_pct: Retracement percentage.
            rating: Rating (shallow/normal/deep/full_reversal).

        Returns:
            Description string.
        """
        if rating == "shallow":
            return f"Shallow pullback ({retracement_pct:.1f}%): buyers eager to re-enter, strength expected"
        elif rating == "normal":
            return f"Normal pullback ({retracement_pct:.1f}%): standard Fibonacci retracement zone"
        elif rating == "deep":
            return f"Deep pullback ({retracement_pct:.1f}%): weakness signal, reversal risk"
        else:
            return "Full retracement: prior swing low/high broken, trend reversal likely"

    def _calculate_combined_score(
        self, momentum_score: float, projection_score: float, depth_score: float
    ) -> float:
        """Calculate combined strength score.

        Overall Score = (Momentum × 0.40) + (Projection × 0.30) + (Depth × 0.30)

        Args:
            momentum_score: Momentum component (0-100).
            projection_score: Projection component (0-100).
            depth_score: Depth component (0-100).

        Returns:
            Combined score (0-100).
        """
        combined = (momentum_score * 0.40) + (projection_score * 0.30) + (depth_score * 0.30)
        return min(100.0, max(0.0, combined))

    def _determine_strength_rating(self, combined_score: float) -> str:
        """Determine overall strength rating.

        Args:
            combined_score: Combined score 0-100.

        Returns:
            "strong" | "moderate" | "weak" | "reversal_warning"
        """
        if combined_score >= 70:
            return "strong"
        elif combined_score >= 40:
            return "moderate"
        else:
            return "weak"

    def _detect_weakness_signals(
        self,
        momentum_analysis: MomentumAnalysis,
        projection_analysis: ProjectionAnalysis,
        depth_analysis: DepthAnalysis,
    ) -> WeaknessSignals:
        """Detect weakness signals.

        Args:
            momentum_analysis: Momentum analysis results.
            projection_analysis: Projection analysis results.
            depth_analysis: Depth analysis results.

        Returns:
            WeaknessSignals with boolean indicators.
        """
        # Rejection bars: small body + large wicks
        rejection_bars = self._detect_rejection_bars()

        # Momentum divergence: momentum fading while price continues
        divergence = self._detect_momentum_divergence(momentum_analysis)

        # Projection failure: ratio < 0.8 (contraction)
        projection_failure = projection_analysis["ratio"] < 0.8

        # Deep pullback: retracement > 61.8%
        deep_pullback = depth_analysis["retracement_ratio"] > 0.618

        # Reversal warning: multiple weakness signals
        reversal_warning = (
            rejection_bars
            and deep_pullback
            and projection_analysis["rating"] == "contracting"
        )

        return {
            "rejection_bars_detected": rejection_bars,
            "momentum_divergence": divergence,
            "projection_failure": projection_failure,
            "deep_pullback": deep_pullback,
            "reversal_warning": reversal_warning,
        }

    def _detect_rejection_bars(self) -> bool:
        """Detect rejection bar patterns (pin bars).

        Returns:
            True if rejection bars detected in last 3 bars.
        """
        if len(self.bars) < 3:
            return False

        for bar in self.bars[-3:]:
            body_ratio = bar.get("body_size", 0) / (bar.get("bar_range", 1) or 1)
            wick_type = bar.get("wick_type", "none")

            # Rejection: small body + large wick
            if body_ratio < 0.4 and wick_type in ["upper", "lower", "both"]:
                return True

        return False

    def _detect_momentum_divergence(self, momentum_analysis: MomentumAnalysis) -> bool:
        """Detect momentum divergence (momentum fading).

        Args:
            momentum_analysis: Momentum analysis results.

        Returns:
            True if momentum divergence detected.
        """
        # Divergence: weak momentum score but continuation in trend direction
        if momentum_analysis["score"] < 40 and len(self.bars) >= 5:
            # Check if price still made new extremes despite weak momentum
            recent_bars = self.bars[-5:]

            if self.trend_direction == "up":
                made_new_high = any(b.get("high", 0) > self.bars[-6].get("high", 0) for b in recent_bars)
                return made_new_high and momentum_analysis["score"] < 30
            else:
                made_new_low = any(b.get("low", 0) < self.bars[-6].get("low", float("inf")) for b in recent_bars)
                return made_new_low and momentum_analysis["score"] < 30

        return False

    def _assess_setup_applicability(
        self,
        combined_score: float,
        weakness_signals: WeaknessSignals,
        overall_rating: str,
    ) -> SetupApplicability:
        """Assess which setup types are applicable.

        Args:
            combined_score: Combined strength score.
            weakness_signals: Detected weakness signals.
            overall_rating: Overall strength rating.

        Returns:
            SetupApplicability assessment.
        """
        # Strong strength → continuation setups (BPB, PB, CPB)
        good_for_continuation = combined_score >= 60

        # Weak strength + weakness signals → reversal setups (TST, BOF)
        good_for_reversal = (
            combined_score < 40
            or weakness_signals.get("rejection_bars_detected", False)
            or weakness_signals.get("deep_pullback", False)
        )

        # Fade weakness opportunity when approaching S/R with weakness
        fade_weakness = (
            self.approaching_sr_level is not None
            and combined_score < 40
            and weakness_signals.get("rejection_bars_detected", False)
        )

        # Expected action
        if good_for_continuation and combined_score >= 70:
            expected_action = "Expect pullback continuation; favorable for BPB, PB, CPB setups in trend direction"
        elif good_for_reversal and weakness_signals.get("reversal_warning", False):
            expected_action = "Reversal warning: multiple weakness signals detected; avoid counter-trend entries"
        elif fade_weakness:
            expected_action = "Fade weakness at S/R level; enter opposite to weakness direction"
        elif overall_rating == "moderate":
            expected_action = "Neutral strength; context dependent; confirm with HTF bias"
        else:
            expected_action = "Monitor for continuation or reversal based on next bars"

        return {
            "good_for_continuation_setups": good_for_continuation,
            "good_for_reversal_setups": good_for_reversal,
            "fade_weakness_opportunity": fade_weakness,
            "expected_action": expected_action,
        }
