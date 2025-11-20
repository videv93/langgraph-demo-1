"""Utilities for fetching real market data from Hummingbot API."""

from typing import Any, Optional
import datetime


async def fetch_current_price(
    hummingbot_client: Any,
    trading_pair: str = "ETH-USDT",
    exchange: str = "binance_perpetual_testnet"
) -> float:
    """Fetch current price for a trading pair from Hummingbot.

    Args:
        hummingbot_client: Initialized HummingbotAPIClient.
        trading_pair: Trading pair to fetch price for (e.g., BTC-USDT).
        exchange: Exchange connector (e.g., binance_perpetual_testnet).

    Returns:
        Current price or 0.0 if fetch fails.
    """
    if not hummingbot_client:
        return 0.0

    try:
        response = await hummingbot_client.market_data.get_prices(
            connector_name=exchange,
            trading_pairs=[trading_pair]
        )
        if response and "prices" in response:
            prices = response.get("prices", {})
            if trading_pair in prices:
                return float(prices[trading_pair])
        return 0.0
    except Exception as e:
        print(f"Error fetching current price: {e}")
        return 0.0


async def fetch_market_data(
    hummingbot_client: Any,
    trading_pair: str = "BTC-USDT",
    exchange: str = "binance_perpetual_testnet"
) -> dict[str, Any]:
    """Fetch market data including price and order book.

    Args:
        hummingbot_client: Initialized HummingbotAPIClient.
        trading_pair: Trading pair to fetch data for.
        exchange: Exchange connector (e.g., binance_perpetual_testnet).

    Returns:
        Dictionary with market data.
    """
    if not hummingbot_client:
        return {}

    try:
        # Get current price
        response = await hummingbot_client.market_data.get_prices(
            connector_name=exchange,
            trading_pairs=[trading_pair]
        )
        current_price = 0.0
        if response and "prices" in response:
            prices = response.get("prices", {})
            current_price = float(prices.get(trading_pair, 0.0)) if prices else 0.0

        # Get order book for bid/ask
        order_book = await hummingbot_client.market_data.get_order_book(
            connector_name=exchange,
            trading_pair=trading_pair
        )

        bid = 0.0
        ask = 0.0
        if order_book:
            bids = order_book.get("bids", [])
            asks = order_book.get("asks", [])
            # Each bid/ask is a dict with 'price' and 'amount' keys
            if bids and isinstance(bids[0], dict):
                bid = float(bids[0].get("price", 0))
            if asks and isinstance(asks[0], dict):
                ask = float(asks[0].get("price", 0))

        return {
            "last_price": current_price,
            "bid": bid,
            "ask": ask,
            "spread": ask - bid if ask > 0 and bid > 0 else 0.0,
            "timestamp": datetime.datetime.now().isoformat(),
        }
    except Exception as e:
        print(f"Error fetching market data: {e}")
        return {}


async def fetch_order_book(
    hummingbot_client: Any,
    trading_pair: str = "BTC-USDT",
    depth: int = 5,
    exchange: str = "binance_perpetual_testnet"
) -> dict[str, Any]:
    """Fetch order book (bids and asks) for a trading pair.

    Args:
        hummingbot_client: Initialized HummingbotAPIClient.
        trading_pair: Trading pair to fetch order book for.
        depth: Number of orders to fetch from each side.
        exchange: Exchange connector (e.g., binance_perpetual_testnet).

    Returns:
        Dictionary with bids and asks.
    """
    if not hummingbot_client:
        return {"bids": [], "asks": []}

    try:
        order_book = await hummingbot_client.market_data.get_order_book(
            connector_name=exchange,
            trading_pair=trading_pair
        )
        if order_book:
            bids = order_book.get("bids", [])
            asks = order_book.get("asks", [])
            return {
                "bids": bids[:depth] if bids else [],
                "asks": asks[:depth] if asks else [],
            }
        return {"bids": [], "asks": []}
    except Exception as e:
        print(f"Error fetching order book: {e}")
        return {"bids": [], "asks": []}


async def fetch_account_positions(hummingbot_client: Any) -> list[dict[str, Any]]:
    """Fetch active positions from Hummingbot account.

    Args:
        hummingbot_client: Initialized HummingbotAPIClient.

    Returns:
        List of active positions.
    """
    if not hummingbot_client:
        return []

    try:
        # Get portfolio state
        portfolio = await hummingbot_client.portfolio.get_state()
        if not portfolio:
            return []

        positions = []
        for account_name, connectors in portfolio.items():
            if isinstance(connectors, dict):
                for connector_name, token_list in connectors.items():
                    if isinstance(token_list, list):
                        for token_item in token_list:
                            if isinstance(token_item, dict):
                                positions.append({
                                    "account": account_name,
                                    "connector": connector_name,
                                    "token": token_item.get("token"),
                                    "units": float(token_item.get("units", 0)),
                                    "available_units": float(
                                        token_item.get("available_units", 0)
                                    ),
                                    "value": float(token_item.get("value", 0)),
                                    "price": float(token_item.get("price", 0)),
                                })
        return positions
    except Exception as e:
        print(f"Error fetching positions: {e}")
        return []


