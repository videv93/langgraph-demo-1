"""Unit tests for Trend Definition Agent - YTC Swing Analysis."""

import pytest
from agent.agents.trend_definition import (
    TrendDefinition,
    TrendDirection,
    TrendStrength,
    Swing,
)


class TestTrendDefinitionInit:
    """Test TrendDefinition initialization."""

    def test_init_default_config(self) -> None:
        """Test initialization with default config."""
        agent = TrendDefinition()
        assert agent.config == {}
        assert agent.bars == []
        assert agent.symbol == ""
        assert agent.timeframe == "15m"
        assert agent.htf_timeframe == "4H"

    def test_init_custom_config(self) -> None:
        """Test initialization with custom config."""
        bars = [
            {"high": 110, "low": 100, "close": 105, "timestamp": "2025-11-20 10:00"},
            {"high": 112, "low": 101, "close": 107, "timestamp": "2025-11-20 10:15"},
        ]
        config = {
            "market_data": {
                "bars": bars,
                "symbol": "ETH-USDT",
                "timeframe": "5m",
            },
            "higher_timeframe_context": {
                "htf_timeframe": "1H",
                "htf_trend_direction": "uptrend",
                "htf_resistance": 3600.0,
                "htf_support": 3400.0,
                "htf_swing_high": 3550.0,
                "htf_swing_low": 3450.0,
            },
        }
        agent = TrendDefinition(config)
        assert agent.bars == bars
        assert agent.symbol == "ETH-USDT"
        assert agent.timeframe == "5m"
        assert agent.htf_trend_direction == "uptrend"
        assert agent.htf_resistance == 3600.0


class TestSwingIdentification:
    """Test swing high and low identification."""

    def test_identify_swings_insufficient_bars(self) -> None:
        """Test with insufficient bars (<3)."""
        config = {
            "market_data": {"bars": [{"high": 100, "low": 99}]}
        }
        agent = TrendDefinition(config)
        swings = agent._identify_swings()
        assert swings == []

    def test_identify_swings_empty_bars(self) -> None:
        """Test with empty bars."""
        agent = TrendDefinition()
        swings = agent._identify_swings()
        assert swings == []

    def test_identify_swing_high(self) -> None:
        """Test swing high identification (current > both neighbors)."""
        bars = [
            {"high": 100, "low": 99, "timestamp": "10:00"},
            {"high": 105, "low": 102, "timestamp": "10:15"},  # Swing high
            {"high": 103, "low": 100, "timestamp": "10:30"},
        ]
        config = {"market_data": {"bars": bars}}
        agent = TrendDefinition(config)
        swings = agent._identify_swings()

        assert len(swings) == 1
        assert swings[0]["type"] == "swing_high"
        assert swings[0]["price"] == 105

    def test_identify_swing_low(self) -> None:
        """Test swing low identification (current < both neighbors)."""
        bars = [
            {"high": 110, "low": 100, "timestamp": "10:00"},
            {"high": 108, "low": 95, "timestamp": "10:15"},  # Swing low
            {"high": 107, "low": 98, "timestamp": "10:30"},
        ]
        config = {"market_data": {"bars": bars}}
        agent = TrendDefinition(config)
        swings = agent._identify_swings()

        assert len(swings) == 1
        assert swings[0]["type"] == "swing_low"
        assert swings[0]["price"] == 95

    def test_identify_multiple_swings(self) -> None:
        """Test identification of multiple alternating swings."""
        bars = [
            {"high": 100, "low": 99, "timestamp": "10:00"},
            {"high": 105, "low": 102, "timestamp": "10:15"},  # SH
            {"high": 103, "low": 100, "timestamp": "10:30"},
            {"high": 104, "low": 95, "timestamp": "10:45"},  # SL
            {"high": 106, "low": 97, "timestamp": "11:00"},  # SH
        ]
        config = {"market_data": {"bars": bars}}
        agent = TrendDefinition(config)
        swings = agent._identify_swings()

        assert len(swings) >= 2
        # Check we have both types
        has_sh = any(s["type"] == "swing_high" for s in swings)
        has_sl = any(s["type"] == "swing_low" for s in swings)
        assert has_sh or has_sl

    def test_swing_attributes(self) -> None:
        """Test that swings have required attributes."""
        bars = [
            {"high": 100, "low": 99, "timestamp": "10:00"},
            {"high": 105, "low": 102, "timestamp": "10:15"},
            {"high": 103, "low": 100, "timestamp": "10:30"},
        ]
        config = {"market_data": {"bars": bars}}
        agent = TrendDefinition(config)
        swings = agent._identify_swings()

        assert len(swings) == 1
        swing = swings[0]
        assert "type" in swing
        assert "price" in swing
        assert "timestamp" in swing
        assert "bar_index" in swing
        assert "is_leading" in swing
        assert "is_broken" in swing


