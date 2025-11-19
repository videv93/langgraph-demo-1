"""Economic calendar agent for monitoring upcoming economic events."""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any, TypedDict


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
    forecast: float
    previous: float
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

    Checks for:
    - High-impact economic announcements
    - Timing of events relative to current time
    - Currency-specific events (relevant for crypto-USD pairs)
    - Risk assessment based on event schedule
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the economic calendar agent.

        Args:
            config: Optional configuration with calendar parameters.
                    Expected keys: currencies, lookback_hours, etc.
        """
        self.config = config or {}
        self.currencies = self.config.get("currencies", ["USD", "ETH"])
        self.lookback_hours = self.config.get("lookback_hours", 24)
        self.current_time = datetime.utcnow()

    def execute(self) -> EconomicCalendarOutput:
        """Execute economic calendar check.

        Returns:
            EconomicCalendarOutput with upcoming events and trading recommendation.
        """
        # Get upcoming events
        upcoming_events = self._get_upcoming_events()

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

    def _get_upcoming_events(self) -> list[EconomicEvent]:
        """Get upcoming economic events for the next 24 hours.

        Returns:
            List of upcoming economic events.
        """
        # Mock economic calendar data
        # In production, fetch from economic calendar API (e.g., Investing.com, Forexfactory)
        events = []

        # US events (relevant for USD-based pairs like ETH-USDT)
        us_events = [
            {
                "event_name": "US CPI (YoY)",
                "impact": EventImpact.HIGH,
                "time": self.current_time + timedelta(hours=2),
                "forecast": 3.2,
                "previous": 3.4,
            },
            {
                "event_name": "Fed Funds Rate Decision",
                "impact": EventImpact.HIGH,
                "time": self.current_time + timedelta(hours=18),
                "forecast": 4.75,
                "previous": 4.75,
            },
            {
                "event_name": "Initial Jobless Claims",
                "impact": EventImpact.MEDIUM,
                "time": self.current_time + timedelta(hours=6),
                "forecast": 210000,
                "previous": 205000,
            },
            {
                "event_name": "Producer Price Index",
                "impact": EventImpact.MEDIUM,
                "time": self.current_time + timedelta(hours=12),
                "forecast": 0.3,
                "previous": 0.2,
            },
        ]

        # Filter to upcoming events within lookback_hours
        for event in us_events:
            time_until = (event["time"] - self.current_time).total_seconds() / 3600
            if 0 <= time_until <= self.lookback_hours:
                events.append(
                    {
                        "event_name": event["event_name"],
                        "impact": event["impact"],
                        "time_until_event": round(time_until, 1),
                        "forecast": event["forecast"],
                        "previous": event["previous"],
                        "currency": "USD",
                    }
                )

        # Sort by time until event
        events.sort(key=lambda x: x["time_until_event"])
        return events

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
            min_time = min(e["time_until_event"] for e in events if e["impact"] == EventImpact.HIGH)
            if min_time < 1:
                return f"⚠️  HIGH IMPACT EVENT IN {min_time:.1f}h. Consider reducing position size or waiting."
            elif min_time < 4:
                return f"⚠️  HIGH IMPACT EVENT IN {min_time:.1f}h. Increased volatility expected."
            else:
                return f"⚠️  HIGH IMPACT EVENT IN {min_time:.1f}h. Plan exit strategy."

        # Only medium-impact events
        return "✓ Only medium-impact events upcoming. Monitor but proceed with caution."
