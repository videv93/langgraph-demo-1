# Hummingbot Integration

This document outlines the integration between the LangGraph trading system and the Hummingbot API Client Python SDK.

## Overview

The system uses the **Hummingbot API Client** - an official asynchronous Python SDK for communicating with Hummingbot. This provides a type-safe, modular interface to Hummingbot's RESTful API without needing to make raw HTTP requests.

### Why Hummingbot API Client?

Instead of making direct REST API calls with `requests` or similar libraries, we use the official Python SDK which provides:

- **Type safety** - Typed responses and parameters
- **Async/await support** - Non-blocking I/O operations
- **Modular structure** - Organized by feature (portfolio, trading, connectors, etc.)
- **Error handling** - Built-in exception handling and retries
- **Authentication** - Username/password auth handled automatically
- **Documentation** - Well-documented methods and examples

### Official Library Details
- **Package**: `hummingbot-api-client`
- **GitHub**: https://github.com/hummingbot/hummingbot-api-client
- **Reputation**: High
- **Code Snippets**: 61+
- **Maintainer**: Hummingbot Foundation

## Configuration

### Environment Variables (.env)

```env
# Hummingbot connection (username/password authentication)
HUMMINGBOT_HOST=localhost
HUMMINGBOT_PORT=8000
HUMMINGBOT_USERNAME=your_username
HUMMINGBOT_PASSWORD=your_password

# Exchange and trading configuration
EXCHANGE=binance
TRADING_PAIR=ETH-USDT

# Risk management parameters
ACCOUNT_RISK_PERCENT=2.0
MAX_POSITION_SIZE=10000.0
MAX_DRAWDOWN_PERCENT=10.0
STOP_LOSS_MARGIN=0.02
TAKE_PROFIT_MARGIN=0.05
```

### Setup

1. **Copy environment template**:
   ```bash
   cp .env.example .env
   ```

2. **Fill in your Hummingbot credentials**:
   - `HUMMINGBOT_HOST`: IP/hostname of running Hummingbot instance (default: localhost)
   - `HUMMINGBOT_PORT`: API port (default: 8000)
   - `HUMMINGBOT_USERNAME`: Hummingbot API username
   - `HUMMINGBOT_PASSWORD`: Hummingbot API password

3. **Install dependencies**:
   ```bash
   pip install -e .
   ```

## Usage

### Initialize Hummingbot API Client

The `create_hummingbot_client()` helper function initializes the official HummingbotAPIClient with credentials from your `.env` file:

```python
from agent.config import create_hummingbot_client

# Create and initialize client (async)
client = await create_hummingbot_client()
# Returns: HummingbotAPIClient instance or None if initialization fails
```

**Internally, this does**:
```python
from hummingbot_api_client import HummingbotAPIClient

client = HummingbotAPIClient(
    base_url="http://localhost:8000",
    username="your_username",
    password="your_password",
)
await client.init()  # Establish connection and authenticate
```

### Get System Initialization Config

```python
from agent.config import create_hummingbot_client, get_system_initialization_config

# Create and initialize the official Hummingbot API Client
client = await create_hummingbot_client()

# Build config for system initialization
config = get_system_initialization_config(hummingbot_client=client)
```

The client is now passed to the SystemInitialization agent which uses its methods to fetch real-time data.

### System Initialization Flow

The `SystemInitialization` agent:

1. **Checks Hummingbot connection** - Verifies client is initialized
2. **Validates exchange connectivity** - Confirms exchange is operational
3. **Validates trading pair** - Checks if trading pair is available on exchange
4. **Fetches account balance** - Retrieves USDT balance from Hummingbot portfolio
5. **Validates minimum balance** - Ensures balance >= 100 USDT
6. **Initializes risk parameters** - Sets up risk management rules

```python
from agent.agents import SystemInitialization

agent = SystemInitialization(config=config)
result = agent.execute()

print(f"Connected: {result['hummingbot_connected']}")
print(f"Balance: {result['account_balance']} USDT")
print(f"Status: {result['system_status']}")
print(f"Errors: {result['validation_errors']}")
```

## Hummingbot API Client Methods

The SDK provides organized, typed methods grouped by feature. Here are the key methods used by the trading system:

### `client.portfolio.get_state()`

**Official SDK Method** from the Portfolio router

Retrieves the current state of the portfolio, including all account balances across connectors.

```python
from hummingbot_api_client import HummingbotAPIClient

client = HummingbotAPIClient(base_url="http://localhost:8000", username="user", password="pass")
await client.init()

# Get portfolio state (no REST call needed - SDK handles it)
portfolio_state = await client.portfolio.get_state()

# Returns: {
#     "account_name": {
#         "connector_name": [
#             {"asset": "USDT", "free": 1000.0, "locked": 0.0, "total": 1000.0},
#             {"asset": "ETH", "free": 1.5, "locked": 0.0, "total": 1.5},
#         ]
#     }
# }
```

**Replaces**: `GET /api/portfolio/state` REST endpoint
**SDK Advantage**: Typed response, automatic auth, error handling

