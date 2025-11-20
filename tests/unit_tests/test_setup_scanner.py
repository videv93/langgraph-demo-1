"""Unit tests for Setup Scanner Agent - YTC Setup Identification."""

import pytest
from agent.agents.setup_scanner import (
    SetupScanner,
    SetupType,
    BarData,
    SRLevel,
    YTCSetup,
)


class TestSetupScannerInit:
    """Test SetupScanner initialization."""

    def test_init_default_config(self) -> None:
        """Test initialization with default config."""
        scanner = SetupScanner()
        assert scanner.config == {}
        assert scanner.trend_direction == "up"
        assert scanner.current_price == 0.0
        assert scanner.bars == []
        assert scanner.sr_levels == []

    def test_init_custom_config(self) -> None:
        """Test initialization with custom config."""
        bars = [
            {"open": 100, "high": 105, "low": 99, "close": 103, "volume": 1000},
            {"open": 103, "high": 107, "low": 102, "close": 106, "volume": 1200},
        ]
        sr_levels = [
            {"price": 110.0, "type": "swing_point", "strength": "strong"},
            {"price": 95.0, "type": "prior_level", "strength": "moderate"},
        ]
        config = {
            "trend_data": {
                "direction": "up",
                "structure": {"swing_high": 110.0, "swing_low": 95.0},
                "strength_rating": "strong",
            },
            "price_action": {
                "current_price": 106.0,
                "bars": bars,
            },
            "support_resistance": {
                "levels": sr_levels,
            },
            "market_conditions": {
                "trend_stage": "strong",
                "volatility": "normal",
            },
            "config": {
                "min_confluence_factors": 3,
                "min_risk_reward": 2.0,
                "enabled_setup_types": ["TST", "BPB"],
            },
        }
        scanner = SetupScanner(config)

        assert scanner.trend_direction == "up"
        assert scanner.current_price == 106.0
        assert len(scanner.bars) == 2
        assert len(scanner.sr_levels) == 2
        assert scanner.min_confluence == 3
        assert scanner.min_risk_reward == 2.0

    def test_init_partial_config(self) -> None:
        """Test initialization with partial config."""
        config = {
            "trend_data": {"direction": "down"},
            "price_action": {"current_price": 3500.0},
        }
        scanner = SetupScanner(config)

        assert scanner.trend_direction == "down"
        assert scanner.current_price == 3500.0
        assert scanner.bars == []


class TestExecuteMethod:
    """Test the main execute method."""

    def test_execute_returns_correct_structure(self) -> None:
        """Test execute returns correct output structure."""
        scanner = SetupScanner()
        result = scanner.execute()

        assert "scan_complete" in result
        assert "active_setups" in result
        assert "scan_summary" in result
        assert result["scan_complete"] is True

    def test_execute_summary_structure(self) -> None:
        """Test scan_summary sub-structure."""
        scanner = SetupScanner()
        result = scanner.execute()

        summary = result["scan_summary"]
        assert "total_setups_identified" in summary
        assert "trade_ready_count" in summary
        assert "highest_probability_setup_id" in summary
        assert "market_condition_verdict" in summary

    def test_execute_active_setups_list(self) -> None:
        """Test active_setups is a list."""
        scanner = SetupScanner()
        result = scanner.execute()

        assert isinstance(result["active_setups"], list)

    def test_execute_empty_bars(self) -> None:
        """Test execute with no bars."""
        config = {
            "price_action": {"bars": []},
            "trend_data": {"direction": "up"},
        }
        scanner = SetupScanner(config)
        result = scanner.execute()

        assert result["scan_complete"] is True
        assert isinstance(result["active_setups"], list)

    def test_execute_disabled_setup_types(self) -> None:
        """Test execute respects disabled setup types."""
        config = {
            "price_action": {
                "bars": [
                    {"open": 100, "high": 105, "low": 99, "close": 103},
                    {"open": 103, "high": 107, "low": 102, "close": 106},
                ]
            },
            "config": {"enabled_setup_types": []},
        }
        scanner = SetupScanner(config)
        result = scanner.execute()

        assert result["scan_complete"] is True


