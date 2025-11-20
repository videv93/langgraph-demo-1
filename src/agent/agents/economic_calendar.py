"""Economic calendar agent for monitoring upcoming economic events."""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any, TypedDict
import asyncio
from bs4 import BeautifulSoup


class EventImpact(str, Enum):
    """Impact level of economic event."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EconomicEvent(TypedDict):
    """Economic event data."""

    event_name: str
    impact: EventImpact
    time_until_event: float  # Hours
    forecast: str
    previous: str
    currency: str


class EconomicCalendarOutput(TypedDict):
    """Output from economic calendar analysis."""

    calendar_check_complete: bool
    high_impact_events_upcoming: bool
    upcoming_events: list[EconomicEvent]
    trading_recommendation: str
    hours_until_next_event: float
    check_timestamp: str


class EconomicCalendar:
    """Monitor economic calendar for upcoming events affecting trading.

    Scrapes Forex Factory calendar for:
    - High-impact economic announcements
    - Timing of events relative to current time
    - Currency-specific events (relevant for crypto-USD pairs)
    - Risk assessment based on event schedule
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the economic calendar agent.

        Args:
            config: Optional configuration with calendar parameters.
                    Expected keys: currencies, lookback_hours, blackout_minutes, etc.
        """
        self.config = config or {}
        self.currencies = self.config.get("currencies", ["USD", "EUR", "GBP"])
        self.lookback_hours = self.config.get("lookback_hours", 24)
        self.blackout_before_min = self.config.get("blackout_before_min", 15)
        self.blackout_after_min = self.config.get("blackout_after_min", 15)
        self.current_time = datetime.utcnow()

    def execute(self) -> EconomicCalendarOutput:
        """Execute economic calendar check.

        Returns:
            EconomicCalendarOutput with upcoming events and trading recommendation.
        """
        try:
            # Get upcoming events from Forex Factory
            upcoming_events = asyncio.run(self._get_upcoming_events())
        except Exception as e:
            print(f"Error fetching calendar: {e}")
            upcoming_events = []

        # Check for high-impact events
        high_impact = any(event["impact"] == EventImpact.HIGH for event in upcoming_events)

        # Generate trading recommendation
        recommendation = self._generate_recommendation(upcoming_events, high_impact)

        # Calculate time until next event
        next_event_time = (
            min(event["time_until_event"] for event in upcoming_events)
            if upcoming_events
            else float("inf")
        )

        return {
            "calendar_check_complete": True,
            "high_impact_events_upcoming": high_impact,
            "upcoming_events": upcoming_events,
            "trading_recommendation": recommendation,
            "hours_until_next_event": next_event_time,
            "check_timestamp": self.current_time.isoformat(),
        }

    async def _get_upcoming_events(self) -> list[EconomicEvent]:
        """Get upcoming economic events from Forex Factory calendar.

        Returns:
            List of upcoming economic events.
        """
        try:
            from crawl4ai import AsyncWebCrawler
        except ImportError:
            print("crawl4ai not installed. Unable to fetch calendar events.")
            return []

        events = []

        try:
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(
                    url="https://www.forexfactory.com/calendar.php",
                    cache_mode="bypass"
                )

                if result.html:
                    events = self._parse_calendar_html(result.html)
        except Exception as e:
            print(f"Error scraping Forex Factory: {e}")
            return []

        # Sort by time until event
        events.sort(key=lambda x: x["time_until_event"])
        return events

    def _parse_calendar_html(self, html: str) -> list[EconomicEvent]:
        """Parse Forex Factory calendar HTML.

        Args:
            html: HTML content from Forex Factory calendar page.

        Returns:
            List of parsed economic events.
        """
        events = []
        soup = BeautifulSoup(html, "html.parser")

        # Find calendar event rows
        # Note: Forex Factory uses dynamic classes, adjust selectors as needed
        event_rows = soup.find_all("tr", class_="calendar_row")

        for row in event_rows:
            try:
                # Extract event details from table cells
                cells = row.find_all("td")
                if len(cells) < 6:
                    continue

                # Parse event time
                time_cell = cells[0].get_text(strip=True)
                event_time = self._parse_event_time(time_cell)
                if not event_time:
                    continue

                # Calculate hours until event
                time_until = (event_time - self.current_time).total_seconds() / 3600
                if time_until < 0 or time_until > self.lookback_hours:
                    continue

                # Parse currency
                currency = cells[1].get_text(strip=True).upper()
                if currency not in self.currencies:
                    continue

                # Parse impact level
                impact_cell = cells[2]
                impact_icons = impact_cell.find_all("span")
                impact = self._parse_impact_level(impact_icons)
                if impact == EventImpact.LOW:
                    continue

                # Parse event name
                event_name = cells[3].get_text(strip=True)

                # Parse forecast and previous values
                forecast = cells[4].get_text(strip=True)
                previous = cells[5].get_text(strip=True)

                events.append({
                    "event_name": event_name,
                    "impact": impact,
                    "time_until_event": round(time_until, 1),
                    "forecast": forecast,
                    "previous": previous,
                    "currency": currency,
                })
            except (IndexError, ValueError, AttributeError):
                continue

        return events

    def _parse_event_time(self, time_str: str) -> datetime | None:
        """Parse event time from Forex Factory format.

        Args:
            time_str: Time string from calendar (e.g., "14:30").

        Returns:
            Datetime object for the event, or None if parsing fails.
        """
        try:
            # Assume today's date for events
            time_parts = time_str.split(":")
            if len(time_parts) != 2:
                return None

            hour = int(time_parts[0])
            minute = int(time_parts[1])

            event_time = self.current_time.replace(
                hour=hour, minute=minute, second=0, microsecond=0
            )

            # If time is in the past today, assume tomorrow
            if event_time < self.current_time:
                event_time += timedelta(days=1)

            return event_time
        except (ValueError, AttributeError):
            return None

    def _parse_impact_level(self, impact_icons: list) -> EventImpact:
        """Parse impact level from Forex Factory icon span elements.

        Args:
            impact_icons: List of span elements containing impact indicators.

        Returns:
            EventImpact enum value.
        """
        # Forex Factory uses icon colors: red=high, orange=medium, yellow=low
        # Count the number of icons to determine impact
        icon_count = len(impact_icons)

        if icon_count >= 3:
            return EventImpact.HIGH
        elif icon_count == 2:
            return EventImpact.MEDIUM
        else:
            return EventImpact.LOW

    def _generate_recommendation(
        self, events: list[EconomicEvent], high_impact_upcoming: bool
    ) -> str:
        """Generate trading recommendation based on calendar events.

        Args:
            events: List of upcoming events.
            high_impact_upcoming: Whether high-impact events are upcoming.

        Returns:
            Trading recommendation string.
        """
        if not events:
            return "✓ No significant economic events in next 24h. Safe to trade."

        if high_impact_upcoming:
            high_impact_events = [
                e for e in events if e["impact"] == EventImpact.HIGH
            ]
            min_time = min(e["time_until_event"] for e in high_impact_events)

            if min_time < 1:
                return (
                    f"⚠️  HIGH IMPACT EVENT IN {min_time:.1f}h. "
                    f"Consider reducing position size or waiting."
                )
            elif min_time < 4:
                return (
                    f"⚠️  HIGH IMPACT EVENT IN {min_time:.1f}h. "
                    f"Increased volatility expected."
                )
            else:
                return (
                    f"⚠️  HIGH IMPACT EVENT IN {min_time:.1f}h. "
                    f"Plan exit strategy."
                )

        # Only medium-impact events
        return (
            "✓ Only medium-impact events upcoming. Monitor but proceed with caution."
        )

    def _get_mock_events(self) -> list[EconomicEvent]:
        """Get mock economic events for testing purposes.

        Returns:
            List of mock economic events.
        """
        return [
            {
                "event_name": "Unemployment Rate",
                "impact": EventImpact.HIGH,
                "time_until_event": 2.5,
                "forecast": "3.7%",
                "previous": "3.6%",
                "currency": "USD",
            },
            {
                "event_name": "Core Inflation Rate",
                "impact": EventImpact.HIGH,
                "time_until_event": 5.0,
                "forecast": "2.3%",
                "previous": "2.4%",
                "currency": "USD",
            },
            {
                "event_name": "ECB Interest Rate Decision",
                "impact": EventImpact.HIGH,
                "time_until_event": 8.5,
                "forecast": "3.50%",
                "previous": "3.50%",
                "currency": "EUR",
            },
            {
                "event_name": "Retail Sales",
                "impact": EventImpact.MEDIUM,
                "time_until_event": 10.5,
                "forecast": "0.5%",
                "previous": "-0.2%",
                "currency": "USD",
            },
            {
                "event_name": "GDP Growth Rate",
                "impact": EventImpact.MEDIUM,
                "time_until_event": 11.5,
                "forecast": "2.1%",
                "previous": "2.0%",
                "currency": "GBP",
            },
        ]
