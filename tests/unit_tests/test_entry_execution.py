"""Unit tests for Entry Execution Agent - Trade entry and position management."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from agent.agents.entry_execution import (
    EntryExecution,
    TradePosition,
    EntryExecutionOutput,
)


class TestEntryExecutionInit:
    """Test EntryExecution initialization."""

    def test_init_default_config(self) -> None:
        """Test initialization with default config."""
        executor = EntryExecution()
        assert executor.config == {}
        assert executor.best_setup is None
        assert executor.account_balance == 100000.0
        assert executor.position_size_limit == 2000.0
        assert executor.current_price == 0.0
        assert executor.entry_bias == "neutral"

    def test_init_custom_config(self) -> None:
        """Test initialization with custom config."""
        setup = {
            "type": "TST",
            "direction": "long",
            "entry_zone": {"ideal": 3500.0},
            "stop_loss": {"price": 3450.0},
            "targets": [{"price": 3600.0}],
            "risk_reward_ratio": 2.0,
        }
        config = {
            "best_setup": setup,
            "account_balance": 50000.0,
            "position_size_limit": 1000.0,
            "current_price": 3500.0,
            "entry_bias": "long",
        }
        executor = EntryExecution(config)

        assert executor.best_setup == setup
        assert executor.account_balance == 50000.0
        assert executor.position_size_limit == 1000.0
        assert executor.current_price == 3500.0
        assert executor.entry_bias == "long"

    def test_init_with_hummingbot_config(self) -> None:
        """Test initialization with Hummingbot client and trading config."""
        mock_client = MagicMock()
        setup = {
            "type": "TST",
            "direction": "long",
            "entry_zone": {"ideal": 3500.0},
            "stop_loss": {"price": 3450.0},
            "targets": [{"price": 3600.0}],
            "risk_reward_ratio": 2.0,
        }
        config = {
            "best_setup": setup,
            "account_balance": 50000.0,
            "hummingbot_client": mock_client,
            "trading_pair": "BTC-USDT",
            "exchange": "binance_perpetual",
        }
        executor = EntryExecution(config)

        assert executor.hummingbot_client == mock_client
        assert executor.trading_pair == "BTC-USDT"
        assert executor.exchange == "binance_perpetual"


class TestExecuteMethod:
    """Test the main execute method."""

    @pytest.mark.asyncio
    async def test_execute_no_setup(self) -> None:
        """Test execute with no setup."""
        executor = EntryExecution()
        result = await executor.execute()

        assert result["execution_complete"] is True
        assert result["entry_successful"] is False
        assert result["trade_position"] is None
        assert "No setup provided" in result["execution_message"]

    @pytest.mark.asyncio
    async def test_execute_returns_correct_structure(self) -> None:
        """Test execute returns correct output structure."""
        setup = {
            "type": "TST",
            "direction": "long",
            "entry_zone": {"ideal": 100.0},
            "stop_loss": {"price": 95.0},
            "targets": [{"price": 110.0}],
            "risk_reward_ratio": 2.0,
        }
        config = {
            "best_setup": setup,
            "account_balance": 100000.0,
            "position_size_limit": 2000.0,
            "current_price": 100.0,
        }
        executor = EntryExecution(config)
        result = await executor.execute()

        assert "execution_complete" in result
        assert "entry_successful" in result
        assert "trade_position" in result
        assert "execution_message" in result
        assert "execution_timestamp" in result

    @pytest.mark.asyncio
    async def test_execute_successful_entry(self) -> None:
        """Test successful trade entry execution."""
        setup = {
            "type": "TST",
            "direction": "long",
            "entry_zone": {"ideal": 100.0},
            "stop_loss": {"price": 95.0},
            "targets": [{"price": 110.0}],
            "risk_reward_ratio": 2.0,
        }
        config = {
            "best_setup": setup,
            "account_balance": 100000.0,
            "position_size_limit": 2000.0,
            "current_price": 100.0,
        }
        executor = EntryExecution(config)
        result = await executor.execute()

        assert result["execution_complete"] is True
        assert result["entry_successful"] is True
        assert result["trade_position"] is not None


class TestPositionSizeCalculation:
    """Test position size calculation."""

    def test_calculate_position_size_no_setup(self) -> None:
        """Test position size with no setup."""
        executor = EntryExecution()
        size = executor._calculate_position_size()

        assert size == 0.0

    def test_calculate_position_size_long_trade(self) -> None:
        """Test position size calculation for long trade."""
        setup = {
            "type": "TST",
            "direction": "long",
            "entry_zone": {"ideal": 100.0},
            "stop_loss": {"price": 95.0},
            "targets": [{"price": 110.0}],
            "risk_reward_ratio": 2.0,
        }
        config = {
            "best_setup": setup,
            "account_balance": 100000.0,
            "position_size_limit": 2000.0,
            "current_price": 100.0,
        }
        executor = EntryExecution(config)
        size = executor._calculate_position_size()

        assert size > 0.0
        # Risk per unit = 100 - 95 = 5
        # Position size = 2000 / 5 = 400, but capped by 5% of account
        # 5% of 100000 = 5000, so position_value = 400 * 100 = 40000
        # This is > 5000, so capped to max_position_value / entry_price = 5000 / 100 = 50
        assert size == pytest.approx(50.0, rel=0.01)

    def test_calculate_position_size_short_trade(self) -> None:
        """Test position size calculation for short trade."""
        setup = {
            "type": "BOF",
            "direction": "short",
            "entry_zone": {"ideal": 100.0},
            "stop_loss": {"price": 105.0},
            "targets": [{"price": 90.0}],
            "risk_reward_ratio": 2.0,
        }
        config = {
            "best_setup": setup,
            "account_balance": 100000.0,
            "position_size_limit": 2000.0,
            "current_price": 100.0,
        }
        executor = EntryExecution(config)
        size = executor._calculate_position_size()

        assert size > 0.0
        # Risk per unit = 105 - 100 = 5
        # Position size = 2000 / 5 = 400, but capped by 5% of account
        # 5% of 100000 = 5000, so position_value = 400 * 100 = 40000
        # This is > 5000, so capped to max_position_value / entry_price = 5000 / 100 = 50
        assert size == pytest.approx(50.0, rel=0.01)

    def test_calculate_position_size_exceeds_account_limit(self) -> None:
        """Test position size when it would exceed account limit."""
        setup = {
            "type": "TST",
            "direction": "long",
            "entry_zone": {"ideal": 100.0},
            "stop_loss": {"price": 99.0},
            "targets": [{"price": 110.0}],
            "risk_reward_ratio": 2.0,
        }
        config = {
            "best_setup": setup,
            "account_balance": 10000.0,  # Small account
            "position_size_limit": 10000.0,  # Large risk per trade
            "current_price": 100.0,
        }
        executor = EntryExecution(config)
        size = executor._calculate_position_size()

        # Position should be capped at 5% of account
        position_value = size * 100.0
        max_position_value = 10000.0 * 0.05
        assert position_value <= max_position_value

    def test_calculate_position_size_zero_entry_price(self) -> None:
        """Test position size with zero entry price."""
        setup = {
            "type": "TST",
            "direction": "long",
            "entry_zone": {"ideal": 0.0},
            "stop_loss": {"price": 95.0},
            "targets": [{"price": 110.0}],
            "risk_reward_ratio": 2.0,
        }
        config = {
            "best_setup": setup,
            "account_balance": 100000.0,
            "position_size_limit": 2000.0,
            "current_price": 0.0,
        }
        executor = EntryExecution(config)
        size = executor._calculate_position_size()

        assert size == 0.0


class TestPositionCreation:
    """Test trade position creation."""

    def test_create_position_long_trade(self) -> None:
        """Test creating a long position."""
        setup = {
            "type": "TST",
            "direction": "long",
            "entry_zone": {"ideal": 100.0},
            "stop_loss": {"price": 95.0},
            "targets": [{"price": 110.0}],
            "risk_reward_ratio": 2.0,
        }
        config = {
            "best_setup": setup,
            "account_balance": 100000.0,
            "position_size_limit": 2000.0,
            "current_price": 100.0,
        }
        executor = EntryExecution(config)
        position = executor._create_position(10.0)

        assert position["entry_price"] == 100.0
        assert position["stop_loss"] == 95.0
        assert position["take_profit"] == 110.0
        assert position["position_size"] == 10.0
        assert position["position_value"] == 1000.0
        assert position["entry_type"] == "long"
        assert position["setup_type"] == "TST"
        assert position["risk_reward_ratio"] == 2.0
        assert "trade_id" in position
        assert position["trade_id"].startswith("TRD-")

    def test_create_position_short_trade(self) -> None:
        """Test creating a short position."""
        setup = {
            "type": "BOF",
            "direction": "short",
            "entry_zone": {"ideal": 100.0},
            "stop_loss": {"price": 105.0},
            "targets": [{"price": 90.0}],
            "risk_reward_ratio": 2.0,
        }
        config = {
            "best_setup": setup,
            "account_balance": 100000.0,
            "position_size_limit": 2000.0,
            "current_price": 100.0,
        }
        executor = EntryExecution(config)
        position = executor._create_position(10.0)

        assert position["entry_type"] == "short"
        assert position["stop_loss"] == 105.0
        assert position["take_profit"] == 90.0

    def test_create_position_has_required_fields(self) -> None:
        """Test that position has all required fields."""
        setup = {
            "type": "PB",
            "direction": "long",
            "entry_zone": {"ideal": 100.0},
            "stop_loss": {"price": 95.0},
            "targets": [{"price": 110.0}],
            "risk_reward_ratio": 2.0,
        }
        config = {"best_setup": setup}
        executor = EntryExecution(config)
        position = executor._create_position(5.0)

        required_fields = [
            "trade_id",
            "entry_price",
            "entry_time",
            "stop_loss",
            "take_profit",
            "position_size",
            "position_value",
            "entry_type",
            "setup_type",
            "risk_reward_ratio",
        ]
        for field in required_fields:
            assert field in position


class TestPositionValidation:
    """Test trade position validation."""

    def test_validate_position_valid_long(self) -> None:
        """Test validation of valid long position."""
        executor = EntryExecution()
        position: TradePosition = {
            "trade_id": "TRD-ABC123",
            "entry_price": 100.0,
            "entry_time": "2025-01-01T00:00:00",
            "stop_loss": 95.0,
            "take_profit": 110.0,
            "position_size": 10.0,
            "position_value": 1000.0,
            "entry_type": "long",
            "setup_type": "TST",
            "risk_reward_ratio": 2.0,
        }

        assert executor._validate_position(position) is True

    def test_validate_position_valid_short(self) -> None:
        """Test validation of valid short position."""
        executor = EntryExecution()
        position: TradePosition = {
            "trade_id": "TRD-ABC123",
            "entry_price": 100.0,
            "entry_time": "2025-01-01T00:00:00",
            "stop_loss": 105.0,
            "take_profit": 90.0,
            "position_size": 10.0,
            "position_value": 1000.0,
            "entry_type": "short",
            "setup_type": "BOF",
            "risk_reward_ratio": 2.0,
        }

        assert executor._validate_position(position) is True

    def test_validate_position_zero_entry_price(self) -> None:
        """Test validation fails with zero entry price."""
        executor = EntryExecution()
        position: TradePosition = {
            "trade_id": "TRD-ABC123",
            "entry_price": 0.0,
            "entry_time": "2025-01-01T00:00:00",
            "stop_loss": 95.0,
            "take_profit": 110.0,
            "position_size": 10.0,
            "position_value": 0.0,
            "entry_type": "long",
            "setup_type": "TST",
            "risk_reward_ratio": 2.0,
        }

        assert executor._validate_position(position) is False

    def test_validate_position_zero_stop_loss(self) -> None:
        """Test validation fails with zero stop loss."""
        executor = EntryExecution()
        position: TradePosition = {
            "trade_id": "TRD-ABC123",
            "entry_price": 100.0,
            "entry_time": "2025-01-01T00:00:00",
            "stop_loss": 0.0,
            "take_profit": 110.0,
            "position_size": 10.0,
            "position_value": 1000.0,
            "entry_type": "long",
            "setup_type": "TST",
            "risk_reward_ratio": 2.0,
        }

        assert executor._validate_position(position) is False

    def test_validate_position_zero_take_profit(self) -> None:
        """Test validation fails with zero take profit."""
        executor = EntryExecution()
        position: TradePosition = {
            "trade_id": "TRD-ABC123",
            "entry_price": 100.0,
            "entry_time": "2025-01-01T00:00:00",
            "stop_loss": 95.0,
            "take_profit": 0.0,
            "position_size": 10.0,
            "position_value": 1000.0,
            "entry_type": "long",
            "setup_type": "TST",
            "risk_reward_ratio": 2.0,
        }

        assert executor._validate_position(position) is False

    def test_validate_position_zero_size(self) -> None:
        """Test validation fails with zero position size."""
        executor = EntryExecution()
        position: TradePosition = {
            "trade_id": "TRD-ABC123",
            "entry_price": 100.0,
            "entry_time": "2025-01-01T00:00:00",
            "stop_loss": 95.0,
            "take_profit": 110.0,
            "position_size": 0.0,
            "position_value": 0.0,
            "entry_type": "long",
            "setup_type": "TST",
            "risk_reward_ratio": 2.0,
        }

        assert executor._validate_position(position) is False

    def test_validate_position_long_sl_above_entry(self) -> None:
        """Test validation fails when long stop loss is above entry."""
        executor = EntryExecution()
        position: TradePosition = {
            "trade_id": "TRD-ABC123",
            "entry_price": 100.0,
            "entry_time": "2025-01-01T00:00:00",
            "stop_loss": 105.0,  # Above entry for long
            "take_profit": 110.0,
            "position_size": 10.0,
            "position_value": 1000.0,
            "entry_type": "long",
            "setup_type": "TST",
            "risk_reward_ratio": 2.0,
        }

        assert executor._validate_position(position) is False

    def test_validate_position_long_tp_below_entry(self) -> None:
        """Test validation fails when long take profit is below entry."""
        executor = EntryExecution()
        position: TradePosition = {
            "trade_id": "TRD-ABC123",
            "entry_price": 100.0,
            "entry_time": "2025-01-01T00:00:00",
            "stop_loss": 95.0,
            "take_profit": 90.0,  # Below entry for long
            "position_size": 10.0,
            "position_value": 1000.0,
            "entry_type": "long",
            "setup_type": "TST",
            "risk_reward_ratio": 2.0,
        }

        assert executor._validate_position(position) is False

    def test_validate_position_short_sl_below_entry(self) -> None:
        """Test validation fails when short stop loss is below entry."""
        executor = EntryExecution()
        position: TradePosition = {
            "trade_id": "TRD-ABC123",
            "entry_price": 100.0,
            "entry_time": "2025-01-01T00:00:00",
            "stop_loss": 95.0,  # Below entry for short
            "take_profit": 90.0,
            "position_size": 10.0,
            "position_value": 1000.0,
            "entry_type": "short",
            "setup_type": "BOF",
            "risk_reward_ratio": 2.0,
        }

        assert executor._validate_position(position) is False

    def test_validate_position_short_tp_above_entry(self) -> None:
        """Test validation fails when short take profit is above entry."""
        executor = EntryExecution()
        position: TradePosition = {
            "trade_id": "TRD-ABC123",
            "entry_price": 100.0,
            "entry_time": "2025-01-01T00:00:00",
            "stop_loss": 105.0,
            "take_profit": 110.0,  # Above entry for short
            "position_size": 10.0,
            "position_value": 1000.0,
            "entry_type": "short",
            "setup_type": "BOF",
            "risk_reward_ratio": 2.0,
        }

        assert executor._validate_position(position) is False

    def test_validate_position_exceeds_account(self) -> None:
        """Test validation fails when position value exceeds account."""
        executor = EntryExecution({"account_balance": 1000.0})
        position: TradePosition = {
            "trade_id": "TRD-ABC123",
            "entry_price": 100.0,
            "entry_time": "2025-01-01T00:00:00",
            "stop_loss": 95.0,
            "take_profit": 110.0,
            "position_size": 20.0,
            "position_value": 2000.0,  # Exceeds 1000 account
            "entry_type": "long",
            "setup_type": "TST",
            "risk_reward_ratio": 2.0,
        }

        assert executor._validate_position(position) is False


class TestTradeIDGeneration:
    """Test trade ID generation."""

    def test_generate_trade_id_format(self) -> None:
        """Test trade ID has correct format."""
        executor = EntryExecution()
        trade_id = executor._generate_trade_id()

        assert trade_id.startswith("TRD-")
        assert len(trade_id) == 12  # "TRD-" (4) + 8 hex chars

    def test_generate_trade_id_unique(self) -> None:
        """Test that generated trade IDs are unique."""
        executor = EntryExecution()
        id1 = executor._generate_trade_id()
        id2 = executor._generate_trade_id()
        id3 = executor._generate_trade_id()

        assert id1 != id2
        assert id2 != id3
        assert id1 != id3


class TestIntegrationScenarios:
    """Test integration scenarios with realistic data."""

    @pytest.mark.asyncio
    async def test_full_entry_execution_long(self) -> None:
        """Test complete entry execution for long trade."""
        setup = {
            "type": "TST",
            "direction": "long",
            "entry_zone": {"ideal": 3500.0},
            "stop_loss": {"price": 3450.0},
            "targets": [{"price": 3650.0}],
            "risk_reward_ratio": 3.0,
        }
        config = {
            "best_setup": setup,
            "account_balance": 50000.0,
            "position_size_limit": 500.0,
            "current_price": 3500.0,
        }
        executor = EntryExecution(config)
        result = await executor.execute()

        assert result["execution_complete"] is True
        assert result["entry_successful"] is True
        assert result["trade_position"] is not None
        assert result["trade_position"]["entry_type"] == "long"
        assert result["trade_position"]["setup_type"] == "TST"

    @pytest.mark.asyncio
    async def test_full_entry_execution_short(self) -> None:
        """Test complete entry execution for short trade."""
        setup = {
            "type": "BOF",
            "direction": "short",
            "entry_zone": {"ideal": 3500.0},
            "stop_loss": {"price": 3550.0},
            "targets": [{"price": 3350.0}],
            "risk_reward_ratio": 2.5,
        }
        config = {
            "best_setup": setup,
            "account_balance": 50000.0,
            "position_size_limit": 500.0,
            "current_price": 3500.0,
        }
        executor = EntryExecution(config)
        result = await executor.execute()

        assert result["execution_complete"] is True
        assert result["entry_successful"] is True
        assert result["trade_position"] is not None
        assert result["trade_position"]["entry_type"] == "short"
        assert result["trade_position"]["setup_type"] == "BOF"

    @pytest.mark.asyncio
    async def test_entry_execution_insufficient_tp_sl(self) -> None:
        """Test entry execution fails with invalid TP/SL."""
        setup = {
            "type": "PB",
            "direction": "long",
            "entry_zone": {"ideal": 100.0},
            "stop_loss": {"price": 0.0},  # Invalid
            "targets": [],  # No targets
            "risk_reward_ratio": 0.0,
        }
        config = {"best_setup": setup, "current_price": 100.0}
        executor = EntryExecution(config)
        result = await executor.execute()

        assert result["execution_complete"] is True
        assert result["entry_successful"] is False


class TestHummingbotIntegration:
    """Test Hummingbot integration for entry execution."""

    @pytest.mark.asyncio
    async def test_update_current_price_with_client(self) -> None:
        """Test price update from Hummingbot client."""
        mock_client = MagicMock()
        setup = {
            "type": "TST",
            "direction": "long",
            "entry_zone": {"ideal": 100.0},
            "stop_loss": {"price": 95.0},
            "targets": [{"price": 110.0}],
            "risk_reward_ratio": 2.0,
        }
        config = {
            "best_setup": setup,
            "current_price": 100.0,
            "hummingbot_client": mock_client,
            "trading_pair": "ETH-USDT",
            "exchange": "binance_perpetual_testnet",
        }
        executor = EntryExecution(config)

        # Mock the fetch_current_price to return a new price
        with pytest.mock.patch(
            "agent.agents.entry_execution.fetch_current_price",
            new_callable=AsyncMock,
            return_value=105.0,
        ):
            await executor._update_current_price()

        assert executor.current_price == 105.0

    @pytest.mark.asyncio
    async def test_update_current_price_without_client(self) -> None:
        """Test price update skipped when no client."""
        setup = {
            "type": "TST",
            "direction": "long",
            "entry_zone": {"ideal": 100.0},
            "stop_loss": {"price": 95.0},
            "targets": [{"price": 110.0}],
            "risk_reward_ratio": 2.0,
        }
        config = {
            "best_setup": setup,
            "current_price": 100.0,
        }
        executor = EntryExecution(config)
        initial_price = executor.current_price

        await executor._update_current_price()

        assert executor.current_price == initial_price

    @pytest.mark.asyncio
    async def test_place_entry_order_long(self) -> None:
        """Test placing entry order for long position."""
        mock_client = MagicMock()
        setup = {
            "type": "TST",
            "direction": "long",
            "entry_zone": {"ideal": 100.0},
            "stop_loss": {"price": 95.0},
            "targets": [{"price": 110.0}],
            "risk_reward_ratio": 2.0,
        }
        config = {
            "best_setup": setup,
            "account_balance": 100000.0,
            "position_size_limit": 2000.0,
            "current_price": 100.0,
            "hummingbot_client": mock_client,
            "trading_pair": "ETH-USDT",
            "exchange": "binance_perpetual_testnet",
        }
        executor = EntryExecution(config)
        position = executor._create_position(10.0)

        with pytest.mock.patch(
            "agent.agents.entry_execution.place_order",
            new_callable=AsyncMock,
            return_value={"order_id": "ORD-123", "status": "pending"},
        ) as mock_place_order:
            result = await executor._place_entry_order(position)

            # Verify order was placed with correct side (buy for long)
            mock_place_order.assert_called_once()
            call_args = mock_place_order.call_args
            assert call_args.kwargs["side"] == "long"
            assert call_args.kwargs["quantity"] == 10.0
            assert call_args.kwargs["price"] == 100.0
            assert result is not None
            assert result["order_id"] == "ORD-123"

    @pytest.mark.asyncio
    async def test_place_entry_order_short(self) -> None:
        """Test placing entry order for short position."""
        mock_client = MagicMock()
        setup = {
            "type": "BOF",
            "direction": "short",
            "entry_zone": {"ideal": 100.0},
            "stop_loss": {"price": 105.0},
            "targets": [{"price": 90.0}],
            "risk_reward_ratio": 2.0,
        }
        config = {
            "best_setup": setup,
            "account_balance": 100000.0,
            "position_size_limit": 2000.0,
            "current_price": 100.0,
            "hummingbot_client": mock_client,
            "trading_pair": "ETH-USDT",
            "exchange": "binance_perpetual_testnet",
        }
        executor = EntryExecution(config)
        position = executor._create_position(10.0)

        with pytest.mock.patch(
            "agent.agents.entry_execution.place_order",
            new_callable=AsyncMock,
            return_value={"order_id": "ORD-124", "status": "pending"},
        ) as mock_place_order:
            result = await executor._place_entry_order(position)

            # Verify order was placed with correct side (short)
            mock_place_order.assert_called_once()
            call_args = mock_place_order.call_args
            assert call_args.kwargs["side"] == "short"
            assert call_args.kwargs["quantity"] == 10.0
            assert call_args.kwargs["price"] == 100.0
            assert result is not None

    @pytest.mark.asyncio
    async def test_place_entry_order_without_client(self) -> None:
        """Test entry order placement skipped when no client."""
        setup = {
            "type": "TST",
            "direction": "long",
            "entry_zone": {"ideal": 100.0},
            "stop_loss": {"price": 95.0},
            "targets": [{"price": 110.0}],
            "risk_reward_ratio": 2.0,
        }
        config = {
            "best_setup": setup,
            "account_balance": 100000.0,
            "position_size_limit": 2000.0,
            "current_price": 100.0,
        }
        executor = EntryExecution(config)
        position = executor._create_position(10.0)

        result = await executor._place_entry_order(position)

        assert result is None