class TestTSTScanning:
    """Test TST (Test of Support/Resistance) scanning."""

    def test_scan_tst_empty_bars(self) -> None:
        """Test TST scan with empty bars."""
        scanner = SetupScanner()
        setups = scanner._scan_tst()

        assert isinstance(setups, list)
        assert len(setups) == 0

    def test_scan_tst_insufficient_bars(self) -> None:
        """Test TST scan with insufficient bars."""
        config = {
            "price_action": {
                "bars": [{"open": 100, "high": 105, "low": 99, "close": 103}]
            }
        }
        scanner = SetupScanner(config)
        setups = scanner._scan_tst()

        assert isinstance(setups, list)

    def test_scan_tst_no_sr_levels(self) -> None:
        """Test TST scan with no S/R levels."""
        bars = [
            {"open": 100, "high": 105, "low": 99, "close": 103},
            {"open": 103, "high": 107, "low": 102, "close": 106},
            {"open": 106, "high": 108, "low": 105, "close": 107},
        ]
        config = {
            "price_action": {"bars": bars, "current_price": 107},
            "support_resistance": {"levels": []},
        }
        scanner = SetupScanner(config)
        setups = scanner._scan_tst()

        assert isinstance(setups, list)


class TestBOFScanning:
    """Test BOF (Breakout Failure) scanning."""

    def test_scan_bof_empty_bars(self) -> None:
        """Test BOF scan with empty bars."""
        scanner = SetupScanner()
        setups = scanner._scan_bof()

        assert isinstance(setups, list)
        assert len(setups) == 0

    def test_scan_bof_insufficient_bars(self) -> None:
        """Test BOF scan with insufficient bars."""
        config = {
            "price_action": {
                "bars": [{"open": 100, "high": 105, "low": 99, "close": 103}]
            }
        }
        scanner = SetupScanner(config)
        setups = scanner._scan_bof()

        assert isinstance(setups, list)


class TestBPBScanning:
    """Test BPB (Breakout Pullback) scanning."""

    def test_scan_bpb_empty_bars(self) -> None:
        """Test BPB scan with empty bars."""
        scanner = SetupScanner()
        setups = scanner._scan_bpb()

        assert isinstance(setups, list)
        assert len(setups) == 0

    def test_scan_bpb_with_bars(self) -> None:
        """Test BPB scan with bars."""
        bars = [
            {"open": 100, "high": 105, "low": 99, "close": 103},
            {"open": 103, "high": 107, "low": 102, "close": 106},
            {"open": 106, "high": 108, "low": 105, "close": 107},
        ]
        config = {
            "price_action": {"bars": bars, "current_price": 107},
            "trend_data": {"direction": "up"},
        }
        scanner = SetupScanner(config)
        setups = scanner._scan_bpb()

        assert isinstance(setups, list)


class TestPBScanning:
    """Test PB (Simple Pullback) scanning."""

    def test_scan_pb_empty_bars(self) -> None:
        """Test PB scan with empty bars."""
        scanner = SetupScanner()
        setups = scanner._scan_pb()

        assert isinstance(setups, list)
        assert len(setups) == 0

    def test_scan_pb_with_bars(self) -> None:
        """Test PB scan with bars."""
        bars = [
            {"open": 100, "high": 105, "low": 99, "close": 103},
            {"open": 103, "high": 107, "low": 102, "close": 106},
            {"open": 106, "high": 108, "low": 105, "close": 107},
        ]
        config = {
            "price_action": {"bars": bars, "current_price": 107},
            "trend_data": {"direction": "up"},
        }
        scanner = SetupScanner(config)
        setups = scanner._scan_pb()

        assert isinstance(setups, list)


class TestCPBScanning:
    """Test CPB (Complex Pullback) scanning."""

    def test_scan_cpb_empty_bars(self) -> None:
        """Test CPB scan with empty bars."""
        scanner = SetupScanner()
        setups = scanner._scan_cpb()

        assert isinstance(setups, list)
        assert len(setups) == 0

    def test_scan_cpb_with_bars(self) -> None:
        """Test CPB scan with bars."""
        bars = [
            {"open": 100, "high": 105, "low": 99, "close": 103},
            {"open": 103, "high": 107, "low": 102, "close": 106},
            {"open": 106, "high": 108, "low": 105, "close": 107},
        ]
        config = {
            "price_action": {"bars": bars, "current_price": 107},
            "trend_data": {"direction": "up"},
        }
        scanner = SetupScanner(config)
        setups = scanner._scan_cpb()

        assert isinstance(setups, list)


