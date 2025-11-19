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

### Custom Tools
- **news_api_fetcher**: Retrieves economic calendar
- **news_classifier**: Rates event impact
- **restriction_manager**: Manages trading restrictions

## Dependencies
- **Before**: System Initialization
- **After**: All trading agents