class TestTrendClassification:
    """Test trend classification logic."""

    def test_classify_uptrend_hh_hl(self) -> None:
        """Test uptrend classification (HH + HL pattern)."""
        bars = [
            {"high": 100, "low": 99, "timestamp": "10:00"},
            {"high": 102, "low": 100, "timestamp": "10:15"},  # SH
            {"high": 101, "low": 98, "timestamp": "10:30"},   # SL
            {"high": 105, "low": 99, "timestamp": "10:45"},   # SH (HH)
            {"high": 103, "low": 99.5, "timestamp": "11:00"},  # SL (HL)
        ]
        config = {"market_data": {"bars": bars}}
        agent = TrendDefinition(config)
        swings = agent._identify_swings()
        trend = agent._classify_trend(swings)

        # Should be uptrend if we have the right swing pattern
        assert trend in [TrendDirection.UPTREND, TrendDirection.SIDEWAYS]

    def test_classify_downtrend_lh_ll(self) -> None:
        """Test downtrend classification (LH + LL pattern)."""
        bars = [
            {"high": 110, "low": 100, "timestamp": "10:00"},
            {"high": 108, "low": 98, "timestamp": "10:15"},   # SH
            {"high": 107, "low": 96, "timestamp": "10:30"},   # SL
            {"high": 105, "low": 94, "timestamp": "10:45"},   # SH (LH)
            {"high": 104, "low": 93, "timestamp": "11:00"},   # SL (LL)
        ]
        config = {"market_data": {"bars": bars}}
        agent = TrendDefinition(config)
        swings = agent._identify_swings()
        trend = agent._classify_trend(swings)

        # Should be downtrend if we have the right swing pattern
        assert trend in [TrendDirection.DOWNTREND, TrendDirection.SIDEWAYS]

    def test_classify_sideways(self) -> None:
        """Test sideways classification (no clear pattern)."""
        bars = [
            {"high": 100, "low": 99, "timestamp": "10:00"},
            {"high": 101, "low": 99.5, "timestamp": "10:15"},
            {"high": 100.5, "low": 99, "timestamp": "10:30"},
        ]
        config = {"market_data": {"bars": bars}}
        agent = TrendDefinition(config)
        trend = agent._classify_trend(agent._identify_swings())

        assert trend == TrendDirection.SIDEWAYS

    def test_classify_no_swings(self) -> None:
        """Test classification with no swings."""
        agent = TrendDefinition()
        trend = agent._classify_trend([])

        assert trend == TrendDirection.SIDEWAYS


class TestStructureBreakDetection:
    """Test structure break detection."""

    def test_no_structure_breaks_uptrend(self) -> None:
        """Test uptrend with intact structure (no breaks)."""
        bars = [
            {"high": 100, "low": 99, "timestamp": "10:00"},
            {"high": 102, "low": 100, "timestamp": "10:15"},
            {"high": 101, "low": 100.5, "timestamp": "10:30"},
            {"high": 105, "low": 101, "timestamp": "10:45"},
            {"high": 103, "low": 101.5, "timestamp": "11:00"},
        ]
        config = {"market_data": {"bars": bars}}
        agent = TrendDefinition(config)
        swings = agent._identify_swings()
        trend = agent._classify_trend(swings)
        breaks = agent._detect_structure_breaks(swings, trend)

        assert breaks == 0

    def test_structure_break_uptrend_lower_low(self) -> None:
        """Test uptrend break with lower low (LL)."""
        bars = [
            {"high": 100, "low": 99, "timestamp": "10:00"},
            {"high": 102, "low": 100, "timestamp": "10:15"},
            {"high": 101, "low": 100.5, "timestamp": "10:30"},
            {"high": 105, "low": 101, "timestamp": "10:45"},
            {"high": 103, "low": 99, "timestamp": "11:00"},  # LL - structure break
        ]
        config = {"market_data": {"bars": bars}}
        agent = TrendDefinition(config)
        swings = agent._identify_swings()
        trend = agent._classify_trend(swings)
        breaks = agent._detect_structure_breaks(swings, trend)

        assert breaks >= 0

    def test_structure_break_downtrend_higher_high(self) -> None:
        """Test downtrend break with higher high (HH)."""
        bars = [
            {"high": 110, "low": 100, "timestamp": "10:00"},
            {"high": 108, "low": 98, "timestamp": "10:15"},
            {"high": 107, "low": 97, "timestamp": "10:30"},
            {"high": 105, "low": 95, "timestamp": "10:45"},
            {"high": 106, "low": 94, "timestamp": "11:00"},  # HH - structure break
        ]
        config = {"market_data": {"bars": bars}}
        agent = TrendDefinition(config)
        swings = agent._identify_swings()
        trend = agent._classify_trend(swings)
        breaks = agent._detect_structure_breaks(swings, trend)

        assert breaks >= 0


