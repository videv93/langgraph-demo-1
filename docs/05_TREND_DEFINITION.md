# Trend Definition Agent (Trading Timeframe)

## Agent Identity
- **Name**: Trend Definition Agent
- **Role**: Trading timeframe trend analysis
- **Type**: Worker Agent
- **Phase**: Session Open (Step 7) + Continuous
- **Priority**: Critical

## Agent Purpose
Identifies trend direction and structure on the trading timeframe (3min) using YTC's precise swing analysis methodology.

## Core Responsibilities

1. **Pivot Detection**
   - Identify significant swing highs/lows on 3min
   - Track leading swing levels
   - Monitor pivot sequences
   - Detect structure breaks

2. **Trend Classification**
   - Classify as uptrend/downtrend/sideways
   - Track higher highs and higher lows
   - Identify lower lows and lower highs
   - Distinguish weakening vs reversal

3. **Trend Integrity**
   - Monitor for structure breaks
   - Detect leading swing violations
   - Track trend strength
   - Identify potential reversals

## Input Schema

```json
{
  "market_data": {
    "symbol": "string",
    "timeframe": "3min",
    "lookback_bars": 50
  },
  "structure_context": {
    "higher_tf_resistance": "float",
    "higher_tf_support": "float"
  }
}
```

## Output Schema

```json
{
  "trend_state": {
    "direction": "uptrend|downtrend|sideways",
    "confidence": "float 0-1",
    "since_timestamp": "ISO 8601"
  },
  "pivot_structure": {
    "swing_highs": [
      {"price": "float", "timestamp": "ISO", "is_leading": "bool"}
    ],
    "swing_lows": [
      {"price": "float", "timestamp": "ISO", "is_leading": "bool"}
    ],
    "current_leading_swing_high": "float",
    "current_leading_swing_low": "float"
  },
  "trend_integrity": {
    "structure_intact": "boolean",
    "structure_breaks": "integer",
    "reversal_warning": "boolean"
  }
}
```

## Skills Required

### SKILL: YTC Trend Analysis

```python
def analyze_trend_structure(pivots):
    """
    YTC Trend Rules:
    - Uptrend: Series of HH and HL
    - Downtrend: Series of LH and LL
    - Trend weakens when structure breaks (LL in uptrend)
    - Trend reverses when leading swing broken
    """
    # Implementation
    pass
```

## Dependencies
- **Before**: Market Structure Agent
- **After**: Strength & Weakness Agent
