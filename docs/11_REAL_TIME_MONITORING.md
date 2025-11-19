# Real-Time Monitoring Agent

## Agent Identity
- **Name**: Real-Time Monitoring Agent  
- **Role**: Continuous market and system monitoring
- **Type**: Support Agent (Always Active)
- **Phase**: All Phases
- **Priority**: High

## Agent Purpose
Provides continuous monitoring of market conditions, position status, system health, and trading progress throughout the session.

## Core Responsibilities

1. **Market Monitoring**
   - Track structure evolution
   - Monitor trend integrity
   - Watch for reversals
   - Detect unusual activity

2. **Position Tracking**
   - Monitor all open positions
   - Track P&L in real-time
   - Alert on significant moves
   - Watch for correlation changes

3. **System Health**
   - Monitor data feed quality
   - Track platform connectivity
   - Measure latency
   - Detect anomalies

4. **Session Progress**
   - Track time remaining
   - Monitor trade count
   - Watch risk utilization
   - Alert on milestones

## Output Schema

```json
{
  "monitoring_update": {
    "timestamp": "ISO 8601",
    "market_status": {
      "trend_intact": "boolean",
      "structure_changed": "boolean",
      "volatility_spike": "boolean"
    },
    "position_status": {
      "open_count": "integer",
      "total_pnl": "float",
      "largest_winner": "float",
      "largest_loser": "float"
    },
    "system_health": {
      "connectivity": "good|degraded|poor",
      "latency_ms": "float",
      "data_quality": "good|issues"
    },
    "session_progress": {
      "time_elapsed_min": "integer",
      "time_remaining_min": "integer",
      "trades_taken": "integer",
      "risk_used_pct": "float"
    },
    "alerts": ["array of alert objects"]
  }
}
```

## Skills Required

### SKILL: Anomaly Detection

```python
def detect_market_anomaly(current_data, baseline):
    """
    Identifies unusual market behavior
    - Volatility spikes
    - Volume anomalies  
    - Price gaps
    - Data quality issues
    """
    anomalies = []
    
    # Check volatility
    if current_data['atr'] > baseline['atr'] * 2:
        anomalies.append({
            'type': 'volatility_spike',
            'severity': 'high',
            'action': 'tighten_stops'
        })
    
    return anomalies
```

## Dependencies
- **Concurrent with**: All agents
