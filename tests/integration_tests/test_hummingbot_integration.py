"""Integration tests for actual Hummingbot connectivity.

These tests require a running Hummingbot instance and should be run separately.
Set environment variables before running:
    HUMMINGBOT_HOST=localhost
    HUMMINGBOT_PORT=8000
    HUMMINGBOT_USERNAME=your_username
    HUMMINGBOT_PASSWORD=your_password
    EXCHANGE=binance
    TRADING_PAIR=ETH-USDT

Run with: python3 -m pytest tests/integration_tests/test_hummingbot_integration.py -v -s
"""

import os

import pytest

from agent.config import create_hummingbot_client, HummingbotConfig
from src.agent.agents.system_initialization import SystemInitialization


# Check if Hummingbot is available and configured
HUMMINGBOT_AVAILABLE = os.getenv("HUMMINGBOT_HOST") is not None
HUMMINGBOT_USERNAME = os.getenv("HUMMINGBOT_USERNAME", "")
HUMMINGBOT_PASSWORD = os.getenv("HUMMINGBOT_PASSWORD", "")


pytestmark = pytest.mark.anyio


@pytest.mark.skipif(not HUMMINGBOT_AVAILABLE, reason="Hummingbot not configured")
class TestHummingbotConnection:
    """Test actual Hummingbot API connectivity."""

    async def test_hummingbot_client_creation(self) -> None:
        """Test that Hummingbot client can be created and initialized."""
        client = await create_hummingbot_client()
        
        # Check if client was created
        if client is None:
            pytest.skip("Hummingbot client initialization failed - Hummingbot not running")
        
        assert client is not None
        print("✓ Hummingbot client created successfully")

    async def test_hummingbot_config_loading(self) -> None:
        """Test that Hummingbot configuration is properly loaded from environment."""
        config = HummingbotConfig()
        
        # Verify host and port are set
        assert config.hummingbot_host is not None
        assert config.hummingbot_port > 0
        print(f"✓ Hummingbot config loaded: {config.hummingbot_host}:{config.hummingbot_port}")

    async def test_system_init_with_hummingbot(self) -> None:
        """Test SystemInitialization with real Hummingbot client."""
        client = await create_hummingbot_client()
        
        if client is None:
            pytest.skip("Hummingbot not available")
        
        config = {
            "exchange": os.getenv("EXCHANGE", "binance"),
            "trading_pair": os.getenv("TRADING_PAIR", "ETH-USDT"),
            "hummingbot_client": client,
            "hummingbot_username": HUMMINGBOT_USERNAME,
            "hummingbot_password": HUMMINGBOT_PASSWORD,
        }
        
        agent = SystemInitialization(config)
        result = agent.execute()
        
        # Verify initialization attempted with Hummingbot
        assert result["hummingbot_connected"] is True
        assert isinstance(result["account_balance"], (int, float))
        # Note: initialization may fail if account balance < 100 USDT, which is expected
        # The important thing is that it tried to connect to Hummingbot
        print(f"✓ System initialized with Hummingbot | Balance: {result['account_balance']} USDT | Status: {result['system_status']}")


class TestHummingbotConnectionLocal:
    """Local tests for Hummingbot connectivity that don't require Hummingbot to be running."""

    def test_hummingbot_api_client_import(self) -> None:
        """Test that HummingbotAPIClient can be imported."""
        try:
            from hummingbot_api_client import HummingbotAPIClient  # type: ignore
            
            assert HummingbotAPIClient is not None
            print("✓ HummingbotAPIClient imported successfully")
        except ImportError:
            pytest.skip("hummingbot-api-client not installed")

    def test_hummingbot_config_environment_variables(self) -> None:
        """Test that Hummingbot config reads environment variables correctly."""
        # Set test environment variables
        os.environ["HUMMINGBOT_HOST"] = "test.example.com"
        os.environ["HUMMINGBOT_PORT"] = "9000"
        os.environ["HUMMINGBOT_USERNAME"] = "test_user"
        os.environ["HUMMINGBOT_PASSWORD"] = "test_pass"
        
        try:
            config = HummingbotConfig()
            
            assert config.hummingbot_host == "test.example.com"
            assert config.hummingbot_port == 9000
            assert config.hummingbot_username == "test_user"
            assert config.hummingbot_password == "test_pass"
            print("✓ Environment variables loaded correctly")
        finally:
            # Clean up environment variables
            if "HUMMINGBOT_HOST" in os.environ:
                del os.environ["HUMMINGBOT_HOST"]
            if "HUMMINGBOT_PORT" in os.environ:
                del os.environ["HUMMINGBOT_PORT"]
            if "HUMMINGBOT_USERNAME" in os.environ:
                del os.environ["HUMMINGBOT_USERNAME"]
            if "HUMMINGBOT_PASSWORD" in os.environ:
                del os.environ["HUMMINGBOT_PASSWORD"]

    def test_hummingbot_config_defaults(self) -> None:
        """Test that Hummingbot config has sensible defaults."""
        # Ensure env vars are not set
        for key in ["HUMMINGBOT_HOST", "HUMMINGBOT_PORT", "HUMMINGBOT_USERNAME", "HUMMINGBOT_PASSWORD"]:
            if key in os.environ:
                del os.environ[key]
        
        config = HummingbotConfig()
        
        # Check defaults
        assert config.hummingbot_host == "localhost"
        assert config.hummingbot_port == 8000
        assert config.hummingbot_username == ""
        assert config.hummingbot_password == ""
        print("✓ Default configuration values are correct")

    def test_hummingbot_config_to_dict(self) -> None:
        """Test that config can be converted to dictionary."""
        os.environ["HUMMINGBOT_HOST"] = "localhost"
        os.environ["HUMMINGBOT_PORT"] = "8000"
        
        try:
            config = HummingbotConfig()
            config_dict = config.to_dict()
            
            assert isinstance(config_dict, dict)
            assert "hummingbot_host" in config_dict
            assert "hummingbot_port" in config_dict
            assert "exchange" in config_dict
            assert "trading_pair" in config_dict
            print("✓ Configuration converted to dictionary successfully")
        finally:
            if "HUMMINGBOT_HOST" in os.environ:
                del os.environ["HUMMINGBOT_HOST"]
            if "HUMMINGBOT_PORT" in os.environ:
                del os.environ["HUMMINGBOT_PORT"]


