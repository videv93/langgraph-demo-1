"""Integration tests for system initialization within the trading graph."""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from agent.graph import TradingState, system_initialization_node


pytestmark = pytest.mark.anyio


class TestSystemInitializationNodeDemoMode:
    """Test system initialization node in demo mode (no Hummingbot)."""

    async def test_system_init_demo_mode_success(self) -> None:
        """Test successful system initialization in demo mode."""
        # Create initial state
        state: TradingState = {
            "session_id": str(uuid.uuid4()),
            "messages": [],
            "human_decisions": [],
            "market_data": {},
            "positions": {"active": False},
            "pnl": 0.0,
            "setup_approved": False,
            "session_status": "active",
            "account_balance": 0.0,
            "hummingbot_client": None,
        }

        # Execute system initialization node
        result = system_initialization_node(state)

        # Verify state was updated
        assert result["session_status"] == "active"
        assert result["account_balance"] == 10000.0
        assert len(result["messages"]) == 1

        # Verify message structure
        msg = result["messages"][0]
        assert msg["node"] == "system_initialization"
        assert msg["status"] == "ready"
        assert msg["hummingbot_connected"] is False

    async def test_system_init_market_data_updated(self) -> None:
        """Test that market data is populated after initialization."""
        state: TradingState = {
            "session_id": str(uuid.uuid4()),
            "messages": [],
            "human_decisions": [],
            "market_data": {},
            "positions": {"active": False},
            "pnl": 0.0,
            "setup_approved": False,
            "session_status": "active",
            "account_balance": 0.0,
            "hummingbot_client": None,
        }

        result = system_initialization_node(state)

        # Verify market data includes account balance
        assert "account_balance" in result["market_data"]
        assert result["market_data"]["account_balance"] == 10000.0

    async def test_system_init_invalid_exchange_fails(self) -> None:
        """Test that initialization fails with invalid exchange config."""
        state: TradingState = {
            "session_id": str(uuid.uuid4()),
            "messages": [],
            "human_decisions": [],
            "market_data": {},
            "positions": {"active": False},
            "pnl": 0.0,
            "setup_approved": False,
            "session_status": "active",
            "account_balance": 0.0,
            "hummingbot_client": None,
        }

        # Patch the config to use invalid exchange
        with patch("agent.graph.get_system_initialization_config") as mock_config:
            mock_config.return_value = {
                "exchange": "invalid_exchange",
                "trading_pair": "ETH-USDT",
                "hummingbot_client": None,
            }

            # Execution should raise RuntimeError
            with pytest.raises(RuntimeError, match="System initialization failed"):
                system_initialization_node(state)


