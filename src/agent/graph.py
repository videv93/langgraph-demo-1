"""Trading system graph using LangGraph StateGraph.

This module defines the main trading graph with 16 agent nodes and human-in-the-loop
checkpoints using interrupt and Command primitives.
"""

import asyncio
import operator
import uuid
from typing import Annotated, Literal, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, END, START
from langgraph.types import Command

from agent.agents import (
    EconomicCalendar,
    EntryExecution,
    ExitExecution,
    LearningOptimization,
    MarketStructure,
    NextSessionPrep,
    PerformanceAnalytics,
    RiskManagement,
    SessionReview,
    SetupScanner,
    StrengthWeakness,
    SystemInitialization,
    TradeManagement,
    TrendDefinition,
)
from agent.config import (
    create_hummingbot_client,
    get_system_initialization_config,
)
from agent.agents.utils.hummingbot import (
    fetch_current_price,
    fetch_market_data,
    fetch_price_history,
)

# Cache for hummingbot client initialization
_hummingbot_client_cache = None

async def get_hummingbot_client():
    """Get or initialize hummingbot client (cached).
    
    Returns:
        Initialized HummingbotAPIClient or None if unavailable.
    """
    global _hummingbot_client_cache
    if _hummingbot_client_cache is None:
        try:
            _hummingbot_client_cache = await create_hummingbot_client()
        except Exception as e:
            print(f"⚠️  Hummingbot initialization failed: {e}")
            _hummingbot_client_cache = False  # Mark as failed to avoid retries
    
    return _hummingbot_client_cache if _hummingbot_client_cache is not False else None


class TradingState(TypedDict):
    """State for the trading system."""

    session_id: str
    messages: Annotated[list, operator.add]
    human_decisions: Annotated[list, operator.add]
    market_data: dict
    positions: dict
    pnl: float
    setup_approved: bool
    session_status: Literal["active", "paused", "closed"]
    account_balance: float


async def system_initialization_node(state: TradingState) -> TradingState:
    """Initialize the trading session and validate system readiness.

    Executes SystemInitialization agent to perform pre-trading checks and
    initialize system parameters with Hummingbot integration.
    """
    print("🟢 System Initialization Node")

    # Get or initialize Hummingbot client (cached)
    hummingbot_client = await get_hummingbot_client()
    
    # Build configuration from environment and defaults with Hummingbot client
    config = get_system_initialization_config(hummingbot_client=hummingbot_client)

    # Instantiate and execute the system initialization agent
    agent = SystemInitialization(config=config)
    result = await agent.execute()

    # Update state with initialization result
    state["messages"].append(
        {
            "node": "system_initialization",
            "status": result["system_status"],
            "timestamp": result["initialization_timestamp"],
            "errors": result["validation_errors"],
            "hummingbot_connected": result["hummingbot_connected"],
            "account_balance": result["account_balance"],
        }
    )

    # Store account balance in state
    state["account_balance"] = result["account_balance"]
    if "market_data" not in state:
        state["market_data"] = {}
    state["market_data"]["account_balance"] = result["account_balance"]

    # Check if initialization was successful
    if not result["session_initialized"]:
        state["session_status"] = "failed"
        raise RuntimeError(
            f"System initialization failed: {', '.join(result['validation_errors'])}"
        )

    state["session_status"] = "active"
    print(
        f"✓ System initialized | Hummingbot: {result['hummingbot_connected']} | "
        f"Balance: {result['account_balance']} USDT"
    )
    return state


def risk_management_node(state: TradingState) -> TradingState:
    """Execute risk management checks and validate position sizing limits.

    Validates account risk percentage, position size limits, and drawdown
    constraints before proceeding with market analysis.
    """
    print("🟡 Risk Management Node")

    # Use account balance from state (fetched from Hummingbot)
    account_balance = state.get("account_balance", 0.0)

    # Instantiate and execute the risk management agent
    agent = RiskManagement(config={"account_balance": account_balance})
    result = agent.execute()

    # Update state with risk management result
    state["messages"].append(
        {
            "node": "risk_management",
            "risk_check_passed": result["risk_check_passed"],
            "account_risk_percentage": result["account_risk_percentage"],
            "position_size_limit": result["position_size_limit"],
            "max_drawdown_limit": result["max_drawdown_limit"],
            "warnings": result["warnings"],
        }
    )

    # Halt if risk checks failed
    if not result["risk_check_passed"]:
        state["session_status"] = "failed"
        raise RuntimeError(
            f"Risk management check failed: {', '.join(result['warnings'])}"
        )

    return state


