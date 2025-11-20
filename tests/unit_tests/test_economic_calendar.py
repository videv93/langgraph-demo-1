"""Unit tests for economic calendar agent."""

from datetime import datetime, timedelta
import pytest
from bs4 import BeautifulSoup

from agent.agents.economic_calendar import (
    EconomicCalendar,
    EventImpact,
    EconomicEvent,
)


class TestEconomicCalendarInit:
    """Test EconomicCalendar initialization."""

    def test_init_default_config(self) -> None:
        """Test initialization with default config."""
        calendar = EconomicCalendar()
        assert calendar.currencies == ["USD", "EUR", "GBP"]
        assert calendar.lookback_hours == 24
        assert calendar.blackout_before_min == 15
        assert calendar.blackout_after_min == 15

    def test_init_custom_config(self) -> None:
        """Test initialization with custom config."""
        config = {
            "currencies": ["USD"],
            "lookback_hours": 48,
            "blackout_before_min": 30,
            "blackout_after_min": 30,
        }
        calendar = EconomicCalendar(config)
        assert calendar.currencies == ["USD"]
        assert calendar.lookback_hours == 48
        assert calendar.blackout_before_min == 30
        assert calendar.blackout_after_min == 30


class TestParseEventTime:
    """Test event time parsing."""

    def test_parse_valid_time(self) -> None:
        """Test parsing valid time string."""
        calendar = EconomicCalendar()
        event_time = calendar._parse_event_time("14:30")
        assert event_time is not None
        assert event_time.hour == 14
        assert event_time.minute == 30

    def test_parse_morning_time(self) -> None:
        """Test parsing morning time."""
        calendar = EconomicCalendar()
        event_time = calendar._parse_event_time("08:00")
        assert event_time is not None
        assert event_time.hour == 8
        assert event_time.minute == 0

    def test_parse_invalid_format(self) -> None:
        """Test parsing invalid time format."""
        calendar = EconomicCalendar()
        event_time = calendar._parse_event_time("invalid")
        assert event_time is None

    def test_parse_malformed_time(self) -> None:
        """Test parsing malformed time string."""
        calendar = EconomicCalendar()
        event_time = calendar._parse_event_time("25:70")
        assert event_time is None

    def test_future_time_same_day(self) -> None:
        """Test that future time stays same day."""
        calendar = EconomicCalendar()
        # Set current time to 10:00
        calendar.current_time = datetime(2025, 11, 20, 10, 0, 0)
        event_time = calendar._parse_event_time("14:30")
        assert event_time is not None
        assert event_time.day == 20
        assert event_time.month == 11

    def test_past_time_next_day(self) -> None:
        """Test that past time wraps to next day."""
        calendar = EconomicCalendar()
        # Set current time to 20:00
        calendar.current_time = datetime(2025, 11, 20, 20, 0, 0)
        event_time = calendar._parse_event_time("14:30")
        assert event_time is not None
        assert event_time.day == 21  # Next day


class TestParseImpactLevel:
    """Test impact level parsing."""

    def test_high_impact_three_icons(self) -> None:
        """Test high impact with 3 icons."""
        calendar = EconomicCalendar()
        icons = [None, None, None]  # Simulating 3 icon elements
        impact = calendar._parse_impact_level(icons)
        assert impact == EventImpact.HIGH

    def test_medium_impact_two_icons(self) -> None:
        """Test medium impact with 2 icons."""
        calendar = EconomicCalendar()
        icons = [None, None]
        impact = calendar._parse_impact_level(icons)
        assert impact == EventImpact.MEDIUM

    def test_low_impact_one_icon(self) -> None:
        """Test low impact with 1 icon."""
        calendar = EconomicCalendar()
        icons = [None]
        impact = calendar._parse_impact_level(icons)
        assert impact == EventImpact.LOW

    def test_no_icons(self) -> None:
        """Test no icons results in low impact."""
        calendar = EconomicCalendar()
        icons = []
        impact = calendar._parse_impact_level(icons)
        assert impact == EventImpact.LOW


class TestGenerateRecommendation:
    """Test trading recommendation generation."""

    def test_no_events(self) -> None:
        """Test recommendation with no events."""
        calendar = EconomicCalendar()
        events: list[EconomicEvent] = []
        recommendation = calendar._generate_recommendation(events, False)
        assert "No significant economic events" in recommendation

    def test_high_impact_within_one_hour(self) -> None:
        """Test high impact event within 1 hour."""
        calendar = EconomicCalendar()
        event: EconomicEvent = {
            "event_name": "CPI",
            "impact": EventImpact.HIGH,
            "time_until_event": 0.5,
            "forecast": "3.2%",
            "previous": "3.4%",
            "currency": "USD",
        }
        recommendation = calendar._generate_recommendation([event], True)
        assert "Consider reducing position size" in recommendation
        assert "0.5h" in recommendation

    def test_high_impact_within_four_hours(self) -> None:
        """Test high impact event within 4 hours."""
        calendar = EconomicCalendar()
        event: EconomicEvent = {
            "event_name": "CPI",
            "impact": EventImpact.HIGH,
            "time_until_event": 2.5,
            "forecast": "3.2%",
            "previous": "3.4%",
            "currency": "USD",
        }
        recommendation = calendar._generate_recommendation([event], True)
        assert "Increased volatility expected" in recommendation
        assert "2.5h" in recommendation

    def test_high_impact_beyond_four_hours(self) -> None:
        """Test high impact event beyond 4 hours."""
        calendar = EconomicCalendar()
        event: EconomicEvent = {
            "event_name": "CPI",
            "impact": EventImpact.HIGH,
            "time_until_event": 8.0,
            "forecast": "3.2%",
            "previous": "3.4%",
            "currency": "USD",
        }
        recommendation = calendar._generate_recommendation([event], True)
        assert "Plan exit strategy" in recommendation
        assert "8.0h" in recommendation

    def test_medium_impact_only(self) -> None:
        """Test recommendation with only medium impact events."""
        calendar = EconomicCalendar()
        event: EconomicEvent = {
            "event_name": "PPI",
            "impact": EventImpact.MEDIUM,
            "time_until_event": 3.0,
            "forecast": "0.3%",
            "previous": "0.2%",
            "currency": "USD",
        }
        recommendation = calendar._generate_recommendation([event], False)
        assert "Only medium-impact events" in recommendation


