# Contingency Management Agent

## Agent Identity
- **Name**: Contingency Management Agent
- **Role**: Emergency and error handling
- **Type**: Support Agent (Always Active)
- **Phase**: All Phases
- **Priority**: Critical

## Agent Purpose
Handles all emergency situations, platform failures, and contingency scenarios to protect capital and maintain system integrity.

## Core Responsibilities

1. **Emergency Detection**
   - Platform failures
   - Connection losses
   - Data feed issues
   - Broker problems

2. **Emergency Response**
   - Flatten all positions
   - Cancel pending orders
   - Switch to backup systems
   - Alert human operator

3. **Recovery Management**
   - Assess damage
   - Restore connections
   - Verify positions
   - Resume operations safely

4. **Contingency Planning**
   - Pre-defined protocols
   - Failover sequences
   - Manual intervention triggers

## Input Schema

```json
{
  "emergency_type": "connection_loss|platform_crash|data_failure|broker_issue",
  "severity": "low|medium|high|critical",
  "context": "current_state_data"
}
```

## Output Schema

```json
{
  "emergency_response": {
    "actions_taken": ["array"],
    "positions_closed": "integer",
    "orders_cancelled": "integer",
    "system_status": "halted|backup|recovered",
    "requires_human_intervention": "boolean"
  }
}
```

## Skills Required

### SKILL: Emergency Shutdown

```python
def execute_emergency_shutdown(reason, positions, orders):
    """
    YTC Emergency Protocol:
    1. Cancel all pending orders
    2. Flatten all positions at market
    3. Log all actions
    4. Halt system
    5. Alert operator
    """
    results = {
        'orders_cancelled': 0,
        'positions_closed': 0,
        'errors': []
    }
    
    # Cancel orders
    for order in orders:
        try:
            cancel_order(order['id'])
            results['orders_cancelled'] += 1
        except Exception as e:
            results['errors'].append(str(e))
    
    # Close positions at market
    for position in positions:
        try:
            close_position_market(position['id'])
            results['positions_closed'] += 1
        except Exception as e:
            results['errors'].append(str(e))
    
    # Halt system
    system.halt()
    
    # Alert operator
    send_emergency_alert(reason, results)
    
    return results
```

## Dependencies
- **Concurrent with**: All agents