async def market_structure_node(state: TradingState) -> TradingState:
    """Analyze market structure to identify support/resistance and key levels.

    Identifies trend direction, support/resistance levels, and volatility
    to establish the foundational technical picture before trend analysis.
    """
    print("🟡 Market Structure Node")

    # Get Hummingbot client for market data
    hummingbot_client = await get_hummingbot_client()
    
    # Fetch real market data from Hummingbot
    trading_pair = "ETH-USDT"
    current_price = await fetch_current_price(hummingbot_client, trading_pair)
    market_data = await fetch_market_data(hummingbot_client, trading_pair)
    price_history = await fetch_price_history(
        hummingbot_client, trading_pair, interval="4h", limit=100
    )

    # Instantiate and execute the market structure agent
    agent = MarketStructure(
        config={
            "instrument": trading_pair,
            "timeframe": "4H",
            "lookback_periods": len(price_history),
            "base_price": current_price,
            "hummingbot_client": hummingbot_client,
            "current_price": current_price,
            "market_data": market_data,
            "price_history": price_history,
        }
    )
    result = agent.execute()

    # Update state with market structure analysis
    state["messages"].append(
        {
            "node": "market_structure",
            "analysis_complete": result["analysis_complete"],
            "instrument": "ETH-USDT",
            "current_price": result["current_price"],
            "trend_direction": result["trend_direction"],
            "support_level": result["support_level"],
            "resistance_level": result["resistance_level"],
            "market_volatility": result["market_volatility"],
            "key_price_levels": result["key_price_levels"],
        }
    )

    # Store key levels in market_data for downstream nodes
    state["market_data"] = {
        "instrument": "ETH-USDT",
        "current_price": result["current_price"],
        "support": result["support_level"],
        "resistance": result["resistance_level"],
        "trend": result["trend_direction"],
        "volatility": result["market_volatility"],
        "key_levels": result["key_price_levels"],
        "price_history": result["price_history"],
    }

    return state


def economic_calendar_node(state: TradingState) -> TradingState:
    """Check economic calendar for upcoming events that may affect trading.

    Identifies high-impact economic announcements and provides trading
    recommendations based on event timing and impact level.
    """
    print("🟡 Economic Calendar Node")

    # Instantiate and execute the economic calendar agent
    agent = EconomicCalendar(
        config={
            "currencies": ["USD"],
            "lookback_hours": 24,
        }
    )
    result = agent.execute()

    # Update state with economic calendar check
    state["messages"].append(
        {
            "node": "economic_calendar",
            "calendar_check_complete": result["calendar_check_complete"],
            "high_impact_events_upcoming": result["high_impact_events_upcoming"],
            "hours_until_next_event": result["hours_until_next_event"],
            "trading_recommendation": result["trading_recommendation"],
            "upcoming_events_count": len(result["upcoming_events"]),
        }
    )

    # Store calendar data for downstream nodes
    state["market_data"]["economic_events"] = result["upcoming_events"]
    state["market_data"]["calendar_recommendation"] = result["trading_recommendation"]

    # Alert if high-impact events are very close (< 2 hours)
    if result["high_impact_events_upcoming"] and result["hours_until_next_event"] < 2:
        print(f"  ⚠️  {result['trading_recommendation']}")

    return state


def checkpoint_1_node(state: TradingState) -> TradingState:
    """First checkpoint - pause for human decision on trend analysis.

    Prompts for user approval before proceeding to trend definition.
    """
    print("🔵 Checkpoint 1 - Awaiting human input")
    response = input("Continue to trend analysis? (yes/no): ").strip().lower()
    approval = response in ["yes", "y", "true", "1"]

    state["human_decisions"].append({"checkpoint": 1, "decision": approval})
    if not approval:
        state["session_status"] = "paused"
        return Command(goto=END)

    return state