class TestGetMockEvents:
    """Test mock event generation."""

    def test_mock_events_structure(self) -> None:
        """Test that mock events have correct structure."""
        calendar = EconomicCalendar()
        events = calendar._get_mock_events()
        assert isinstance(events, list)
        assert len(events) > 0

        for event in events:
            assert "event_name" in event
            assert "impact" in event
            assert "time_until_event" in event
            assert "forecast" in event
            assert "previous" in event
            assert "currency" in event

    def test_mock_events_structure_valid(self) -> None:
        """Test that mock events have valid structure for sorting."""
        calendar = EconomicCalendar()
        events = calendar._get_mock_events()
        # Events should have time_until_event for sorting
        assert all("time_until_event" in e for e in events)

    def test_mock_events_within_lookback(self) -> None:
        """Test that all mock events are within lookback hours."""
        calendar = EconomicCalendar()
        calendar.lookback_hours = 12
        events = calendar._get_mock_events()
        for event in events:
            assert event["time_until_event"] <= 12

    def test_mock_events_include_high_impact(self) -> None:
        """Test that mock events include high impact items."""
        calendar = EconomicCalendar()
        events = calendar._get_mock_events()
        high_impact = [e for e in events if e["impact"] == EventImpact.HIGH]
        assert len(high_impact) > 0


class TestParseCalendarHtml:
    """Test HTML parsing."""

    def test_parse_empty_html(self) -> None:
        """Test parsing empty HTML."""
        calendar = EconomicCalendar()
        events = calendar._parse_calendar_html("")
        assert events == []

    def test_parse_malformed_html(self) -> None:
        """Test parsing malformed HTML."""
        calendar = EconomicCalendar()
        html = "<div>invalid html</div>"
        events = calendar._parse_calendar_html(html)
        assert isinstance(events, list)

    def test_parse_html_no_events(self) -> None:
        """Test parsing HTML with no event rows."""
        calendar = EconomicCalendar()
        html = "<table><tr><td>No events</td></tr></table>"
        events = calendar._parse_calendar_html(html)
        assert events == []


class TestExecute:
    """Test execute method."""

    def test_execute_returns_correct_structure(self) -> None:
        """Test that execute returns correct output structure."""
        calendar = EconomicCalendar()
        result = calendar.execute()

        assert isinstance(result, dict)
        assert "calendar_check_complete" in result
        assert "high_impact_events_upcoming" in result
        assert "upcoming_events" in result
        assert "trading_recommendation" in result
        assert "hours_until_next_event" in result
        assert "check_timestamp" in result

    def test_execute_calendar_check_complete(self) -> None:
        """Test that calendar check completes."""
        calendar = EconomicCalendar()
        result = calendar.execute()
        assert result["calendar_check_complete"] is True

    def test_execute_with_no_events(self) -> None:
        """Test execute when no events are found."""
        calendar = EconomicCalendar()
        calendar.lookback_hours = 0  # No events in 0 hour window
        result = calendar.execute()

        assert result["high_impact_events_upcoming"] is False
        assert result["upcoming_events"] == []
        assert result["hours_until_next_event"] == float("inf")

    def test_execute_recommendation_reflects_events(self) -> None:
        """Test that recommendation reflects the events found."""
        calendar = EconomicCalendar()
        result = calendar.execute()

        if result["high_impact_events_upcoming"]:
            assert "HIGH IMPACT" in result["trading_recommendation"]
        else:
            # Either no events or only medium impact
            assert "safe" in result["trading_recommendation"].lower() or \
                   "medium" in result["trading_recommendation"].lower()


class TestEventImpactEnum:
    """Test EventImpact enum."""

    def test_event_impact_values(self) -> None:
        """Test EventImpact enum values."""
        assert EventImpact.LOW.value == "low"
        assert EventImpact.MEDIUM.value == "medium"
        assert EventImpact.HIGH.value == "high"

    def test_event_impact_comparison(self) -> None:
        """Test EventImpact enum comparison."""
        assert EventImpact.HIGH != EventImpact.MEDIUM
        assert EventImpact.LOW != EventImpact.HIGH
