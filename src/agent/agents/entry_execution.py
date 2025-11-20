"""Entry execution agent for executing trade entries and managing initial position."""

from datetime import datetime
from typing import Any, TypedDict
from .utils.hummingbot import (
    fetch_current_price,
    fetch_market_data,
    place_order,
)


class TradePosition(TypedDict):
    """Representation of an open trade position."""

    trade_id: str
    entry_price: float
    entry_time: str
    stop_loss: float
    take_profit: float
    position_size: float  # In base currency (ETH)
    position_value: float  # In quote currency (USDT)
    entry_type: str  # "long" or "short"
    setup_type: str
    risk_reward_ratio: float


class EntryExecutionOutput(TypedDict):
    """Output from entry execution."""

    execution_complete: bool
    entry_successful: bool
    trade_position: TradePosition | None
    execution_message: str
    execution_timestamp: str


class EntryExecution:
    """Execute trade entry and manage initial position setup.

    Handles:
    - Entry order placement
    - Position size calculation
    - Stop loss and take profit setting
    - Trade ID generation
    - Position tracking initialization
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the entry execution agent.

        Args:
            config: Configuration with setup, account, and trade parameters.
                    Expected keys: best_setup, account_balance, position_size_limit,
                    hummingbot_client, trading_pair, exchange, etc.
        """
        self.config = config or {}
        self.best_setup = self.config.get("best_setup")
        self.account_balance = self.config.get("account_balance", 100000.0)
        self.position_size_limit = self.config.get("position_size_limit", 2000.0)
        self.current_price = self.config.get("current_price", 0.0)
        self.entry_bias = self.config.get("entry_bias", "neutral")
        self.hummingbot_client = self.config.get("hummingbot_client")
        self.trading_pair = self.config.get("trading_pair", "ETH-USDT")
        self.exchange = self.config.get("exchange", "binance_perpetual_testnet")

    async def execute(self) -> EntryExecutionOutput:
        """Execute trade entry with real market data and order placement.

        Returns:
            EntryExecutionOutput with position details or error message.
        """
        if not self.best_setup:
            return {
                "execution_complete": True,
                "entry_successful": False,
                "trade_position": None,
                "execution_message": "No setup provided for entry execution",
                "execution_timestamp": datetime.utcnow().isoformat(),
            }

        # Fetch real current price from market
        await self._update_current_price()

        # Calculate position size
        position_size = self._calculate_position_size()

        if position_size <= 0:
            return {
                "execution_complete": True,
                "entry_successful": False,
                "trade_position": None,
                "execution_message": "Position size calculation failed or insufficient capital",
                "execution_timestamp": datetime.utcnow().isoformat(),
            }

        # Create trade position
        trade_position = self._create_position(position_size)

        # Validate position
        if not self._validate_position(trade_position):
            return {
                "execution_complete": True,
                "entry_successful": False,
                "trade_position": None,
                "execution_message": "Position validation failed",
                "execution_timestamp": datetime.utcnow().isoformat(),
            }

        # Place actual order
        order_result = await self._place_entry_order(trade_position)
        if not order_result:
            return {
                "execution_complete": True,
                "entry_successful": False,
                "trade_position": None,
                "execution_message": "Failed to place entry order",
                "execution_timestamp": datetime.utcnow().isoformat(),
            }

        return {
            "execution_complete": True,
            "entry_successful": True,
            "trade_position": trade_position,
            "execution_message": f"Entry executed: {trade_position['setup_type']} setup at {trade_position['entry_price']} | Order ID: {order_result.get('order_id')}",
            "execution_timestamp": datetime.utcnow().isoformat(),
        }

    def _calculate_position_size(self) -> float:
        """Calculate position size based on risk management rules.

        Returns:
            Position size in base currency (ETH).
        """
        if not self.best_setup:
            return 0.0

        # Extract from entry_zone ideal or use current price
        entry_zone = self.best_setup.get("entry_zone", {})
        entry_price = entry_zone.get("ideal", self.current_price)
        
        # Extract from stop_loss
        stop_loss_data = self.best_setup.get("stop_loss", {})
        stop_loss = stop_loss_data.get("price", 0.0)

        if entry_price <= 0 or stop_loss <= 0:
            return 0.0

        # Risk per trade in USDT
        max_loss = self.position_size_limit

        # Calculate position size
        # Risk = Position Size * (Entry - Stop Loss)
        # Position Size = Risk / (Entry - Stop Loss)
        if entry_price > stop_loss:  # Long trade
            risk_per_unit = entry_price - stop_loss
        elif entry_price < stop_loss:  # Short trade
            risk_per_unit = stop_loss - entry_price
        else:
            return 0.0

        # Position size in base currency
        position_size_eth = max_loss / risk_per_unit

        # Validate against account balance
        position_value_usdt = position_size_eth * entry_price
        max_position_value = self.account_balance * 0.05  # Max 5% of account per trade

        if position_value_usdt > max_position_value:
            # Reduce position size
            position_size_eth = max_position_value / entry_price

        return max(0, position_size_eth)

    def _create_position(self, position_size: float) -> TradePosition:
        """Create a trade position object.

        Args:
            position_size: Position size in ETH.

        Returns:
            TradePosition object.
        """
        # Extract entry price from entry_zone
        entry_zone = self.best_setup.get("entry_zone", {})
        entry_price = entry_zone.get("ideal", self.current_price)
        position_value = position_size * entry_price

        # Determine entry direction from setup
        direction = self.best_setup.get("direction", "long")
        entry_type = direction if direction in ["long", "short"] else self.entry_bias

        # Extract stop loss and targets
        stop_loss_data = self.best_setup.get("stop_loss", {})
        stop_loss = stop_loss_data.get("price", 0.0)
        
        targets = self.best_setup.get("targets", [])
        take_profit = targets[0].get("price", 0.0) if targets else 0.0

        return {
            "trade_id": self._generate_trade_id(),
            "entry_price": round(entry_price, 2),
            "entry_time": datetime.utcnow().isoformat(),
            "stop_loss": round(stop_loss, 2),
            "take_profit": round(take_profit, 2),
            "position_size": round(position_size, 4),
            "position_value": round(position_value, 2),
            "entry_type": entry_type,
            "setup_type": str(self.best_setup.get("type", "none")),
            "risk_reward_ratio": round(self.best_setup.get("risk_reward_ratio", 1.5), 2),
        }

    def _validate_position(self, position: TradePosition) -> bool:
        """Validate trade position parameters.

        Args:
            position: Trade position to validate.

        Returns:
            True if position is valid, False otherwise.
        """
        # Validate entry price is reasonable
        if position["entry_price"] <= 0:
            return False

        # Validate stop loss is set
        if position["stop_loss"] <= 0:
            return False

        # Validate take profit is set
        if position["take_profit"] <= 0:
            return False

        # Validate position size
        if position["position_size"] <= 0:
            return False

        # Validate stop loss and take profit make sense
        if position["entry_type"] == "long":
            if position["stop_loss"] >= position["entry_price"]:
                return False
            if position["take_profit"] <= position["entry_price"]:
                return False
        else:  # short
            if position["stop_loss"] <= position["entry_price"]:
                return False
            if position["take_profit"] >= position["entry_price"]:
                return False

        # Validate position value doesn't exceed account balance
        if position["position_value"] > self.account_balance:
            return False

        return True

    def _generate_trade_id(self) -> str:
        """Generate unique trade ID.

        Returns:
            Trade ID string.
        """
        import uuid

        return f"TRD-{uuid.uuid4().hex[:8].upper()}"

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

    async def _place_entry_order(self, position: TradePosition) -> dict[str, Any] | None:
        """Place entry order via Hummingbot.

        Args:
            position: Trade position with entry details.

        Returns:
            Order result dictionary or None if placement failed.
        """
        if not self.hummingbot_client:
            return None

        order_result = await place_order(
            self.hummingbot_client,
            trading_pair=self.trading_pair,
            side=position["entry_type"],
            quantity=position["position_size"],
            price=position["entry_price"],
            exchange=self.exchange
        )
        return order_result