def trend_definition_node(state: TradingState) -> TradingState:
    """Define and confirm market trend using technical indicators.

    Uses moving averages and price action to identify the primary trend
    and establish bias for entry direction (long/short).
    """
    print("🟡 Trend Definition Node")

    # Instantiate and execute the trend definition agent
    agent = TrendDefinition(
        config={
            "price_history": state["market_data"].get("price_history", []),
            "current_price": state["market_data"].get("current_price", 0.0),
            "trend_direction": str(state["market_data"].get("trend", "unknown")),
        }
    )
    result = agent.execute()

    # Update state with trend definition
    state["messages"].append(
        {
            "node": "trend_definition",
            "trend_confirmed": result["trend_confirmed"],
            "primary_trend": result["primary_trend"],
            "trend_strength": result["trend_strength"],
            "entry_bias": result["entry_bias"],
            "moving_averages": {
                "ma_10": result["moving_average_10"],
                "ma_20": result["moving_average_20"],
                "ma_50": result["moving_average_50"],
            },
        }
    )

    # Store trend data for downstream nodes
    state["market_data"]["primary_trend"] = result["primary_trend"]
    state["market_data"]["trend_strength"] = result["trend_strength"]
    state["market_data"]["entry_bias"] = result["entry_bias"]
    state["market_data"]["trend_confirmed"] = result["trend_confirmed"]
    state["market_data"]["moving_averages"] = {
        "ma_10": result["moving_average_10"],
        "ma_20": result["moving_average_20"],
        "ma_50": result["moving_average_50"],
    }

    return state


def strength_weakness_node(state: TradingState) -> TradingState:
    """Analyze market strength and weakness using momentum indicators.

    Calculates RSI, MACD, and detects divergences to assess the conviction
    behind the trend and identify potential reversal signals.
    """
    print("🟡 Strength/Weakness Node")

    # Instantiate and execute the strength and weakness agent
    agent = StrengthWeakness(
        config={
            "price_history": state["market_data"].get("price_history", []),
            "current_price": state["market_data"].get("current_price", 0.0),
            "entry_bias": state["market_data"].get("entry_bias", "neutral"),
        }
    )
    result = agent.execute()

    # Update state with strength/weakness analysis
    state["messages"].append(
        {
            "node": "strength_weakness",
            "momentum_direction": result["momentum_direction"],
            "rsi_value": result["rsi_value"],
            "macd_signal": result["macd_signal"],
            "divergence_detected": result["divergence_detected"],
            "divergence_type": result["divergence_type"],
            "overall_strength": result["overall_strength"],
            "trading_probability": result["trading_probability"],
        }
    )

    # Store momentum data for downstream nodes
    state["market_data"]["momentum"] = result["momentum_direction"]
    state["market_data"]["rsi"] = result["rsi_value"]
    state["market_data"]["macd_signal"] = result["macd_signal"]
    state["market_data"]["divergence_detected"] = result["divergence_detected"]
    state["market_data"]["divergence_type"] = result["divergence_type"]
    state["market_data"]["overall_strength"] = result["overall_strength"]
    state["market_data"]["trading_probability"] = result["trading_probability"]

    # Log strength assessment
    print(
        f"  📊 Momentum: {result['momentum_direction']} | RSI: {result['rsi_value']} | Strength: {result['overall_strength']}"
    )
    if result["divergence_detected"]:
        print(f"  ⚠️  {result['divergence_type'].upper()} divergence detected")

    return state


def checkpoint_2_node(state: TradingState) -> TradingState:
    """Second checkpoint - pause for setup review.

    Uses interrupt to pause execution and wait for human approval of the setup
    before proceeding to entry execution.
    """
    print("🔵 Checkpoint 2 - Setup Review")

    # Get setup details for approval
    best_setup = state["market_data"].get("best_setup")
    setup_info = (
        {
            "setup_type": best_setup["setup_type"].value if best_setup else "none",
            "entry": best_setup["entry_level"] if best_setup else 0,
            "stop_loss": best_setup["stop_loss_level"] if best_setup else 0,
            "take_profit": best_setup["take_profit_level"] if best_setup else 0,
            "confidence": best_setup["setup_confidence"] if best_setup else 0,
        }
        if best_setup
        else None
    )

    # Display setup details for approval
    if setup_info:
        print(f"  Setup Type: {setup_info['setup_type']}")
        print(f"  Entry: {setup_info['entry']}, SL: {setup_info['stop_loss']}, TP: {setup_info['take_profit']}")
        print(f"  Confidence: {setup_info['confidence']}")
    
    response = input("Approve setup for execution? (yes/no): ").strip().lower()
    approval = response in ["yes", "y", "true", "1"]

    state["human_decisions"].append({"checkpoint": 2, "decision": approval})
    state["setup_approved"] = approval

    if not approval:
        return Command(goto=END)

    return state