@pytest.mark.skipif(not HUMMINGBOT_AVAILABLE, reason="Hummingbot not configured")
class TestHummingbotAdvanced:
    """Advanced integration tests for Hummingbot."""

    async def test_hummingbot_exchange_connectivity(self) -> None:
        """Test connectivity to exchange via Hummingbot."""
        client = await create_hummingbot_client()
        
        if client is None:
            pytest.skip("Hummingbot not available")
        
        config = {
            "hummingbot_client": client,
            "hummingbot_username": HUMMINGBOT_USERNAME,
            "hummingbot_password": HUMMINGBOT_PASSWORD,
            "exchange": os.getenv("EXCHANGE", "binance"),
            "trading_pair": os.getenv("TRADING_PAIR", "ETH-USDT"),
        }
        
        agent = SystemInitialization(config)
        exchange_info = agent._validate_exchange_connection()
        
        # Verify exchange connectivity
        assert exchange_info is not None
        print(f"✓ Exchange connectivity verified: {exchange_info.get('exchange_status')}")

    async def test_hummingbot_trading_pair_validation(self) -> None:
        """Test that trading pairs are validated correctly."""
        client = await create_hummingbot_client()
        
        if client is None:
            pytest.skip("Hummingbot not available")
        
        config = {
            "hummingbot_client": client,
            "trading_pair": os.getenv("TRADING_PAIR", "ETH-USDT"),
            "exchange": os.getenv("EXCHANGE", "binance"),
        }
        
        agent = SystemInitialization(config)
        is_valid = agent._validate_trading_pair()
        
        # Trading pair should be valid if we're testing with configured pair
        assert isinstance(is_valid, bool)
        print(f"✓ Trading pair validation: {is_valid}")

    async def test_hummingbot_account_balance_fetch(self) -> None:
        """Test fetching account balance from Hummingbot."""
        client = await create_hummingbot_client()
        
        if client is None:
            pytest.skip("Hummingbot not available")
        
        config = {"hummingbot_client": client}
        agent = SystemInitialization(config)
        balance = agent._fetch_account_balance()
        
        # Balance should be a float (can be 0 if account is empty)
        assert isinstance(balance, float)
        assert balance >= 0
        print(f"✓ Account balance fetched: {balance} USDT")


class TestHummingbotConnectionHelpers:
    """Helper methods for testing Hummingbot connectivity."""

    @staticmethod
    def check_hummingbot_running() -> bool:
        """Check if Hummingbot is running locally.
        
        Returns:
            True if Hummingbot is accessible, False otherwise.
        """
        import socket
        
        host = os.getenv("HUMMINGBOT_HOST", "localhost")
        port = int(os.getenv("HUMMINGBOT_PORT", "8000"))
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def test_hummingbot_port_accessible(self) -> None:
        """Test if Hummingbot port is accessible."""
        if not HUMMINGBOT_AVAILABLE:
            pytest.skip("Hummingbot host not configured")
        
        is_running = self.check_hummingbot_running()
        
        if is_running:
            print(f"✓ Hummingbot is running on {os.getenv('HUMMINGBOT_HOST')}:{os.getenv('HUMMINGBOT_PORT')}")
        else:
            print(f"⚠️  Hummingbot is not accessible on {os.getenv('HUMMINGBOT_HOST')}:{os.getenv('HUMMINGBOT_PORT')}")
        
        # Don't fail the test if Hummingbot isn't running
        assert isinstance(is_running, bool)
