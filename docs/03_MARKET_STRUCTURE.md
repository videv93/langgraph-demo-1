# Market Structure Agent (Higher Timeframe)

## Agent Identity
- **Name**: Market Structure Agent
- **Role**: Higher timeframe analysis and S/R identification
- **Type**: Worker Agent
- **Phase**: Pre-Market (Step 3)
- **Priority**: High

## Agent Purpose
Identifies support/resistance zones on the higher timeframe (30min) to provide structural context for trading timeframe decisions. Implements YTC's multiple timeframe analysis approach.

## Core Responsibilities

1. **S/R Zone Identification**
   - Detect swing highs/lows on 30min chart
   - Mark prior session high/low
   - Identify broken support becoming resistance
   - Calculate zone strength scores

2. **Structural Framework**
   - Define trading boundaries
   - Identify key price levels
   - Map potential reversal zones
   - Track structure evolution

3. **Timeframe Context**
   - Place 3min action within 30min context
   - Identify trending vs ranging structure
   - Warn of approaching major levels
   - Track breakout/breakdown scenarios

## Input Schema

```json
{
  "market_data": {
    "symbol": "string",
    "timeframe_higher": "30min",
    "lookback_periods": 100,
    "session_type": "regular|extended"
  },
  "historical_data": {
    "ohlcv": "DataFrame with 30min candles",
    "volume_profile": "optional"
  },
  "configuration": {
    "min_swing_bars": 3,
    "sr_zone_thickness_pct": 0.5,
    "prior_session_levels": true
  }
}
```

## Output Schema

```json
{
  "timestamp": "ISO 8601",
  "structural_framework": {
    "trend_structure": "uptrend|downtrend|sideways",
    "resistance_zones": [
      {
        "level": "float",
        "strength": "1-10",
        "type": "swing_high|prior_resistance|broken_support",
        "touches": "integer",
        "zone_range": [lower, upper]
      }
    ],
    "support_zones": [
      {
        "level": "float",
        "strength": "1-10",
        "type": "swing_low|prior_support|broken_resistance",
        "touches": "integer",
        "zone_range": [lower, upper]
      }
    ],
    "prior_session": {
      "high": "float",
      "low": "float",
      "close": "float"
    }
  },
  "current_context": {
    "price_location": "at_support|at_resistance|in_range|breakout",
    "nearest_resistance": "float",
    "nearest_support": "float",
    "distance_to_resistance_pct": "float",
    "distance_to_support_pct": "float"
  }
}
```

## Tools Required

### Hummingbot API Tools
```python
hummingbot.get_price_history(connector, pair, interval="30m", limit=100)
hummingbot.get_order_book_snapshot()
```

### Custom Tools
- **pivot_detector**: Identifies swing highs/lows
- **sr_zone_calculator**: Calculates support/resistance zones
- **structure_classifier**: Classifies market structure

## Skills Required

### SKILL: Swing Point Detection (YTC Method)

```python
def detect_swing_points(ohlc_data, min_bars=3):
    """
    YTC Swing Detection:
    - Swing High: High point with lower highs on both sides
    - Swing Low: Low point with higher lows on both sides
    """
    swing_highs = []
    swing_lows = []
    
    for i in range(min_bars, len(ohlc_data) - min_bars):
        # Check for swing high
        is_swing_high = True
        current_high = ohlc_data[i]['high']
        
        for j in range(1, min_bars + 1):
            if ohlc_data[i-j]['high'] >= current_high or ohlc_data[i+j]['high'] >= current_high:
                is_swing_high = False
                break
        
        if is_swing_high:
            swing_highs.append({
                'index': i,
                'price': current_high,
                'timestamp': ohlc_data[i]['timestamp']
            })
        
        # Check for swing low (similar logic)
        # ... implementation
    
    return swing_highs, swing_lows
```

## Dependencies
- **Before**: System Initialization Agent
- **After**: Trend Definition Agent
- **Concurrent**: Economic Calendar Agent