### `client.connectors.list_connectors()`

**Official SDK Method** from the Connectors router

Lists all available connectors (exchanges) configured in Hummingbot.

```python
connectors = await client.connectors.list_connectors()
# Returns: ["binance", "kucoin", "coinbase", ...]
```

**Replaces**: `GET /api/connectors` REST endpoint

### `client.connectors.get_trading_rules(connector_name)`

**Official SDK Method** from the Connectors router

Fetches trading rules for a specific connector (minimum order size, tick sizes, fees, etc).

```python
rules = await client.connectors.get_trading_rules("binance")
# Returns exchange-specific trading parameters
```

**Replaces**: `GET /api/connectors/{connector}/trading-rules` REST endpoint

## Account Balance Fetching

The system dynamically fetches account balances using the Hummingbot API Client instead of hardcoded values:

### Implementation

```python
async def _get_balance_async(self) -> float:
    """Asynchronously fetch USDT balance from Hummingbot portfolio using the SDK."""
    # Calls client.portfolio.get_state() - Official SDK method
    portfolio_state = await self.hummingbot_client.portfolio.get_state()
    
    # Parse response and sum USDT across all accounts
    total_usdt = 0.0
    for account_name, connectors in portfolio_state.items():
        for connector_name, balances in connectors.items():
            for balance_item in balances:
                if balance_item.get("asset") == "USDT":
                    total_usdt += float(balance_item.get("free", 0))
    
    return total_usdt
```

### API Client Benefits

Using the SDK instead of raw REST API:

- **No manual HTTP requests** - SDK handles all HTTP communication internally
- **Typed responses** - Full type hints for portfolio state
- **Automatic authentication** - Credentials handled transparently
- **Error handling** - Built-in retries and exception handling
- **Synchronization** - Async/await support without additional setup
- **Real-time data** - Always fetches current exchange balance
- **Zero config** - No need to hardcode static balance values
- **Minimum validation** - Automatic check that balance >= 100 USDT

## Error Handling

The API Client SDK includes built-in error handling. Connection failures are gracefully handled:

```python
# SystemInitialization agent catches SDK exceptions
result = agent.execute()

if result['hummingbot_connected'] is False:
    errors = result['validation_errors']
    print(f"Connection failed: {errors}")
    # Possible errors:
    # - "Hummingbot client not initialized"
    # - "Exchange connectivity check failed: ..."
    # - "Failed to fetch account balance from Hummingbot"
    # - "Account balance is below minimum 100 USDT"
```

### SDK Exception Handling

The SDK handles common errors:

```python
try:
    client = HummingbotAPIClient(base_url=url, username=user, password=pass)
    await client.init()  # Raises exception if connection fails
    portfolio = await client.portfolio.get_state()  # Built-in retry logic
except Exception as e:
    print(f"API error: {e}")
    # SDK provides helpful error messages
```

## Running Hummingbot Instance

Before using this system, ensure Hummingbot is running with the API enabled:

```bash
# Start Hummingbot locally
hummingbot

# Or with Docker
docker run -it hummingbot/hummingbot:latest
```

The Hummingbot API will be available at:
```
http://HUMMINGBOT_HOST:HUMMINGBOT_PORT
# Default: http://localhost:8000
```

## Architecture: API Client vs REST API

```
┌─────────────────────────────────────────┐
│  LangGraph Trading System               │
│  (src/agent/agents/system_init.py)      │
└─────────┬───────────────────────────────┘
          │
          │ Uses
          ▼
┌─────────────────────────────────────────┐
│  Hummingbot API Client (Python SDK)     │
│  - HummingbotAPIClient class            │
│  - portfolio.get_state()                │
│  - connectors.list_connectors()         │
│  - Error handling & auth                │
└─────────┬───────────────────────────────┘
          │
          │ Makes HTTP requests to
          ▼
┌─────────────────────────────────────────┐
│  Hummingbot REST API                    │
│  - http://localhost:8000/api/*          │
│  - Requires Bearer token auth           │
│  - Used transparently by SDK            │
└─────────┬───────────────────────────────┘
          │
          │ Connects to
          ▼
┌─────────────────────────────────────────┐
│  Hummingbot Instance                    │
│  - Exchange connectors (Binance, etc)   │
│  - Account balances & trading           │
│  - Market data                          │
└─────────────────────────────────────────┘
```

**Key Point**: The SDK abstracts away REST API details - you never make direct HTTP calls.

## Dependencies

### Installation

The `hummingbot-api-client` package is specified in `pyproject.toml`:

```toml
dependencies = [
    "langgraph>=1.0.0",
    "python-dotenv>=1.0.1",
    "hummingbot-api-client>=0.1.0",  # Official Python SDK
]
```

Install with:
```bash
pip install -e .
```

Or install the SDK directly:
```bash
pip install hummingbot-api-client
```

### Import

```python
from hummingbot_api_client import HummingbotAPIClient

# Now you can use the SDK
client = HummingbotAPIClient(base_url="http://localhost:8000", username="user", password="pass")
await client.init()
```