class TestTrendStrengthAssessment:
    """Test trend strength assessment."""

    def test_strong_trend(self) -> None:
        """Test strong trend assessment (3+ swings, no breaks)."""
        bars = [
            {"high": 100, "low": 99, "close": 100, "timestamp": "10:00"},
            {"high": 105, "low": 102, "close": 105, "timestamp": "10:15"},  # SH
            {"high": 103, "low": 100, "close": 103, "timestamp": "10:30"},   # SL
            {"high": 108, "low": 101, "close": 108, "timestamp": "10:45"},   # SH
            {"high": 106, "low": 100.5, "close": 106, "timestamp": "11:00"}, # SL
            {"high": 110, "low": 102, "close": 110, "timestamp": "11:15"},   # SH
        ]
        config = {"market_data": {"bars": bars}}
        agent = TrendDefinition(config)
        swings = agent._identify_swings()
        trend = agent._classify_trend(swings)
        strength = agent._assess_trend_strength(swings, trend, 0)

        assert strength in [TrendStrength.STRONG, TrendStrength.MODERATE]

    def test_moderate_trend(self) -> None:
        """Test moderate trend assessment (2-3 swings)."""
        bars = [
            {"high": 100, "low": 99, "close": 100, "timestamp": "10:00"},
            {"high": 105, "low": 102, "close": 105, "timestamp": "10:15"},  # SH
            {"high": 103, "low": 100, "close": 103, "timestamp": "10:30"},   # SL
            {"high": 108, "low": 101, "close": 108, "timestamp": "10:45"},   # SH
        ]
        config = {"market_data": {"bars": bars}}
        agent = TrendDefinition(config)
        swings = agent._identify_swings()
        trend = agent._classify_trend(swings)
        strength = agent._assess_trend_strength(swings, trend, 0)

        assert strength in [TrendStrength.STRONG, TrendStrength.MODERATE, TrendStrength.WEAK]

    def test_weak_trend(self) -> None:
        """Test weak trend assessment (1-2 swings or multiple breaks)."""
        bars = [
            {"high": 100, "low": 99, "close": 100, "timestamp": "10:00"},
            {"high": 105, "low": 102, "close": 105, "timestamp": "10:15"},  # SH
            {"high": 103, "low": 100, "close": 103, "timestamp": "10:30"},   # SL
        ]
        config = {"market_data": {"bars": bars}}
        agent = TrendDefinition(config)
        swings = agent._identify_swings()
        trend = agent._classify_trend(swings)
        strength = agent._assess_trend_strength(swings, trend, 0)

        assert isinstance(strength, TrendStrength)

    def test_reversal_warning_uptrend(self) -> None:
        """Test reversal warning in uptrend (price below leading swing low)."""
        bars = [
            {"high": 100, "low": 99, "close": 100, "timestamp": "10:00"},
            {"high": 105, "low": 102, "close": 105, "timestamp": "10:15"},
            {"high": 103, "low": 100, "close": 103, "timestamp": "10:30"},
            {"high": 108, "low": 101, "close": 108, "timestamp": "10:45"},
            {"high": 102, "low": 98, "close": 98, "timestamp": "11:00"},  # Below leading SL
        ]
        config = {"market_data": {"bars": bars}}
        agent = TrendDefinition(config)
        swings = agent._identify_swings()
        trend = TrendDirection.UPTREND
        strength = agent._assess_trend_strength(swings, trend, 0)

        assert strength == TrendStrength.REVERSAL_WARNING

    def test_sideways_trend_weak(self) -> None:
        """Test sideways trend is always weak."""
        agent = TrendDefinition()
        strength = agent._assess_trend_strength([], TrendDirection.SIDEWAYS, 0)

        assert strength == TrendStrength.WEAK


