"""Trade management agent for monitoring and managing open positions."""

from typing import Any, TypedDict


class PositionStatus(TypedDict):
    """Current status of a trade position."""

    trade_id: str
    position_value: float
    current_pnl: float
    current_pnl_percent: float
    position_status: str  # "winning", "losing", "breakeven"
    stop_level: float
    profit_target: float
    is_breakeven_eligible: bool
    partial_profit_eligible: bool
    exit_signal_detected: bool
    exit_reason: str


class TradeManagementOutput(TypedDict):
    """Output from trade management analysis."""

    management_complete: bool
    position_status: PositionStatus | None
    stop_adjusted: bool
    new_stop_level: float | None
    position_update_message: str
    management_timestamp: str


class TradeManagement:
    """Manage open trade positions and monitor for adjustments and exits.

    Handles:
    - Real-time P&L monitoring
    - Trailing stop loss adjustment
    - Breakeven stop activation
    - Partial profit taking
    - Exit signal detection
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the trade management agent.

        Args:
            config: Configuration with open position and current market data.
                    Expected keys: open_position, current_price, momentum, rsi, etc.
        """
        self.config = config or {}
        self.open_position = self.config.get("open_position")
        self.current_price = self.config.get("current_price", 0.0)
        self.momentum = self.config.get("momentum", "weak")
        self.rsi = self.config.get("rsi", 50.0)
        self.divergence_detected = self.config.get("divergence_detected", False)

    def execute(self) -> TradeManagementOutput:
        """Execute trade management checks.

        Returns:
            TradeManagementOutput with position status and any adjustments.
        """
        from datetime import datetime

        if not self.open_position:
            return {
                "management_complete": True,
                "position_status": None,
                "stop_adjusted": False,
                "new_stop_level": None,
                "position_update_message": "No open position to manage",
                "management_timestamp": datetime.utcnow().isoformat(),
            }

        # Calculate current position status
        position_status = self._calculate_position_status()

        # Check for stop loss adjustment opportunities
        stop_adjusted = False
        new_stop_level = None

        if position_status["is_breakeven_eligible"]:
            new_stop_level = self._adjust_to_breakeven(position_status)
            stop_adjusted = True

        elif position_status["position_status"] == "winning":
            new_stop_level = self._calculate_trailing_stop(position_status)
            if new_stop_level != self.open_position["stop_loss"]:
                stop_adjusted = True

        # Generate management message
        message = self._generate_management_message(position_status, stop_adjusted)

        return {
            "management_complete": True,
            "position_status": position_status,
            "stop_adjusted": stop_adjusted,
            "new_stop_level": new_stop_level,
            "position_update_message": message,
            "management_timestamp": datetime.utcnow().isoformat(),
        }

    def _calculate_position_status(self) -> PositionStatus:
        """Calculate current position status.

        Returns:
            PositionStatus with current P&L and status.
        """
        entry_price = self.open_position["entry_price"]
        position_size = self.open_position["position_size"]
        entry_type = self.open_position["entry_type"]

        # Calculate P&L
        if entry_type == "long":
            pnl = (self.current_price - entry_price) * position_size
            pnl_percent = ((self.current_price - entry_price) / entry_price) * 100
        else:  # short
            pnl = (entry_price - self.current_price) * position_size
            pnl_percent = ((entry_price - self.current_price) / entry_price) * 100

        # Determine position status
        if pnl > 0:
            position_status = "winning"
        elif pnl < 0:
            position_status = "losing"
        else:
            position_status = "breakeven"

        # Check if eligible for breakeven stop
        is_breakeven_eligible = pnl_percent >= 1.0  # 1% profit threshold

        # Check if eligible for partial profit
        partial_profit_eligible = pnl_percent >= 2.0  # 2% profit threshold

        # Detect exit signals
        exit_signal = self._detect_exit_signal()

        return {
            "trade_id": self.open_position["trade_id"],
            "position_value": self.open_position["position_value"],
            "current_pnl": round(pnl, 2),
            "current_pnl_percent": round(pnl_percent, 2),
            "position_status": position_status,
            "stop_level": self.open_position["stop_loss"],
            "profit_target": self.open_position["take_profit"],
            "is_breakeven_eligible": is_breakeven_eligible,
            "partial_profit_eligible": partial_profit_eligible,
            "exit_signal_detected": exit_signal,
            "exit_reason": self._get_exit_reason() if exit_signal else "",
        }

    def _adjust_to_breakeven(self, position_status: PositionStatus) -> float:
        """Adjust stop loss to breakeven entry.

        Args:
            position_status: Current position status.

        Returns:
            New stop loss level at or above entry price.
        """
        entry_price = self.open_position["entry_price"]
        entry_type = self.open_position["entry_type"]

        if entry_type == "long":
            # Move stop to entry price for long
            return entry_price
        else:  # short
            # Move stop to entry price for short
            return entry_price

    def _calculate_trailing_stop(self, position_status: PositionStatus) -> float:
        """Calculate trailing stop loss for winning positions.

        Args:
            position_status: Current position status.

        Returns:
            New stop loss level with trailing distance.
        """
        entry_type = self.open_position["entry_type"]
        current_price = self.current_price
        current_stop = self.open_position["stop_loss"]

        # Trailing distance: 2% below high (for long) or 2% above low (for short)
        trailing_distance_pct = 0.02

        if entry_type == "long":
            # For long: move stop up, but never down
            trailing_stop = current_price * (1 - trailing_distance_pct)
            new_stop = max(trailing_stop, current_stop)
            return round(new_stop, 2)
        else:  # short
            # For short: move stop down, but never up
            trailing_stop = current_price * (1 + trailing_distance_pct)
            new_stop = min(trailing_stop, current_stop)
            return round(new_stop, 2)

    def _detect_exit_signal(self) -> bool:
        """Detect if exit signal is triggered.

        Returns:
            True if exit signal detected, False otherwise.
        """
        # Exit signals
        # 1. RSI divergence
        if self.divergence_detected:
            return True

        # 2. Strong momentum reversal
        entry_type = self.open_position["entry_type"]
        if entry_type == "long" and self.momentum == "strong_down":
            return True
        if entry_type == "short" and self.momentum == "strong_up":
            return True

        # 3. RSI extremes (overbought/oversold)
        if self.rsi > 85 or self.rsi < 15:
            return True

        return False

    def _get_exit_reason(self) -> str:
        """Get the reason for exit signal.

        Returns:
            Exit reason description.
        """
        if self.divergence_detected:
            return "Divergence detected - potential reversal"

        entry_type = self.open_position["entry_type"]
        if entry_type == "long" and self.momentum == "strong_down":
            return "Strong downside momentum - reversal risk"
        if entry_type == "short" and self.momentum == "strong_up":
            return "Strong upside momentum - reversal risk"

        if self.rsi > 85:
            return "RSI overbought - extreme level"
        if self.rsi < 15:
            return "RSI oversold - extreme level"

        return "Unknown signal"

    def _generate_management_message(
        self, position_status: PositionStatus, stop_adjusted: bool
    ) -> str:
        """Generate management status message.

        Args:
            position_status: Current position status.
            stop_adjusted: Whether stop was adjusted.

        Returns:
            Management message string.
        """
        trade_id = position_status["trade_id"]
        pnl = position_status["current_pnl"]
        pnl_pct = position_status["current_pnl_percent"]
        status = position_status["position_status"]

        message = f"{trade_id}: {status.upper()} | P&L: {pnl} USDT ({pnl_pct}%)"

        if stop_adjusted:
            message += f" | Stop adjusted to {position_status['stop_level']}"

        if position_status["exit_signal_detected"]:
            message += f" | ⚠️ EXIT SIGNAL: {position_status['exit_reason']}"

        return message
