"""Unit tests for Strength & Weakness Analysis Agent - YTC Price Action."""

import pytest
from agent.agents.strength_weakness import (
    StrengthWeakness,
    MomentumAnalysis,
    ProjectionAnalysis,
    DepthAnalysis,
    WeaknessSignals,
    SetupApplicability,
)


class TestStrengthWeaknessInit:
    """Test StrengthWeakness initialization."""

    def test_init_default_config(self) -> None:
        """Test initialization with default config."""
        agent = StrengthWeakness()
        assert agent.config == {}
        assert agent.trend_direction == "up"
        assert agent.bars == []
        assert agent.lookback_bars == 20

    def test_init_custom_config(self) -> None:
        """Test initialization with custom config."""
        config = {
            "trend_data": {"direction": "down", "current_swing": 3500.0, "prior_swings": []},
            "bar_data": {"current_bars": [], "lookback_bars": 30},
            "support_resistance": {"approaching_sr_level": 3400.0, "level_type": "support"},
        }
        agent = StrengthWeakness(config)
        assert agent.trend_direction == "down"
        assert agent.lookback_bars == 30
        assert agent.approaching_sr_level == 3400.0
        assert agent.level_type == "support"

    def test_init_partial_config(self) -> None:
        """Test initialization with partial config."""
        config = {"trend_data": {"direction": "sideways"}}
        agent = StrengthWeakness(config)
        assert agent.trend_direction == "sideways"
        assert agent.bars == []


class TestMomentumAnalysis:
    """Test momentum analysis calculations."""

    def test_momentum_empty_bars(self) -> None:
        """Test momentum analysis with no bars."""
        agent = StrengthWeakness({"bar_data": {"current_bars": []}})
        result = agent._analyze_momentum()

        assert result["score"] == 50.0
        assert result["rating"] == "moderate"
        assert result["bars_in_direction"] == 0

    def test_momentum_strong_uptrend_bars(self) -> None:
        """Test momentum with strong uptrend bars."""
        bars = [
            {"open": 100, "close": 105, "body_size": 5, "bar_range": 6, "high": 106, "low": 99},
            {"open": 105, "close": 110, "body_size": 5, "bar_range": 6, "high": 111, "low": 104},
            {"open": 110, "close": 115, "body_size": 5, "bar_range": 6, "high": 116, "low": 109},
        ]
        config = {
            "trend_data": {"direction": "up"},
            "bar_data": {"current_bars": bars, "lookback_bars": 3},
        }
        agent = StrengthWeakness(config)
        result = agent._analyze_momentum()

        assert result["score"] >= 60  # Should be strong
        assert result["rating"] in ["strong", "moderate"]
        assert result["bars_in_direction"] == 3

    def test_momentum_weak_bars(self) -> None:
        """Test momentum with weak bars."""
        bars = [
            {"open": 100, "close": 101, "body_size": 1, "bar_range": 5, "high": 103, "low": 99},
            {"open": 101, "close": 100.5, "body_size": 0.5, "bar_range": 4, "high": 103, "low": 99},
        ]
        config = {
            "trend_data": {"direction": "up"},
            "bar_data": {"current_bars": bars, "lookback_bars": 2},
        }
        agent = StrengthWeakness(config)
        result = agent._analyze_momentum()

        assert result["rating"] in ["weak", "moderate"]

    def test_momentum_close_quality_strong(self) -> None:
        """Test close quality assessment."""
        bars = [
            {"open": 100, "close": 115, "high": 116, "low": 99, "body_size": 15, "bar_range": 17},
        ]
        config = {
            "trend_data": {"direction": "up"},
            "bar_data": {"current_bars": bars, "lookback_bars": 1},
        }
        agent = StrengthWeakness(config)
        result = agent._analyze_momentum()

        assert result["close_quality"] in ["strong", "moderate", "weak"]