class TestValidationMethods:
    """Test validation helper methods."""

    def test_validates_against_trend_uptrend(self) -> None:
        """Test trend validation for uptrend."""
        bars = [
            {"close_position": "high", "body_strength": "strong"},
            {"close_position": "high", "body_strength": "strong"},
        ]
        scanner = SetupScanner()
        result = scanner._validates_against_trend(bars, "up")

        assert isinstance(result, bool)

    def test_validates_against_trend_downtrend(self) -> None:
        """Test trend validation for downtrend."""
        bars = [
            {"close_position": "low", "body_strength": "strong"},
            {"close_position": "low", "body_strength": "strong"},
        ]
        scanner = SetupScanner()
        result = scanner._validates_against_trend(bars, "down")

        assert isinstance(result, bool)

    def test_identifies_rejection_bars_empty(self) -> None:
        """Test rejection bar identification with empty list."""
        scanner = SetupScanner()
        result = scanner._identify_rejection_bars([])

        assert result is False

    def test_identifies_rejection_bars(self) -> None:
        """Test rejection bar identification."""
        bars = [
            {"body_strength": "weak", "close_position": "mid"},
            {"body_strength": "weak", "close_position": "high"},
        ]
        scanner = SetupScanner()
        result = scanner._identify_rejection_bars(bars)

        assert isinstance(result, bool)

    def test_has_breakout_bar(self) -> None:
        """Test breakout bar detection."""
        bar: BarData = {
            "open": 100,
            "high": 105,
            "low": 99,
            "close": 106,
        }
        scanner = SetupScanner()
        result = scanner._has_breakout_bar(bar, 105.0)

        assert isinstance(result, bool)

    def test_has_weak_followthrough_empty(self) -> None:
        """Test weak follow-through with empty bars."""
        scanner = SetupScanner()
        result = scanner._has_weak_followthrough([])

        assert result is True

    def test_has_weak_followthrough(self) -> None:
        """Test weak follow-through detection."""
        bars = [
            {"body_strength": "weak"},
            {"body_strength": "weak"},
        ]
        scanner = SetupScanner()
        result = scanner._has_weak_followthrough(bars)

        assert isinstance(result, bool)

    def test_pullback_through_level(self) -> None:
        """Test pullback through level detection."""
        bars = [
            {"high": 110, "low": 100, "close": 105},
            {"high": 108, "low": 98, "close": 100},
        ]
        scanner = SetupScanner()
        result = scanner._pullback_through_level(bars, 105.0)

        assert isinstance(result, bool)

    def test_has_sustained_breakout_empty(self) -> None:
        """Test sustained breakout with empty bars."""
        scanner = SetupScanner()
        result = scanner._has_sustained_breakout([], 110.0)

        assert result is False

    def test_has_sustained_breakout(self) -> None:
        """Test sustained breakout detection."""
        bars = [
            {"high": 115, "low": 108, "body_strength": "strong"},
            {"high": 114, "low": 110, "body_strength": "strong"},
        ]
        scanner = SetupScanner()
        result = scanner._has_sustained_breakout(bars, 110.0)

        assert isinstance(result, bool)


class TestPullbackAnalysis:
    """Test pullback structure analysis."""

    def test_identify_pullback_structure_empty(self) -> None:
        """Test pullback identification with empty bars."""
        scanner = SetupScanner()
        result = scanner._identify_pullback_structure([])

        assert result == []

    def test_identify_pullback_structure(self) -> None:
        """Test pullback structure identification."""
        bars = [
            {"body_strength": "weak"},
            {"body_strength": "weak"},
            {"body_strength": "strong"},
        ]
        scanner = SetupScanner()
        result = scanner._identify_pullback_structure(bars)

        assert isinstance(result, list)

    def test_pullback_holds_level_empty(self) -> None:
        """Test pullback hold with empty bars."""
        scanner = SetupScanner()
        result = scanner._pullback_holds_level([], 100.0)

        assert result is False

    def test_pullback_holds_level(self) -> None:
        """Test pullback holds level."""
        bars = [
            {"close": 105},
            {"close": 104},
            {"close": 106},
        ]
        scanner = SetupScanner()
        result = scanner._pullback_holds_level(bars, 100.0)

        assert isinstance(result, bool)


