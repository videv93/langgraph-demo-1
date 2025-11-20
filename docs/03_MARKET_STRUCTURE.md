# Market Structure Agent (Higher Timeframe)

## Agent Identity

- **Name**: Market Structure Agent
- **Role**: Higher timeframe analysis and S/R identification
- **Type**: Worker Agent
- **Phase**: Pre-Market (Step 3)
- **Priority**: High

## Agent Purpose

Identifies support/resistance zones on the higher timeframe (4H) to provide structural context for trading timeframe decisions. Implements YTC's multiple timeframe analysis approach.

## Core Responsibilities

1. **S/R Zone Identification**
   - Detect swing highs/lows on 4H chart
   - Mark prior session high/low
   - Identify broken support becoming resistance
   - Calculate zone strength scores

2. **Structural Framework**
   - Define trading boundaries
   - Identify key price levels
   - Map potential reversal zones
   - Track structure evolution

3. **Timeframe Context**
   - Place 3min action within 4H context
   - Identify trending vs ranging structure
   - Warn of approaching major levels
   - Track breakout/breakdown scenarios

## Input Schema

```json
{
  "market_data": {
    "symbol": "string",
    "timeframe_higher": "4H",
    "lookback_periods": 100,
    "session_type": "regular|extended"
  },
  "historical_data": {
    "ohlcv": "DataFrame with 4H candles",
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

### SKILL: Swing Point Detection (SciPy Method)

```python
from scipy.signal import argrelextrema
import numpy as np

def detect_swing_points(ohlc_data, min_bars=3):
    """
    Swing point detection using scipy.signal.argrelextrema.
    
    Identifies local maxima (swing highs) and minima (swing lows)
    using relative extrema with configurable order parameter.
    
    Args:
        ohlc_data: DataFrame with 'high' and 'low' columns
        min_bars: Order parameter for extrema detection (lookback/lookahead bars)
    
    Returns:
        dict with 'swing_highs' and 'swing_lows' lists
    """
    highs = ohlc_data['high'].values
    lows = ohlc_data['low'].values
    
    # Detect local maxima and minima
    swing_high_indices = argrelextrema(highs, np.greater, order=min_bars)[0]
    swing_low_indices = argrelextrema(lows, np.less, order=min_bars)[0]
    
    swing_highs = [
        {
            'index': int(idx),
            'price': float(highs[idx]),
            'timestamp': ohlc_data.index[idx]
        }
        for idx in swing_high_indices
    ]
    
    swing_lows = [
        {
            'index': int(idx),
            'price': float(lows[idx]),
            'timestamp': ohlc_data.index[idx]
        }
        for idx in swing_low_indices
    ]
    
    return {
        'swing_highs': swing_highs,
        'swing_lows': swing_lows
    }
```

## Dependencies

- **Before**: System Initialization Agent
- **After**: Trend Definition Agent
- **Concurrent**: Economic Calendar Agent
