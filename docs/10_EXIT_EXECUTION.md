# Exit Execution Agent

## Agent Identity
- **Name**: Exit Execution Agent
- **Role**: Position exit execution
- **Type**: Worker Agent
- **Phase**: Active Trading (Step 12)
- **Priority**: Critical

## Agent Purpose
Executes all exit types (targets, stops, time-based, counter-trend) and ensures clean position closure.

## Core Responsibilities

1. **Exit Types**
   - Target hits (T1, T2)
   - Stop loss execution
   - Time-based exits
   - Counter-trend signals
   - Session timeout

2. **Order Verification**
   - Confirm fill prices
   - Verify quantities
   - Validate flat position
   - Record results

## Input Schema

```json
{
  "position": "position_data",
  "exit_trigger": {
    "type": "target|stop|time|signal",
    "reason": "string"
  }
}
```

## Output Schema

```json
{
  "exit_result": {
    "order_id": "string",
    "exit_price": "float",
    "quantity": "integer",
    "pnl": "float",
    "r_multiple": "float",
    "duration": "seconds",
    "exit_type": "string"
  },
  "position_closed": "boolean"
}
```

## Dependencies
- **Before**: Trade Management Agent
- **After**: Performance Analytics Agent
