# YTC Automated Trading System - LangGraph Implementation

## Overview

This is a complete multi-agent system for automating the YTC (Your Trading Coach) Price Action methodology created by Lance Beggs. The system uses LangGraph to orchestrate stateful agents powered by Anthropic's Claude, with Hummingbot API integration to execute a comprehensive trading workflow from pre-market analysis through post-market review.

## System Architecture

Built on LangGraph's StateGraph with cyclic execution patterns for real-time market monitoring and decision-making:

```
┌──────────────────────────────────────────────────────────────┐
│                    TRADING STATE GRAPH                        │
│             (LangGraph StateGraph with Cycles)                │
└────────────────────┬─────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼──────────────┐  ┌───────▼──────────────┐
│   PRE-SESSION NODES  │  │  SUPPORT NODES       │
│   (Linear Execution) │  │  (Async/Persistent)  │
│                      │  │                      │
│ • system_init        │  │ • real_time_monitor  │
│ • risk_setup         │  │ • contingency_check  │
│ • market_structure   │  │ • logging_audit      │
│ • economic_calendar  │  │                      │
└──────────┬───────────┘  └──────────────────────┘
           │
┌──────────▼─────────────────────┐
│     SESSION_OPEN NODES         │
│  (Conditional Routing)         │
│                                │
│ • trend_definition             │
│ • strength_weakness_analysis   │
└──────────┬────────────────────┘
           │
┌──────────▼──────────────────────────────┐
│   TRADING CYCLE (Subgraph Loop)         │
│   Continuous real-time execution        │
│                                          │
│ ┌──────────────────────────────┐       │
│ │ setup_scanner ─┐             │       │
│ │                ├─> router ───┼──────►│
│ │ entry_exec  ───┤             │       │
│ │ trade_mgmt  ───┤             │       │
│ │ exit_exec   ────┘             │       │
│ └──────────────────────────────┘       │
│                                          │
│ Edges: continue_trading / session_close │
└──────────┬───────────────────────────────┘
           │
┌──────────▼─────────────────────┐
│    POST-SESSION NODES          │
│   (Sequential Review)          │
│                                │
│ • session_review               │
│ • performance_analytics        │
│ • learning_optimization        │
│ • next_session_prep            │
└────────────────────────────────┘
```

## Agent Inventory

### Critical Path Agents (16 Total)

*Orchestration handled by LangGraph conditional routing instead of dedicated agent*

1. **01_SYSTEM_INITIALIZATION** - Platform connectivity
2. **02_RISK_MANAGEMENT** - Position sizing & limits
3. **03_MARKET_STRUCTURE** - Higher timeframe S/R
4. **04_ECONOMIC_CALENDAR** - News filtering
5. **05_TREND_DEFINITION** - Trading timeframe trend
6. **06_STRENGTH_WEAKNESS** - Momentum analysis
7. **07_SETUP_SCANNER** - Pattern recognition
8. **08_ENTRY_EXECUTION** - Trade entry
9. **09_TRADE_MANAGEMENT** - Position management
10. **10_EXIT_EXECUTION** - Trade exits
11. **11_REAL_TIME_MONITORING** - Continuous monitoring
12. **12_SESSION_REVIEW** - Post-session analysis
13. **13_PERFORMANCE_ANALYTICS** - Statistics tracking
14. **14_LEARNING_OPTIMIZATION** - Parameter tuning
15. **15_NEXT_SESSION_PREP** - Goal setting
16. **16_CONTINGENCY_MANAGEMENT** - Emergency handling
17. **17_LOGGING_AUDIT** - Audit trail

## Key Features

### YTC Methodology Implementation

- ✅ **Multiple Timeframe Analysis** (4h structure / 15m trading / 5m entry)
- ✅ **Precise Risk Management** (1% per trade, 3% session max)
- ✅ **Swing-Based Trend Analysis** (HH/HL for uptrends, LH/LL for downtrends)
- ✅ **Strength & Weakness Scoring** (Momentum + Projection + Depth)
- ✅ **Setup Recognition** (Pullbacks, 3-Swing Traps, Continuation)
- ✅ **Fibonacci Retracements** (50%, 61.8% entry zones)
- ✅ **Trade Management** (Pivot-based trailing stops, partial exits)
- ✅ **Session Review Process** (Compare to hindsight-perfect execution)

### Technical Features

