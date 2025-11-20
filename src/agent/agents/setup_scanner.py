"""Setup Scanner Agent - YTC Setup Identification and Validation.

Identifies high-probability YTC trading setups (TST, BOF, BPB, PB, CPB)
aligned with trend structure and strength/weakness signals.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, TypedDict


class SetupType(str, Enum):
    """YTC trading setup types."""

    TST = "TST"  # Test of Support/Resistance
    BOF = "BOF"  # Breakout Failure
    BPB = "BPB"  # Breakout Pullback
    PB = "PB"  # Simple Pullback
    CPB = "CPB"  # Complex Pullback
    NONE = "none"


class BarData(TypedDict, total=False):
    """Price bar data."""

    open: float
    high: float
    low: float
    close: float
    volume: int
    body_strength: str  # "strong" | "weak"
    close_position: str  # "high" | "mid" | "low"


class SRLevel(TypedDict, total=False):
    """Support/Resistance level."""

    price: float
    type: str  # "swing_point" | "prior_level" | "fibonacci"
    strength: str  # "strong" | "moderate" | "weak"


class EntryZone(TypedDict, total=False):
    """Entry zone definition."""

    upper: float
    lower: float
    ideal: float
    trigger_bar_pattern: str


class StopLoss(TypedDict, total=False):
    """Stop loss definition."""

    price: float
    placement_rationale: str
    distance_pips: float


class Target(TypedDict, total=False):
    """Profit target."""

    level: str  # "T1" | "T2" | "T3"
    price: float
    type: str  # "next_sr" | "swing_point" | "multiple_r"
    r_multiple: float


class YTCSetup(TypedDict, total=False):
    """YTC trading setup with all details."""

    setup_id: str
    type: SetupType
    direction: str  # "long" | "short"
    probability_score: float  # 0-100
    sr_level: SRLevel
    entry_zone: EntryZone
    stop_loss: StopLoss
    targets: list[Target]
    risk_reward_ratio: float
    confluence_factors: list[str]
    trapped_trader_potential: str  # "high" | "moderate" | "low"
    market_condition_alignment: str
    ready_to_trade: bool
    quality_rating: str  # "A" | "B" | "C"


class SetupScannerOutput(TypedDict, total=False):
    """Output from setup scanning."""

    scan_complete: bool
    active_setups: list[YTCSetup]
    scan_summary: dict[str, Any]


class SetupScanner:
    """YTC Setup Scanner Agent.

    Scans market price action to identify high-probability YTC trading setups
    (TST, BOF, BPB, PB, CPB) aligned with trend structure and strength/weakness.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the setup scanner agent.

        Args:
            config: Configuration with trend data, price action, S/R levels,
                   market conditions, and scanner parameters.
        """
        self.config = config or {}
        self._extract_config()

    def _extract_config(self) -> None:
        """Extract configuration parameters."""
        # Trend data
        trend_data = self.config.get("trend_data", {})
        self.trend_direction = trend_data.get("direction", "up")  # "up" | "down"
        trend_structure = trend_data.get("structure", {})
        self.swing_high = trend_structure.get("swing_high", 0.0)
        self.swing_low = trend_structure.get("swing_low", 0.0)
        self.trend_strength = trend_data.get("strength_rating", "moderate")

        # Price action
        price_action = self.config.get("price_action", {})
        self.current_price = price_action.get("current_price", 0.0)
        self.bars = price_action.get("bars", [])

        # Support/Resistance levels
        sr_data = self.config.get("support_resistance", {})
        self.sr_levels = sr_data.get("levels", [])

        # Market conditions
        market_conditions = self.config.get("market_conditions", {})
        self.trend_stage = market_conditions.get("trend_stage", "strong")
        self.volatility = market_conditions.get("volatility", "normal")

        # Scanner config
        scanner_config = self.config.get("config", {})
        self.min_confluence = scanner_config.get("min_confluence_factors", 2)
        self.min_risk_reward = scanner_config.get("min_risk_reward", 1.5)
        self.enabled_setup_types = scanner_config.get(
            "enabled_setup_types", ["TST", "BOF", "BPB", "PB", "CPB"]
        )

    def execute(self) -> SetupScannerOutput:
        """Execute setup scanning.

        Returns:
            SetupScannerOutput with identified YTC trading setups.
        """
        setups = []

        # Scan for each YTC setup type
        if "TST" in self.enabled_setup_types:
            tst_setups = self._scan_tst()
            setups.extend(tst_setups)

        if "BOF" in self.enabled_setup_types:
            bof_setups = self._scan_bof()
            setups.extend(bof_setups)

        if "BPB" in self.enabled_setup_types:
            bpb_setups = self._scan_bpb()
            setups.extend(bpb_setups)

        if "PB" in self.enabled_setup_types:
            pb_setups = self._scan_pb()
            setups.extend(pb_setups)

        if "CPB" in self.enabled_setup_types:
            cpb_setups = self._scan_cpb()
            setups.extend(cpb_setups)

        # Sort by probability score (descending)
        setups.sort(key=lambda x: x.get("probability_score", 0), reverse=True)

        # Filter trade-ready setups
        trade_ready = [s for s in setups if s.get("ready_to_trade", False)]

        # Summary
        summary = {
            "total_setups_identified": len(setups),
            "trade_ready_count": len(trade_ready),
            "highest_probability_setup_id": (
                setups[0].get("setup_id") if setups else None
            ),
            "market_condition_verdict": self._assess_market_conditions(),
        }

        return {
            "scan_complete": True,
            "active_setups": setups,
            "scan_summary": summary,
        }

    def _scan_tst(self) -> list[YTCSetup]:
        """Scan for TST (Test of Support/Resistance) setups.

        TST: Price tests S/R level with expectation of holding.
        High probability when price shows rejection/weakness at the level.

        Returns:
            List of detected TST setups.
        """
        setups = []

        if len(self.bars) < 3:
            return setups

        # Check if price is approaching any S/R level
        for sr_level in self.sr_levels:
            level_price = sr_level.get("price", 0.0)
            proximity_pct = abs(self.current_price - level_price) / level_price * 100

            # Price within 1% of S/R level (approaching)
            if 0 < proximity_pct <= 1.0:
                # Check for rejection bars at the level
                has_rejection_bars = self._identify_rejection_bars(self.bars[-3:])

                if has_rejection_bars and self._validates_against_trend(
                    self.bars[-3:], self.trend_direction
                ):
                    # Determine setup direction
                    if self.trend_direction == "up":
                        direction = "long"
                        entry_ideal = level_price * 1.001
                        stop = level_price * 0.99
                    else:
                        direction = "short"
                        entry_ideal = level_price * 0.999
                        stop = level_price * 1.01

                    # Calculate targets
                    targets = self._calculate_targets(direction, level_price)

                    # Risk-to-reward ratio
                    if direction == "long":
                        rrr = (targets[0]["price"] - entry_ideal) / (
                            entry_ideal - stop
                        )
                    else:
                        rrr = (entry_ideal - targets[0]["price"]) / (
                            stop - entry_ideal
                        )

                    # Confidence score
                    base_score = 70.0
                    confluence_factors = [
                        "HTF trend alignment",
                        f"rejection bars at {sr_level['type']}",
                    ]
                    confidence = base_score + (3 if has_rejection_bars else 0)

                    # Market condition adjustment
                    if self.trend_stage == "strong":
                        confidence += 20
                    elif self.trend_stage == "slowing":
                        confidence -= 10

                    confidence = min(100.0, confidence)

                    setup = self._create_setup(
                        setup_type=SetupType.TST,
                        direction=direction,
                        sr_level=sr_level,
                        entry_zone={
                            "upper": level_price * 1.005,
                            "lower": level_price * 0.995,
                            "ideal": entry_ideal,
                            "trigger_bar_pattern": "rejection bar reversal",
                        },
                        stop_loss={
                            "price": stop,
                            "placement_rationale": "below/above S/R level hold",
                            "distance_pips": abs(entry_ideal - stop) * 10000,
                        },
                        targets=targets,
                        risk_reward_ratio=rrr,
                        confluence_factors=confluence_factors,
                        trapped_trader_potential="high",
                        market_condition_alignment=f"{self.trend_stage} trend favorable for TST",
                        probability_score=confidence,
                    )

                    setups.append(setup)

        return setups

    def _scan_bof(self) -> list[YTCSetup]:
        """Scan for BOF (Breakout Failure) setups.

        BOF: Price breaches S/R but fails to sustain breakout.
        High probability reversal as trapped traders exit.

        Returns:
            List of detected BOF setups.
        """
        setups = []

        if len(self.bars) < 10:
            return setups

        # Check for recent breakout attempts
        recent_bars = self.bars[-10:]
        breakout_bar = recent_bars[0]

        for sr_level in self.sr_levels:
            level_price = sr_level.get("price", 0.0)

            # Detect breakout bar (opposite to trend direction)
            if self._has_breakout_bar(breakout_bar, level_price):
                # Check for failure in follow-through bars
                if self._has_weak_followthrough(recent_bars[1:]) or self._pullback_through_level(
                    recent_bars[1:], level_price
                ):
                    # Determine direction (counter to breakout)
                    if breakout_bar["high"] > level_price:
                        direction = "short"
                        entry_ideal = level_price * 0.999
                        stop = breakout_bar["high"] * 1.001
                    else:
                        direction = "long"
                        entry_ideal = level_price * 1.001
                        stop = breakout_bar["low"] * 0.999

                    # Calculate targets
                    targets = self._calculate_targets(direction, level_price)

                    # Risk-to-reward ratio
                    if direction == "long":
                        rrr = (targets[0]["price"] - entry_ideal) / (
                            entry_ideal - stop
                        )
                    else:
                        rrr = (entry_ideal - targets[0]["price"]) / (
                            stop - entry_ideal
                        )

                    # Confidence score
                    base_score = 75.0
                    confluence_factors = ["failed breakout", "trapped trader reversal"]
                    confidence = base_score + 15  # BOF has good trapped trader potential

                    if self.trend_stage == "ranging":
                        confidence -= 10  # BOF less reliable in ranging

                    confidence = min(100.0, max(50.0, confidence))

                    setup = self._create_setup(
                        setup_type=SetupType.BOF,
                        direction=direction,
                        sr_level=sr_level,
                        entry_zone={
                            "upper": level_price * 1.002,
                            "lower": level_price * 0.998,
                            "ideal": entry_ideal,
                            "trigger_bar_pattern": "reverse bar or close back through level",
                        },
                        stop_loss={
                            "price": stop,
                            "placement_rationale": "beyond failed breakout extreme",
                            "distance_pips": abs(entry_ideal - stop) * 10000,
                        },
                        targets=targets,
                        risk_reward_ratio=rrr,
                        confluence_factors=confluence_factors,
                        trapped_trader_potential="high",
                        market_condition_alignment="trapped traders forced to exit",
                        probability_score=confidence,
                    )

                    setups.append(setup)

        return setups

    def _scan_bpb(self) -> list[YTCSetup]:
        """Scan for BPB (Breakout Pullback) setups.

        BPB: Price sustains breakout, then pullbacks without retracing.
        Indicates strength; fewer trapped traders than TST.

        Returns:
            List of detected BPB setups.
        """
        setups = []

        if len(self.bars) < 15:
            return setups

        # Look for sustained breakouts followed by pullbacks
        for sr_level in self.sr_levels:
            level_price = sr_level.get("price", 0.0)

            if self._has_sustained_breakout(self.bars[-5:], level_price):
                pullback_legs = self._identify_pullback_structure(self.bars[-15:])

                if pullback_legs and self._pullback_holds_level(
                    pullback_legs, level_price
                ):
                    # Determine direction (continuation of breakout)
                    if self.trend_direction == "up":
                        direction = "long"
                        entry_ideal = pullback_legs[-1]["high"] * 1.001
                        stop = pullback_legs[-1]["low"] * 0.99
                    else:
                        direction = "short"
                        entry_ideal = pullback_legs[-1]["low"] * 0.999
                        stop = pullback_legs[-1]["high"] * 1.01

                    # Calculate targets
                    targets = self._calculate_targets(direction, level_price)

                    # Risk-to-reward ratio
                    if direction == "long":
                        rrr = (targets[0]["price"] - entry_ideal) / (
                            entry_ideal - stop
                        )
                    else:
                        rrr = (entry_ideal - targets[0]["price"]) / (
                            stop - entry_ideal
                        )

                    # Confidence score
                    base_score = 70.0
                    confluence_factors = [
                        "sustained breakout",
                        "pullback holds support",
                        "strength confirmation",
                    ]
                    confidence = base_score + 10

                    if self.trend_stage == "strong":
                        confidence += 15

                    confidence = min(100.0, confidence)

                    setup = self._create_setup(
                        setup_type=SetupType.BPB,
                        direction=direction,
                        sr_level=sr_level,
                        entry_zone={
                            "upper": pullback_legs[-1]["high"] * 1.005,
                            "lower": pullback_legs[-1]["low"] * 0.995,
                            "ideal": entry_ideal,
                            "trigger_bar_pattern": "resume breakout direction",
                        },
                        stop_loss={
                            "price": stop,
                            "placement_rationale": "below/above pullback extreme",
                            "distance_pips": abs(entry_ideal - stop) * 10000,
                        },
                        targets=targets,
                        risk_reward_ratio=rrr,
                        confluence_factors=confluence_factors,
                        trapped_trader_potential="moderate",
                        market_condition_alignment="pullback exhaustion setup",
                        probability_score=confidence,
                    )

                    setups.append(setup)

        return setups

    def _scan_pb(self) -> list[YTCSetup]:
        """Scan for PB (Simple Pullback) setups.

        PB: Single-leg pullback within established trend.
        Lower probability than CPB; order flow balance point.

        Returns:
            List of detected PB setups.
        """
        setups = []

        if len(self.bars) < 5:
            return setups

        swing_structure = self._identify_swing_structure(self.bars)

        if len(swing_structure) >= 3 and self._is_simple_pullback(
            swing_structure, self.trend_direction
        ):
            pullback_extreme = swing_structure[-1]

            # Entry after pullback reversal
            if self.trend_direction == "up":
                direction = "long"
                entry_ideal = pullback_extreme["low"] * 1.001
                stop = pullback_extreme["low"] * 0.99
                # Target is previous swing high
                target_price = swing_structure[-3]["high"]
            else:
                direction = "short"
                entry_ideal = pullback_extreme["high"] * 0.999
                stop = pullback_extreme["high"] * 1.01
                target_price = swing_structure[-3]["low"]

            # Create synthetic S/R level from pullback
            sr_level: SRLevel = {
                "price": pullback_extreme["low"]
                if self.trend_direction == "up"
                else pullback_extreme["high"],
                "type": "swing_point",
                "strength": "moderate",
            }

            # Risk-to-reward ratio
            if direction == "long":
                rrr = (target_price - entry_ideal) / (entry_ideal - stop)
            else:
                rrr = (entry_ideal - target_price) / (stop - entry_ideal)

            # Confidence score
            base_score = 65.0
            confluence_factors = [
                "trend alignment",
                "pullback reversal",
                "order flow balance",
            ]
            confidence = base_score

            if self.trend_strength == "strong":
                confidence += 10

            confidence = min(100.0, confidence)

            targets = [
                {
                    "level": "T1",
                    "price": target_price,
                    "type": "swing_point",
                    "r_multiple": rrr,
                }
            ]

            setup = self._create_setup(
                setup_type=SetupType.PB,
                direction=direction,
                sr_level=sr_level,
                entry_zone={
                    "upper": entry_ideal * 1.002,
                    "lower": entry_ideal * 0.998,
                    "ideal": entry_ideal,
                    "trigger_bar_pattern": "move resuming trend direction",
                },
                stop_loss={
                    "price": stop,
                    "placement_rationale": "beyond pullback extreme",
                    "distance_pips": abs(entry_ideal - stop) * 10000,
                },
                targets=targets,
                risk_reward_ratio=rrr,
                confluence_factors=confluence_factors,
                trapped_trader_potential="low",
                market_condition_alignment="single-leg pullback within trend",
                probability_score=confidence,
            )

            setups.append(setup)

        return setups

    def _scan_cpb(self) -> list[YTCSetup]:
        """Scan for CPB (Complex Pullback) setups.

        CPB: Multi-swing pullback within trend.
        Higher probability due to greater accumulation of trapped traders.

        Returns:
            List of detected CPB setups.
        """
        setups = []

        if len(self.bars) < 15:
            return setups

        swing_structure = self._identify_swing_structure(self.bars)

        if len(swing_structure) >= 5 and self._is_complex_pullback(
            swing_structure, self.trend_direction
        ):
            # Check if pullback structure is complete
            if self._structure_formation_complete(swing_structure[-3:]):
                # Get pullback extreme
                pullback_bars = swing_structure[-5:]
                if self.trend_direction == "up":
                    pullback_low = min(b["low"] for b in pullback_bars)
                    direction = "long"
                    entry_ideal = pullback_low * 1.001
                    stop = pullback_low * 0.98
                    target_price = swing_structure[-6]["high"]
                else:
                    pullback_high = max(b["high"] for b in pullback_bars)
                    direction = "short"
                    entry_ideal = pullback_high * 0.999
                    stop = pullback_high * 1.02
                    target_price = swing_structure[-6]["low"]

                # Create S/R level from pullback
                sr_level: SRLevel = {
                    "price": pullback_low
                    if self.trend_direction == "up"
                    else pullback_high,
                    "type": "swing_point",
                    "strength": "strong",
                }

                # Risk-to-reward ratio
                if direction == "long":
                    rrr = (target_price - entry_ideal) / (entry_ideal - stop)
                else:
                    rrr = (entry_ideal - target_price) / (stop - entry_ideal)

                # Confidence score - CPB is higher probability
                base_score = 80.0
                confluence_factors = [
                    "multi-swing pullback",
                    "trapped traders accumulated",
                    "structure confirmation",
                ]
                confidence = base_score + 15

                if self.trend_stage == "strong":
                    confidence += 10
                elif self.trend_stage == "slowing":
                    confidence += 5

                confidence = min(100.0, confidence)

                targets = [
                    {
                        "level": "T1",
                        "price": target_price,
                        "type": "swing_point",
                        "r_multiple": rrr,
                    }
                ]

                setup = self._create_setup(
                    setup_type=SetupType.CPB,
                    direction=direction,
                    sr_level=sr_level,
                    entry_zone={
                        "upper": entry_ideal * 1.003,
                        "lower": entry_ideal * 0.997,
                        "ideal": entry_ideal,
                        "trigger_bar_pattern": "break above/below pullback structure",
                    },
                    stop_loss={
                        "price": stop,
                        "placement_rationale": "beyond pullback structure extreme",
                        "distance_pips": abs(entry_ideal - stop) * 10000,
                    },
                    targets=targets,
                    risk_reward_ratio=rrr,
                    confluence_factors=confluence_factors,
                    trapped_trader_potential="high",
                    market_condition_alignment="multi-swing structure = more trapped traders",
                    probability_score=confidence,
                )

                setups.append(setup)

        return setups

    # Helper methods for setup detection

    def _identify_rejection_bars(self, bars: list[BarData]) -> bool:
        """Identify if rejection/pin bars exist (open strong, close weak or vice versa).

        Args:
            bars: List of price bars to analyze.

        Returns:
            True if rejection bars are found, False otherwise.
        """
        if not bars:
            return False

        for bar in bars:
            # Skip bars without required OHLC data
            if "close" not in bar or "open" not in bar:
                continue
            if "high" not in bar or "low" not in bar:
                continue

            body_size = abs(bar["close"] - bar["open"])
            wick_size = max(
                abs(bar["high"] - bar["close"]), abs(bar["open"] - bar["low"])
            )

            # Rejection bar: large wick relative to body
            if wick_size > body_size * 1.5:
                return True

        return False

    def _validates_against_trend(self, bars: list[BarData], trend: str) -> bool:
        """Check if bars validate against trend direction.

        Args:
            bars: Price bars to validate.
            trend: Trend direction ("up" or "down").

        Returns:
            True if bars validate against trend.
        """
        if not bars:
            return False

        if trend == "up":
            # Uptrend: rejection bars should have weak closes
            return any(b.get("close_position") == "low" for b in bars)
        else:
            # Downtrend: rejection bars should have strong closes down
            return any(b.get("close_position") == "high" for b in bars)

    def _has_breakout_bar(
        self, bar: BarData, level_price: float
    ) -> bool:
        """Check if a bar is a breakout bar (closes beyond level).

        Args:
            bar: Price bar to check.
            level_price: S/R level price.

        Returns:
            True if bar is a breakout bar.
        """
        return bar["close"] > level_price or bar["close"] < level_price

    def _has_weak_followthrough(self, bars: list[BarData]) -> bool:
        """Check if follow-through bars show weak momentum.

        Args:
            bars: Bars following a breakout.

        Returns:
            True if follow-through is weak.
        """
        if not bars:
            return True

        # Weak follow-through: decreasing bar sizes, weak closes
        weak_count = sum(
            1 for b in bars if b.get("body_strength") == "weak"
        )
        return weak_count >= len(bars) * 0.5

    def _pullback_through_level(
        self, bars: list[BarData], level_price: float
    ) -> bool:
        """Check if bars pullback through a level.

        Args:
            bars: Bars to check for pullback.
            level_price: Level to check against.

        Returns:
            True if pullback breaks through level.
        """
        return any(
            (b["low"] < level_price and b["close"] < level_price)
            or (b["high"] > level_price and b["close"] > level_price)
            for b in bars
        )

    def _has_sustained_breakout(
        self, bars: list[BarData], level_price: float
    ) -> bool:
        """Check if bars show sustained breakout past level.

        Args:
            bars: Bars to check.
            level_price: Level that was broken.

        Returns:
            True if breakout is sustained.
        """
        if not bars:
            return False

        breakout_bar = bars[0]
        follow_bars = bars[1:]

        # Check if initial bar breaks level
        if not (breakout_bar["high"] > level_price or breakout_bar["low"] < level_price):
            return False

        # Check if follow-through sustains it (doesn't immediately reverse)
        if follow_bars:
            strong_bars = sum(
                1 for b in follow_bars if b.get("body_strength") == "strong"
            )
            return strong_bars >= len(follow_bars) * 0.4

        return True

    def _identify_pullback_structure(
        self, bars: list[BarData]
    ) -> list[BarData]:
        """Identify pullback structure legs.

        Args:
            bars: Price bars.

        Returns:
            List of bars forming pullback structure.
        """
        if not bars:
            return []

        # Simple pullback detection: identify consecutive bars moving against trend
        pullback = []
        for bar in bars[-5:]:  # Last 5 bars
            if bar.get("body_strength") == "weak":
                pullback.append(bar)

        return pullback

    def _pullback_holds_level(
        self, pullback_bars: list[BarData], level_price: float
    ) -> bool:
        """Check if pullback structure holds above/below a level.

        Args:
            pullback_bars: Bars forming pullback.
            level_price: Level to check.

        Returns:
            True if pullback holds the level.
        """
        if not pullback_bars:
            return False

        # Check if no bar closes beyond the level
        return not any(b["close"] < level_price for b in pullback_bars) or not any(
            b["close"] > level_price for b in pullback_bars
        )

    def _identify_swing_structure(
        self, bars: list[BarData]
    ) -> list[BarData]:
        """Identify swing structure (swing highs and lows).

        Args:
            bars: Price bars.

        Returns:
            List of bars representing swing structure.
        """
        if len(bars) < 3:
            return []

        structure = []
        for i in range(1, len(bars) - 1):
            bar = bars[i]
            prev_bar = bars[i - 1]
            next_bar = bars[i + 1]

            # Swing high
            if bar["high"] > prev_bar["high"] and bar["high"] > next_bar["high"]:
                structure.append(bar)
            # Swing low
            elif bar["low"] < prev_bar["low"] and bar["low"] < next_bar["low"]:
                structure.append(bar)

        return structure

    def _is_simple_pullback(
        self, swing_structure: list[BarData], trend: str
    ) -> bool:
        """Check if swing structure represents a simple pullback.

        Args:
            swing_structure: List of swing bars.
            trend: Trend direction.

        Returns:
            True if structure is a simple pullback.
        """
        if len(swing_structure) < 3:
            return False

        # Simple pullback: 3 swings, one against the trend
        if trend == "up":
            # Should be: high, low, high (pullback low)
            return (
                swing_structure[-3].get("high")
                < swing_structure[-1].get("high")
            )
        else:
            # Should be: low, high, low (pullback high)
            return (
                swing_structure[-3].get("low")
                > swing_structure[-1].get("low")
            )

    def _is_complex_pullback(
        self, swing_structure: list[BarData], trend: str
    ) -> bool:
        """Check if swing structure represents a complex pullback.

        Args:
            swing_structure: List of swing bars.
            trend: Trend direction.

        Returns:
            True if structure is a complex pullback.
        """
        if len(swing_structure) < 5:
            return False

        # Complex pullback: 5+ swings with multiple legs against trend
        against_trend_count = 0

        for i in range(len(swing_structure) - 1):
            current = swing_structure[i]
            next_swing = swing_structure[i + 1]

            if trend == "up":
                if current["high"] > next_swing["high"]:
                    against_trend_count += 1
            else:
                if current["low"] < next_swing["low"]:
                    against_trend_count += 1

        return against_trend_count >= 2  # At least 2 legs against trend

    def _structure_formation_complete(
        self, recent_swings: list[BarData]
    ) -> bool:
        """Check if pullback structure formation is complete.

        Args:
            recent_swings: Recent swing bars.

        Returns:
            True if structure is complete.
        """
        if len(recent_swings) < 3:
            return False

        # Structure complete if last swing is higher/lower than previous
        # indicating potential reversal
        return True

    def _calculate_targets(
        self, direction: str, sr_level: float
    ) -> list[Target]:
        """Calculate profit targets based on direction and level.

        Args:
            direction: "long" or "short".
            sr_level: Support/resistance level.

        Returns:
            List of Target definitions.
        """
        # T1: Next S/R level
        if direction == "long":
            # Assume next resistance is proportional distance above current level
            t1_price = sr_level + (sr_level - self.swing_low)
        else:
            # Assume next support is proportional distance below current level
            t1_price = sr_level - (self.swing_high - sr_level)

        return [
            {
                "level": "T1",
                "price": t1_price,
                "type": "next_sr",
                "r_multiple": 1.0,
            }
        ]

    def _assess_market_conditions(self) -> str:
        """Assess overall market conditions for trading.

        Returns:
            Market condition verdict string.
        """
        if self.trend_stage == "strong" and self.volatility == "normal":
            return "Excellent conditions for trend-following setups (TST, PB, CPB)"
        elif self.trend_stage == "slowing":
            return "Good conditions for CPB (multi-swing = trapped traders)"
        elif self.trend_stage == "ranging":
            return "Caution: BOF/BPB less reliable in ranges"
        elif self.trend_stage == "volatile":
            return "Wider stops needed; watch for whipsaws"
        else:
            return "Neutral market conditions"

    def _define_entry_zone(
        self,
        direction: str,
        level: float,
        confluence_strength: str,
    ) -> EntryZone:
        """Define entry zone for a setup.

        Args:
            direction: "long" or "short".
            level: Key support/resistance level.
            confluence_strength: "strong", "moderate", or "weak".

        Returns:
            EntryZone definition.
        """
        # Adjust zone width based on confluence strength
        if confluence_strength == "strong":
            width_pct = 0.003  # 0.3%
        elif confluence_strength == "moderate":
            width_pct = 0.005  # 0.5%
        else:
            width_pct = 0.008  # 0.8%

        if direction == "long":
            ideal = level * 1.001
            upper = level * (1 + width_pct)
            lower = level * (1 - width_pct)
        else:
            ideal = level * 0.999
            upper = level * (1 + width_pct)
            lower = level * (1 - width_pct)

        return {
            "upper": upper,
            "lower": lower,
            "ideal": ideal,
            "trigger_bar_pattern": f"{direction} entry at {level}",
        }

    def _identify_confluence_factors(
        self,
        direction: str,
        level: float,
        bars: list[BarData],
    ) -> list[str]:
        """Identify confluence factors for a setup.

        Args:
            direction: "long" or "short".
            level: Key support/resistance level.
            bars: Price bars to analyze.

        Returns:
            List of confluence factors identified.
        """
        factors = []

        if not bars:
            return factors

        # Check trend alignment
        if direction == "long":
            strong_closes = sum(
                1 for b in bars if b.get("close_position") == "high"
            )
        else:
            strong_closes = sum(
                1 for b in bars if b.get("close_position") == "low"
            )

        if strong_closes >= len(bars) * 0.6:
            factors.append("close position alignment")

        # Check body strength
        strong_bodies = sum(
            1 for b in bars if b.get("body_strength") == "strong"
        )
        if strong_bodies >= len(bars) * 0.5:
            factors.append("strong body confirmation")

        # Check proximity to level
        bar_closes = [b.get("close", 0) for b in bars]
        if bar_closes:
            avg_close = sum(bar_closes) / len(bar_closes)
            if abs(avg_close - level) / level < 0.01:  # Within 1% of level
                factors.append("price proximity to level")

        return factors

    def _assess_trapped_trader_potential(
        self,
        direction: str,
        sr_level: float,
        rejection_bars: bool,
    ) -> str:
        """Assess trapped trader potential for a setup.

        Args:
            direction: "long" or "short".
            sr_level: Support/resistance level.
            rejection_bars: Whether rejection bars are present.

        Returns:
            Assessment: "high", "moderate", or "low".
        """
        # Trapped traders more likely with rejection bars
        if rejection_bars:
            return "high"

        # Check if we're in strong trend (implies more trapped traders)
        if self.trend_stage == "strong":
            return "moderate"

        return "low"

    def _rate_setup_quality(
        self,
        probability_score: float,
        confluence_count: int,
        risk_reward_ratio: float,
        min_confluence: int,
    ) -> str:
        """Rate the quality of a setup.

        Args:
            probability_score: Setup probability (0-100).
            confluence_count: Number of confluence factors.
            risk_reward_ratio: Risk-to-reward ratio.
            min_confluence: Minimum confluence factors required.

        Returns:
            Quality rating: "A", "B", or "C".
        """
        # A-rating: high probability + strong confluence + good R:R
        if (
            probability_score >= 80
            and confluence_count >= min_confluence + 1
            and risk_reward_ratio >= 2.5
        ):
            return "A"

        # B-rating: good probability + confluence met + acceptable R:R
        if (
            probability_score >= 70
            and confluence_count >= min_confluence
            and risk_reward_ratio >= 1.5
        ):
            return "B"

        # C-rating: everything else that passes minimum requirements
        return "C"

    def _create_setup(
        self,
        setup_type: SetupType,
        direction: str,
        sr_level: SRLevel,
        entry_zone: EntryZone,
        stop_loss: StopLoss,
        targets: list[Target],
        risk_reward_ratio: float,
        confluence_factors: list[str],
        trapped_trader_potential: str,
        market_condition_alignment: str,
        probability_score: float,
    ) -> YTCSetup:
        """Create a YTC setup object.

        Args:
            setup_type: Type of YTC setup.
            direction: Long or short.
            sr_level: Support/resistance level.
            entry_zone: Entry zone details.
            stop_loss: Stop loss details.
            targets: List of profit targets.
            risk_reward_ratio: Risk-to-reward ratio.
            confluence_factors: List of confluence factors.
            trapped_trader_potential: Trapped trader assessment.
            market_condition_alignment: Market condition description.
            probability_score: Setup probability score.

        Returns:
            YTCSetup object.
        """
        # Determine quality rating based on confluence and probability
        quality_rating = self._rate_setup_quality(
            probability_score=probability_score,
            confluence_count=len(confluence_factors),
            risk_reward_ratio=risk_reward_ratio,
            min_confluence=self.min_confluence,
        )

        # Ready to trade if confluence met and R:R acceptable
        ready = (
            len(confluence_factors) >= self.min_confluence
            and risk_reward_ratio >= self.min_risk_reward
            and probability_score >= 65
        )

        return {
            "setup_id": str(uuid.uuid4()),
            "type": setup_type,
            "direction": direction,
            "probability_score": round(probability_score, 1),
            "sr_level": sr_level,
            "entry_zone": entry_zone,
            "stop_loss": stop_loss,
            "targets": targets,
            "risk_reward_ratio": round(risk_reward_ratio, 2),
            "confluence_factors": confluence_factors,
            "trapped_trader_potential": trapped_trader_potential,
            "market_condition_alignment": market_condition_alignment,
            "ready_to_trade": ready,
            "quality_rating": quality_rating,
        }