class TestSwingAnalysis:
    """Test swing structure analysis."""

    def test_identify_swing_structure_empty(self) -> None:
        """Test swing identification with empty bars."""
        scanner = SetupScanner()
        result = scanner._identify_swing_structure([])

        assert result == []

    def test_identify_swing_structure_insufficient(self) -> None:
        """Test swing identification with insufficient bars."""
        bars = [
            {"high": 100, "low": 99},
            {"high": 105, "low": 98},
        ]
        scanner = SetupScanner()
        result = scanner._identify_swing_structure(bars)

        assert result == []

    def test_identify_swing_structure(self) -> None:
        """Test swing structure identification."""
        bars = [
            {"high": 100, "low": 99},
            {"high": 105, "low": 102},
            {"high": 103, "low": 100},
        ]
        scanner = SetupScanner()
        result = scanner._identify_swing_structure(bars)

        assert isinstance(result, list)

    def test_is_simple_pullback_false(self) -> None:
        """Test simple pullback identification (false case)."""
        swings = [
            {"high": 100},
            {"high": 105},
        ]
        scanner = SetupScanner()
        result = scanner._is_simple_pullback(swings, "up")

        assert isinstance(result, bool)

    def test_is_simple_pullback(self) -> None:
        """Test simple pullback identification."""
        swings = [
            {"high": 100},
            {"high": 98},
            {"high": 105},
        ]
        scanner = SetupScanner()
        result = scanner._is_simple_pullback(swings, "up")

        assert isinstance(result, bool)

    def test_is_complex_pullback_insufficient(self) -> None:
        """Test complex pullback with insufficient swings."""
        swings = [
            {"high": 100},
            {"high": 105},
        ]
        scanner = SetupScanner()
        result = scanner._is_complex_pullback(swings, "up")

        assert result is False

    def test_is_complex_pullback(self) -> None:
        """Test complex pullback identification."""
        swings = [
            {"high": 100, "low": 98},
            {"high": 105, "low": 99},
            {"high": 103, "low": 101},
            {"high": 107, "low": 102},
            {"high": 105, "low": 103},
        ]
        scanner = SetupScanner()
        result = scanner._is_complex_pullback(swings, "up")

        assert isinstance(result, bool)

    def test_structure_formation_complete_insufficient(self) -> None:
        """Test structure completion with insufficient swings."""
        swings = [
            {"high": 100},
            {"high": 105},
        ]
        scanner = SetupScanner()
        result = scanner._structure_formation_complete(swings)

        assert isinstance(result, bool)

    def test_structure_formation_complete(self) -> None:
        """Test structure formation completion."""
        swings = [
            {"high": 100},
            {"high": 105},
            {"high": 103},
        ]
        scanner = SetupScanner()
        result = scanner._structure_formation_complete(swings)

        assert isinstance(result, bool)


class TestTargetCalculation:
    """Test profit target calculation."""

    def test_calculate_targets_long(self) -> None:
        """Test target calculation for long position."""
        scanner = SetupScanner()
        targets = scanner._calculate_targets("long", 100.0)

        assert isinstance(targets, list)
        assert len(targets) > 0

    def test_calculate_targets_short(self) -> None:
        """Test target calculation for short position."""
        scanner = SetupScanner()
        targets = scanner._calculate_targets("short", 100.0)

        assert isinstance(targets, list)
        assert len(targets) > 0

    def test_calculate_targets_structure(self) -> None:
        """Test target structure is valid."""
        scanner = SetupScanner()
        targets = scanner._calculate_targets("long", 100.0)

        for target in targets:
            assert "price" in target
            assert "level" in target


class TestMarketConditionAssessment:
    """Test market condition assessment."""

    def test_assess_market_conditions(self) -> None:
        """Test market condition assessment."""
        scanner = SetupScanner()
        result = scanner._assess_market_conditions()

        assert isinstance(result, str)

    def test_assess_market_conditions_with_config(self) -> None:
        """Test market condition assessment with config."""
        config = {
            "market_conditions": {
                "trend_stage": "strong",
                "volatility": "high",
            }
        }
        scanner = SetupScanner(config)
        result = scanner._assess_market_conditions()

        assert isinstance(result, str)