async def fetch_price_history_htf(
    hummingbot_client: Any,
    trading_pair: str = "BTC-USDT",
    limit: int = 50,
    exchange: str = "binance_perpetual"
) -> list[dict[str, Any]]:
    """Fetch higher timeframe (4H) OHLCV price history.

    Args:
        hummingbot_client: Initialized HummingbotAPIClient.
        trading_pair: Trading pair to fetch history for.
        limit: Number of candles to fetch (default 50 for 4H = ~8 days).
        exchange: Exchange connector (e.g., binance_perpetual_testnet).

    Returns:
        List of OHLCV candles for HTF (4H).
    """
    if not hummingbot_client:
        return []

    try:
        candles = await hummingbot_client.market_data.get_candles(
            connector_name=exchange,
            trading_pair=trading_pair,
            interval="4h",
            max_records=limit,
        )
        if candles:
            return [
                {
                    "timestamp": c.get("timestamp"),
                    "open": float(c.get("open", 0)),
                    "high": float(c.get("high", 0)),
                    "low": float(c.get("low", 0)),
                    "close": float(c.get("close", 0)),
                    "volume": float(c.get("volume", 0)),
                }
                for c in candles
            ]
        return []
    except Exception as e:
        print(f"Error fetching HTF price history: {e}")
        return []


async def fetch_price_history_tf(
    hummingbot_client: Any,
    trading_pair: str = "BTC-USDT",
    limit: int = 100,
    exchange: str = "binance_perpetual"
) -> list[dict[str, Any]]:
    """Fetch primary timeframe (15m) OHLCV price history.

    Args:
        hummingbot_client: Initialized HummingbotAPIClient.
        trading_pair: Trading pair to fetch history for.
        limit: Number of candles to fetch (default 100 for 15m = ~25 hours).
        exchange: Exchange connector (e.g., binance_perpetual_testnet).

    Returns:
        List of OHLCV candles for TF (15m).
    """
    if not hummingbot_client:
        return []

    try:
        candles = await hummingbot_client.market_data.get_candles(
            connector_name=exchange,
            trading_pair=trading_pair,
            interval="15m",
            max_records=limit,
        )
        if candles:
            return [
                {
                    "timestamp": c.get("timestamp"),
                    "open": float(c.get("open", 0)),
                    "high": float(c.get("high", 0)),
                    "low": float(c.get("low", 0)),
                    "close": float(c.get("close", 0)),
                    "volume": float(c.get("volume", 0)),
                }
                for c in candles
            ]
        return []
    except Exception as e:
        print(f"Error fetching TF price history: {e}")
        return []


async def fetch_price_history_ltf(
    hummingbot_client: Any,
    trading_pair: str = "BTC-USDT",
    limit: int = 100,
    exchange: str = "binance_perpetual"
) -> list[dict[str, Any]]:
    """Fetch lower timeframe (5m) OHLCV price history.

    Args:
        hummingbot_client: Initialized HummingbotAPIClient.
        trading_pair: Trading pair to fetch history for.
        limit: Number of candles to fetch (default 100 for 5m = ~8 hours).
        exchange: Exchange connector (e.g., binance_perpetual_testnet).

    Returns:
        List of OHLCV candles for LTF (5m).
    """
    if not hummingbot_client:
        return []

    try:
        candles = await hummingbot_client.market_data.get_candles(
            connector_name=exchange,
            trading_pair=trading_pair,
            interval="5m",
            max_records=limit,
        )
        if candles:
            return [
                {
                    "timestamp": c.get("timestamp"),
                    "open": float(c.get("open", 0)),
                    "high": float(c.get("high", 0)),
                    "low": float(c.get("low", 0)),
                    "close": float(c.get("close", 0)),
                    "volume": float(c.get("volume", 0)),
                }
                for c in candles
            ]
        return []
    except Exception as e:
        print(f"Error fetching LTF price history: {e}")
        return []


async def fetch_price_history(
    hummingbot_client: Any,
    trading_pair: str = "BTC-USDT",
    interval: str = "1m",
    limit: int = 100,
    exchange: str = "binance_perpetual"
) -> list[dict[str, Any]]:
    """Fetch OHLCV price history for a trading pair.

    Args:
        hummingbot_client: Initialized HummingbotAPIClient.
        trading_pair: Trading pair to fetch history for.
        interval: Candle interval (e.g., 1m, 5m, 1h, 1d).
        limit: Number of candles to fetch.
        exchange: Exchange connector (e.g., binance_perpetual_testnet).

    Returns:
        List of OHLCV candles.
    """
    if not hummingbot_client:
        return []

    try:
        candles = await hummingbot_client.market_data.get_candles(
            connector_name=exchange,
            trading_pair=trading_pair,
            interval=interval,
            max_records=limit,
        )
        if candles:
            return [
                {
                    "timestamp": c.get("timestamp"),
                    "open": float(c.get("open", 0)),
                    "high": float(c.get("high", 0)),
                    "low": float(c.get("low", 0)),
                    "close": float(c.get("close", 0)),
                    "volume": float(c.get("volume", 0)),
                }
                for c in candles
            ]
        return []
    except Exception as e:
        print(f"Error fetching price history: {e}")
        return []


