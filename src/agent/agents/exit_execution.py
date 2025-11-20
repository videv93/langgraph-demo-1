"""Exit execution agent for closing positions and finalizing trades."""

from datetime import datetime
from typing import Any, TypedDict
from .utils.hummingbot import (
    fetch_current_price,
    place_order,
    cancel_order,
)


class TradeResult(TypedDict):
    """Result of a closed trade."""

    trade_id: str
    entry_price: float
    exit_price: float
    position_size: float
    entry_type: str  # "long" or "short"
    exit_reason: str
    gross_pnl: float  # Profit/loss in USDT
    pnl_percent: float
    exit_time: str


class ExitExecutionOutput(TypedDict):
    """Output from exit execution."""

    execution_complete: bool
    exit_successful: bool
    trade_result: TradeResult | None
    exit_message: str
    execution_timestamp: str


class ExitExecution:
    """Execute trade exit and finalize position.

    Handles:
    - Exit order execution at take profit or stop loss
    - Trade result calculation
    - P&L finalization
    - Position closure
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the exit execution agent.

        Args:
            config: Configuration with open position and exit parameters.
                    Expected keys: open_position, current_price, exit_reason,
                    hummingbot_client, trading_pair, exchange, etc.
        """
        self.config = config or {}
        self.open_position = self.config.get("open_position")
        self.current_price = self.config.get("current_price", 0.0)
        self.exit_reason = self.config.get("exit_reason", "manual")
        self.exit_signal = self.config.get("exit_signal_detected", False)
        self.hummingbot_client = self.config.get("hummingbot_client")
        self.trading_pair = self.config.get("trading_pair", "ETH-USDT")
        self.exchange = self.config.get("exchange", "binance_perpetual_testnet")

    async def execute(self) -> ExitExecutionOutput:
        """Execute trade exit with real market data and order placement.

        Returns:
            ExitExecutionOutput with trade result or error message.
        """
        if not self.open_position:
            return {
                "execution_complete": True,
                "exit_successful": False,
                "trade_result": None,
                "exit_message": "No open position to exit",
                "execution_timestamp": datetime.utcnow().isoformat(),
            }

        # Fetch real current price from market
        await self._update_current_price()

        # Determine exit price
        exit_price = self._determine_exit_price()

        # Calculate trade result
        trade_result = self._calculate_trade_result(exit_price)

        # Validate exit
        if not trade_result:
            return {
                "execution_complete": True,
                "exit_successful": False,
                "trade_result": None,
                "exit_message": "Trade result calculation failed",
                "execution_timestamp": datetime.utcnow().isoformat(),
            }

        # Place exit order
        order_result = await self._place_exit_order(trade_result)
        if not order_result:
            return {
                "execution_complete": True,
                "exit_successful": False,
                "trade_result": None,
                "exit_message": "Failed to place exit order",
                "execution_timestamp": datetime.utcnow().isoformat(),
            }

        return {
            "execution_complete": True,
            "exit_successful": True,
            "trade_result": trade_result,
            "exit_message": f"Position closed: {trade_result['exit_reason']} | P&L: {trade_result['gross_pnl']} USDT ({trade_result['pnl_percent']}%) | Order ID: {order_result.get('order_id')}",
            "execution_timestamp": datetime.utcnow().isoformat(),
        }

    def _determine_exit_price(self) -> float:
        """Determine the exit price based on current market conditions.

        Returns:
            Exit price (USDT).
        """
        entry_type = self.open_position.get("entry_type", "long")
        take_profit = self.open_position.get("take_profit", 0.0)
        stop_loss = self.open_position.get("stop_loss", 0.0)

        # For simplification: use current price capped between SL and TP
        if entry_type == "long":
            # Long: exit between stop loss and take profit
            exit_price = max(stop_loss, min(self.current_price, take_profit))
        else:  # short
            # Short: exit between take profit and stop loss
            exit_price = min(stop_loss, max(self.current_price, take_profit))

        return exit_price if exit_price > 0 else self.current_price

    def _calculate_trade_result(self, exit_price: float) -> TradeResult | None:
        """Calculate final trade result.

        Args:
            exit_price: Price at which position is exited.

        Returns:
            TradeResult with P&L calculation or None if invalid.
        """
        entry_price = self.open_position.get("entry_price", 0.0)
        position_size = self.open_position.get("position_size", 0.0)
        entry_type = self.open_position.get("entry_type", "long")

        if entry_price <= 0 or position_size <= 0 or exit_price <= 0:
            return None

        # Calculate P&L
        if entry_type == "long":
            gross_pnl = (exit_price - entry_price) * position_size
            pnl_percent = ((exit_price - entry_price) / entry_price) * 100
        else:  # short
            gross_pnl = (entry_price - exit_price) * position_size
            pnl_percent = ((entry_price - exit_price) / entry_price) * 100

        # Determine exit reason if not already set
        exit_reason = self._determine_exit_reason(exit_price)

        return {
            "trade_id": self.open_position.get("trade_id", "unknown"),
            "entry_price": round(entry_price, 2),
            "exit_price": round(exit_price, 2),
            "position_size": round(position_size, 4),
            "entry_type": entry_type,
            "exit_reason": exit_reason,
            "gross_pnl": round(gross_pnl, 2),
            "pnl_percent": round(pnl_percent, 2),
            "exit_time": self._get_exit_time(),
        }

    def _determine_exit_reason(self, exit_price: float) -> str:
        """Determine the reason for exit.

        Args:
            exit_price: Exit price level.

        Returns:
            Exit reason description.
        """
        if self.exit_reason != "manual":
            return self.exit_reason

        take_profit = self.open_position.get("take_profit", 0.0)
        stop_loss = self.open_position.get("stop_loss", 0.0)

        # Check if hit take profit
        if take_profit > 0 and abs(exit_price - take_profit) < 0.01:
            return "Take Profit Hit"

        # Check if hit stop loss
        if stop_loss > 0 and abs(exit_price - stop_loss) < 0.01:
            return "Stop Loss Hit"

        # Check if exit signal triggered
        if self.exit_signal:
            return "Exit Signal - Technical Reversal"

        return "Manual Exit"

    def _get_exit_time(self) -> str:
        """Get exit timestamp.

        Returns:
            ISO format timestamp.
        """
        return datetime.utcnow().isoformat()

    async def _update_current_price(self) -> None:
        """Fetch current market price from Hummingbot.

        Updates self.current_price with real market data.
        """
        if not self.hummingbot_client:
            return

        price = await fetch_current_price(
            self.hummingbot_client,
            trading_pair=self.trading_pair,
            exchange=self.exchange
        )
        if price > 0:
            self.current_price = price

    async def _place_exit_order(self, trade_result: TradeResult) -> dict[str, Any] | None:
        """Place exit order via Hummingbot.

        Args:
            trade_result: Trade result with exit details.

        Returns:
            Order result dictionary or None if placement failed.
        """
        if not self.hummingbot_client:
            return None

        # Determine exit side (opposite of entry)
        entry_type = self.open_position.get("entry_type", "long")
        exit_side = "sell" if entry_type == "long" else "buy"

        order_result = await place_order(
            self.hummingbot_client,
            trading_pair=self.trading_pair,
            side=exit_side,
            quantity=trade_result["position_size"],
            price=trade_result["exit_price"],
            exchange=self.exchange
        )
        return order_result