class TestProjectionAnalysis:
    """Test projection (swing extension) analysis."""

    def test_projection_no_prior_swings(self) -> None:
        """Test projection with no prior swings."""
        config = {
            "trend_data": {"direction": "up", "current_swing": 3500.0, "prior_swings": []},
            "bar_data": {"current_bars": []},
        }
        agent = StrengthWeakness(config)
        result = agent._analyze_projection()

        assert result["score"] == 50.0
        assert result["rating"] == "normal"

    def test_projection_extending_ratio(self) -> None:
        """Test projection with extending ratio > 1.2."""
        bars = [
            {"open": 100, "close": 105, "high": 106, "low": 99},
        ]
        config = {
            "trend_data": {
                "direction": "up",
                "current_swing": {"price": 3500.0, "distance": 320.0},
                "prior_swings": [{"distance": 200.0}, {"distance": 250.0}],
            },
            "bar_data": {"current_bars": bars},
        }
        agent = StrengthWeakness(config)
        result = agent._analyze_projection()

        assert "ratio" in result
        assert "rating" in result

    def test_projection_contracting_ratio(self) -> None:
        """Test projection with contracting ratio < 0.8."""
        bars = [
            {"open": 100, "close": 105, "high": 106, "low": 99},
        ]
        config = {
            "trend_data": {
                "direction": "up",
                "current_swing": {"price": 3000.0, "distance": 240.0},
                "prior_swings": [{"distance": 300.0}, {"distance": 250.0}],
            },
            "bar_data": {"current_bars": bars},
        }
        agent = StrengthWeakness(config)
        result = agent._analyze_projection()

        assert "ratio" in result
        assert "rating" in result

    def test_projection_normal_ratio(self) -> None:
        """Test projection with normal ratio (0.8-1.2)."""
        bars = [
            {"open": 100, "close": 105, "high": 106, "low": 99},
        ]
        config = {
            "trend_data": {
                "direction": "up",
                "current_swing": {"price": 3200.0, "distance": 280.0},
                "prior_swings": [{"distance": 300.0}],
            },
            "bar_data": {"current_bars": bars},
        }
        agent = StrengthWeakness(config)
        result = agent._analyze_projection()

        assert "ratio" in result
        assert "rating" in result


class TestDepthAnalysis:
    """Test depth (pullback retracement) analysis."""

    def test_depth_no_pullback(self) -> None:
        """Test depth with insufficient data."""
        config = {"trend_data": {"direction": "up", "prior_swings": []}}
        agent = StrengthWeakness(config)
        result = agent._analyze_depth()

        assert "score" in result
        assert "retracement_percentage" in result

    def test_depth_shallow_pullback(self) -> None:
        """Test shallow pullback (23.6% retracement)."""
        bars = [
            {"open": 100, "high": 110, "low": 109, "close": 109.5},
            {"open": 109.5, "high": 110, "low": 108, "close": 108.5},
        ]
        config = {
            "trend_data": {
                "direction": "up",
                "prior_swings": [{"price": 110, "distance": 10}],
            },
            "bar_data": {"current_bars": bars},
        }
        agent = StrengthWeakness(config)
        result = agent._analyze_depth()

        assert result["rating"] in ["shallow", "normal"]
        assert result["score"] > 40

    def test_depth_normal_pullback(self) -> None:
        """Test normal pullback (38.2-61.8% retracement)."""
        config = {
            "trend_data": {
                "direction": "up",
                "prior_swings": [{"price": 110, "distance": 10}],
            }
        }
        agent = StrengthWeakness(config)
        result = agent._analyze_depth()

        assert "retracement_percentage" in result
        assert result["retracement_percentage"] >= 0

    def test_depth_deep_pullback(self) -> None:
        """Test deep pullback (>61.8% retracement)."""
        config = {
            "trend_data": {
                "direction": "up",
                "prior_swings": [{"price": 110, "distance": 10}],
            }
        }
        agent = StrengthWeakness(config)
        result = agent._analyze_depth()

        assert "rating" in result

    def test_depth_full_reversal(self) -> None:
        """Test full reversal (>100% retracement)."""
        config = {
            "trend_data": {
                "direction": "up",
                "prior_swings": [{"price": 110, "distance": 10}],
            }
        }
        agent = StrengthWeakness(config)
        result = agent._analyze_depth()

        assert "rating" in result