async def fetch_price_history_range(
    hummingbot_client: Any,
    trading_pair: str = "BTC-USDT",
    interval: str = "1m",
    start_time: float = None,
    end_time: float = None,
    exchange: str = "binance_perpetual_testnet"
) -> list[dict[str, Any]]:
    """Fetch historical OHLCV data for a time range.

    Args:
        hummingbot_client: Initialized HummingbotAPIClient.
        trading_pair: Trading pair to fetch history for.
        interval: Candle interval (e.g., 1m, 5m, 1h, 1d).
        start_time: Start timestamp (Unix time).
        end_time: End timestamp (Unix time).
        exchange: Exchange connector (e.g., binance_perpetual_testnet).

    Returns:
        List of OHLCV candles.
    """
    if not hummingbot_client:
        return []

    try:
        candles = await hummingbot_client.market_data.get_historical_candles(
            connector_name=exchange,
            trading_pair=trading_pair,
            interval=interval,
            start_time=start_time,
            end_time=end_time,
        )
        if candles:
            return [
                {
                    "timestamp": c.get("timestamp"),
                    "open": float(c.get("open", 0)),
                    "high": float(c.get("high", 0)),
                    "low": float(c.get("low", 0)),
                    "close": float(c.get("close", 0)),
                    "volume": float(c.get("volume", 0)),
                }
                for c in candles
            ]
        return []
    except Exception as e:
        print(f"Error fetching historical price data: {e}")
        return []


async def fetch_funding_info(
    hummingbot_client: Any,
    trading_pair: str = "BTC-USDT",
    exchange: str = "binance_perpetual_testnet"
) -> dict[str, Any]:
    """Fetch funding rate info for perpetual pairs.

    Args:
        hummingbot_client: Initialized HummingbotAPIClient.
        trading_pair: Trading pair to fetch funding info for.
        exchange: Exchange connector (e.g., binance_perpetual_testnet).

    Returns:
        Funding info dictionary or empty dict if unavailable.
    """
    if not hummingbot_client:
        return {}

    try:
        funding_info = await hummingbot_client.market_data.get_funding_info(
            connector_name=exchange,
            trading_pair=trading_pair,
        )
        return funding_info if funding_info else {}
    except Exception as e:
        print(f"Error fetching funding info: {e}")
        return {}


async def place_order(
    hummingbot_client: Any,
    trading_pair: str,
    side: str,
    quantity: float,
    price: float,
    exchange: str = "binance_perpetual_testnet"
) -> Optional[dict[str, Any]]:
    """Place a limit order via Hummingbot.

    Args:
        hummingbot_client: Initialized HummingbotAPIClient.
        trading_pair: Trading pair (e.g., BTC-USDT).
        side: Order side (buy or sell).
        quantity: Order quantity.
        price: Order price.
        exchange: Exchange connector (e.g., binance_perpetual_testnet).

    Returns:
        Order result with order ID or None if failed.
    """
    if not hummingbot_client:
        return None

    try:
        order = await hummingbot_client.trading.place_order(
            connector_name=exchange,
            trading_pair=trading_pair,
            is_buy=(side.lower() == "buy"),
            quantity=quantity,
            price=price
        )
        if order:
            return {
                "order_id": order.get("orderId") or order.get("id"),
                "trading_pair": trading_pair,
                "side": side,
                "quantity": quantity,
                "price": price,
                "status": order.get("status", "pending"),
            }
        return None
    except Exception as e:
        print(f"Error placing order: {e}")
        return None


async def cancel_order(
    hummingbot_client: Any,
    order_id: str,
    trading_pair: str,
    exchange: str = "binance_perpetual_testnet"
) -> bool:
    """Cancel an order via Hummingbot.

    Args:
        hummingbot_client: Initialized HummingbotAPIClient.
        order_id: Order ID to cancel.
        trading_pair: Trading pair.
        exchange: Exchange connector (e.g., binance_perpetual_testnet).

    Returns:
        True if cancellation successful, False otherwise.
    """
    if not hummingbot_client:
        return False

    try:
        result = await hummingbot_client.trading.cancel_order(
            connector_name=exchange,
            order_id=order_id,
            trading_pair=trading_pair
        )
        return bool(result)
    except Exception as e:
        print(f"Error canceling order: {e}")
        return False