class TestSystemInitializationNodeWithHummingbot:
    """Test system initialization node with Hummingbot client."""

    async def test_system_init_hummingbot_connected(self) -> None:
        """Test successful initialization with Hummingbot client."""
        mock_hummingbot_client = MagicMock()

        state: TradingState = {
            "session_id": str(uuid.uuid4()),
            "messages": [],
            "human_decisions": [],
            "market_data": {},
            "positions": {"active": False},
            "pnl": 0.0,
            "setup_approved": False,
            "session_status": "active",
            "account_balance": 0.0,
            "hummingbot_client": mock_hummingbot_client,
        }

        # Mock the config and agent
        with patch("agent.graph.get_system_initialization_config") as mock_config, \
             patch("agent.graph.SystemInitialization") as mock_agent_class:
            
            mock_config.return_value = {
                "exchange": "binance",
                "trading_pair": "ETH-USDT",
                "hummingbot_client": mock_hummingbot_client,
                "hummingbot_username": "test",
                "hummingbot_password": "test",
            }

            mock_agent_instance = MagicMock()
            mock_agent_instance.execute.return_value = {
                "session_initialized": True,
                "initialization_timestamp": "2024-01-01T00:00:00Z",
                "system_status": "ready",
                "validation_errors": [],
                "hummingbot_connected": True,
                "exchange_info": {"exchange": "binance", "connected": True},
                "account_balance": 5000.0,
            }
            mock_agent_class.return_value = mock_agent_instance

            result = system_initialization_node(state)

            # Verify state was updated with Hummingbot info
            assert result["session_status"] == "active"
            assert result["account_balance"] == 5000.0
            assert result["messages"][0]["hummingbot_connected"] is True

    async def test_system_init_hummingbot_insufficient_balance(self) -> None:
        """Test initialization fails when Hummingbot balance is too low."""
        mock_hummingbot_client = MagicMock()

        state: TradingState = {
            "session_id": str(uuid.uuid4()),
            "messages": [],
            "human_decisions": [],
            "market_data": {},
            "positions": {"active": False},
            "pnl": 0.0,
            "setup_approved": False,
            "session_status": "active",
            "account_balance": 0.0,
            "hummingbot_client": mock_hummingbot_client,
        }

        with patch("agent.graph.get_system_initialization_config") as mock_config, \
             patch("agent.graph.SystemInitialization") as mock_agent_class:
            
            mock_config.return_value = {
                "exchange": "binance",
                "trading_pair": "ETH-USDT",
                "hummingbot_client": mock_hummingbot_client,
                "hummingbot_username": "test",
                "hummingbot_password": "test",
            }

            mock_agent_instance = MagicMock()
            mock_agent_instance.execute.return_value = {
                "session_initialized": False,
                "initialization_timestamp": "2024-01-01T00:00:00Z",
                "system_status": "failed",
                "validation_errors": ["Account balance 50.0 USDT is below minimum 100 USDT"],
                "hummingbot_connected": True,
                "exchange_info": {"exchange": "binance", "connected": True},
                "account_balance": 50.0,
            }
            mock_agent_class.return_value = mock_agent_instance

            with pytest.raises(RuntimeError, match="System initialization failed"):
                system_initialization_node(state)


class TestSystemInitializationNodeStateTransitions:
    """Test state transitions during system initialization."""

    async def test_system_init_preserves_session_id(self) -> None:
        """Test that session ID is preserved during initialization."""
        session_id = str(uuid.uuid4())
        state: TradingState = {
            "session_id": session_id,
            "messages": [],
            "human_decisions": [],
            "market_data": {},
            "positions": {"active": False},
            "pnl": 0.0,
            "setup_approved": False,
            "session_status": "active",
            "account_balance": 0.0,
            "hummingbot_client": None,
        }

        result = system_initialization_node(state)

        assert result["session_id"] == session_id

    async def test_system_init_positions_remain_inactive(self) -> None:
        """Test that positions remain inactive after initialization."""
        state: TradingState = {
            "session_id": str(uuid.uuid4()),
            "messages": [],
            "human_decisions": [],
            "market_data": {},
            "positions": {"active": False},
            "pnl": 0.0,
            "setup_approved": False,
            "session_status": "active",
            "account_balance": 0.0,
            "hummingbot_client": None,
        }

        result = system_initialization_node(state)

        assert result["positions"]["active"] is False

    async def test_system_init_pnl_starts_at_zero(self) -> None:
        """Test that P&L remains at zero after system initialization."""
        state: TradingState = {
            "session_id": str(uuid.uuid4()),
            "messages": [],
            "human_decisions": [],
            "market_data": {},
            "positions": {"active": False},
            "pnl": 0.0,
            "setup_approved": False,
            "session_status": "active",
            "account_balance": 0.0,
            "hummingbot_client": None,
        }

        result = system_initialization_node(state)

        assert result["pnl"] == 0.0

    async def test_system_init_setup_not_yet_approved(self) -> None:
        """Test that setup is not approved until checkpoint."""
        state: TradingState = {
            "session_id": str(uuid.uuid4()),
            "messages": [],
            "human_decisions": [],
            "market_data": {},
            "positions": {"active": False},
            "pnl": 0.0,
            "setup_approved": False,
            "session_status": "active",
            "account_balance": 0.0,
            "hummingbot_client": None,
        }

        result = system_initialization_node(state)

        assert result["setup_approved"] is False