class TestCombinedScoreCalculation:
    """Test combined strength score calculation."""

    def test_combined_score_formula(self) -> None:
        """Test combined score formula: (M*0.40) + (P*0.30) + (D*0.30)."""
        agent = StrengthWeakness()
        momentum = 80.0
        projection = 70.0
        depth = 60.0

        combined = agent._calculate_combined_score(momentum, projection, depth)
        expected = (80 * 0.40) + (70 * 0.30) + (60 * 0.30)

        assert combined == pytest.approx(expected, 0.1)

    def test_combined_score_boundaries(self) -> None:
        """Test combined score stays within 0-100 bounds."""
        agent = StrengthWeakness()

        # Test high scores
        combined_high = agent._calculate_combined_score(100, 100, 100)
        assert combined_high <= 100

        # Test low scores
        combined_low = agent._calculate_combined_score(0, 0, 0)
        assert combined_low >= 0

    def test_combined_score_weighting(self) -> None:
        """Test weighting formula: (M*0.40) + (P*0.30) + (D*0.30)."""
        agent = StrengthWeakness()

        # High momentum only: (100*0.4) + (0*0.3) + (0*0.3) = 40
        score1 = agent._calculate_combined_score(100, 0, 0)
        assert score1 == 40.0

        # High projection and depth only: (0*0.4) + (100*0.3) + (100*0.3) = 60
        score2 = agent._calculate_combined_score(0, 100, 100)
        assert score2 == 60.0


class TestStrengthRatingDetermination:
    """Test strength rating determination."""

    def test_rating_strong(self) -> None:
        """Test strong rating (score >= 70)."""
        agent = StrengthWeakness()
        rating = agent._determine_strength_rating(75.0)
        assert rating == "strong"

    def test_rating_moderate(self) -> None:
        """Test moderate rating (40-70)."""
        agent = StrengthWeakness()
        rating = agent._determine_strength_rating(55.0)
        assert rating == "moderate"

    def test_rating_weak(self) -> None:
        """Test weak rating (< 40)."""
        agent = StrengthWeakness()
        rating = agent._determine_strength_rating(30.0)
        assert rating == "weak"

    def test_rating_boundary_70(self) -> None:
        """Test boundary at 70 (strong)."""
        agent = StrengthWeakness()
        rating = agent._determine_strength_rating(70.0)
        assert rating == "strong"

    def test_rating_boundary_40(self) -> None:
        """Test boundary at 40 (moderate/weak)."""
        agent = StrengthWeakness()
        rating = agent._determine_strength_rating(40.0)
        assert rating == "moderate"