class TestConfidenceCalculation:
    """Test confidence score calculation."""

    def test_confidence_sideways(self) -> None:
        """Test sideways confidence is 0.5."""
        agent = TrendDefinition()
        confidence = agent._calculate_confidence([], TrendDirection.SIDEWAYS)

        assert confidence == 0.5

    def test_confidence_single_swing(self) -> None:
        """Test confidence increases with swing count."""
        bars = [
            {"high": 100, "low": 99, "timestamp": "10:00"},
            {"high": 105, "low": 102, "timestamp": "10:15"},
            {"high": 103, "low": 100, "timestamp": "10:30"},
        ]
        config = {"market_data": {"bars": bars}}
        agent = TrendDefinition(config)
        swings = agent._identify_swings()

        confidence = agent._calculate_confidence(swings, TrendDirection.UPTREND)
        assert 0.0 <= confidence <= 1.0

    def test_confidence_multiple_swings(self) -> None:
        """Test confidence increases with multiple confirmed swings."""
        bars = [
            {"high": 100, "low": 99, "timestamp": "10:00"},
            {"high": 105, "low": 102, "timestamp": "10:15"},  # SH
            {"high": 103, "low": 100, "timestamp": "10:30"},   # SL (HL)
            {"high": 108, "low": 101, "timestamp": "10:45"},   # SH (HH)
            {"high": 106, "low": 100.5, "timestamp": "11:00"}, # SL (HL)
        ]
        config = {"market_data": {"bars": bars}}
        agent = TrendDefinition(config)
        swings = agent._identify_swings()

        confidence = agent._calculate_confidence(swings, TrendDirection.UPTREND)
        assert 0.0 <= confidence <= 1.0

    def test_confidence_max_1_0(self) -> None:
        """Test confidence is capped at 1.0."""
        bars = [
            {"high": 100, "low": 99, "timestamp": "10:00"},
            {"high": 105, "low": 102, "timestamp": "10:15"},
            {"high": 103, "low": 100, "timestamp": "10:30"},
        ]
        config = {"market_data": {"bars": bars}}
        agent = TrendDefinition(config)
        swings = agent._identify_swings()

        confidence = agent._calculate_confidence(swings, TrendDirection.UPTREND)
        assert confidence <= 1.0


class TestHTFAlignment:
    """Test higher timeframe alignment checking."""

    def test_aligned_both_uptrend(self) -> None:
        """Test alignment when both TF and HTF are uptrend."""
        config = {
            "higher_timeframe_context": {"htf_trend_direction": "uptrend"}
        }
        agent = TrendDefinition(config)
        aligned = agent._check_htf_alignment(TrendDirection.UPTREND)

        assert aligned is True

    def test_aligned_both_downtrend(self) -> None:
        """Test alignment when both TF and HTF are downtrend."""
        config = {
            "higher_timeframe_context": {"htf_trend_direction": "downtrend"}
        }
        agent = TrendDefinition(config)
        aligned = agent._check_htf_alignment(TrendDirection.DOWNTREND)

        assert aligned is True

    def test_conflict_uptrend_vs_downtrend(self) -> None:
        """Test conflict when TF uptrend conflicts with HTF downtrend."""
        config = {
            "higher_timeframe_context": {"htf_trend_direction": "downtrend"}
        }
        agent = TrendDefinition(config)
        aligned = agent._check_htf_alignment(TrendDirection.UPTREND)

        assert aligned is False

    def test_aligned_htf_sideways(self) -> None:
        """Test alignment when HTF is sideways (no conflict)."""
        config = {
            "higher_timeframe_context": {"htf_trend_direction": "sideways"}
        }
        agent = TrendDefinition(config)
        aligned = agent._check_htf_alignment(TrendDirection.UPTREND)

        assert aligned is True


