# Entry Execution Agent

## Agent Identity
- **Name**: Entry Execution Agent
- **Role**: Trade entry execution and order management
- **Type**: Worker Agent
- **Phase**: Active Trading (Step 10)
- **Priority**: Critical

## Agent Purpose
Executes entries at optimal prices using YTC entry techniques (LWP, limit orders, stop orders).

## Core Responsibilities

1. **Entry Timing**
   - Wait for trend change confirmation
   - Monitor Fibonacci levels
   - Track lower timeframe (1min) triggers
   - Identify LWP (Last Worthwhile Price)

2. **Order Management**
   - Place limit orders in zones
   - Set stop entries for breakouts
   - Bracket price at LWP
   - Manage partial fills

3. **Dynamic Updates**
   - Update Fib levels on new pivots
   - Adjust entry zones
   - Cancel stale orders
   - Reposition entries

## Input Schema

```json
{
  "setup": "setup_data",
  "position_size": "integer",
  "entry_method": "limit|stop|market"
}
```

## Output Schema

```json
{
  "entry_result": {
    "order_id": "string",
    "status": "pending|filled|cancelled",
    "entry_price": "float",
    "quantity": "integer",
    "timestamp": "ISO 8601"
  },
  "position": {
    "position_id": "string",
    "entry_avg": "float",
    "stop_loss": "float",
    "targets": "dict"
  }
}
```

## Tools Required

### Hummingbot API
```python
hummingbot.create_order(connector, pair, side, amount, type, price)
hummingbot.cancel_order(order_id)
hummingbot.get_order(order_id)
```

## Skills Required

### SKILL: LWP Identification

```python
def identify_lwp(price_action, entry_zone):
    """
    Last Worthwhile Price:
    Final acceptable entry before price runs away
    """
    # Implementation
    pass
```

## Dependencies
- **Before**: Setup Scanner Agent
- **After**: Trade Management Agent
