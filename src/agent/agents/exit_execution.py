"""Exit execution agent for closing positions and finalizing trades."""

from typing import Any, TypedDict


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
                    Expected keys: open_position, current_price, exit_reason, etc.
        """
        self.config = config or {}
        self.open_position = self.config.get("open_position")
        self.current_price = self.config.get("current_price", 0.0)
        self.exit_reason = self.config.get("exit_reason", "manual")
        self.exit_signal = self.config.get("exit_signal_detected", False)

    def execute(self) -> ExitExecutionOutput:
        """Execute trade exit.

        Returns:
            ExitExecutionOutput with trade result or error message.
        """
        from datetime import datetime

        if not self.open_position:
            return {
                "execution_complete": True,
                "exit_successful": False,
                "trade_result": None,
                "exit_message": "No open position to exit",
                "execution_timestamp": datetime.utcnow().isoformat(),
            }

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

        return {
            "execution_complete": True,
            "exit_successful": True,
            "trade_result": trade_result,
            "exit_message": f"Position closed: {trade_result['exit_reason']} | P&L: {trade_result['gross_pnl']} USDT ({trade_result['pnl_percent']}%)",
            "execution_timestamp": datetime.utcnow().isoformat(),
        }

    def _determine_exit_price(self) -> float:
        """Determine the exit price based on current market conditions.

        Returns:
            Exit price (USDT).
        """
        entry_type = self.open_position["entry_type"]
        take_profit = self.open_position["take_profit"]
        stop_loss = self.open_position["stop_loss"]

        # For simplification: use current price capped between SL and TP
        if entry_type == "long":
            # Long: exit between stop loss and take profit
            exit_price = max(stop_loss, min(self.current_price, take_profit))
        else:  # short
            # Short: exit between take profit and stop loss
            exit_price = min(stop_loss, max(self.current_price, take_profit))

        return exit_price

    def _calculate_trade_result(self, exit_price: float) -> TradeResult | None:
        """Calculate final trade result.

        Args:
            exit_price: Price at which position is exited.

        Returns:
            TradeResult with P&L calculation or None if invalid.
        """
        entry_price = self.open_position["entry_price"]
        position_size = self.open_position["position_size"]
        entry_type = self.open_position["entry_type"]

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
            "trade_id": self.open_position["trade_id"],
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

        take_profit = self.open_position["take_profit"]
        stop_loss = self.open_position["stop_loss"]

        # Check if hit take profit
        if abs(exit_price - take_profit) < 0.01:
            return "Take Profit Hit"

        # Check if hit stop loss
        if abs(exit_price - stop_loss) < 0.01:
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
        from datetime import datetime

        return datetime.utcnow().isoformat()