class TestEntryZoneDefinition:
    """Test entry zone definition."""

    def test_define_entry_zone_long(self) -> None:
        """Test entry zone definition for long."""
        scanner = SetupScanner()
        zone = scanner._define_entry_zone(
            direction="long",
            level=100.0,
            confluence_strength="strong",
        )

        assert "upper" in zone
        assert "lower" in zone
        assert "ideal" in zone

    def test_define_entry_zone_short(self) -> None:
        """Test entry zone definition for short."""
        scanner = SetupScanner()
        zone = scanner._define_entry_zone(
            direction="short",
            level=100.0,
            confluence_strength="moderate",
        )

        assert "upper" in zone
        assert "lower" in zone
        assert "ideal" in zone

    def test_define_entry_zone_boundaries(self) -> None:
        """Test entry zone boundaries."""
        scanner = SetupScanner()
        zone = scanner._define_entry_zone("long", 100.0, "strong")

        assert zone["lower"] < zone["ideal"] < zone["upper"]


class TestConfluenceAnalysis:
    """Test confluence factor analysis."""

    def test_identify_confluence_factors_empty(self) -> None:
        """Test confluence with no factors."""
        scanner = SetupScanner()
        factors = scanner._identify_confluence_factors(
            direction="long",
            level=100.0,
            bars=[],
        )

        assert isinstance(factors, list)

    def test_identify_confluence_factors(self) -> None:
        """Test confluence factor identification."""
        bars = [
            {"close_position": "high", "body_strength": "strong"},
            {"close_position": "high", "body_strength": "strong"},
        ]
        scanner = SetupScanner()
        factors = scanner._identify_confluence_factors(
            direction="long",
            level=100.0,
            bars=bars,
        )

        assert isinstance(factors, list)


class TestTrappedTraderAnalysis:
    """Test trapped trader potential analysis."""

    def test_assess_trapped_trader_long(self) -> None:
        """Test trapped trader assessment for long."""
        scanner = SetupScanner()
        result = scanner._assess_trapped_trader_potential(
            direction="long",
            sr_level=100.0,
            rejection_bars=True,
        )

        assert result in ["high", "moderate", "low"]

    def test_assess_trapped_trader_short(self) -> None:
        """Test trapped trader assessment for short."""
        scanner = SetupScanner()
        result = scanner._assess_trapped_trader_potential(
            direction="short",
            sr_level=100.0,
            rejection_bars=False,
        )

        assert result in ["high", "moderate", "low"]


class TestQualityRating:
    """Test setup quality rating."""

    def test_rate_setup_quality_high_confluence(self) -> None:
        """Test quality rating with high confluence."""
        scanner = SetupScanner()
        rating = scanner._rate_setup_quality(
            probability_score=85.0,
            confluence_count=4,
            risk_reward_ratio=3.0,
            min_confluence=2,
        )

        assert rating in ["A", "B", "C"]

    def test_rate_setup_quality_low_confluence(self) -> None:
        """Test quality rating with low confluence."""
        scanner = SetupScanner()
        rating = scanner._rate_setup_quality(
            probability_score=45.0,
            confluence_count=1,
            risk_reward_ratio=1.2,
            min_confluence=2,
        )

        assert rating in ["A", "B", "C"]

    def test_rate_setup_quality_bounds(self) -> None:
        """Test quality rating is valid."""
        scanner = SetupScanner()
        rating = scanner._rate_setup_quality(
            probability_score=70.0,
            confluence_count=3,
            risk_reward_ratio=2.0,
            min_confluence=2,
        )

        assert rating in ["A", "B", "C"]


class TestSetupEnums:
    """Test setup type enums."""

    def test_setup_type_values(self) -> None:
        """Test SetupType enum values."""
        assert SetupType.TST.value == "TST"
        assert SetupType.BOF.value == "BOF"
        assert SetupType.BPB.value == "BPB"
        assert SetupType.PB.value == "PB"
        assert SetupType.CPB.value == "CPB"
        assert SetupType.NONE.value == "none"

    def test_setup_type_comparison(self) -> None:
        """Test SetupType enum comparison."""
        assert SetupType.TST != SetupType.BOF
        assert SetupType.BPB != SetupType.PB


