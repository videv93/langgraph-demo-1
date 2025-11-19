# Logging & Audit Agent

## Agent Identity
- **Name**: Logging & Audit Agent
- **Role**: Comprehensive logging and audit trail
- **Type**: Support Agent (Always Active)
- **Phase**: All Phases
- **Priority**: High

## Agent Purpose
Maintains complete audit trail of all decisions, calculations, trades, and system events for compliance, debugging, and review.

## Core Responsibilities

1. **Decision Logging**
   - Log all agent decisions
   - Record calculation inputs/outputs
   - Track reasoning
   - Timestamp everything

2. **Trade Logging**
   - Record trade setups
   - Log entry decisions
   - Track management actions
   - Document exits

3. **System Logging**
   - Platform events
   - API calls
   - Errors and warnings
   - Performance metrics

4. **Audit Trail**
   - Maintain immutable records
   - Enable replay capability
   - Support compliance
   - Facilitate debugging

## Output Schema

```json
{
  "log_entry": {
    "timestamp": "ISO 8601",
    "agent": "string",
    "event_type": "decision|trade|system|error",
    "level": "debug|info|warning|error|critical",
    "data": "dict",
    "context": "dict"
  }
}
```

## Skills Required

### SKILL: Structured Logging

```python
def log_decision(agent_name, decision_type, inputs, outputs, reasoning):
    """
    Creates structured log entry for agent decisions
    """
    log_entry = {
        'timestamp': get_timestamp(),
        'agent': agent_name,
        'event_type': 'decision',
        'decision_type': decision_type,
        'inputs': inputs,
        'outputs': outputs,
        'reasoning': reasoning,
        'session_id': get_current_session_id()
    }
    
    # Write to database
    db.insert('audit_log', log_entry)
    
    # Write to file
    file_logger.info(json.dumps(log_entry))
    
    return log_entry
```

## Dependencies
- **Concurrent with**: All agents