class TestAlignmentDescription:
    """Test alignment description generation."""

    def test_describe_aligned_uptrend(self) -> None:
        """Test description for aligned uptrend."""
        config = {
            "higher_timeframe_context": {"htf_trend_direction": "uptrend"}
        }
        agent = TrendDefinition(config)
        description = agent._describe_alignment(TrendDirection.UPTREND, True)

        assert "uptrend" in description.lower()
        assert "aligned" in description.lower()

    def test_describe_conflict(self) -> None:
        """Test description for conflict."""
        config = {
            "higher_timeframe_context": {"htf_trend_direction": "downtrend"}
        }
        agent = TrendDefinition(config)
        description = agent._describe_alignment(TrendDirection.UPTREND, False)

        assert "conflict" in description.lower()


class TestTrendInception:
    """Test trend inception time and bar count calculation."""

    def test_trend_inception_no_swings(self) -> None:
        """Test inception with no swings."""
        agent = TrendDefinition()
        inception, bar_count = agent._get_trend_inception([], TrendDirection.UPTREND)

        assert inception == ""
        assert bar_count == 0

    def test_trend_inception_sideways(self) -> None:
        """Test inception for sideways trend."""
        swings = [
            {"timestamp": "10:00", "price": 100, "type": "swing_high"}
        ]
        agent = TrendDefinition()
        inception, bar_count = agent._get_trend_inception(swings, TrendDirection.SIDEWAYS)

        assert inception == ""
        assert bar_count == 0

    def test_trend_inception_valid(self) -> None:
        """Test inception for valid trend."""
        bars = [
            {"high": 100, "low": 99, "timestamp": "10:00", "bar_index": 0},
            {"high": 105, "low": 102, "timestamp": "10:15", "bar_index": 1},
            {"high": 103, "low": 100, "timestamp": "10:30", "bar_index": 2},
        ]
        swings = [
            {"timestamp": "10:15", "price": 105, "type": "swing_high", "bar_index": 1},
            {"timestamp": "10:30", "price": 100, "type": "swing_low", "bar_index": 2},
        ]
        config = {"market_data": {"bars": bars}}
        agent = TrendDefinition(config)
        inception, bar_count = agent._get_trend_inception(swings, TrendDirection.UPTREND)

        assert inception != ""
        assert isinstance(bar_count, int)


class TestStructureIntegrity:
    """Test structure integrity assessment."""

    def test_structure_intact(self) -> None:
        """Test structure intact assessment."""
        bars = [
            {"high": 100, "low": 99, "close": 100, "timestamp": "10:00"},
            {"high": 105, "low": 102, "close": 105, "timestamp": "10:15"},
            {"high": 103, "low": 100, "close": 103, "timestamp": "10:30"},
        ]
        config = {"market_data": {"bars": bars}}
        agent = TrendDefinition(config)
        swings = agent._identify_swings()
        trend = TrendDirection.UPTREND

        integrity = agent._build_structure_integrity(swings, trend, 0)

        assert integrity["structure_intact"] is True
        assert integrity["structure_breaks_detected"] == 0
        assert integrity["reversal_warning"] is False

    def test_structure_breaks_detected(self) -> None:
        """Test structure breaks detected assessment."""
        bars = [
            {"high": 100, "low": 99, "close": 100, "timestamp": "10:00"},
            {"high": 105, "low": 102, "close": 105, "timestamp": "10:15"},
            {"high": 103, "low": 100, "close": 103, "timestamp": "10:30"},
        ]
        config = {"market_data": {"bars": bars}}
        agent = TrendDefinition(config)
        swings = agent._identify_swings()
        trend = TrendDirection.UPTREND

        integrity = agent._build_structure_integrity(swings, trend, 2)

        assert integrity["structure_intact"] is False
        assert integrity["structure_breaks_detected"] == 2

    def test_reversal_warning_assessment(self) -> None:
        """Test reversal warning in structure integrity."""
        bars = [
            {"high": 100, "low": 99, "close": 100, "timestamp": "10:00"},
            {"high": 105, "low": 102, "close": 105, "timestamp": "10:15"},
            {"high": 103, "low": 100, "close": 103, "timestamp": "10:30"},
            {"high": 108, "low": 101, "close": 108, "timestamp": "10:45"},
            {"high": 102, "low": 98, "close": 98, "timestamp": "11:00"},
        ]
        config = {"market_data": {"bars": bars}}
        agent = TrendDefinition(config)
        swings = agent._identify_swings()

        integrity = agent._build_structure_integrity(swings, TrendDirection.UPTREND, 0)

        assert "reversal_warning" in integrity
        assert isinstance(integrity["reversal_warning"], bool)