def setup_scanner_node(state: TradingState) -> TradingState:
    """Scan for trading setups based on identified patterns and levels.

    Identifies specific entry and exit points for trades based on:
    - Support/resistance levels
    - Trend direction and strength
    - Momentum and divergences
    - Risk/reward ratios
    """
    print("🟡 Setup Scanner Node")

    # Instantiate and execute the setup scanner agent
    # Use state values if available, otherwise SetupScanner defaults apply
    agent = SetupScanner(
        config={
            "current_price": state["market_data"].get("current_price") or 100.0,
            "support": state["market_data"].get("support") or 95.0,
            "resistance": state["market_data"].get("resistance") or 110.0,
            "trend": state["market_data"].get("primary_trend") or "uptrend",
            "trend_strength": state["market_data"].get("trend_strength") or "strong",
            "momentum": state["market_data"].get("momentum") or "strong_up",
            "rsi": state["market_data"].get("rsi") or 70.0,
            "entry_bias": state["market_data"].get("entry_bias", "neutral"),
            "trading_probability": state["market_data"].get(
                "trading_probability", 75.0
            ),
            "divergence_detected": state["market_data"].get(
                "divergence_detected", False
            ),
            "divergence_type": state["market_data"].get("divergence_type", "none"),
        }
    )
    result = agent.execute()

    # Update state with setup scan results
    state["messages"].append(
        {
            "node": "setup_scanner",
            "scan_complete": result["scan_complete"],
            "total_setups": result["total_setups"],
            "best_setup": result["best_setup"],
        }
    )

    # Store setup data for downstream nodes
    state["market_data"]["setups_found"] = result["setups_found"]
    state["market_data"]["best_setup"] = result["best_setup"]
    state["market_data"]["total_setups"] = result["total_setups"]

    # Log setup scan results
    if result["best_setup"]:
        setup = result["best_setup"]
        print(
            f"  ✓ {setup['setup_type'].value.upper()} setup found "
            f"| Entry: {setup['entry_level']} | R:R: {setup['risk_reward_ratio']}"
        )
        print(
            f"    Confidence: {setup['setup_confidence']}% | {setup['entry_strategy']}"
        )
    else:
        print(
            f"  ℹ️  No setups found. {len(result['setups_found'])} total scenarios scanned."
        )

    return state