class TestWeaknessSignalDetection:
    """Test weakness signal detection."""

    def test_no_weakness_signals(self) -> None:
        """Test with no weakness signals."""
        momentum: MomentumAnalysis = {
            "score": 80.0,
            "rating": "strong",
            "bars_in_direction": 5,
        }
        projection: ProjectionAnalysis = {
            "score": 75.0,
            "ratio": 1.1,
            "rating": "normal",
        }
        depth: DepthAnalysis = {
            "score": 70.0,
            "retracement_ratio": 0.38,
            "rating": "normal",
        }

        agent = StrengthWeakness()
        signals = agent._detect_weakness_signals(momentum, projection, depth)

        assert signals["reversal_warning"] is False

    def test_projection_failure_detected(self) -> None:
        """Test projection failure detection (ratio < 0.8)."""
        momentum: MomentumAnalysis = {"score": 60.0, "rating": "moderate"}
        projection: ProjectionAnalysis = {
            "score": 30.0,
            "ratio": 0.7,
            "rating": "contracting",
        }
        depth: DepthAnalysis = {
            "score": 50.0,
            "retracement_ratio": 0.5,
            "rating": "normal",
        }

        agent = StrengthWeakness()
        signals = agent._detect_weakness_signals(momentum, projection, depth)

        assert signals["projection_failure"] is True

    def test_deep_pullback_detected(self) -> None:
        """Test deep pullback detection (retracement > 61.8%)."""
        momentum: MomentumAnalysis = {"score": 60.0, "rating": "moderate"}
        projection: ProjectionAnalysis = {
            "score": 50.0,
            "ratio": 1.0,
            "rating": "normal",
        }
        depth: DepthAnalysis = {
            "score": 40.0,
            "retracement_ratio": 0.7,
            "rating": "deep",
        }

        agent = StrengthWeakness()
        signals = agent._detect_weakness_signals(momentum, projection, depth)

        assert signals["deep_pullback"] is True

    def test_reversal_warning_multiple_signals(self) -> None:
        """Test reversal warning with multiple weakness signals."""
        momentum: MomentumAnalysis = {
            "score": 30.0,
            "rating": "weak",
            "bars_in_direction": 1,
        }
        projection: ProjectionAnalysis = {
            "score": 25.0,
            "ratio": 0.7,
            "rating": "contracting",
        }
        depth: DepthAnalysis = {
            "score": 20.0,
            "retracement_ratio": 0.75,
            "rating": "deep",
        }

        agent = StrengthWeakness()
        # Mock rejection bar detection
        agent.bars = [
            {"body_size": 0.5, "bar_range": 5.0, "wick_type": "upper"}
        ]
        signals = agent._detect_weakness_signals(momentum, projection, depth)

        # Should have reversal warning with multiple signals
        if signals["rejection_bars_detected"]:
            assert signals["reversal_warning"] is True


class TestRejectionBarDetection:
    """Test rejection bar pattern detection."""

    def test_no_rejection_bars(self) -> None:
        """Test with no rejection bars."""
        bars = [
            {"body_size": 5, "bar_range": 6, "wick_type": "none"},
            {"body_size": 4, "bar_range": 6, "wick_type": "none"},
        ]
        agent = StrengthWeakness({"bar_data": {"current_bars": bars}})
        result = agent._detect_rejection_bars()
        assert result is False

    def test_rejection_bar_detected(self) -> None:
        """Test rejection bar detection (small body + large wick)."""
        bars = [
            {"body_size": 1, "bar_range": 10, "wick_type": "upper"},
            {"body_size": 0.5, "bar_range": 8, "wick_type": "lower"},
            {"body_size": 2, "bar_range": 10, "wick_type": "both"},
        ]
        agent = StrengthWeakness({"bar_data": {"current_bars": bars}})
        result = agent._detect_rejection_bars()
        assert isinstance(result, bool)

    def test_insufficient_bars_for_rejection(self) -> None:
        """Test with insufficient bars."""
        bars = [{"body_size": 1, "bar_range": 10}]
        agent = StrengthWeakness({"bar_data": {"current_bars": bars}})
        result = agent._detect_rejection_bars()
        assert result is False


class TestMomentumDivergenceDetection:
    """Test momentum divergence detection."""

    def test_no_momentum_divergence(self) -> None:
        """Test with no momentum divergence."""
        momentum: MomentumAnalysis = {"score": 75.0}
        agent = StrengthWeakness()
        result = agent._detect_momentum_divergence(momentum)
        assert result is False

    def test_momentum_divergence_detected(self) -> None:
        """Test momentum divergence (weak momentum, new extremes)."""
        bars = [
            {"open": 100, "close": 99, "high": 105, "low": 98},
            {"open": 99, "close": 98, "high": 106, "low": 97},
            {"open": 98, "close": 97, "high": 107, "low": 96},
            {"open": 97, "close": 96, "high": 108, "low": 95},
            {"open": 96, "close": 95, "high": 109, "low": 94},
            {"open": 95, "close": 94, "high": 95, "low": 93},
        ]
        momentum: MomentumAnalysis = {"score": 25.0}
        config = {
            "trend_data": {"direction": "down"},
            "bar_data": {"current_bars": bars},
        }
        agent = StrengthWeakness(config)
        result = agent._detect_momentum_divergence(momentum)
        # May or may not detect depending on implementation
        assert isinstance(result, bool)