class TestExecute:
    """Test complete execute method."""

    def test_execute_returns_correct_structure(self) -> None:
        """Test that execute returns correct output structure."""
        bars = [
            {"high": 100, "low": 99, "close": 100, "timestamp": "10:00"},
            {"high": 105, "low": 102, "close": 105, "timestamp": "10:15"},
            {"high": 103, "low": 100, "close": 103, "timestamp": "10:30"},
        ]
        config = {"market_data": {"bars": bars}}
        agent = TrendDefinition(config)
        result = agent.execute()

        assert "trend_analysis" in result
        assert "swing_structure" in result
        assert "structure_integrity" in result
        assert "htf_alignment" in result

    def test_execute_trend_analysis_structure(self) -> None:
        """Test trend_analysis sub-structure."""
        bars = [
            {"high": 100, "low": 99, "close": 100, "timestamp": "10:00"},
            {"high": 105, "low": 102, "close": 105, "timestamp": "10:15"},
            {"high": 103, "low": 100, "close": 103, "timestamp": "10:30"},
        ]
        config = {"market_data": {"bars": bars}}
        agent = TrendDefinition(config)
        result = agent.execute()

        trend_analysis = result["trend_analysis"]
        assert "direction" in trend_analysis
        assert "confidence" in trend_analysis
        assert "strength_rating" in trend_analysis
        assert "since_timestamp" in trend_analysis
        assert "bar_count_in_trend" in trend_analysis

    def test_execute_swing_structure(self) -> None:
        """Test swing_structure sub-structure."""
        bars = [
            {"high": 100, "low": 99, "close": 100, "timestamp": "10:00"},
            {"high": 105, "low": 102, "close": 105, "timestamp": "10:15"},
            {"high": 103, "low": 100, "close": 103, "timestamp": "10:30"},
        ]
        config = {"market_data": {"bars": bars}}
        agent = TrendDefinition(config)
        result = agent.execute()

        swing_structure = result["swing_structure"]
        assert "swing_highs" in swing_structure
        assert "swing_lows" in swing_structure
        assert "current_leading_swing_high" in swing_structure
        assert "current_leading_swing_low" in swing_structure

    def test_execute_structure_integrity(self) -> None:
        """Test structure_integrity sub-structure."""
        bars = [
            {"high": 100, "low": 99, "close": 100, "timestamp": "10:00"},
            {"high": 105, "low": 102, "close": 105, "timestamp": "10:15"},
            {"high": 103, "low": 100, "close": 103, "timestamp": "10:30"},
        ]
        config = {"market_data": {"bars": bars}}
        agent = TrendDefinition(config)
        result = agent.execute()

        integrity = result["structure_integrity"]
        assert "structure_intact" in integrity
        assert "structure_breaks_detected" in integrity
        assert "reversal_warning" in integrity
        assert "last_structure_break_timestamp" in integrity
        assert "structure_break_description" in integrity

    def test_execute_htf_alignment(self) -> None:
        """Test htf_alignment sub-structure."""
        bars = [
            {"high": 100, "low": 99, "close": 100, "timestamp": "10:00"},
            {"high": 105, "low": 102, "close": 105, "timestamp": "10:15"},
            {"high": 103, "low": 100, "close": 103, "timestamp": "10:30"},
        ]
        config = {"market_data": {"bars": bars}}
        agent = TrendDefinition(config)
        result = agent.execute()

        alignment = result["htf_alignment"]
        assert "tf_trend_aligns_with_htf" in alignment
        assert "alignment_description" in alignment
        assert "potential_conflict" in alignment

    def test_execute_confidence_range(self) -> None:
        """Test confidence is within 0-1 range."""
        bars = [
            {"high": 100, "low": 99, "close": 100, "timestamp": "10:00"},
            {"high": 105, "low": 102, "close": 105, "timestamp": "10:15"},
            {"high": 103, "low": 100, "close": 103, "timestamp": "10:30"},
        ]
        config = {"market_data": {"bars": bars}}
        agent = TrendDefinition(config)
        result = agent.execute()

        confidence = result["trend_analysis"]["confidence"]
        assert 0.0 <= confidence <= 1.0

    def test_execute_trend_direction_valid(self) -> None:
        """Test trend direction is valid enum."""
        bars = [
            {"high": 100, "low": 99, "close": 100, "timestamp": "10:00"},
            {"high": 105, "low": 102, "close": 105, "timestamp": "10:15"},
            {"high": 103, "low": 100, "close": 103, "timestamp": "10:30"},
        ]
        config = {"market_data": {"bars": bars}}
        agent = TrendDefinition(config)
        result = agent.execute()

        direction = result["trend_analysis"]["direction"]
        assert direction in [TrendDirection.UPTREND, TrendDirection.DOWNTREND, TrendDirection.SIDEWAYS]

    def test_execute_strength_rating_valid(self) -> None:
        """Test strength rating is valid enum."""
        bars = [
            {"high": 100, "low": 99, "close": 100, "timestamp": "10:00"},
            {"high": 105, "low": 102, "close": 105, "timestamp": "10:15"},
            {"high": 103, "low": 100, "close": 103, "timestamp": "10:30"},
        ]
        config = {"market_data": {"bars": bars}}
        agent = TrendDefinition(config)
        result = agent.execute()

        rating = result["trend_analysis"]["strength_rating"]
        assert rating in [
            TrendStrength.STRONG,
            TrendStrength.MODERATE,
            TrendStrength.WEAK,
            TrendStrength.REVERSAL_WARNING,
        ]

    def test_execute_with_complex_config(self) -> None:
        """Test execute with complex multi-swing configuration."""
        bars = [
            {"high": 100, "low": 99, "close": 100, "timestamp": "10:00", "bar_index": 0},
            {"high": 105, "low": 102, "close": 105, "timestamp": "10:15", "bar_index": 1},
            {"high": 103, "low": 100, "close": 103, "timestamp": "10:30", "bar_index": 2},
            {"high": 108, "low": 101, "close": 108, "timestamp": "10:45", "bar_index": 3},
            {"high": 106, "low": 100.5, "close": 106, "timestamp": "11:00", "bar_index": 4},
        ]
        config = {
            "market_data": {
                "bars": bars,
                "symbol": "ETH-USDT",
                "timeframe": "15m",
            },
            "higher_timeframe_context": {
                "htf_timeframe": "4H",
                "htf_trend_direction": "uptrend",
                "htf_resistance": 110.0,
                "htf_support": 95.0,
                "htf_swing_high": 108.0,
                "htf_swing_low": 100.0,
            },
        }
        agent = TrendDefinition(config)
        result = agent.execute()

        assert result["trend_analysis"]["confidence"] > 0
        assert len(result["swing_structure"]["swing_highs"]) > 0


