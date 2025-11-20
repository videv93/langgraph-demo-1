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

## Tools Required

### Pinecone Vector Database
Queries strategy patterns and rules from Pinecone knowledge base.

```python
from pinecone import Pinecone

def query_strategy_patterns(setup_data: dict) -> list[dict]:
    """
    Query Pinecone for similar strategy patterns and rules.
    
    Args:
        setup_data: Current market setup data (trend, structure, price action)
    
    Returns:
        List of similar historical patterns with confidence scores
    """
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index("ytc-strategy-patterns")
    
    # Embed setup characteristics
    query_vector = embed_setup_features(setup_data)
    
    # Search for similar patterns
    results = index.query(
        vector=query_vector,
        top_k=5,
        include_metadata=True
    )
    
    return [
        {
            "pattern_name": match["metadata"]["pattern"],
            "similarity": match["score"],
            "rules": match["metadata"]["rules"],
            "historical_winrate": match["metadata"]["winrate"],
            "optimal_sl": match["metadata"]["stop_loss_pct"],
            "targets": match["metadata"]["targets"]
        }
        for match in results["matches"]
    ]
```

## Skills Required

### SKILL: 3-Swing Trap Detection

```python
def detect_3_swing_trap(price_data, trend, strategy_rules=None):
    """
    YTC 3-Swing Trap Pattern:
    Counter-trend traders trapped by failed swing.
    Very high probability setup.
    
    Uses Pinecone to retrieve optimal parameters and historical context.
    """
    if strategy_rules is None:
        strategy_rules = query_strategy_patterns({
            "pattern_type": "3_swing_trap",
            "trend": trend
        })
    
    # Detect failed swings indicating trap setup
    failed_swings = identify_failed_swings(price_data, trend)
    
    if len(failed_swings) >= 2:
        # Validate against retrieved strategy rules
        for rules in strategy_rules:
            if validate_against_rules(failed_swings, rules):
                return {
                    "detected": True,
                    "confidence": rules["similarity"],
                    "historical_winrate": rules["historical_winrate"],
                    "recommended_entry": calculate_entry_zone(failed_swings, rules),
                    "recommended_sl": calculate_sl(failed_swings, rules),
                }
    
    return {"detected": False}
```

### SKILL: Fibonacci Retracement Levels

```python
def calculate_fibonacci_retracements(high, low, trend_direction="up"):
    """
    Calculate Fibonacci retracement levels for entry zone identification.
    """
    move = abs(high - low)
    
    if trend_direction == "up":
        levels = {
            "38.2%": high - (move * 0.382),
            "50%": high - (move * 0.50),
            "61.8%": high - (move * 0.618),
        }
    else:
        levels = {
            "38.2%": low + (move * 0.382),
            "50%": low + (move * 0.50),
            "61.8%": low + (move * 0.618),
        }
    
    return levels
```

## Dependencies
- **Before**: Strength & Weakness Agent
- **After**: Entry Execution Agent
- **External**: Pinecone Vector Database (strategy patterns index)