async def entry_execution_node(state: TradingState) -> TradingState:
    """Execute trade entry and initialize position with stop loss and take profit.

    Places entry order at calculated entry level with proper position sizing
    and risk management parameters.
    """
    print("🟡 Entry Execution Node")

    # Get Hummingbot client for trade execution
    hummingbot_client = await get_hummingbot_client()
    
    # Fetch real current price
    trading_pair = "ETH-USDT"
    current_price = await fetch_current_price(hummingbot_client, trading_pair)

    # Instantiate and execute the entry execution agent
    agent = EntryExecution(
        config={
            "best_setup": state["market_data"].get("best_setup"),
            "account_balance": state.get("account_balance", 10000.0),
            "position_size_limit": 2000.0,
            "current_price": current_price if current_price > 0 else state["market_data"].get("current_price", 0.0),
            "entry_bias": state["market_data"].get("entry_bias", "neutral"),
            "hummingbot_client": hummingbot_client,
        }
    )
    result = agent.execute()

    # Update state with entry execution results
    state["messages"].append(
        {
            "node": "entry_execution",
            "execution_complete": result["execution_complete"],
            "entry_successful": result["entry_successful"],
            "execution_message": result["execution_message"],
        }
    )

    # Handle successful entry
    if result["entry_successful"] and result["trade_position"]:
        position = result["trade_position"]

        # Update positions in state
        state["positions"] = {
            "active": True,
            "trade_id": position["trade_id"],
            "entry_price": position["entry_price"],
            "entry_time": position["entry_time"],
            "entry_type": position["entry_type"],
            "position_size": position["position_size"],
            "position_value": position["position_value"],
            "stop_loss": position["stop_loss"],
            "take_profit": position["take_profit"],
            "setup_type": position["setup_type"],
            "risk_reward_ratio": position["risk_reward_ratio"],
        }

        # Store position in market data
        state["market_data"]["open_position"] = position

        # Log entry details
        print(
            f"  ✅ Entry executed: {position['entry_type'].upper()} {position['position_size']} ETH @ {position['entry_price']} USDT"
        )
        print(f"     Trade ID: {position['trade_id']}")
        print(
            f"     SL: {position['stop_loss']} | TP: {position['take_profit']} | R:R: {position['risk_reward_ratio']}"
        )

        return state

    # Handle failed entry
    if "positions" not in state:
        state["positions"] = {}
    state["positions"]["active"] = False
    print(f"  ❌ {result['execution_message']}")

    return state


async def trade_management_node(state: TradingState) -> TradingState:
    """Monitor and manage open position with dynamic stop loss and exit signals.

    Adjusts stops to breakeven or trailing levels, monitors for exit signals
    based on momentum, RSI, and divergences.
    """
    print("🟡 Trade Management Node")

    # Get Hummingbot client for position management
    hummingbot_client = await get_hummingbot_client()
    
    # Fetch real current price
    trading_pair = "ETH-USDT"
    current_price = await fetch_current_price(hummingbot_client, trading_pair)

    # Instantiate and execute the trade management agent
    agent = TradeManagement(
        config={
            "open_position": state.get("positions", {}).get("active")
            and state["market_data"].get("open_position"),
            "current_price": current_price if current_price > 0 else state["market_data"].get("current_price", 0.0),
            "momentum": state["market_data"].get("momentum", "weak"),
            "rsi": state["market_data"].get("rsi", 50.0),
            "divergence_detected": state["market_data"].get(
                "divergence_detected", False
            ),
            "hummingbot_client": hummingbot_client,
        }
    )
    result = agent.execute()

    # Update state with management results
    state["messages"].append(
        {
            "node": "trade_management",
            "management_complete": result["management_complete"],
            "position_update_message": result["position_update_message"],
            "stop_adjusted": result["stop_adjusted"],
        }
    )

    # Handle active position management
    if result["position_status"]:
        position_status = result["position_status"]

        # Update position in state with current P&L
        if state.get("positions", {}).get("active"):
            state["positions"]["current_pnl"] = position_status["current_pnl"]
            state["positions"]["current_pnl_percent"] = position_status[
                "current_pnl_percent"
            ]

            # Update stop loss if adjusted
            if result["stop_adjusted"] and result["new_stop_level"]:
                state["positions"]["stop_loss"] = result["new_stop_level"]
                print(f"  📊 Stop adjusted to {result['new_stop_level']}")

            # Log position status
            symbol = "📈" if position_status["position_status"] == "winning" else "📉"
            print(
                f"  {symbol} {position_status['position_status'].upper()}: "
                f"P&L {position_status['current_pnl']} USDT ({position_status['current_pnl_percent']}%)"
            )

            # Alert on exit signal
            if position_status["exit_signal_detected"]:
                print(f"  ⚠️  EXIT SIGNAL: {position_status['exit_reason']}")

    return state