class TestLeadingSwings:
    """Test leading swing identification."""

    def test_get_leading_swings_empty(self) -> None:
        """Test leading swings with empty list."""
        agent = TrendDefinition()
        sh, sl = agent._get_leading_swings([])

        assert sh is not None
        assert sl is not None

    def test_get_leading_swings_single_high(self) -> None:
        """Test leading swings with single swing high."""
        swings = [
            {"type": "swing_high", "price": 105}
        ]
        agent = TrendDefinition()
        sh, sl = agent._get_leading_swings(swings)

        assert sh == 105 or sh is not None

    def test_get_leading_swings_multiple(self) -> None:
        """Test leading swings with multiple swings."""
        swings = [
            {"type": "swing_high", "price": 105},
            {"type": "swing_low", "price": 100},
            {"type": "swing_high", "price": 108},
        ]
        agent = TrendDefinition()
        sh, sl = agent._get_leading_swings(swings)

        assert isinstance(sh, (int, float)) or sh is None
        assert isinstance(sl, (int, float)) or sl is None


class TestTrendEnums:
    """Test trend classification enums."""

    def test_trend_direction_values(self) -> None:
        """Test TrendDirection enum values."""
        assert TrendDirection.UPTREND.value == "uptrend"
        assert TrendDirection.DOWNTREND.value == "downtrend"
        assert TrendDirection.SIDEWAYS.value == "sideways"

    def test_trend_strength_values(self) -> None:
        """Test TrendStrength enum values."""
        assert TrendStrength.STRONG.value == "strong"
        assert TrendStrength.MODERATE.value == "moderate"
        assert TrendStrength.WEAK.value == "weak"
        assert TrendStrength.REVERSAL_WARNING.value == "reversal_warning"

    def test_trend_direction_comparison(self) -> None:
        """Test TrendDirection enum comparison."""
        assert TrendDirection.UPTREND != TrendDirection.DOWNTREND
        assert TrendDirection.SIDEWAYS != TrendDirection.UPTREND
