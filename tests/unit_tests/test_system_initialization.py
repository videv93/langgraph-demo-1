"""Unit tests for system initialization agent."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agent.agents.system_initialization import SystemInitialization, SystemInitializationOutput


class TestSystemInitializationInit:
    """Test SystemInitialization initialization."""

    def test_init_with_no_config(self) -> None:
        """Test initialization with no config uses defaults."""
        agent = SystemInitialization()
        assert agent.config == {}
        assert agent.exchange == "binance"
        assert agent.trading_pair == "ETH-USDT"
        assert agent.hummingbot_host == "localhost"
        assert agent.hummingbot_port == 8000

    def test_init_with_custom_config(self) -> None:
        """Test initialization with custom config."""
        config = {
            "exchange": "kucoin",
            "trading_pair": "BTC-USDT",
            "hummingbot_host": "192.168.1.1",
            "hummingbot_port": 9000,
            "hummingbot_username": "test_user",
            "hummingbot_password": "test_pass",
        }
        agent = SystemInitialization(config)
        assert agent.exchange == "kucoin"
        assert agent.trading_pair == "BTC-USDT"
        assert agent.hummingbot_host == "192.168.1.1"
        assert agent.hummingbot_port == 9000
        assert agent.hummingbot_username == "test_user"
        assert agent.hummingbot_password == "test_pass"

    def test_init_stores_timestamp(self) -> None:
        """Test that timestamp is stored on initialization."""
        agent = SystemInitialization()
        assert agent.timestamp is not None
        assert isinstance(agent.timestamp, str)


class TestSystemInitializationValidation:
    """Test validation methods."""

    def test_validate_configuration_success(self) -> None:
        """Test successful configuration validation."""
        config = {
            "exchange": "binance",
            "trading_pair": "ETH-USDT",
        }
        agent = SystemInitialization(config)
        assert agent._validate_configuration() is True

    def test_validate_configuration_missing_exchange(self) -> None:
        """Test configuration validation fails without exchange."""
        config = {"trading_pair": "ETH-USDT"}
        agent = SystemInitialization(config)
        agent.exchange = None  # type: ignore
        assert agent._validate_configuration() is False

    def test_validate_configuration_unsupported_exchange(self) -> None:
        """Test configuration validation fails with unsupported exchange."""
        config = {
            "exchange": "unsupported_exchange",
            "trading_pair": "ETH-USDT",
        }
        agent = SystemInitialization(config)
        assert agent._validate_configuration() is False

    def test_validate_configuration_invalid_trading_pair(self) -> None:
        """Test configuration validation fails with invalid trading pair format."""
        config = {
            "exchange": "binance",
            "trading_pair": "ETHUSDT",  # Missing dash
        }
        agent = SystemInitialization(config)
        assert agent._validate_configuration() is False

    def test_validate_trading_pair_with_hummingbot(self) -> None:
        """Test trading pair validation when Hummingbot is available."""
        config = {
            "exchange": "binance",
            "trading_pair": "ETH-USDT",
            "hummingbot_client": MagicMock(),
        }
        agent = SystemInitialization(config)
        assert agent._validate_trading_pair() is True

    def test_validate_trading_pair_unsupported(self) -> None:
        """Test trading pair validation with unsupported pair."""
        config = {
            "exchange": "binance",
            "trading_pair": "XYZ-USDT",
            "hummingbot_client": MagicMock(),
        }
        agent = SystemInitialization(config)
        assert agent._validate_trading_pair() is False

    def test_validate_trading_pair_no_hummingbot(self) -> None:
        """Test trading pair validation without Hummingbot client."""
        config = {"exchange": "binance", "trading_pair": "ETH-USDT"}
        agent = SystemInitialization(config)
        assert agent._validate_trading_pair() is False


class TestSystemInitializationExchange:
    """Test exchange connection validation."""

    def test_validate_exchange_connection_success(self) -> None:
        """Test successful exchange connection validation."""
        config = {
            "exchange": "binance",
            "trading_pair": "ETH-USDT",
            "hummingbot_username": "test_user",
            "hummingbot_password": "test_pass",
        }
        agent = SystemInitialization(config)
        result = agent._validate_exchange_connection()

        assert result["connected"] is True
        assert result["exchange_status"] == "operational"
        assert result["exchange"] == "binance"
        assert "exchange_fees" in result

    def test_validate_exchange_connection_no_credentials(self) -> None:
        """Test exchange connection validation fails without credentials."""
        config = {"exchange": "binance", "trading_pair": "ETH-USDT"}
        agent = SystemInitialization(config)
        result = agent._validate_exchange_connection()

        assert result["connected"] is False
        assert "credentials not provided" in result["error"]

    def test_check_hummingbot_connection_present(self) -> None:
        """Test Hummingbot connection check when client is present."""
        config = {"hummingbot_client": MagicMock()}
        agent = SystemInitialization(config)
        assert agent._check_hummingbot_connection() is True

    def test_check_hummingbot_connection_missing(self) -> None:
        """Test Hummingbot connection check when client is not present."""
        agent = SystemInitialization()
        assert agent._check_hummingbot_connection() is False


class TestSystemInitializationBalance:
    """Test account balance fetching."""

    def test_fetch_account_balance_no_client(self) -> None:
        """Test balance fetch returns 0 without Hummingbot client."""
        agent = SystemInitialization()
        assert agent._fetch_account_balance() == 0.0

    @pytest.mark.asyncio
    async def test_get_balance_async_with_valid_state(self) -> None:
        """Test async balance fetch with valid portfolio state."""
        mock_client = MagicMock()
        portfolio_state = {
            "account_1": {
                "binance": [
                    {"asset": "USDT", "free": 100.0},
                    {"asset": "ETH", "free": 1.0},
                ],
            },
        }
        mock_client.portfolio.get_state = AsyncMock(return_value=portfolio_state)

        config = {"hummingbot_client": mock_client}
        agent = SystemInitialization(config)
        balance = await agent._get_balance_async()

        assert balance == 100.0

    @pytest.mark.asyncio
    async def test_get_balance_async_multiple_accounts(self) -> None:
        """Test async balance fetch with multiple accounts."""
        mock_client = MagicMock()
        portfolio_state = {
            "account_1": {
                "binance": [{"asset": "USDT", "free": 100.0}],
            },
            "account_2": {
                "kucoin": [{"asset": "USDT", "free": 50.0}],
            },
        }
        mock_client.portfolio.get_state = AsyncMock(return_value=portfolio_state)

        config = {"hummingbot_client": mock_client}
        agent = SystemInitialization(config)
        balance = await agent._get_balance_async()

        assert balance == 150.0

    @pytest.mark.asyncio
    async def test_get_balance_async_no_usdt(self) -> None:
        """Test async balance fetch with no USDT balance."""
        mock_client = MagicMock()
        portfolio_state = {
            "account_1": {
                "binance": [
                    {"asset": "ETH", "free": 1.0},
                    {"asset": "BTC", "free": 0.5},
                ],
            },
        }
        mock_client.portfolio.get_state = AsyncMock(return_value=portfolio_state)

        config = {"hummingbot_client": mock_client}
        agent = SystemInitialization(config)
        balance = await agent._get_balance_async()

        assert balance == 0.0

    @pytest.mark.asyncio
    async def test_get_balance_async_exception(self) -> None:
        """Test async balance fetch handles exceptions."""
        mock_client = MagicMock()
        mock_client.portfolio.get_state = AsyncMock(side_effect=Exception("API Error"))

        config = {"hummingbot_client": mock_client}
        agent = SystemInitialization(config)
        balance = await agent._get_balance_async()

        assert balance == 0.0


class TestSystemInitializationRisk:
    """Test risk parameter initialization."""

    def test_initialize_risk_parameters_default(self) -> None:
        """Test risk parameters initialization with defaults."""
        agent = SystemInitialization()
        assert agent._initialize_risk_parameters() is True
        assert agent.config["risk_config"]["account_risk_percent"] == 2.0
        assert agent.config["risk_config"]["max_position_size"] == 10000.0
        assert agent.config["risk_config"]["max_drawdown_percent"] == 10.0

    def test_initialize_risk_parameters_custom(self) -> None:
        """Test risk parameters initialization preserves custom values."""
        config = {
            "risk_config": {
                "account_risk_percent": 5.0,
                "max_position_size": 50000.0,
            },
        }
        agent = SystemInitialization(config)
        assert agent._initialize_risk_parameters() is True
        assert agent.config["risk_config"]["account_risk_percent"] == 5.0
        assert agent.config["risk_config"]["max_position_size"] == 50000.0
        # Defaults should fill in missing ones
        assert agent.config["risk_config"]["max_drawdown_percent"] == 10.0


class TestSystemInitializationExecute:
    """Test execute method."""

    def test_execute_no_hummingbot_demo_mode(self) -> None:
        """Test execution in demo mode without Hummingbot."""
        config = {
            "exchange": "binance",
            "trading_pair": "ETH-USDT",
        }
        agent = SystemInitialization(config)
        result = agent.execute()

        assert isinstance(result, dict)
        assert result["session_initialized"] is True
        assert result["hummingbot_connected"] is False
        assert result["account_balance"] == 10000.0
        assert result["system_status"] == "ready"
        assert result["exchange_info"]["demo_mode"] is True

    def test_execute_with_hummingbot_success(self) -> None:
        """Test successful execution with Hummingbot."""
        mock_client = MagicMock()
        config = {
            "exchange": "binance",
            "trading_pair": "ETH-USDT",
            "hummingbot_client": mock_client,
            "hummingbot_username": "test_user",
            "hummingbot_password": "test_pass",
        }
        agent = SystemInitialization(config)

        with patch.object(agent, "_fetch_account_balance", return_value=5000.0):
            result = agent.execute()

        assert result["session_initialized"] is True
        assert result["hummingbot_connected"] is True
        assert result["account_balance"] == 5000.0
        assert result["system_status"] == "ready"

    def test_execute_insufficient_balance(self) -> None:
        """Test execution fails with insufficient balance."""
        mock_client = MagicMock()
        config = {
            "exchange": "binance",
            "trading_pair": "ETH-USDT",
            "hummingbot_client": mock_client,
            "hummingbot_username": "test_user",
            "hummingbot_password": "test_pass",
        }
        agent = SystemInitialization(config)

        with patch.object(agent, "_fetch_account_balance", return_value=50.0):
            result = agent.execute()

        assert result["session_initialized"] is False
        assert result["system_status"] == "failed"
        assert any("below minimum" in error for error in result["validation_errors"])

    def test_execute_invalid_configuration(self) -> None:
        """Test execution fails with invalid configuration."""
        config = {
            "exchange": "invalid_exchange",
            "trading_pair": "ETH-USDT",
        }
        agent = SystemInitialization(config)
        result = agent.execute()

        assert result["session_initialized"] is False
        assert result["system_status"] == "failed"
        assert any("Configuration validation" in error for error in result["validation_errors"])

    def test_execute_returns_correct_type(self) -> None:
        """Test execute returns SystemInitializationOutput type."""
        config = {
            "exchange": "binance",
            "trading_pair": "ETH-USDT",
        }
        agent = SystemInitialization(config)
        result = agent.execute()

        # Verify all required keys are present
        required_keys = {
            "session_initialized",
            "initialization_timestamp",
            "system_status",
            "validation_errors",
            "hummingbot_connected",
            "exchange_info",
            "account_balance",
        }
        assert set(result.keys()) == required_keys
        assert isinstance(result["session_initialized"], bool)
        assert isinstance(result["validation_errors"], list)
        assert isinstance(result["exchange_info"], dict)
        assert isinstance(result["account_balance"], (int, float))