async def exit_execution_node(state: TradingState) -> TradingState:
    """Execute trade exit and finalize position with P&L calculation.

    Closes the position at market conditions, calculates final profit/loss,
    and records trade result for analysis.
    """
    print("🟡 Exit Execution Node")

    # Get Hummingbot client for trade execution
    hummingbot_client = await get_hummingbot_client()
    
    # Fetch real current price
    trading_pair = "ETH-USDT"
    current_price = await fetch_current_price(hummingbot_client, trading_pair)

    # Instantiate and execute the exit execution agent
    agent = ExitExecution(
        config={
            "open_position": state["market_data"].get("open_position")
            if state.get("positions", {}).get("active")
            else None,
            "current_price": current_price if current_price > 0 else state["market_data"].get("current_price", 0.0),
            "exit_reason": "manual",
            "exit_signal_detected": state["market_data"].get(
                "exit_signal_detected", False
            ),
            "hummingbot_client": hummingbot_client,
        }
    )
    result = agent.execute()

    # Update state with exit execution results
    state["messages"].append(
        {
            "node": "exit_execution",
            "execution_complete": result["execution_complete"],
            "exit_successful": result["exit_successful"],
            "exit_message": result["exit_message"],
        }
    )

    # Handle successful exit
    if result["exit_successful"] and result["trade_result"]:
        trade_result = result["trade_result"]

        # Update position as closed
        if "positions" not in state:
            state["positions"] = {}
        state["positions"]["active"] = False

        # Store trade result
        state["positions"]["trade_result"] = {
            "trade_id": trade_result["trade_id"],
            "entry_price": trade_result["entry_price"],
            "exit_price": trade_result["exit_price"],
            "position_size": trade_result["position_size"],
            "entry_type": trade_result["entry_type"],
            "exit_reason": trade_result["exit_reason"],
            "gross_pnl": trade_result["gross_pnl"],
            "pnl_percent": trade_result["pnl_percent"],
            "exit_time": trade_result["exit_time"],
        }

        # Update overall session P&L
        state["pnl"] += trade_result["gross_pnl"]

        # Log exit details
        pnl_symbol = "✅" if trade_result["gross_pnl"] > 0 else "❌"
        print(
            f"  {pnl_symbol} Exit: {trade_result['exit_reason']} @ {trade_result['exit_price']}"
        )
        print(
            f"     P&L: {trade_result['gross_pnl']} USDT ({trade_result['pnl_percent']}%) | Total: {state['pnl']} USDT"
        )

        return state

    # Handle failed exit
    print(f"  ⚠️  {result['exit_message']}")
    if "positions" not in state:
        state["positions"] = {}
    state["positions"]["active"] = False

    return state


def session_review_node(state: TradingState) -> TradingState:
    """Review trading session comparing actual vs optimal execution.

    Analyzes session performance using YTC methodology with hindsight-perfect
    comparison to identify lessons and improvement areas.
    """
    print("🟣 Session Review Node")

    # Collect trades from messages for review
    trades = []
    for msg in state["messages"]:
        if msg.get("node") == "exit_execution" and msg.get("exit_successful"):
            trades.append(msg)

    # Instantiate and execute the session review agent
    agent = SessionReview(
        config={
            "trades": trades,
            "pnl": state.get("pnl", 0.0),
            "predicted_environment": state["market_data"].get(
                "primary_trend", "unknown"
            ),
            "actual_environment": state["market_data"].get("primary_trend", "unknown"),
        }
    )
    result = agent.execute()

    # Update state with session review results
    state["messages"].append(
        {
            "node": "session_review",
            "review_complete": result["review_complete"],
            "environment_accuracy": result["environment_classification"]["accuracy"],
            "key_lessons": len(result["lessons_learned"]),
        }
    )

    # Store review for downstream nodes
    state["market_data"]["session_review"] = result

    # Log session review summary
    env_match = "✓" if result["environment_classification"]["accuracy"] else "✗"
    print(
        f"  {env_match} Environment: predicted {result['environment_classification']['predicted']}, "
        f"actual {result['environment_classification']['actual']}"
    )
    print(f"    Lessons identified: {len(result['lessons_learned'])}")
    print(f"    Improvement goals: {len(result['improvement_goals'])}")

    return state