- 🔧 **Hummingbot Integration** - Binance Perpetual testnet connectivity
- 🤖 **Anthropic Claude** - Intelligent decision making
- 📊 **Real-Time Monitoring** - Continuous market surveillance
- 🛡️ **Risk Controls** - Multiple layers of protection
- 📝 **Complete Audit Trail** - Every decision logged
- ⚡ **Emergency Protocols** - Automatic failure handling
- 📈 **Performance Analytics** - Comprehensive statistics
- 🎯 **Correlation Detection** - Multi-position risk management

## Technology Stack

### Core Components

1. **LangGraph** - Agent orchestration and state management
2. **Anthropic Claude API** - Agent intelligence
3. **Hummingbot Framework** - Binance Perpetual testnet integration
4. **Python 3.10+** - Core language (required for LangGraph features)
5. **Pydantic** - State validation and serialization
6. **LangChain** - LLM interactions and tool use

### Data & Infrastructure

- **PostgreSQL** - Persistent state and audit logs
- **Redis** - Memory-based state caching and coordination
- **SQLAlchemy** - ORM for database interactions

### Optional Components

- **LangSmith** - LLM tracing and debugging
- **Prometheus/Grafana** - Metrics and monitoring
- **Docker** - Containerization
- **Kubernetes** - Orchestration
- **Jupyter** - Analysis notebooks

## File Structure

```
langgraph-ytc-agents/
├── README.md                          # This file
├── IMPLEMENTATION_GUIDE.md            # Setup instructions
├── ARCHITECTURE.md                    # Detailed LangGraph architecture
├── HUMMINGBOT_INTEGRATION.md         # Hummingbot + Binance Perpetual testnet
│
├── src/
│   ├── __init__.py
│   ├── state.py                       # Shared state schema (Pydantic)
│   ├── config.py                      # Configuration management
│   ├── tools.py                       # Tool definitions for agents
│   │
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── graph.py                   # Main StateGraph definition
│   │   ├── nodes/
│   │   │   ├── __init__.py
│   │   │   ├── pre_session.py         # system_init, risk_setup, market_structure, etc.
│   │   │   ├── session_open.py        # trend_definition, strength_weakness_analysis
│   │   │   ├── trading_cycle.py       # setup_scanner, entry_exec, trade_mgmt, exit_exec
│   │   │   ├── post_session.py        # session_review, performance_analytics, etc.
│   │   │   ├── support.py             # real_time_monitor, contingency_check, logging_audit
│   │   │   └── router.py              # Conditional routing logic
│   │   │
│   │   └── subgraphs/
│   │       ├── __init__.py
│   │       └── trading_cycle.py       # Looping trading subgraph
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py              # Base agent with Claude integration
│   │   ├── system_init.py             # 01. System Initialization
│   │   ├── risk_management.py         # 02. Risk Management
│   │   ├── market_structure.py        # 03. Market Structure
│   │   ├── economic_calendar.py       # 04. Economic Calendar
│   │   ├── trend_definition.py        # 05. Trend Definition
│   │   ├── strength_weakness.py       # 06. Strength & Weakness
│   │   ├── setup_scanner.py           # 07. Setup Scanner
│   │   ├── entry_execution.py         # 08. Entry Execution
│   │   ├── trade_management.py        # 09. Trade Management
│   │   ├── exit_execution.py          # 10. Exit Execution
│   │   ├── real_time_monitoring.py    # 11. Real-Time Monitoring
│   │   ├── session_review.py          # 12. Session Review
│   │   ├── performance_analytics.py   # 13. Performance Analytics
│   │   ├── learning_optimization.py   # 14. Learning & Optimization
│   │   ├── next_session_prep.py       # 15. Next Session Prep
│   │   ├── contingency_management.py  # 16. Contingency Management
│   │   └── logging_audit.py           # 17. Logging & Audit
│   │   
│   │   # Orchestration via LangGraph conditional routing (no dedicated agent)
│   │
│   ├── hummingbot/
│   │   ├── __init__.py
│   │   ├── connector.py               # Hummingbot client for Binance Perpetual testnet
│   │   ├── order_manager.py           # Order execution wrapper
│   │   └── market_data.py             # Real-time market data feeds
│   │
│   └── database/
│       ├── __init__.py
│       ├── models.py                  # SQLAlchemy models
│       └── persistence.py             # State checkpointing
│
├── tests/
│   ├── unit/
│   │   ├── test_state.py
│   │   ├── test_agents/
│   │   └── test_tools.py
│   └── integration/
│       ├── test_graph.py
│       └── test_hummingbot_integration.py
│
├── examples/
│   ├── simple_session.py              # Basic trading session example
│   └── backtest_replay.py             # Replay historical trades
│
├── pyproject.toml                     # Dependencies and package config
├── docker-compose.yml                 # Local development setup
└── .env.example                       # Environment variables template
```