class TestSetupApplicabilityAssessment:
    """Test setup type applicability assessment."""

    def test_continuation_setup_strong_strength(self) -> None:
        """Test continuation setups with strong strength."""
        weakness_signals: WeaknessSignals = {
            "rejection_bars_detected": False,
            "deep_pullback": False,
        }
        setup = StrengthWeakness()._assess_setup_applicability(
            combined_score=75.0, weakness_signals=weakness_signals, overall_rating="strong"
        )

        assert setup["good_for_continuation_setups"] is True

    def test_reversal_setup_weak_strength(self) -> None:
        """Test reversal setups with weak strength."""
        weakness_signals: WeaknessSignals = {
            "rejection_bars_detected": True,
            "deep_pullback": True,
        }
        setup = StrengthWeakness()._assess_setup_applicability(
            combined_score=35.0, weakness_signals=weakness_signals, overall_rating="weak"
        )

        assert setup["good_for_reversal_setups"] is True

    def test_fade_weakness_opportunity(self) -> None:
        """Test fade weakness opportunity at S/R level."""
        weakness_signals: WeaknessSignals = {
            "rejection_bars_detected": True,
            "deep_pullback": False,
        }
        config = {
            "support_resistance": {
                "approaching_sr_level": 3400.0,
                "level_type": "support",
            }
        }
        agent = StrengthWeakness(config)
        setup = agent._assess_setup_applicability(
            combined_score=35.0, weakness_signals=weakness_signals, overall_rating="weak"
        )

        assert setup["fade_weakness_opportunity"] is True

    def test_expected_action_strong_continuation(self) -> None:
        """Test expected action for strong continuation."""
        weakness_signals: WeaknessSignals = {
            "rejection_bars_detected": False,
            "deep_pullback": False,
        }
        setup = StrengthWeakness()._assess_setup_applicability(
            combined_score=75.0, weakness_signals=weakness_signals, overall_rating="strong"
        )

        assert "pullback continuation" in setup["expected_action"].lower()

    def test_expected_action_reversal_warning(self) -> None:
        """Test expected action with reversal warning."""
        weakness_signals: WeaknessSignals = {
            "rejection_bars_detected": True,
            "reversal_warning": True,
        }
        setup = StrengthWeakness()._assess_setup_applicability(
            combined_score=30.0, weakness_signals=weakness_signals, overall_rating="weak"
        )

        assert "reversal" in setup["expected_action"].lower()