def performance_analytics_node(state: TradingState) -> TradingState:
    """Calculate performance statistics and track metrics.

    Analyzes session and cumulative performance across multiple dimensions
    including win rate, R-multiple, profit factor, and drawdown.
    """
    print("🟣 Performance Analytics Node")

    # Collect trade statistics
    trades = []
    for msg in state["messages"]:
        if msg.get("node") == "exit_execution" and msg.get("exit_successful"):
            trades.append(msg)

    win_count = sum(
        1
        for msg in state["messages"]
        if msg.get("node") == "exit_execution" and msg.get("exit_successful")
    )

    # Instantiate and execute the performance analytics agent
    agent = PerformanceAnalytics(
        config={
            "trades": trades,
            "pnl": state.get("pnl", 0.0),
            "win_count": win_count,
            "loss_count": max(0, len(trades) - win_count),
            "total_trades_all_time": len(trades),
            "cumulative_pnl": state.get("pnl", 0.0),
        }
    )
    result = agent.execute()

    # Update state with performance analytics
    state["messages"].append(
        {
            "node": "performance_analytics",
            "analytics_complete": result["analytics_complete"],
            "win_rate": result["session_stats"]["win_rate"],
            "total_r": result["session_stats"]["total_r"],
            "profit_factor": result["session_stats"]["profit_factor"],
        }
    )

    # Store analytics for downstream nodes
    state["market_data"]["performance_analytics"] = result

    # Log analytics summary
    stats = result["session_stats"]
    print(
        f"  📊 Win Rate: {stats['win_rate']}% | Avg R: {stats['total_r']}/{stats['trades_taken']} | "
        f"PF: {stats['profit_factor']}"
    )

    return state


def learning_optimization_node(state: TradingState) -> TradingState:
    """Analyze performance and recommend strategy refinements.

    Reviews empirical results to suggest parameter adjustments and identify
    skill development opportunities.
    """
    print("🟣 Learning & Optimization Node")

    # Get analytics results
    analytics = state["market_data"].get("performance_analytics")
    session_stats = analytics["session_stats"] if analytics else {}

    # Instantiate and execute the learning optimization agent
    agent = LearningOptimization(
        config={
            "win_rate": session_stats.get("win_rate", 50.0),
            "avg_r": session_stats.get("total_r", 0.0),
            "trades_taken": session_stats.get("trades_taken", 0),
            "pnl": state.get("pnl", 0.0),
        }
    )
    result = agent.execute()

    # Update state with optimization recommendations
    state["messages"].append(
        {
            "node": "learning_optimization",
            "optimization_complete": result["optimization_complete"],
            "recommendations": len(
                result["optimization_report"]["parameter_recommendations"]
            ),
            "practice_scenarios": len(
                result["optimization_report"]["practice_scenarios"]
            ),
        }
    )

    # Store optimization report
    state["market_data"]["optimization_report"] = result

    # Log optimization summary
    report = result["optimization_report"]
    print(f"  💡 Recommendations: {len(report['parameter_recommendations'])}")
    print(f"     Practice scenarios: {len(report['practice_scenarios'])}")
    for rec in report["parameter_recommendations"][:2]:
        print(
            f"     - {rec['parameter']}: {rec['suggested_value']} ({rec['confidence']} confidence)"
        )

    return state


def next_session_prep_node(state: TradingState) -> TradingState:
    """Prepare configuration and goals for next trading session.

    Sets process and performance goals, schedules strategy adjustments,
    and creates system maintenance checklist for next session.
    """
    print("🟣 Next Session Preparation Node")

    # Get optimization results
    optimization = state["market_data"].get("optimization_report")
    analytics = state["market_data"].get("performance_analytics")
    session_stats = analytics["session_stats"] if analytics else {}

    # Instantiate and execute the next session prep agent
    agent = NextSessionPrep(
        config={
            "win_rate": session_stats.get("win_rate", 50.0),
            "pnl": state.get("pnl", 0.0),
            "improvement_goals": optimization["optimization_report"].get(
                "improvement_areas", []
            )
            if optimization
            else [],
        }
    )
    result = agent.execute()

    # Update state with next session configuration
    state["messages"].append(
        {
            "node": "next_session_prep",
            "prep_complete": result["prep_complete"],
            "next_session_date": result["next_session_config"]["date"],
            "goals_count": len(result["next_session_config"]["goals"]["process_goals"]),
        }
    )

    # Store configuration for next session
    state["market_data"]["next_session_config"] = result

    # Log next session preparation summary
    config = result["next_session_config"]
    print(f"  📅 Next Session: {config['date']}")
    print(f"     Process goals: {len(config['goals']['process_goals'])}")
    print(f"     Strategy updates: {len(config['strategy_updates'])}")
    print(f"     Maintenance tasks: {len(config['system_maintenance'])}")

    return state