## Quick Start

### Prerequisites

```bash
# Clone and setup
git clone <repo>
cd langgraph-ytc-agents
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Setup local services (PostgreSQL, Redis)
docker-compose up -d

# Configure environment
cp .env.example .env
# Edit .env with your API keys and settings
export ANTHROPIC_API_KEY="your_key_here"
```

### Basic Usage

```python
from src.graph.graph import build_trading_graph
from src.state import TradingState

# Create the graph
graph = build_trading_graph()

# Compile for execution
compiled_graph = graph.compile()

# Initial state
initial_state = TradingState(
    session_id="2025-01-15-001",
    market="crypto",
    instrument="ETH-USDT",
    exchange="binance_perpetual_testnet",
    session_duration_hours=4,
    risk_per_trade_pct=1.0,
    max_session_risk_pct=3.0
)

# Run trading session (blocking)
final_state = compiled_graph.invoke(initial_state)

# Or stream results for real-time monitoring
for output in compiled_graph.stream(initial_state):
    print(f"State update: {output}")

# Access final results
print(f"Session P&L: {final_state.session_pnl}")
print(f"Trades executed: {len(final_state.trades)}")
print(f"Win rate: {final_state.win_rate:.2%}")
```

### Advanced Usage with Checkpointing

```python
from langgraph.checkpoint.postgres import PostgresSaver

# Use persistent checkpointing for production
checkpoint_dir = PostgresSaver(
    conn_string="postgresql://user:password@localhost/langgraph"
)

# Compile with checkpointing
compiled_graph = graph.compile(checkpointer=checkpoint_dir)

# Run with persistence (can resume if interrupted)
config = {"configurable": {"thread_id": "trading-session-001"}}
final_state = compiled_graph.invoke(initial_state, config)
```

## Configuration

All configuration is managed via Pydantic models in `src/config.py` and environment variables:

### Risk Parameters (in TradingState)

```python
# src/config.py
class RiskConfig(BaseModel):
    risk_per_trade_pct: float = 1.0           # 1% per trade
    max_session_risk_pct: float = 3.0         # 3% max session loss
    max_positions: int = 3                    # Max simultaneous
    max_total_exposure_pct: float = 3.0       # Total exposure cap
    consecutive_loss_limit: int = 5           # Stop after 5 losses
    stop_loss_points: int = 50                # Default SL in pips
```

### Timeframe Configuration

```python
class TimeframeConfig(BaseModel):
    higher: str = "4h"       # Structure & S/R
    trading: str = "15m"     # Trend & Setups
    lower: str = "5m"        # Entry refinement
```

### Session Configuration

```python
class SessionConfig(BaseModel):
    session_id: str
    market: str = "crypto"
    instrument: str = "ETH-USDT"
    exchange: str = "binance_perpetual_testnet"
    start_time: str = "00:00:00"  # 24/7 crypto market
    duration_hours: int = 4
    timezone: str = "UTC"
    enable_pre_market: bool = False
    enable_post_market: bool = False
```

## Risk Controls

Risk is enforced at multiple levels in the LangGraph state management:

### Multi-Layer Protection

1. **Pre-Trade Node** (`risk_management` agent)
   - Pydantic validation of position sizes
   - Risk limit checks against state limits
   - Correlation analysis with active positions
   - Margin validation through Hummingbot API

2. **Continuous Monitoring** (Real-time monitoring node)
   - Streaming state updates with P&L tracking
   - Session limit validation on each cycle
   - Structure break detection from market data
   - Time-based exit triggers

3. **Contingency Node** (Emergency handling)
   - Automatic position flattening if risk exceeded
   - Connection loss recovery via state checkpoints
   - Platform failure handling with PostgreSQL persistence
   - Manual override via state mutations

### Session Stop Loss

```python
# In trading_cycle router node:
if state.session_pnl <= -state.account_balance * state.max_session_risk_pct / 100:
    state.status = "emergency_halt"
    # Returns to contingency node for flattening all positions
```

## Performance Monitoring

### Real-Time Metrics (Streamed from Graph)

Metrics are computed and updated in the shared `TradingState`:

```python
# Real-time state fields:
session_pnl: float           # Current session profit/loss
risk_utilization: float      # % of session risk used
win_rate: float              # Winning trades / total trades
avg_r_multiple: float        # Average risk/reward ratio
time_in_session: timedelta   # Duration in session
trades: List[Trade]          # All executed trades
positions: List[Position]    # Active positions
system_health: str           # "healthy", "warning", "critical"
```

