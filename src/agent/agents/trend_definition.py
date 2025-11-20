"""Trend Definition Agent - YTC Swing Analysis.

Identifies trend direction and structure using YTC's precise swing analysis methodology.
Determines uptrend (HH + HL), downtrend (LH + LL), or sideways movement.
"""

from datetime import datetime
from enum import Enum
from typing import Any, TypedDict


class TrendDirection(str, Enum):
    """Trend direction classification."""

    UPTREND = "uptrend"
    DOWNTREND = "downtrend"
    SIDEWAYS = "sideways"


class TrendStrength(str, Enum):
    """Strength rating of the trend."""

    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    REVERSAL_WARNING = "reversal_warning"


class Swing(TypedDict, total=False):
    """Swing high or low."""

    type: str  # "swing_high" | "swing_low"
    price: float
    timestamp: str
    bar_index: int
    is_leading: bool
    is_broken: bool


class SwingStructure(TypedDict, total=False):
    """Swing structure data."""

    swing_highs: list[Swing]
    swing_lows: list[Swing]
    current_leading_swing_high: float
    current_leading_swing_low: float


class StructureIntegrity(TypedDict, total=False):
    """Trend structure integrity assessment."""

    structure_intact: bool
    structure_breaks_detected: int
    reversal_warning: bool
    last_structure_break_timestamp: str | None
    structure_break_description: str


class HTFAlignment(TypedDict, total=False):
    """Higher timeframe alignment assessment."""

    tf_trend_aligns_with_htf: bool
    alignment_description: str
    potential_conflict: str | None


class TrendAnalysis(TypedDict, total=False):
    """Trend direction and strength assessment."""

    direction: TrendDirection
    confidence: float
    strength_rating: TrendStrength
    since_timestamp: str
    bar_count_in_trend: int


class TrendDefinitionOutput(TypedDict, total=False):
    """Complete trend definition analysis output."""

    trend_analysis: TrendAnalysis
    swing_structure: SwingStructure
    structure_integrity: StructureIntegrity
    htf_alignment: HTFAlignment