def route_entry_to_management(
    state: TradingState,
) -> Literal["trade_management", "exit_execution"]:
    """Route from entry to management or exit."""
    if state["positions"].get("active"):
        return "trade_management"
    return "exit_execution"


# Build the graph
graph_builder = StateGraph(TradingState)

# Add nodes
graph_builder.add_node("system_initialization", system_initialization_node)
graph_builder.add_node("risk_management", risk_management_node)
graph_builder.add_node("market_structure", market_structure_node)
graph_builder.add_node("economic_calendar", economic_calendar_node)
graph_builder.add_node("checkpoint_1", checkpoint_1_node)
graph_builder.add_node("trend_definition", trend_definition_node)
graph_builder.add_node("strength_weakness", strength_weakness_node)
graph_builder.add_node("checkpoint_2", checkpoint_2_node)
graph_builder.add_node("setup_scanner", setup_scanner_node)
graph_builder.add_node("entry_execution", entry_execution_node)
graph_builder.add_node("trade_management", trade_management_node)
graph_builder.add_node("exit_execution", exit_execution_node)
graph_builder.add_node("session_review", session_review_node)
graph_builder.add_node("performance_analytics", performance_analytics_node)
graph_builder.add_node("learning_optimization", learning_optimization_node)
graph_builder.add_node("next_session_prep", next_session_prep_node)

# Add edges
graph_builder.add_edge(START, "system_initialization")
graph_builder.add_edge("system_initialization", "risk_management")
graph_builder.add_edge("risk_management", "market_structure")
graph_builder.add_edge("market_structure", "economic_calendar")
graph_builder.add_edge("economic_calendar", "checkpoint_1")

graph_builder.add_edge("checkpoint_1", "trend_definition")
graph_builder.add_edge("trend_definition", "strength_weakness")
graph_builder.add_edge("strength_weakness", "setup_scanner")

graph_builder.add_edge("setup_scanner", "checkpoint_2")
graph_builder.add_edge("checkpoint_2", "entry_execution")
graph_builder.add_conditional_edges("entry_execution", route_entry_to_management)

graph_builder.add_edge("trade_management", "exit_execution")
graph_builder.add_edge("exit_execution", "session_review")
graph_builder.add_edge("session_review", "performance_analytics")
graph_builder.add_edge("performance_analytics", "learning_optimization")
graph_builder.add_edge("learning_optimization", "next_session_prep")
graph_builder.add_edge("next_session_prep", END)

# Compile the graph (LangGraph platform handles checkpointing automatically)
graph = graph_builder.compile()


async def run_trading_graph() -> dict:
    """Run the trading graph with Hummingbot integration.
    
    Returns:
        Final state from the graph execution.
    """
    # Example usage with human-in-the-loop (local testing)
    thread_id = str(uuid.uuid4())
    checkpointer = InMemorySaver()
    local_graph = graph_builder.compile(checkpointer=checkpointer)

    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "session_id": thread_id,
        "messages": [],
        "human_decisions": [],
        "market_data": {},
        "positions": {"active": False},
        "pnl": 0.0,
        "setup_approved": False,
        "session_status": "active",
        "account_balance": 0.0,
    }

    # Build system initialization config
    init_config = get_system_initialization_config(hummingbot_client=None)
    
    print(f"\n📊 Starting trading session: {thread_id}")
    print(f"   Hummingbot Host: {init_config.get('hummingbot_host')}")
    print(f"   Exchange: {init_config.get('exchange')}")
    print(f"   Trading Pair: {init_config.get('trading_pair')}\n")

    # Run the graph until first interrupt (using async API)
    result = await local_graph.ainvoke(initial_state, config)
    return result


if __name__ == "__main__":
    # Run the trading graph
    try:
        result = asyncio.run(run_trading_graph())
        print("\n__interrupt__:", result.get("__interrupt__"))
    except KeyboardInterrupt:
        print("\n\n⏹️  Trading session interrupted by user")
    except Exception as e:
        print(f"\n❌ Trading session failed: {e}")
