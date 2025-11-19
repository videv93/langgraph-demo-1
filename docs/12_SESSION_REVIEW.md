# Session Review Agent

## Agent Identity
- **Name**: Session Review Agent
- **Role**: Post-session analysis and learning
- **Type**: Worker Agent
- **Phase**: Post-Market (Step 14)
- **Priority**: High

## Agent Purpose
Conducts comprehensive review of trading session comparing actual performance against hindsight-perfect performance per YTC review methodology.

## Core Responsibilities

1. **Market Environment Analysis**
   - Classify actual environment
   - Compare to pre-session assessment
   - Identify missed signals
   - Document key patterns

2. **Trade Review**
   - Analyze each trade
   - Compare entry quality
   - Evaluate exit timing
   - Calculate optimal R-multiples

3. **Execution Analysis**
   - Review entry precision
   - Assess stop placement
   - Evaluate trade management
   - Identify improvements

4. **Lessons Extraction**
   - Document key learnings
   - Identify pattern recognition gaps
   - Note psychological insights
   - Generate improvement goals

## Input Schema

```json
{
  "session_data": {
    "trades": ["array of trade objects"],
    "market_data": "full session data",
    "decisions": "array of key decisions"
  },
  "performance_data": {
    "pnl": "float",
    "win_rate": "float",
    "avg_r_multiple": "float"
  }
}
```

## Output Schema

```json
{
  "session_review": {
    "environment_classification": {
      "actual": "trending|ranging|choppy",
      "predicted": "string",
      "accuracy": "boolean"
    },
    "trade_reviews": [
      {
        "trade_id": "string",
        "was_valid_setup": "boolean",
        "entry_quality": "excellent|good|poor",
        "optimal_entry": "float",
        "actual_entry": "float",
        "optimal_exit": "float",
        "actual_exit": "float",
        "optimal_r": "float",
        "actual_r": "float",
        "lessons": ["array"]
      }
    ],
    "key_observations": ["array"],
    "lessons_learned": ["array"],
    "improvement_goals": ["array"]
  }
}
```

## Skills Required

### SKILL: Hindsight Analysis

```python
def compare_to_perfect_execution(trade, market_data):
    """
    YTC Review Process:
    Compare actual performance with hindsight-perfect execution
    """
    # Find optimal entry in zone
    optimal_entry = find_best_entry_in_zone(
        trade['entry_zone'],
        market_data
    )
    
    # Find optimal exit
    optimal_exit = find_maximum_favorable_excursion(
        trade,
        market_data
    )
    
    # Calculate performance gap
    optimal_r = calculate_r_multiple(optimal_entry, optimal_exit, trade['stop'])
    actual_r = trade['r_multiple']
    
    return {
        'optimal_entry': optimal_entry,
        'optimal_exit': optimal_exit,
        'optimal_r': optimal_r,
        'execution_efficiency': actual_r / optimal_r if optimal_r > 0 else 0
    }
```

## Dependencies
- **Before**: Data Collection Agent
- **After**: Performance Analytics Agent