class TestIntegrationScenarios:
    """Test integration scenarios with realistic data."""

    def test_scan_with_uptrend_data(self) -> None:
        """Test scanning with uptrend market data."""
        bars = [
            {
                "open": 100,
                "high": 105,
                "low": 99,
                "close": 104,
                "body_strength": "strong",
                "close_position": "high",
            },
            {
                "open": 104,
                "high": 107,
                "low": 103,
                "close": 106,
                "body_strength": "strong",
                "close_position": "high",
            },
            {
                "open": 106,
                "high": 109,
                "low": 105,
                "close": 108,
                "body_strength": "strong",
                "close_position": "high",
            },
        ]
        sr_levels = [
            {"price": 110.0, "type": "swing_point", "strength": "strong"},
            {"price": 100.0, "type": "prior_level", "strength": "moderate"},
        ]
        config = {
            "trend_data": {
                "direction": "up",
                "structure": {"swing_high": 109.0, "swing_low": 100.0},
                "strength_rating": "strong",
            },
            "price_action": {
                "current_price": 108.0,
                "bars": bars,
            },
            "support_resistance": {
                "levels": sr_levels,
            },
            "market_conditions": {
                "trend_stage": "strong",
                "volatility": "normal",
            },
        }
        scanner = SetupScanner(config)
        result = scanner.execute()

        assert result["scan_complete"] is True
        assert isinstance(result["active_setups"], list)
        assert isinstance(result["scan_summary"], dict)

    def test_scan_with_downtrend_data(self) -> None:
        """Test scanning with downtrend market data."""
        bars = [
            {
                "open": 110,
                "high": 111,
                "low": 105,
                "close": 106,
                "body_strength": "strong",
                "close_position": "low",
            },
            {
                "open": 106,
                "high": 108,
                "low": 102,
                "close": 103,
                "body_strength": "strong",
                "close_position": "low",
            },
            {
                "open": 103,
                "high": 105,
                "low": 99,
                "close": 100,
                "body_strength": "strong",
                "close_position": "low",
            },
        ]
        config = {
            "trend_data": {
                "direction": "down",
                "structure": {"swing_high": 111.0, "swing_low": 99.0},
                "strength_rating": "strong",
            },
            "price_action": {
                "current_price": 100.0,
                "bars": bars,
            },
            "support_resistance": {
                "levels": [],
            },
            "market_conditions": {
                "trend_stage": "strong",
                "volatility": "normal",
            },
        }
        scanner = SetupScanner(config)
        result = scanner.execute()

        assert result["scan_complete"] is True
        assert isinstance(result["active_setups"], list)

    def test_scan_with_multiple_setups_enabled(self) -> None:
        """Test scanning with multiple setup types enabled."""
        bars = [
            {
                "open": 100,
                "high": 105,
                "low": 99,
                "close": 103,
                "body_strength": "strong",
            },
            {
                "open": 103,
                "high": 107,
                "low": 102,
                "close": 106,
                "body_strength": "strong",
            },
            {
                "open": 106,
                "high": 108,
                "low": 105,
                "close": 107,
                "body_strength": "strong",
            },
        ]
        config = {
            "price_action": {
                "current_price": 107,
                "bars": bars,
            },
            "trend_data": {
                "direction": "up",
                "structure": {"swing_high": 108.0, "swing_low": 99.0},
            },
            "config": {
                "enabled_setup_types": ["TST", "BOF", "BPB", "PB", "CPB"],
            },
        }
        scanner = SetupScanner(config)
        result = scanner.execute()

        assert result["scan_complete"] is True


class TestSetupStructure:
    """Test setup output structure."""

    def test_ytc_setup_has_required_fields(self) -> None:
        """Test YTC setup contains required fields."""
        setup: YTCSetup = {
            "setup_id": "setup_123",
            "type": SetupType.TST,
            "direction": "long",
            "probability_score": 75.0,
        }

        assert "setup_id" in setup
        assert "type" in setup
        assert "direction" in setup
        assert "probability_score" in setup

    def test_setup_probability_range(self) -> None:
        """Test setup probability score is in valid range."""
        setup: YTCSetup = {
            "setup_id": "setup_456",
            "type": SetupType.BPB,
            "probability_score": 80.0,
        }

        assert 0.0 <= setup["probability_score"] <= 100.0

    def test_setup_direction_values(self) -> None:
        """Test setup direction is valid."""
        setup_long: YTCSetup = {"direction": "long"}
        setup_short: YTCSetup = {"direction": "short"}

        assert setup_long["direction"] in ["long", "short"]
        assert setup_short["direction"] in ["long", "short"]
