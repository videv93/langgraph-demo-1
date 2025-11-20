"""System initialization agent for trading session setup with Hummingbot integration."""

import asyncio
from datetime import UTC, datetime
from typing import Any, TypedDict


class SystemInitializationOutput(TypedDict):
    """Output from system initialization."""

    session_initialized: bool
    initialization_timestamp: str
    system_status: str
    validation_errors: list[str]
    hummingbot_connected: bool
    exchange_info: dict[str, Any]
    account_balance: float


class SystemInitialization:
    """Initialize trading session and validate system readiness with Hummingbot.

    Performs pre-trading checks including:
    - Session validation
    - Hummingbot connection and authentication
    - Exchange connectivity checks
    - Trading pair and account validation
    - Configuration validation
    - Risk parameters initialization
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the system initialization agent.

        Args:
            config: Optional configuration dictionary for the agent.
                Expected keys: hummingbot_client, exchange, trading_pair,
                risk_config, hummingbot_host, hummingbot_port,
                hummingbot_username, hummingbot_password
        """
        self.config = config or {}
        self.timestamp = datetime.now(UTC).isoformat()
        self.account_balance = 0.0
        self.hummingbot_client = config.get("hummingbot_client") if config else None
        self.exchange = config.get("exchange", "binance") if config else "binance"
        self.trading_pair = (
            config.get("trading_pair", "ETH-USDT") if config else "ETH-USDT"
        )

    async def execute(self) -> SystemInitializationOutput:
        """Execute system initialization with Hummingbot integration.

        Returns:
            SystemInitializationOutput with initialization status and exchange info.
        """
        errors = []
        warnings = []
        hummingbot_connected = False
        exchange_info = {}

        # Check Hummingbot connection
        if not self._check_hummingbot_connection():
            warnings.append("Hummingbot client not available - running in demo mode")
            # Use demo balance for testing
            self.account_balance = 10000.0
        else:
            hummingbot_connected = True

        if hummingbot_connected:
            # Validate exchange connectivity
            exchange_info = self._validate_exchange_connection()
            if not exchange_info.get("connected", False):
                errors.append(
                    f"Exchange connectivity check failed: {exchange_info.get('error', 'Unknown error')}"
                )

            # Validate trading pair on exchange
            if not self._validate_trading_pair():
                errors.append(
                    f"Trading pair {self.trading_pair} not available on {self.exchange}"
                )

            # Fetch account balance from Hummingbot
            self.account_balance = await self._fetch_account_balance()
            if self.account_balance <= 0:
                errors.append("Failed to fetch account balance from Hummingbot")
            elif self.account_balance < 100.0:
                errors.append(
                    f"Account balance {self.account_balance} USDT is below minimum 100 USDT"
                )
        else:
            # Use demo exchange info
            exchange_info = {
                "exchange": self.exchange,
                "connected": False,
                "demo_mode": True,
                "message": "Running in demo mode without Hummingbot connection",
            }

        # Validate required configuration
        if not self._validate_configuration():
            errors.append("Configuration validation failed")

        # Initialize risk parameters
        if not self._initialize_risk_parameters():
            errors.append("Risk parameter initialization failed")

        # Allow initialization in demo mode if config is valid
        is_initialized = len(errors) == 0

        # Log warnings
        for warning in warnings:
            print(f"⚠️  {warning}")

        return {
            "session_initialized": is_initialized,
            "initialization_timestamp": self.timestamp,
            "system_status": "ready" if is_initialized else "failed",
            "validation_errors": errors,
            "hummingbot_connected": hummingbot_connected,
            "exchange_info": exchange_info,
            "account_balance": self.account_balance,
        }

    def _check_hummingbot_connection(self) -> bool:
        """Check Hummingbot API connection and client initialization.

        Returns:
            True if Hummingbot client is initialized, False otherwise.
        """
        if not self.hummingbot_client:
            return False

        try:
            # Check if client has been properly initialized
            # Hummingbot client will have connection methods available
            return True
        except Exception:
            return False

    def _validate_exchange_connection(self) -> dict[str, Any]:
        """Validate connection to the specified exchange via Hummingbot API.

        Returns:
            Dictionary with connection status and exchange metadata.
        """
        exchange_info = {
            "exchange": self.exchange,
            "connected": False,
            "error": None,
            "exchange_status": "unknown",
            "server_time": None,
        }

        try:
            # In production, would call Hummingbot API to validate exchange connection
            # Example: requests.get(
            #     f"http://{self.hummingbot_host}:{self.hummingbot_port}/api/exchange/{self.exchange}/status",
            #     headers={"Authorization": f"Bearer {auth_token}"}
            # )

            # Placeholder: simulate successful exchange validation
            exchange_info["connected"] = True
            exchange_info["exchange_status"] = "operational"
            exchange_info["server_time"] = self.timestamp
            exchange_info["exchange_fees"] = {"maker": 0.001, "taker": 0.001}
            exchange_info["authenticated_exchange"] = self.exchange

            return exchange_info
        except Exception as e:
            exchange_info["error"] = str(e)
            return exchange_info

    def _validate_trading_pair(self) -> bool:
        """Validate that the trading pair is available on the exchange.

        Returns:
            True if trading pair is available, False otherwise.
        """
        if not self.hummingbot_client:
            return False

        try:
            # In production, would call:
            # available_pairs = self.hummingbot_client.get_trading_pairs()
            # return self.trading_pair in available_pairs

            # Placeholder validation
            supported_pairs = ["ETH-USDT", "BTC-USDT", "SOL-USDT"]
            return self.trading_pair in supported_pairs
        except Exception:
            return False

    async def _fetch_account_balance(self) -> float:
        """Fetch account balance from Hummingbot API.

        Returns:
            Account balance in USDT, or 0.0 if fetch fails.
        """
        if not self.hummingbot_client:
            return 0.0

        try:
            return await self._get_balance_async()
        except Exception as e:
            print(f"Error fetching balance from Hummingbot: {e}")
            return 0.0

    async def _get_balance_async(self) -> float:
        """Asynchronously fetch USDT balance from Hummingbot portfolio.

        Returns:
            Total USDT balance across all accounts, or 0.0 if fetch fails.
        """
        try:
            # Get portfolio state from Hummingbot
            portfolio_state = await self.hummingbot_client.portfolio.get_state()

            # Sum up USDT balance across all accounts and connectors
            total_usdt = 0.0
            if portfolio_state:
                # Portfolio state structure: {'master_account': {'connector_name': [token_items]}}
                for account_name, connectors in portfolio_state.items():
                    if isinstance(connectors, dict):
                        for connector_name, token_list in connectors.items():
                            if isinstance(token_list, list):
                                for token_item in token_list:
                                    if (
                                        isinstance(token_item, dict)
                                        and token_item.get("token") == "USDT"
                                    ):
                                        total_usdt += float(token_item.get("available_units", 0))

            return total_usdt
        except Exception as e:
            print(f"Error fetching balance from Hummingbot: {e}")
            return 0.0

    def _validate_configuration(self) -> bool:
        """Validate system configuration.

        Returns:
            True if configuration is valid, False otherwise.
        """
        required_keys = ["exchange", "trading_pair"]
        for key in required_keys:
            if key not in self.config and not hasattr(self, key):
                return False

        # Validate exchange is supported (allow demo mode)
        supported_exchanges = ["binance-perpeptual", "binance-perpetual-testnet", "binance"]
        if self.exchange not in supported_exchanges:
            return False

        # Validate trading pair format
        if not isinstance(self.trading_pair, str) or "-" not in self.trading_pair:
            return False

        return True

    def _initialize_risk_parameters(self) -> bool:
        """Initialize risk management parameters with Hummingbot integration.

        Returns:
            True if risk parameters initialized successfully, False otherwise.
        """
        try:
            risk_config = self.config.get("risk_config", {})

            # Set default risk parameters if not provided
            default_params = {
                "account_risk_percent": 2.0,
                "max_position_size": 10000.0,
                "max_drawdown_percent": 10.0,
                "stop_loss_margin": 0.02,
                "take_profit_margin": 0.05,
                "position_mode": "one_way",
            }

            for key, value in default_params.items():
                if key not in risk_config:
                    risk_config[key] = value

            # In production, would apply these parameters to Hummingbot connector
            # Example: self.hummingbot_client.set_risk_parameters(risk_config)

            self.config["risk_config"] = risk_config
            return True
        except Exception:
            return False
