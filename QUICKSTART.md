# Quick Start Guide - Hummingbot Trading System

This guide walks you through setting up and running the LangGraph trading system with Hummingbot integration.

## Prerequisites

- Python 3.10+
- A running Hummingbot instance
- Hummingbot API credentials (username/password)

## Setup Steps

### 1. Configure Environment Variables

Copy the example environment file and fill in your Hummingbot credentials:

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
# Hummingbot API credentials
HUMMINGBOT_HOST=localhost        # Your Hummingbot host
HUMMINGBOT_PORT=8000             # Your Hummingbot API port
HUMMINGBOT_USERNAME=your_user    # Hummingbot username
HUMMINGBOT_PASSWORD=your_pass    # Hummingbot password

# Trading configuration
EXCHANGE=binance
TRADING_PAIR=ETH-USDT

# Risk parameters (optional - defaults provided)
ACCOUNT_RISK_PERCENT=2.0
MAX_POSITION_SIZE=10000.0
```

### 2. Install Dependencies

```bash
# Install the package and all dependencies
pip install -e .

# Verify installation
python -c "from hummingbot_api_client import HummingbotAPIClient; print('✓ Hummingbot API Client installed')"
```

### 3. Test Hummingbot Connection

Before running the full trading system, verify your Hummingbot setup:

```bash
# Run the connection test
python test_hummingbot_init.py
```

**Expected output:**
```
============================================================
Testing Hummingbot API Client Initialization
============================================================

📋 Loading Hummingbot configuration from .env...
   Host: localhost
   Port: 8000
   Username: your_user
   Exchange: binance
   Trading Pair: ETH-USDT

🔄 Initializing Hummingbot API Client...
✓ Hummingbot API Client initialized successfully!

📊 Fetching portfolio state...
✓ Portfolio state retrieved:
   Account: default
     Connector: binance
       USDT: 10000.0
       ETH: 1.5

🔌 Listing available connectors...
✓ Available connectors: ['binance', 'kucoin']

📐 Fetching trading rules for binance...
✓ Trading rules retrieved for binance
   Total trading pairs: 1400+

============================================================
✓ Hummingbot initialization test completed successfully!
============================================================
```

### 4. Run the Trading System

Once the connection test passes, run the trading graph:

```bash
# Run the main trading system
python -m src.agent.graph
```

**Expected output:**
```
🔄 Initializing Hummingbot API Client...
✓ Hummingbot API Client initialized successfully

📊 Starting trading session: a1b2c3d4-e5f6-7890-abcd-ef1234567890
   Hummingbot Host: localhost
   Exchange: binance
   Trading Pair: ETH-USDT

🟢 System Initialization Node
✓ System initialized | Hummingbot: True | Balance: 10000.0 USDT

🟡 Risk Management Node
...
```

## Troubleshooting

### Hummingbot Connection Failed

**Error**: `❌ Failed to initialize Hummingbot client`

**Solution**:
1. Verify Hummingbot is running: `curl http://localhost:8000/api/health`
2. Check credentials in `.env`: `HUMMINGBOT_USERNAME`, `HUMMINGBOT_PASSWORD`
3. Verify host/port: `ping localhost` and check HUMMINGBOT_PORT=8000
4. Review Hummingbot logs for authentication errors

### Port Already in Use

**Error**: `Address already in use`

**Solution**:
```bash
# Check what's using the port
lsof -i :8000

# If needed, change HUMMINGBOT_PORT in .env
HUMMINGBOT_PORT=8001
```

### Module Import Errors

**Error**: `ModuleNotFoundError: No module named 'hummingbot_api_client'`

**Solution**:
```bash
# Reinstall dependencies
pip install -e .

# Or install directly
pip install hummingbot-api-client
```

### Account Balance Zero

**Error**: System initialization fails with "Account balance is below minimum 100 USDT"

**Solution**:
1. Check your Hummingbot account has USDT: `python test_hummingbot_init.py`
2. Deposit funds to your connected exchange account
3. Verify trading account is properly configured in Hummingbot

## Architecture Overview

```
User runs:
    python -m src.agent.graph
           ↓
Initializes Hummingbot API Client (async)
           ↓
LangGraph executes system_initialization_node
           ↓
SystemInitialization agent:
  - Checks Hummingbot connection
  - Validates exchange connectivity
  - Fetches account balance via portfolio.get_state()
  - Initializes risk parameters
           ↓
Trading state updated with:
  - account_balance (from Hummingbot)
  - Hummingbot connection status
  - Exchange information
           ↓
Graph continues to next nodes (risk management, market analysis, etc.)
```

## Running in Development Mode

For development and testing:

```bash
# Run with detailed logging
DEBUG=1 python -m src.agent.graph

# Run tests
make test

# Run with type checking
mypy src/

# Format code
ruff format src/
```

## Next Steps

1. **Review the trading flow**: See `src/agent/graph.py` for the 16-node trading pipeline
2. **Customize agents**: Edit individual agents in `src/agent/agents/`
3. **Add trading strategies**: Extend the setup scanner with your strategies
4. **Deploy to production**: Use LangGraph Platform for persistent state and scaling

See [HUMMINGBOT_INTEGRATION.md](docs/HUMMINGBOT_INTEGRATION.md) for detailed API documentation.
