# YTC Trading Assistant

## Overview

The YTC Trading Assistant provides an interactive chat interface for accessing YTC (Your Trading Coach) trading methodology knowledge through **Pinecone Assistant** with **OpenAI-compatible API**.

This allows agents and traders to:
- Query the complete YTC trading method knowledge base
- Get real-time guidance on trade setups and patterns
- Validate trading decisions against YTC principles
- Access entry/exit rules, stop loss placement, and risk management

## Architecture

```
┌─────────────────────┐
│   Trading Agents    │
│  (LangGraph nodes)  │
└──────────┬──────────┘
           │
           ▼
┌──────────────────────────┐
│ YTCTradingAssistant      │
│ (src/agent/utils/)       │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ OpenAI-Compatible API            │
│ (Pinecone Assistant endpoint)     │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ Pinecone Assistant               │
│ (YTC Knowledge Base)             │
└──────────────────────────────────┘
```

## Setup

### 1. Environment Configuration

Add to `.env` file:

```env
# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=ytc-strategy-patterns
PINECONE_ENVIRONMENT=us-east-1

# Pinecone Assistant
PINECONE_ASSISTANT_NAME=ytc-trading-assistant

# OpenAI API (for Pinecone Assistant access)
OPENAI_API_KEY=your_openai_api_key
```

### 2. Install Dependencies

```bash
pip install openai pinecone
```

### 3. Create Pinecone Assistant

Set up Pinecone Assistant following [Pinecone documentation](https://docs.pinecone.io/guides/assistant/chat-through-the-openai-compatible-interface):

1. Create a Pinecone Assistant named `ytc-trading-assistant`
2. Configure it with your YTC knowledge base
3. Get your OpenAI API key for authentication

## Usage

### Interactive CLI

```bash
python ytc_assistant_cli.py
```

Commands:
- `1` - Ask about YTC method
- `2` - Get pattern analysis
- `3` - Get entry rules
- `4` - Get Fibonacci strategy
- `5` - Get stop loss guidance
- `6` - Get risk management rules
- `7` - Validate a setup
- `help` - Show menu
- `exit` - Quit

### Python API

```python
from src.agent.utils.ytc_assistant import YTCTradingAssistant

# Initialize assistant
assistant = YTCTradingAssistant()

# Query the methodology
response = assistant.query_ytc_method(
    "What are the entry rules for a pullback in an uptrend?"
)
print(response)

# Get pattern analysis
analysis = assistant.get_pattern_analysis(
    pattern_type="3_swing_trap",
    trend="uptrend",
    price_data={
        "current_price": 2500.0,
        "recent_high": 2550.0,
        "recent_low": 2450.0,
    }
)
print(analysis)

# Validate a setup
setup = {
    "pattern_type": "pullback",
    "trend": "uptrend",
    "entry_price": 2475.0,
    "stop_loss": 2450.0,
    "targets": [2525.0, 2575.0],
    "supporting_factors": ["RSI oversold", "Support bounce", "Volume confirmation"],
}

result = assistant.validate_setup(setup)
print(f"Validated: {result['validated']}")
print(f"Analysis: {result['analysis']}")
```

### Integration with LangGraph Agents

```python
from src.agent.utils.ytc_assistant import YTCTradingAssistant

class SetupScannerAgent:
    def __init__(self, config):
        self.config = config
        self.assistant = YTCTradingAssistant()

    def execute(self) -> dict:
        # Get setup analysis
        analysis = self.assistant.get_pattern_analysis(
            pattern_type=self.config["pattern"],
            trend=self.config["trend"],
            price_data=self.config["price_data"],
        )
        
        # Validate setup
        validation = self.assistant.validate_setup(self.config["setup"])
        
        return {
            "analysis": analysis,
            "validation": validation,
            "ready_to_trade": validation["validated"],
        }
```

## API Methods

### Core Query Methods

#### `query_ytc_method(question, market_context=None)`
General query to YTC knowledge base.

**Parameters:**
- `question` (str): Question about YTC trading methodology
- `market_context` (dict, optional): Current market data for context

**Returns:** str - Assistant response

**Example:**
```python
response = assistant.query_ytc_method(
    "How do I identify a 3-swing trap?",
    market_context={
        "trend": "uptrend",
        "current_price": 2500.0,
        "volatility": "medium"
    }
)
```

#### `get_pattern_analysis(pattern_type, trend, price_data)`
Analyze specific YTC pattern in current conditions.

**Parameters:**
- `pattern_type` (str): Pattern type (3_swing_trap, pullback, breakout, etc.)
- `trend` (str): Market trend (uptrend, downtrend, sideways)
- `price_data` (dict): Price data (current_price, recent_high, recent_low)

**Returns:** str - Pattern analysis with entry/exit guidance

#### `get_entry_rules(setup_type, direction)`
Get detailed entry rules for specific setup.

**Parameters:**
- `setup_type` (str): Type of setup
- `direction` (str): Trade direction (long, short)

**Returns:** str - Entry rules and triggers

#### `get_fibonacci_strategy()`
Get Fibonacci retracement strategy.

**Returns:** str - Fibonacci entry/exit strategy details

#### `get_stop_loss_guidance(setup_type, entry_price, structure)`
Get YTC stop loss placement guidance.

**Parameters:**
- `setup_type` (str): Type of setup
- `entry_price` (float): Planned entry price
- `structure` (dict): Market structure (support, resistance levels)

**Returns:** str - Stop loss placement recommendations

#### `get_risk_management_rules()`
Get YTC risk management principles.

**Returns:** str - Risk management rules and position sizing

#### `validate_setup(setup_data)`
Validate setup against YTC rules.

**Parameters:**
- `setup_data` (dict): Setup with pattern_type, trend, entry_price, stop_loss, targets, supporting_factors

**Returns:** dict - Validation result with confidence score and analysis

## Response Quality

The assistant provides high-quality responses by:
- Using lower temperature (0.3) for methodology consistency
- Including system prompt with YTC methodology principles
- Leveraging Pinecone's semantic search for relevant context
- Filtering responses through YTC rule validation

## Error Handling

The assistant gracefully handles errors:

```python
assistant = YTCTradingAssistant()

try:
    response = assistant.query_ytc_method("question")
except Exception as e:
    logger.error(f"Assistant error: {e}")
    # Fallback to manual rules or skip validation
```

## Performance Considerations

- **Cache responses** for commonly asked questions
- **Batch validate** multiple setups in a single request
- **Use market context** to reduce response length
- **Monitor API usage** through OpenAI dashboard

## Limitations

- Requires internet connection for Pinecone/OpenAI
- Limited to knowledge in training data
- Not real-time market data (use Hummingbot for that)
- Should not be sole basis for trading decisions

## Future Enhancements

- [ ] Caching layer for frequent queries
- [ ] Multi-turn conversation history
- [ ] Real-time market data integration
- [ ] Setup template library
- [ ] Historical performance tracking
- [ ] Custom training on user trade logs
