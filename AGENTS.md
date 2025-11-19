# Agent Guidelines for YTC LangGraph Trading System

## Build & Test Commands

### Run Tests
```bash
make test                           # Run unit tests (default: tests/unit_tests/)
make test TEST_FILE=tests/unit_tests/test_configuration.py  # Run single test file
make test_watch                     # Watch mode (reruns on file changes)
make integration_tests              # Run integration tests
make extended_tests                 # Run extended test suite
```

### Linting & Formatting
```bash
make lint                           # Check code style (ruff + mypy)
make format                         # Auto-format code (ruff)
make spell_check                    # Check spelling
```

## Running the Trading System

### Local Execution (Recommended for Development)
```bash
python3 run_local.py                # Run complete trading graph locally
python3 test_hummingbot_connection.py  # Test Hummingbot connectivity
```

### LangGraph Dev (Interactive UI)
```bash
python3 init_hummingbot.py          # Initialize Hummingbot client first
langgraph dev                       # Start dev server at http://localhost:8123
```

### Hummingbot Setup (Optional but Recommended)
```bash
docker run -it -p 8000:8000 hummingbot/hummingbot  # Run Hummingbot in Docker
```

See [RUN_GUIDE.md](RUN_GUIDE.md) for detailed instructions.

## Architecture & Structure

**Core Framework**: LangGraph StateGraph with 16 trading agents (no master orchestrator—routing via LangGraph conditionals)

**Key Files**:
- `src/agent/graph.py` - Main graph definition (TradingState, nodes, conditional routing)
- `pyproject.toml` - Dependencies (LangGraph ≥1.0.0, Python ≥3.10)
- `tests/` - Unit tests in `unit_tests/`, integration tests in `integration_tests/`

**Agent Nodes** (placeholder imports from `agents/` module):
system_init → risk_mgmt → market_structure → economic_calendar → (checkpoint) → trend_definition → strength_weakness → (checkpoint) → setup_scanner → (conditional loop) → entry_execution → trade_management → exit_execution

**State**: TypedDict (TradingState) with session info, positions, P&L, human decisions, agent outputs. Uses `Annotated[list, operator.add]` for accumulating fields.

## Code Style & Conventions

**Imports**: LangGraph (`StateGraph`, `END`, `MemorySaver`), standard library first, then external packages. Use absolute imports from `agent.` namespace.

**Types**: Full type hints required (mypy strict mode). TypedDict for state, Literal for enums, Annotated for reducers. Return TradingState from all node functions.

**Naming**: 
- Nodes: `{name}_node` (e.g., `system_initialization_node`)
- Routers: `route_after_{checkpoint}` returning Literal string routes
- State fields: snake_case; status fields use Literal unions

**Docstrings**: Google-style docstrings required (pydocstyle convention); describe what agent does, not "Execute agent"

**Error Handling**: Exceptions propagate (agents raise, graph halts). State mutations via direct updates (e.g., `state["field"] = value`). No silent failures.

**Node Pattern**: Print emoji indicator, import agent class, instantiate with config, call `execute()`, update state dict, append to `messages` list for audit trail.

## Key Implementation Notes

- **Human Checkpoints**: Pause graph with input() for decisions; return state with appended decision to `human_decisions`
- **Conditional Edges**: Router functions check state fields (e.g., `setup_approved`, `session_status`) and return Literal route strings
- **Checkpointing**: MemorySaver used for state persistence; `thread_id` in config enables resumable runs
- **Agent Stubs**: Actual agents not yet implemented; nodes import from `agents/` module (add implementations there)
