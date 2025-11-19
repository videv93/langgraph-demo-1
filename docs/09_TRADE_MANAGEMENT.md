# Trade Management Agent

## Agent Identity
- **Name**: Trade Management Agent
- **Role**: Active position monitoring and management
- **Type**: Worker Agent
- **Phase**: Active Trading (Step 11)
- **Priority**: Critical

## Agent Purpose
Manages open positions through stop adjustments, partial exits, and risk mitigation per YTC trade management rules.

## Core Responsibilities

1. **Stop Loss Management**
   - Initial stop placement
   - Trailing stops at pivots
   - Breakeven moves
   - Structure-based adjustments

2. **Partial Exits**
   - T1 target execution
   - Profit securing
   - Position scaling

3. **Position Monitoring**
   - Track P&L
   - Monitor time in trade
   - Watch structure integrity
   - Detect adverse conditions

## Input Schema

```json
{
  "position": "position_data",
  "market_state": "current_market_data",
  "management_rules": "config"
}
```

## Output Schema

```json
{
  "position_updates": {
    "stop_loss": "float",
    "targets_remaining": ["array"],
    "breakeven": "boolean",
    "partial_fills": ["array"]
  },
  "actions_taken": ["list of actions"],
  "alerts": ["warnings/notices"]
}
```

## Skills Required

### SKILL: Trailing Stop Logic

```python
def update_trailing_stop(position, new_pivots, trend):
    """
    YTC Trailing Stops:
    - Move behind new pivots in trend direction
    - Never move stop against position
    - Breakeven at +1R or first pivot
    """
    # Implementation
    pass
```

## Dependencies
- **Before**: Entry Execution Agent
- **After**: Exit Execution Agent