Use LangSmith for visualization:
- Stream node execution times
- Track state mutations
- Monitor decision branches

### Post-Session Analytics Node

The `session_review` node computes comprehensive metrics:

```python
# Computed by performance_analytics agent:
trade_by_trade_stats: List[TradeMetrics]
setup_performance: Dict[str, SetupStats]
entry_quality_score: float
exit_quality_score: float
optimal_vs_actual_comparison: Dict
lessons_learned: List[str]
improvement_recommendations: List[str]
```

## YTC Methodology Compliance

### Core Principles

✅ **Trade What You See** - Pure price action analysis  
✅ **Risk Management First** - Never exceed limits  
✅ **Quality Over Quantity** - Wait for A+ setups  
✅ **Trend Structure** - Trade with structure alignment  
✅ **Review & Improve** - Deliberate practice cycle  

### Procedures Manual

Each agent implements YTC's procedures manual:
- Pre-session checklist
- During-session workflow
- Post-session review
- Continuous improvement

## Testing

### Unit Tests (Agent Logic)

```bash
# Test individual agent nodes
pytest tests/unit/test_agents/ -v

# Test state schema validation
pytest tests/unit/test_state.py -v

# Test tools and utilities
pytest tests/unit/test_tools.py -v
```

### Integration Tests (Graph Execution)

```bash
# Test full graph flow
pytest tests/integration/test_graph.py -v

# Test Hummingbot integration
pytest tests/integration/test_hummingbot_integration.py -v
```

### End-to-End Testing with LangSmith

```python
# Enable LangSmith tracing
import os
os.environ["LANGSMITH_API_KEY"] = "your_key"
os.environ["LANGSMITH_PROJECT"] = "ytc-agents"

# Run with tracing enabled
compiled_graph.invoke(initial_state)
# View traces at https://smith.langchain.com/
```

## Deployment

### Local Development

```bash
# Setup and run locally
docker-compose up -d
python examples/simple_session.py
```

### Docker Deployment

```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f agent-service
```

### Kubernetes Deployment

```bash
# Deploy to K8s
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/statefulset.yaml
kubectl apply -f k8s/service.yaml

# Check status
kubectl get pods -n ytc-agents
```

## Monitoring & Alerts

### LangGraph Native Monitoring

- **Node Execution Times**: Tracked via `compiled_graph.stream()` callbacks
- **State Mutations**: Logged at each node transition
- **Conditional Routing**: Tracked in graph.invoke() traces
- **Error Handling**: Caught and logged with state snapshots

### External Monitoring

```python
# Prometheus metrics integration
from prometheus_client import Counter, Histogram

trades_executed = Counter('ytc_trades_executed_total', 'Total trades')
graph_execution_time = Histogram('ytc_graph_execution_seconds', 'Graph execution time')

# Custom callbacks for state changes
def on_state_change(state):
    # Publish to Prometheus, send alerts, etc.
    pass

# PostgreSQL audit logs
# All state changes logged to trading_audit table
```

### Alert Channels

- **LangSmith**: Real-time trace monitoring
- **PostgreSQL Logs**: Persistent audit trail
- **Webhook Integrations**: Custom downstream systems
- **Email/Slack**: Critical errors only (contingency node)

## Security

- API keys encrypted at rest
- Secure credential storage
- Audit logging enabled
- Access control implemented
- Network isolation

## Compliance

- Complete audit trail
- Trade justification logging
- Decision reasoning captured
- Regulatory reporting ready
- Performance attribution

## Support

### Documentation

- See individual agent .md files
- Check IMPLEMENTATION_GUIDE.md
- Review ARCHITECTURE.md
- Read YTC volumes 1-6

### Community

- GitHub Issues
- Discord Channel
- Email Support

## Disclaimer

This system is for educational purposes. Trading involves substantial risk of loss. Past performance does not guarantee future results. Only trade with capital you can afford to lose.

The YTC methodology is the intellectual property of Lance Beggs (YourTradingCoach.com). This implementation is an independent interpretation and not endorsed by the original author.

## License

MIT License - See LICENSE file

## Version History

- v1.0.0 - Initial release with complete agent architecture
- Full YTC methodology implementation
- Hummingbot integration
- Complete documentation

## Credits

- **YTC Methodology**: Lance Beggs (YourTradingCoach.com)
- **Trading Platform**: Hummingbot + Binance Perpetual Testnet
- **AI Framework**: Anthropic Claude
- **Graph Orchestration**: LangGraph
- **Implementation**: Vi (2025)

---

**Ready to automate your YTC trading? Start with IMPLEMENTATION_GUIDE.md**