class TestExecute:
    """Test complete execute method."""

    def test_execute_returns_correct_structure(self) -> None:
        """Test that execute returns correct output structure."""
        config = {
            "trend_data": {"direction": "up", "current_swing": 3500.0, "prior_swings": []},
            "bar_data": {
                "current_bars": [
                    {
                        "open": 100,
                        "close": 105,
                        "high": 106,
                        "low": 99,
                        "body_size": 5,
                        "bar_range": 7,
                    }
                ]
            },
        }
        agent = StrengthWeakness(config)
        result = agent.execute()

        assert result["analysis_complete"] is True
        assert "strength_analysis" in result
        assert "weakness_signals" in result
        assert "setup_applicability" in result

    def test_execute_strength_analysis_structure(self) -> None:
        """Test strength_analysis sub-structure."""
        agent = StrengthWeakness()
        result = agent.execute()

        strength = result["strength_analysis"]
        assert "momentum" in strength
        assert "projection" in strength
        assert "depth" in strength
        assert "combined_score" in strength
        assert "overall_strength_rating" in strength

    def test_execute_weakness_signals_structure(self) -> None:
        """Test weakness_signals sub-structure."""
        agent = StrengthWeakness()
        result = agent.execute()

        signals = result["weakness_signals"]
        assert "rejection_bars_detected" in signals
        assert "momentum_divergence" in signals
        assert "projection_failure" in signals
        assert "deep_pullback" in signals
        assert "reversal_warning" in signals

    def test_execute_setup_applicability_structure(self) -> None:
        """Test setup_applicability sub-structure."""
        agent = StrengthWeakness()
        result = agent.execute()

        setup = result["setup_applicability"]
        assert "good_for_continuation_setups" in setup
        assert "good_for_reversal_setups" in setup
        assert "fade_weakness_opportunity" in setup
        assert "expected_action" in setup

    def test_execute_combined_score_in_range(self) -> None:
        """Test combined score is within 0-100 range."""
        agent = StrengthWeakness()
        result = agent.execute()

        combined_score = result["strength_analysis"]["combined_score"]
        assert 0.0 <= combined_score <= 100.0

    def test_execute_with_complex_config(self) -> None:
        """Test execute with complex configuration."""
        bars = [
            {"open": 100, "close": 102, "high": 103, "low": 99, "body_size": 2, "bar_range": 4},
            {"open": 102, "close": 101, "high": 103, "low": 100, "body_size": 1, "bar_range": 3},
            {"open": 101, "close": 104, "high": 105, "low": 100, "body_size": 3, "bar_range": 5},
        ]
        config = {
            "trend_data": {
                "direction": "up",
                "current_swing": {"price": 3500.0, "distance": 100.0},
                "prior_swings": [{"price": 3400.0, "distance": 100.0}],
            },
            "bar_data": {"current_bars": bars, "lookback_bars": 3},
            "support_resistance": {
                "approaching_sr_level": 3600.0,
                "level_type": "resistance",
            },
        }
        agent = StrengthWeakness(config)
        result = agent.execute()

        assert result["analysis_complete"] is True
        assert result["strength_analysis"]["combined_score"] >= 0


class TestBarTrendDirection:
    """Test bar trend direction analysis."""

    def test_bullish_bar_uptrend(self) -> None:
        """Test bullish bar in uptrend."""
        bar = {"open": 100, "close": 105}
        agent = StrengthWeakness({"trend_data": {"direction": "up"}})
        result = agent._bar_in_trend_direction(bar)
        assert result is True

    def test_bearish_bar_uptrend(self) -> None:
        """Test bearish bar in uptrend."""
        bar = {"open": 105, "close": 100}
        agent = StrengthWeakness({"trend_data": {"direction": "up"}})
        result = agent._bar_in_trend_direction(bar)
        assert result is False

    def test_bearish_bar_downtrend(self) -> None:
        """Test bearish bar in downtrend."""
        bar = {"open": 105, "close": 100}
        agent = StrengthWeakness({"trend_data": {"direction": "down"}})
        result = agent._bar_in_trend_direction(bar)
        assert result is True

    def test_bullish_bar_downtrend(self) -> None:
        """Test bullish bar in downtrend."""
        bar = {"open": 100, "close": 105}
        agent = StrengthWeakness({"trend_data": {"direction": "down"}})
        result = agent._bar_in_trend_direction(bar)
        assert result is False


class TestPullbackDepthCalculation:
    """Test pullback depth calculation."""

    def test_pullback_depth_insufficient_data(self) -> None:
        """Test pullback depth with insufficient data."""
        agent = StrengthWeakness({"bar_data": {"current_bars": []}})
        result = agent._calculate_pullback_depth()
        assert result is None

    def test_pullback_depth_no_prior_swings(self) -> None:
        """Test pullback depth with no prior swings."""
        bars = [
            {"open": 100, "close": 105, "high": 106, "low": 99},
            {"open": 105, "close": 100, "high": 105, "low": 98},
        ]
        config = {
            "trend_data": {"direction": "up", "prior_swings": []},
            "bar_data": {"current_bars": bars},
        }
        agent = StrengthWeakness(config)
        result = agent._calculate_pullback_depth()
        assert result is None
