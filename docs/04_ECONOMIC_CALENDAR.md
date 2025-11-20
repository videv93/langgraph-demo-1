# Economic Calendar Agent

## Agent Identity
- **Name**: Economic Calendar Agent
- **Role**: News event monitor and filter
- **Type**: Worker Agent
- **Phase**: Pre-Market (Step 4) + Real-time Updates
- **Priority**: High

## Agent Purpose
Fetches high-impact economic events, creates trading restriction windows, and monitors for unexpected news that could affect trading decisions.

## Core Responsibilities

1. **News Event Retrieval**
   - Fetch daily economic calendar
   - Filter for high-impact events
   - Identify currency-specific releases
   - Track earnings reports (if trading stocks)

2. **Trading Restrictions**
   - Create blackout windows (±15min around news)
   - Set volatility filters
   - Configure position management rules
   - Alert upcoming events

3. **Real-time Monitoring**
   - Track event releases
   - Monitor for flash news
   - Detect unexpected announcements
   - Update restrictions dynamically

## Input Schema

```json
{
  "calendar_config": {
    "date": "YYYY-MM-DD",
    "currencies": ["USD", "EUR", "GBP"],
    "min_impact": "high",
    "timezone": "America/New_York"
  },
  "restriction_config": {
    "blackout_before_min": 15,
    "blackout_after_min": 15,
    "pause_new_trades": true,
    "tighten_stops": false
  }
}
```

## Output Schema

```json
{
  "news_events": [
    {
      "time": "HH:MM",
      "currency": "USD",
      "event": "NFP",
      "impact": "high",
      "forecast": "string",
      "previous": "string",
      "blackout_window": {
        "start": "HH:MM",
        "end": "HH:MM"
      }
    }
  ],
  "trading_restrictions": {
    "blackout_periods": ["time ranges"],
    "current_status": "normal|restricted|blackout",
    "next_event_time": "HH:MM"
  }
}
```

## Tools Required

### External Dependencies
- **crawl4ai**: Web scraper for Forex Factory calendar
  - Scrapes https://www.forexfactory.com/calendar
  - Extracts event details (time, currency, impact, forecast, previous)
  - Handles dynamic content loading

### Custom Tools
- **calendar_scraper**: Fetches and parses Forex Factory calendar using crawl4ai
- **restriction_manager**: Manages trading restrictions based on events
- **event_processor**: Formats scraped data and creates blackout windows

## Implementation Notes

### Calendar Scraping
```python
from crawl4ai import AsyncWebCrawler

async def fetch_economic_calendar(date: str, currencies: list[str]):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://www.forexfactory.com/calendar.php",
            cache_mode="bypass"
        )
        # Parse event table and filter by:
        # - Date
        # - Currency pairs
        # - Impact level (high)
```

### Event Filtering
- Filter events by impact level (high only)
- Match currency pairs (USD, EUR, GBP, etc.)
- Parse timestamps in broker's timezone
- Calculate blackout windows (±15 minutes)

## Dependencies
- **Before**: System Initialization
- **After**: All trading agents
