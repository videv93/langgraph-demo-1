"""Configuration for trading agents and Hummingbot integration."""

import asyncio
import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()

# Lazy import to avoid import errors if hummingbot-api-client not installed yet
try:
    from hummingbot_api_client import HummingbotAPIClient
except ImportError:
    HummingbotAPIClient = None  # type: ignore


class HummingbotConfig:
    """Hummingbot connection and exchange configuration."""

    def __init__(self):
        """Initialize Hummingbot configuration from environment or defaults."""
        # Exchange settings
        self.exchange = os.getenv("EXCHANGE", "binance")
        self.trading_pair = os.getenv("TRADING_PAIR", "ETH-USDT")

        # Hummingbot connection (username/password authentication)
        self.hummingbot_host = os.getenv("HUMMINGBOT_HOST", "localhost")
        self.hummingbot_port = int(os.getenv("HUMMINGBOT_PORT", "8000"))
        self.hummingbot_username = os.getenv("HUMMINGBOT_USERNAME", "")
        self.hummingbot_password = os.getenv("HUMMINGBOT_PASSWORD", "")

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary for agent initialization."""
        return {
            "exchange": self.exchange,
            "trading_pair": self.trading_pair,
            "hummingbot_host": self.hummingbot_host,
            "hummingbot_port": self.hummingbot_port,
            "hummingbot_username": self.hummingbot_username,
            "hummingbot_password": self.hummingbot_password,
        }


class RiskConfig:
    """Risk management parameters."""

    def __init__(self):
        """Initialize risk configuration from environment or defaults."""
        self.account_risk_percent = float(os.getenv("ACCOUNT_RISK_PERCENT", "2.0"))
        self.max_position_size = float(os.getenv("MAX_POSITION_SIZE", "10000.0"))
        self.max_drawdown_percent = float(os.getenv("MAX_DRAWDOWN_PERCENT", "10.0"))
        self.stop_loss_margin = float(os.getenv("STOP_LOSS_MARGIN", "0.02"))
        self.take_profit_margin = float(os.getenv("TAKE_PROFIT_MARGIN", "0.05"))

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "account_risk_percent": self.account_risk_percent,
            "max_position_size": self.max_position_size,
            "max_drawdown_percent": self.max_drawdown_percent,
            "stop_loss_margin": self.stop_loss_margin,
            "take_profit_margin": self.take_profit_margin,
        }


async def create_hummingbot_client() -> Any:
    """Create and initialize Hummingbot API client.

    Returns:
        Initialized HummingbotAPIClient or None if initialization fails.
    """
    if HummingbotAPIClient is None:
        print("⚠️  hummingbot-api-client not installed - running in demo mode")
        return None

    try:
        hummingbot_config = HummingbotConfig()
        base_url = f"http://{hummingbot_config.hummingbot_host}:{hummingbot_config.hummingbot_port}"
        
        client = HummingbotAPIClient(
            base_url=base_url,
            username=hummingbot_config.hummingbot_username,
            password=hummingbot_config.hummingbot_password,
        )
        await client.init()
        return client
    except Exception as e:
        print(f"Failed to initialize Hummingbot client: {e}")
        return None


def get_system_initialization_config(
    hummingbot_client: Any = None,
) -> dict[str, Any]:
    """Build complete config dict for SystemInitialization agent.

    Args:
        hummingbot_client: Optional initialized Hummingbot client instance.

    Returns:
        Configuration dictionary for SystemInitialization.
    """
    hummingbot_config = HummingbotConfig()
    risk_config = RiskConfig()

    return {
        "hummingbot_client": hummingbot_client,
        "exchange": hummingbot_config.exchange,
        "trading_pair": hummingbot_config.trading_pair,
        "risk_config": risk_config.to_dict(),
        **hummingbot_config.to_dict(),
    }