class TrendDefinition:
    """YTC Trend Definition Agent.

    Identifies trend using swing analysis:
    - Uptrend: Series of higher highs (HH) and higher lows (HL)
    - Downtrend: Series of lower highs (LH) and lower lows (LL)
    - Sideways: Price within range without clear directional bias

    Tracks leading swings, detects structure breaks, and validates against HTF.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize trend definition agent.

        Args:
            config: Configuration with bars, HTF context, and analysis parameters.
                   Expected keys: market_data (with bars list),
                                 higher_timeframe_context
        """
        self.config = config or {}
        self._extract_config()

    def _extract_config(self) -> None:
        """Extract configuration parameters."""
        # Market data
        market_data = self.config.get("market_data", {})
        self.bars = market_data.get("bars", [])
        self.symbol = market_data.get("symbol", "")
        self.timeframe = market_data.get("timeframe", "15m")

        # HTF context
        htf_context = self.config.get("higher_timeframe_context", {})
        self.htf_timeframe = htf_context.get("htf_timeframe", "4H")
        self.htf_trend_direction = htf_context.get("htf_trend_direction", "sideways")
        self.htf_resistance = htf_context.get("htf_resistance", 0.0)
        self.htf_support = htf_context.get("htf_support", 0.0)
        self.htf_swing_high = htf_context.get("htf_swing_high", 0.0)
        self.htf_swing_low = htf_context.get("htf_swing_low", 0.0)

    def execute(self) -> TrendDefinitionOutput:
        """Execute YTC trend definition analysis.

        Returns:
            TrendDefinitionOutput with trend direction, swing structure,
            and HTF alignment assessment.
        """
        # Step 1: Identify swing highs and lows
        swings = self._identify_swings()

        # Step 2: Classify trend type
        trend_direction = self._classify_trend(swings)

        # Step 3: Track leading swings
        leading_sh, leading_sl = self._get_leading_swings(swings)

        # Step 4: Detect structure breaks
        structure_breaks = self._detect_structure_breaks(swings, trend_direction)

        # Step 5: Assess trend strength
        strength_rating = self._assess_trend_strength(
            swings, trend_direction, structure_breaks
        )

        # Step 6: Calculate confidence
        confidence = self._calculate_confidence(swings, trend_direction)

        # Step 7: Check HTF alignment
        htf_aligned = self._check_htf_alignment(trend_direction)

        # Step 8: Determine trend inception and bar count
        trend_inception, bar_count = self._get_trend_inception(swings, trend_direction)

        # Build output
        return {
            "trend_analysis": {
                "direction": trend_direction,
                "confidence": round(confidence, 2),
                "strength_rating": strength_rating,
                "since_timestamp": trend_inception,
                "bar_count_in_trend": bar_count,
            },
            "swing_structure": {
                "swing_highs": [s for s in swings if s["type"] == "swing_high"],
                "swing_lows": [s for s in swings if s["type"] == "swing_low"],
                "current_leading_swing_high": leading_sh,
                "current_leading_swing_low": leading_sl,
            },
            "structure_integrity": self._build_structure_integrity(
                swings, trend_direction, structure_breaks
            ),
            "htf_alignment": {
                "tf_trend_aligns_with_htf": htf_aligned,
                "alignment_description": self._describe_alignment(
                    trend_direction, htf_aligned
                ),
                "potential_conflict": (
                    f"TF {trend_direction} conflicts with HTF {self.htf_trend_direction}"
                    if not htf_aligned
                    else None
                ),
            },
        }

    def _identify_swings(self) -> list[Swing]:
        """Identify swing highs and lows using YTC methodology.

        A swing high requires: bar high > left bar high AND bar high > right bar high
        A swing low requires: bar low < left bar low AND bar low < right bar low

        Returns:
            List of identified swings (chronologically ordered).
        """
        swings: list[Swing] = []

        if len(self.bars) < 3:
            return swings

        for i in range(1, len(self.bars) - 1):
            current = self.bars[i]
            prev = self.bars[i - 1]
            next_bar = self.bars[i + 1]

            # Swing high: current high > both neighbors
            if current.get("high", 0) > prev.get("high", 0) and current.get(
                "high", 0
            ) > next_bar.get("high", 0):
                swings.append(
                    {
                        "type": "swing_high",
                        "price": current.get("high", 0),
                        "timestamp": current.get("timestamp", ""),
                        "bar_index": i,
                        "is_leading": False,
                        "is_broken": False,
                    }
                )

            # Swing low: current low < both neighbors
            elif current.get("low", 0) < prev.get("low", 0) and current.get(
                "low", 0
            ) < next_bar.get("low", 0):
                swings.append(
                    {
                        "type": "swing_low",
                        "price": current.get("low", 0),
                        "timestamp": current.get("timestamp", ""),
                        "bar_index": i,
                        "is_leading": False,
                        "is_broken": False,
                    }
                )

        return swings

    def _classify_trend(self, swings: list[Swing]) -> TrendDirection:
        """Classify trend using swing sequence pattern.

        Uptrend: Series of higher highs (HH) and higher lows (HL)
        Downtrend: Series of lower highs (LH) and lower lows (LL)
        Sideways: No clear pattern

        Args:
            swings: List of identified swings.

        Returns:
            TrendDirection (uptrend, downtrend, or sideways).
        """
        if len(swings) < 3:
            return TrendDirection.SIDEWAYS

        # Separate swing highs and lows
        swing_highs = [s for s in swings if s["type"] == "swing_high"]
        swing_lows = [s for s in swings if s["type"] == "swing_low"]

        if len(swing_highs) < 2 or len(swing_lows) < 2:
            return TrendDirection.SIDEWAYS

        # Count higher highs and higher lows (uptrend pattern)
        higher_highs = 0
        higher_lows = 0

        for i in range(1, len(swing_highs)):
            if swing_highs[i]["price"] > swing_highs[i - 1]["price"]:
                higher_highs += 1

        for i in range(1, len(swing_lows)):
            if swing_lows[i]["price"] > swing_lows[i - 1]["price"]:
                higher_lows += 1

        # Count lower highs and lower lows (downtrend pattern)
        lower_highs = len(swing_highs) - 1 - higher_highs
        lower_lows = len(swing_lows) - 1 - higher_lows

        # Determine trend based on pattern dominance
        if higher_highs >= 2 and higher_lows >= 2:
            return TrendDirection.UPTREND

        if lower_highs >= 2 and lower_lows >= 2:
            return TrendDirection.DOWNTREND

        # Weighted scoring if patterns are mixed
        uptrend_score = higher_highs + higher_lows
        downtrend_score = lower_highs + lower_lows

        if uptrend_score > downtrend_score + 1:
            return TrendDirection.UPTREND
        elif downtrend_score > uptrend_score + 1:
            return TrendDirection.DOWNTREND
        else:
            return TrendDirection.SIDEWAYS

    def _get_leading_swings(self, swings: list[Swing]) -> tuple[float, float]:
        """Get current leading swing high and swing low.

        Leading swings are the most recent significant swings.
        Used to detect reversals when broken.

        Args:
            swings: List of identified swings.

        Returns:
            Tuple of (leading_swing_high, leading_swing_low).
        """
        swing_highs = [s for s in swings if s["type"] == "swing_high"]
        swing_lows = [s for s in swings if s["type"] == "swing_low"]

        leading_sh = swing_highs[-1]["price"] if swing_highs else 0.0
        leading_sl = swing_lows[-1]["price"] if swing_lows else 0.0

        return leading_sh, leading_sl

    def _detect_structure_breaks(
        self, swings: list[Swing], trend: TrendDirection
    ) -> int:
        """Detect structure breaks indicating trend weakness.

        In uptrend: Look for Lower Low (LL) - breaks HL pattern
        In downtrend: Look for Higher High (HH) - breaks LH pattern

        Args:
            swings: List of identified swings.
            trend: Current trend direction.

        Returns:
            Count of structure breaks detected.
        """
        if trend == TrendDirection.SIDEWAYS:
            return 0

        swing_highs = [s for s in swings if s["type"] == "swing_high"]
        swing_lows = [s for s in swings if s["type"] == "swing_low"]

        breaks = 0

        if trend == TrendDirection.UPTREND:
            # Look for lower lows (LL) - breaks higher low pattern
            for i in range(1, len(swing_lows)):
                if swing_lows[i]["price"] < swing_lows[i - 1]["price"]:
                    breaks += 1
                    swing_lows[i]["is_broken"] = True

        elif trend == TrendDirection.DOWNTREND:
            # Look for higher highs (HH) - breaks lower high pattern
            for i in range(1, len(swing_highs)):
                if swing_highs[i]["price"] > swing_highs[i - 1]["price"]:
                    breaks += 1
                    swing_highs[i]["is_broken"] = True

        return breaks

    def _assess_trend_strength(
        self, swings: list[Swing], trend: TrendDirection, structure_breaks: int
    ) -> TrendStrength:
        """Assess trend strength based on swing count and breaks.

        Strong: 3+ confirmed swings, 0 structure breaks
        Moderate: 2-3 swings, 0-1 structure breaks
        Weak: 1-2 swings or multiple breaks
        Reversal Warning: Leading swing broken

        Args:
            swings: List of swings.
            trend: Trend direction.
            structure_breaks: Count of structure breaks.

        Returns:
            TrendStrength assessment.
        """
        if trend == TrendDirection.SIDEWAYS:
            return TrendStrength.WEAK

        # Count confirmed swings in trend direction
        swing_highs = [s for s in swings if s["type"] == "swing_high"]
        swing_lows = [s for s in swings if s["type"] == "swing_low"]

        confirmed_swings = len(swing_highs) + len(swing_lows)

        # Check if leading swing is broken
        leading_sh, leading_sl = self._get_leading_swings(swings)

        if self.bars:
            current_price = self.bars[-1].get("close", 0)

            # Leading swing broken indicates reversal risk
            if trend == TrendDirection.UPTREND and current_price < leading_sl:
                return TrendStrength.REVERSAL_WARNING

            if trend == TrendDirection.DOWNTREND and current_price > leading_sh:
                return TrendStrength.REVERSAL_WARNING

        # Assess based on swing count and breaks
        if confirmed_swings >= 5 and structure_breaks == 0:
            return TrendStrength.STRONG

        if confirmed_swings >= 3 and structure_breaks <= 1:
            return TrendStrength.STRONG

        if confirmed_swings >= 2 and structure_breaks == 0:
            return TrendStrength.MODERATE

        if structure_breaks >= 2:
            return TrendStrength.WEAK

        return TrendStrength.WEAK

    def _calculate_confidence(
        self, swings: list[Swing], trend: TrendDirection
    ) -> float:
        """Calculate confidence score for trend classification.

        Each confirmed swing adds ~0.2 to confidence (max 1.0).

        Args:
            swings: List of identified swings.
            trend: Trend direction.

        Returns:
            Confidence score (0.0 to 1.0).
        """
        if trend == TrendDirection.SIDEWAYS:
            return 0.5

        swing_highs = [s for s in swings if s["type"] == "swing_high"]
        swing_lows = [s for s in swings if s["type"] == "swing_low"]

        confirmed_swings = len(swing_highs) + len(swing_lows)

        # Base confidence on swing count
        confidence = min(confirmed_swings * 0.15, 0.95)

        # Add bonus for trending structure
        if trend == TrendDirection.UPTREND:
            hh_count = sum(
                1
                for i in range(1, len(swing_highs))
                if swing_highs[i]["price"] > swing_highs[i - 1]["price"]
            )
            hl_count = sum(
                1
                for i in range(1, len(swing_lows))
                if swing_lows[i]["price"] > swing_lows[i - 1]["price"]
            )
            if hh_count >= 2 and hl_count >= 2:
                confidence += 0.15

        elif trend == TrendDirection.DOWNTREND:
            lh_count = sum(
                1
                for i in range(1, len(swing_highs))
                if swing_highs[i]["price"] < swing_highs[i - 1]["price"]
            )
            ll_count = sum(
                1
                for i in range(1, len(swing_lows))
                if swing_lows[i]["price"] < swing_lows[i - 1]["price"]
            )
            if lh_count >= 2 and ll_count >= 2:
                confidence += 0.15

        return min(confidence, 1.0)

    def _check_htf_alignment(self, trend_direction: TrendDirection) -> bool:
        """Check if trading timeframe trend aligns with HTF trend.

        Args:
            trend_direction: Trading timeframe trend direction.

        Returns:
            True if TF trend aligns with HTF bias.
        """
        # Convert string HTF direction to enum for comparison
        tf_dir = str(trend_direction.value)
        htf_dir = str(self.htf_trend_direction).lower()

        if htf_dir == "sideways":
            return True  # No conflict in sideways HTF

        return tf_dir == htf_dir

    def _describe_alignment(
        self, trend_direction: TrendDirection, aligned: bool
    ) -> str:
        """Build alignment description string.

        Args:
            trend_direction: Trading timeframe trend.
            aligned: Whether trends align.

        Returns:
            Description string.
        """
        tf_dir = str(trend_direction.value)
        htf_dir = str(self.htf_trend_direction).lower()

        if aligned:
            return f"Trading TF {tf_dir} aligned with HTF {htf_dir}"
        else:
            return f"Trading TF {tf_dir} conflicts with HTF {htf_dir}"

    def _get_trend_inception(
        self, swings: list[Swing], trend: TrendDirection
    ) -> tuple[str, int]:
        """Determine when trend started and bar count.

        Args:
            swings: List of swings.
            trend: Trend direction.

        Returns:
            Tuple of (trend_inception_timestamp, bar_count_in_trend).
        """
        if not swings:
            return "", 0

        if trend == TrendDirection.SIDEWAYS:
            return "", 0

        # Trend starts after the first confirmatory swing
        if len(swings) >= 2:
            inception_swing = swings[-2]  # Before last swing
            inception_timestamp = inception_swing.get("timestamp", "")
            bar_count = self.bars[-1].get("bar_index", 0) - inception_swing.get(
                "bar_index", 0
            )

            return inception_timestamp, max(bar_count, 0)

        return swings[0].get("timestamp", ""), len(self.bars)

    def _build_structure_integrity(
        self, swings: list[Swing], trend: TrendDirection, structure_breaks: int
    ) -> StructureIntegrity:
        """Build structure integrity assessment.

        Args:
            swings: List of swings.
            trend: Trend direction.
            structure_breaks: Count of structure breaks.

        Returns:
            StructureIntegrity assessment.
        """
        structure_intact = structure_breaks == 0
        reversal_warning = False

        # Check if leading swing is broken
        leading_sh, leading_sl = self._get_leading_swings(swings)

        if self.bars:
            current_price = self.bars[-1].get("close", 0)

            if trend == TrendDirection.UPTREND and current_price < leading_sl:
                reversal_warning = True

            if trend == TrendDirection.DOWNTREND and current_price > leading_sh:
                reversal_warning = True

        # Get last structure break description
        last_break_ts = None
        break_description = ""

        if structure_breaks > 0:
            if trend == TrendDirection.UPTREND:
                swing_lows = [s for s in swings if s["type"] == "swing_low"]
                for i in range(1, len(swing_lows)):
                    if swing_lows[i]["price"] < swing_lows[i - 1]["price"]:
                        last_break_ts = swing_lows[i].get("timestamp")
                        break_description = (
                            f"LL formed in uptrend at {swing_lows[i]['price']}"
                        )

            elif trend == TrendDirection.DOWNTREND:
                swing_highs = [s for s in swings if s["type"] == "swing_high"]
                for i in range(1, len(swing_highs)):
                    if swing_highs[i]["price"] > swing_highs[i - 1]["price"]:
                        last_break_ts = swing_highs[i].get("timestamp")
                        break_description = (
                            f"HH formed in downtrend at {swing_highs[i]['price']}"
                        )

        return {
            "structure_intact": structure_intact,
            "structure_breaks_detected": structure_breaks,
            "reversal_warning": reversal_warning,
            "last_structure_break_timestamp": last_break_ts,
            "structure_break_description": break_description,
        }
