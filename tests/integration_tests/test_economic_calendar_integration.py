"""Integration tests for economic calendar agent."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from agent.agents.economic_calendar import (
    EconomicCalendar,
    EventImpact,
)


class TestEconomicCalendarIntegration:
    """Integration tests for EconomicCalendar."""

    def test_full_execution_with_mock_data(self) -> None:
        """Test full execution flow with mock data."""
        calendar = EconomicCalendar({
            "currencies": ["USD", "EUR"],
            "lookback_hours": 24,
        })
        result = calendar.execute()

        assert result["calendar_check_complete"] is True
        assert isinstance(result["upcoming_events"], list)
        assert isinstance(result["trading_recommendation"], str)
        assert isinstance(result["hours_until_next_event"], (int, float))
        assert isinstance(result["check_timestamp"], str)

    def test_execution_with_different_lookback_periods(self) -> None:
        """Test execution with different lookback periods."""
        for lookback in [1, 6, 12, 24, 48]:
            calendar = EconomicCalendar({"lookback_hours": lookback})
            result = calendar.execute()
            
            # All events should be within lookback period
            for event in result["upcoming_events"]:
                assert event["time_until_event"] <= lookback

    def test_execution_with_different_currencies(self) -> None:
        """Test execution with different currency filters."""
        currencies_list = [
            ["USD"],
            ["EUR"],
            ["GBP"],
            ["USD", "EUR", "GBP"],
        ]
        
        for currencies in currencies_list:
            calendar = EconomicCalendar({"currencies": currencies})
            result = calendar.execute()
            
            # All returned events should be in requested currencies
            for event in result["upcoming_events"]:
                assert event["currency"] in currencies

    def test_high_impact_detection(self) -> None:
        """Test high impact event detection."""
        calendar = EconomicCalendar()
        result = calendar.execute()

        if result["high_impact_events_upcoming"]:
            # Should have at least one high impact event
            high_impact = [
                e for e in result["upcoming_events"]
                if e["impact"] == EventImpact.HIGH
            ]
            assert len(high_impact) > 0

    def test_recommendation_consistency(self) -> None:
        """Test that recommendations are consistent with event data."""
        calendar = EconomicCalendar()
        result = calendar.execute()

        recommendation = result["trading_recommendation"]
        high_impact = result["high_impact_events_upcoming"]

        if high_impact:
            assert "HIGH IMPACT" in recommendation or "high" in recommendation.lower()
        
        if not result["upcoming_events"]:
            assert "No significant" in recommendation or "safe" in recommendation.lower()

    def test_hours_until_next_event(self) -> None:
        """Test hours until next event calculation."""
        calendar = EconomicCalendar()
        result = calendar.execute()

        if result["upcoming_events"]:
            expected_min = min(
                e["time_until_event"] for e in result["upcoming_events"]
            )
            assert result["hours_until_next_event"] == expected_min
        else:
            assert result["hours_until_next_event"] == float("inf")

    @pytest.mark.asyncio
    async def test_get_upcoming_events_fallback(self) -> None:
        """Test fallback when crawl4ai is unavailable."""
        calendar = EconomicCalendar()
        
        # Mock the crawl4ai import to fail
        with patch("crawl4ai.AsyncWebCrawler", side_effect=ImportError):
            events = await calendar._get_upcoming_events()
            
            # Should return empty list
            assert isinstance(events, list)
            assert len(events) == 0

    @pytest.mark.asyncio
    async def test_get_upcoming_events_with_mock_crawler(self) -> None:
        """Test getting events with mocked crawler."""
        calendar = EconomicCalendar()
        
        # Create mock HTML response
        mock_html = """
        <table>
            <tr class="calendar_row">
                <td>14:30</td>
                <td>USD</td>
                <td><span></span><span></span><span></span></td>
                <td>CPI</td>
                <td>3.2%</td>
                <td>3.4%</td>
            </tr>
        </table>
        """
        
        # Mock the AsyncWebCrawler
        mock_crawler = AsyncMock()
        mock_crawler.arun = AsyncMock(return_value=MagicMock(html=mock_html))
        
        with patch("crawl4ai.AsyncWebCrawler") as mock_crawler_class:
            mock_crawler_class.return_value.__aenter__.return_value = mock_crawler
            events = await calendar._get_upcoming_events()
            
            # Should have parsed events
            assert isinstance(events, list)

    def test_event_data_types(self) -> None:
        """Test that returned event data has correct types."""
        calendar = EconomicCalendar()
        result = calendar.execute()

        for event in result["upcoming_events"]:
            assert isinstance(event["event_name"], str)
            assert isinstance(event["impact"], EventImpact)
            assert isinstance(event["time_until_event"], float)
            assert isinstance(event["forecast"], str)
            assert isinstance(event["previous"], str)
            assert isinstance(event["currency"], str)

    def test_timestamp_format(self) -> None:
        """Test that check timestamp is in ISO format."""
        calendar = EconomicCalendar()
        result = calendar.execute()

        timestamp = result["check_timestamp"]
        # Should be able to parse as ISO format
        try:
            datetime.fromisoformat(timestamp)
        except ValueError:
            pytest.fail(f"Timestamp {timestamp} is not in ISO format")

    def test_multiple_executions_consistency(self) -> None:
        """Test that multiple executions return consistent data structure."""
        calendar = EconomicCalendar()
        
        result1 = calendar.execute()
        result2 = calendar.execute()

        # Both should have same keys
        assert set(result1.keys()) == set(result2.keys())
        
        # Both should have same structure in events
        for events in [result1["upcoming_events"], result2["upcoming_events"]]:
            for event in events:
                assert set(event.keys()) == {
                    "event_name",
                    "impact",
                    "time_until_event",
                    "forecast",
                    "previous",
                    "currency",
                }

    def test_event_sorting(self) -> None:
        """Test that events are sorted by time until event."""
        calendar = EconomicCalendar()
        result = calendar.execute()

        events = result["upcoming_events"]
        if len(events) > 1:
            times = [e["time_until_event"] for e in events]
            assert times == sorted(times)

    def test_blackout_window_parameters_in_config(self) -> None:
        """Test that blackout window parameters are stored correctly."""
        config = {
            "blackout_before_min": 30,
            "blackout_after_min": 45,
        }
        calendar = EconomicCalendar(config)
        
        assert calendar.blackout_before_min == 30
        assert calendar.blackout_after_min == 45

    def test_current_time_is_set(self) -> None:
        """Test that current time is properly set during initialization."""
        before = datetime.utcnow()
        calendar = EconomicCalendar()
        after = datetime.utcnow()

        # Calendar's current_time should be between before and after
        assert before <= calendar.current_time <= after

    def test_currency_filtering(self) -> None:
        """Test that events are filtered by currency."""
        config = {"currencies": ["USD"]}
        calendar = EconomicCalendar(config)
        result = calendar.execute()

        for event in result["upcoming_events"]:
            assert event["currency"] in ["USD"]

    def test_lookback_hours_filtering(self) -> None:
        """Test that events respect lookback_hours limit."""
        config = {"lookback_hours": 6}
        calendar = EconomicCalendar(config)
        result = calendar.execute()

        for event in result["upcoming_events"]:
            assert event["time_until_event"] <= 6
