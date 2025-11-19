# Setup Scanner Agent

## Agent Identity
- **Name**: Setup Scanner Agent
- **Role**: Pattern recognition and setup identification
- **Type**: Worker Agent
- **Phase**: Active Trading (Step 9)
- **Priority**: Critical

## Agent Purpose
Identifies high-probability YTC pullback setups including 3-swing traps, trend pullbacks, and other pattern-based entries.

## Core Responsibilities

1. **Pattern Detection**
   - Identify pullback patterns
   - Detect 3-swing traps
   - Recognize trend continuation setups
   - Find counter-trend opportunities

2. **Fibonacci Analysis**
   - Calculate retracement levels (50%, 61.8%)
   - Track extreme pivots
   - Update levels dynamically
   - Monitor for entries

3. **Setup Scoring**
   - Rate setup quality
   - Assess confluence factors
   - Check structural alignment
   - Generate priority ranking

## Input Schema

```json
{
  "market_state": {
    "trend": "trend_data",
    "structure": "structure_data",
    "strength": "strength_data"
  },
  "setup_config": {
    "enabled_patterns": ["pullback", "3_swing_trap"],
    "min_score": 70,
    "require_trend_alignment": true
  }
}
```

## Output Schema

```json
{
  "active_setups": [
    {
      "setup_id": "uuid",
      "type": "pullback|3_swing_trap|other",
      "score": 0-100,
      "direction": "long|short",
      "entry_zone": {
        "upper": "float",
        "lower": "float",
        "ideal": "float"
      },
      "fibonacci_levels": {
        "50%": "float",
        "61.8%": "float"
      },
      "stop_loss": "float",
      "targets": {
        "T1": "float",
        "T2": "float"
      },
      "confluence_factors": ["list"],
      "ready_to_trade": "boolean"
    }
  ]
}
```

## Skills Required

### SKILL: 3-Swing Trap Detection

```python
def detect_3_swing_trap(price_data, trend):
    """
    YTC 3-Swing Trap Pattern:
    Counter-trend traders trapped by failed swing
    Very high probability setup
    """
    # Implementation
    pass
```

## Dependencies
- **Before**: Strength & Weakness Agent
- **After**: Entry Execution Agent