class TestSystemInitializationNodeErrorHandling:
    """Test error handling in system initialization node."""

    async def test_system_init_agent_exception_propagates(self) -> None:
        """Test that agent exceptions are properly propagated."""
        state: TradingState = {
            "session_id": str(uuid.uuid4()),
            "messages": [],
            "human_decisions": [],
            "market_data": {},
            "positions": {"active": False},
            "pnl": 0.0,
            "setup_approved": False,
            "session_status": "active",
            "account_balance": 0.0,
            "hummingbot_client": None,
        }

        with patch("agent.graph.get_system_initialization_config") as mock_config, \
             patch("agent.graph.SystemInitialization") as mock_agent_class:
            
            mock_config.return_value = {
                "exchange": "binance",
                "trading_pair": "ETH-USDT",
            }

            mock_agent_instance = MagicMock()
            mock_agent_instance.execute.side_effect = Exception("Agent execution failed")
            mock_agent_class.return_value = mock_agent_instance

            with pytest.raises(Exception, match="Agent execution failed"):
                system_initialization_node(state)

    async def test_system_init_config_retrieval_failure(self) -> None:
        """Test handling of config retrieval failure."""
        state: TradingState = {
            "session_id": str(uuid.uuid4()),
            "messages": [],
            "human_decisions": [],
            "market_data": {},
            "positions": {"active": False},
            "pnl": 0.0,
            "setup_approved": False,
            "session_status": "active",
            "account_balance": 0.0,
            "hummingbot_client": None,
        }

        with patch("agent.graph.get_system_initialization_config") as mock_config:
            mock_config.side_effect = Exception("Config retrieval failed")

            with pytest.raises(Exception, match="Config retrieval failed"):
                system_initialization_node(state)


class TestSystemInitializationNodeMessageAuditTrail:
    """Test message audit trail in system initialization node."""

    async def test_system_init_appends_to_messages(self) -> None:
        """Test that initialization appends to messages list."""
        state: TradingState = {
            "session_id": str(uuid.uuid4()),
            "messages": [{"previous": "message"}],
            "human_decisions": [],
            "market_data": {},
            "positions": {"active": False},
            "pnl": 0.0,
            "setup_approved": False,
            "session_status": "active",
            "account_balance": 0.0,
            "hummingbot_client": None,
        }

        result = system_initialization_node(state)

        # Should have original message plus new one
        assert len(result["messages"]) == 2
        assert result["messages"][0] == {"previous": "message"}
        assert result["messages"][1]["node"] == "system_initialization"

    async def test_system_init_message_contains_errors(self) -> None:
        """Test that validation errors are included in message."""
        state: TradingState = {
            "session_id": str(uuid.uuid4()),
            "messages": [],
            "human_decisions": [],
            "market_data": {},
            "positions": {"active": False},
            "pnl": 0.0,
            "setup_approved": False,
            "session_status": "active",
            "account_balance": 0.0,
            "hummingbot_client": None,
        }

        result = system_initialization_node(state)

        msg = result["messages"][0]
        assert "errors" in msg
        assert isinstance(msg["errors"], list)

    async def test_system_init_message_contains_timestamp(self) -> None:
        """Test that initialization timestamp is in message."""
        state: TradingState = {
            "session_id": str(uuid.uuid4()),
            "messages": [],
            "human_decisions": [],
            "market_data": {},
            "positions": {"active": False},
            "pnl": 0.0,
            "setup_approved": False,
            "session_status": "active",
            "account_balance": 0.0,
            "hummingbot_client": None,
        }

        result = system_initialization_node(state)

        msg = result["messages"][0]
        assert "timestamp" in msg
        assert isinstance(msg["timestamp"], str)
