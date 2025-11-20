"""Unit tests for Exit Execution Agent - Trade exit and position closure."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from agent.agents.exit_execution import (
    ExitExecution,
    TradeResult,
    ExitExecutionOutput,
)


class TestExitExecutionInit:
    """Test ExitExecution initialization."""

    def test_init_default_config(self) -> None:
        """Test initialization with default config."""
        executor = ExitExecution()
        assert executor.config == {}
        assert executor.open_position is None
        assert executor.current_price == 0.0
        assert executor.exit_reason == "manual"
        assert executor.exit_signal is False

    def test_init_custom_config(self) -> None:
        """Test initialization with custom config."""
        position = {
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
        config = {
            "open_position": position,
            "current_price": 108.0,
            "exit_reason": "Take Profit Hit",
            "exit_signal_detected": True,
        }
        executor = ExitExecution(config)

        assert executor.open_position == position
        assert executor.current_price == 108.0
        assert executor.exit_reason == "Take Profit Hit"
        assert executor.exit_signal is True

    def test_init_with_hummingbot_config(self) -> None:
        """Test initialization with Hummingbot client and trading config."""
        mock_client = MagicMock()
        position = {
            "trade_id": "TRD-ABC123",
            "entry_price": 100.0,
            "entry_type": "long",
            "position_size": 10.0,
            "stop_loss": 95.0,
            "take_profit": 110.0,
        }
        config = {
            "open_position": position,
            "current_price": 108.0,
            "hummingbot_client": mock_client,
            "trading_pair": "ETH-USDT",
            "exchange": "binance_perpetual_testnet",
        }
        executor = ExitExecution(config)

        assert executor.hummingbot_client == mock_client
        assert executor.trading_pair == "ETH-USDT"
        assert executor.exchange == "binance_perpetual_testnet"


class TestExecuteMethod:
    """Test the main execute method."""

    @pytest.mark.asyncio
    async def test_execute_no_position(self) -> None:
        """Test execute with no open position."""
        executor = ExitExecution()
        result = await executor.execute()

        assert result["execution_complete"] is True
        assert result["exit_successful"] is False
        assert result["trade_result"] is None
        assert "No open position" in result["exit_message"]

    @pytest.mark.asyncio
    async def test_execute_returns_correct_structure(self) -> None:
        """Test execute returns correct output structure."""
        position = {
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
        config = {
            "open_position": position,
            "current_price": 110.0,
        }
        executor = ExitExecution(config)
        result = await executor.execute()

        assert "execution_complete" in result
        assert "exit_successful" in result
        assert "trade_result" in result
        assert "exit_message" in result
        assert "execution_timestamp" in result

    @pytest.mark.asyncio
    async def test_execute_successful_exit(self) -> None:
        """Test successful trade exit execution."""
        position = {
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
        config = {
            "open_position": position,
            "current_price": 110.0,
        }
        executor = ExitExecution(config)
        result = await executor.execute()

        assert result["execution_complete"] is True
        assert result["exit_successful"] is True
        assert result["trade_result"] is not None


class TestExitPriceDetermination:
    """Test exit price determination logic."""

    def test_determine_exit_price_long_hit_tp(self) -> None:
        """Test exit price when long trade hits take profit."""
        position = {
            "entry_type": "long",
            "take_profit": 110.0,
            "stop_loss": 95.0,
        }
        config = {
            "open_position": position,
            "current_price": 110.0,
        }
        executor = ExitExecution(config)
        exit_price = executor._determine_exit_price()

        assert exit_price == 110.0

    def test_determine_exit_price_long_hit_sl(self) -> None:
        """Test exit price when long trade hits stop loss."""
        position = {
            "entry_type": "long",
            "take_profit": 110.0,
            "stop_loss": 95.0,
        }
        config = {
            "open_position": position,
            "current_price": 95.0,
        }
        executor = ExitExecution(config)
        exit_price = executor._determine_exit_price()

        assert exit_price == 95.0

    def test_determine_exit_price_long_between_sl_tp(self) -> None:
        """Test exit price for long trade between SL and TP."""
        position = {
            "entry_type": "long",
            "take_profit": 110.0,
            "stop_loss": 95.0,
        }
        config = {
            "open_position": position,
            "current_price": 105.0,
        }
        executor = ExitExecution(config)
        exit_price = executor._determine_exit_price()

        assert exit_price == 105.0

    def test_determine_exit_price_long_below_sl(self) -> None:
        """Test exit price when long trade falls below stop loss."""
        position = {
            "entry_type": "long",
            "take_profit": 110.0,
            "stop_loss": 95.0,
        }
        config = {
            "open_position": position,
            "current_price": 90.0,
        }
        executor = ExitExecution(config)
        exit_price = executor._determine_exit_price()

        # Should be capped at SL
        assert exit_price == 95.0

    def test_determine_exit_price_long_above_tp(self) -> None:
        """Test exit price when long trade goes above take profit."""
        position = {
            "entry_type": "long",
            "take_profit": 110.0,
            "stop_loss": 95.0,
        }
        config = {
            "open_position": position,
            "current_price": 115.0,
        }
        executor = ExitExecution(config)
        exit_price = executor._determine_exit_price()

        # Should be capped at TP
        assert exit_price == 110.0

    def test_determine_exit_price_short_hit_tp(self) -> None:
        """Test exit price when short trade hits take profit."""
        position = {
            "entry_type": "short",
            "take_profit": 90.0,
            "stop_loss": 105.0,
        }
        config = {
            "open_position": position,
            "current_price": 90.0,
        }
        executor = ExitExecution(config)
        exit_price = executor._determine_exit_price()

        assert exit_price == 90.0

    def test_determine_exit_price_short_hit_sl(self) -> None:
        """Test exit price when short trade hits stop loss."""
        position = {
            "entry_type": "short",
            "take_profit": 90.0,
            "stop_loss": 105.0,
        }
        config = {
            "open_position": position,
            "current_price": 105.0,
        }
        executor = ExitExecution(config)
        exit_price = executor._determine_exit_price()

        assert exit_price == 105.0

    def test_determine_exit_price_short_between_sl_tp(self) -> None:
        """Test exit price for short trade between TP and SL."""
        position = {
            "entry_type": "short",
            "take_profit": 90.0,
            "stop_loss": 105.0,
        }
        config = {
            "open_position": position,
            "current_price": 95.0,
        }
        executor = ExitExecution(config)
        exit_price = executor._determine_exit_price()

        assert exit_price == 95.0

    def test_determine_exit_price_zero_exit(self) -> None:
        """Test exit price returns current price when result is zero."""
        position = {
            "entry_type": "long",
            "take_profit": 0.0,
            "stop_loss": 0.0,
        }
        config = {
            "open_position": position,
            "current_price": 100.0,
        }
        executor = ExitExecution(config)
        exit_price = executor._determine_exit_price()

        assert exit_price == 100.0


class TestTradeResultCalculation:
    """Test trade result calculation."""

    def test_calculate_trade_result_long_profit(self) -> None:
        """Test P&L calculation for profitable long trade."""
        position = {
            "trade_id": "TRD-001",
            "entry_price": 100.0,
            "entry_type": "long",
            "position_size": 10.0,
            "stop_loss": 95.0,
            "take_profit": 110.0,
        }
        config = {"open_position": position}
        executor = ExitExecution(config)
        result = executor._calculate_trade_result(110.0)

        assert result is not None
        assert result["trade_id"] == "TRD-001"
        assert result["entry_price"] == 100.0
        assert result["exit_price"] == 110.0
        assert result["position_size"] == 10.0
        assert result["entry_type"] == "long"
        assert result["gross_pnl"] == pytest.approx(100.0)  # (110-100)*10
        assert result["pnl_percent"] == pytest.approx(10.0)  # (110-100)/100*100

    def test_calculate_trade_result_long_loss(self) -> None:
        """Test P&L calculation for losing long trade."""
        position = {
            "trade_id": "TRD-002",
            "entry_price": 100.0,
            "entry_type": "long",
            "position_size": 10.0,
            "stop_loss": 95.0,
            "take_profit": 110.0,
        }
        config = {"open_position": position}
        executor = ExitExecution(config)
        result = executor._calculate_trade_result(95.0)

        assert result is not None
        assert result["gross_pnl"] == pytest.approx(-50.0)  # (95-100)*10
        assert result["pnl_percent"] == pytest.approx(-5.0)  # (95-100)/100*100

    def test_calculate_trade_result_short_profit(self) -> None:
        """Test P&L calculation for profitable short trade."""
        position = {
            "trade_id": "TRD-003",
            "entry_price": 100.0,
            "entry_type": "short",
            "position_size": 10.0,
            "stop_loss": 105.0,
            "take_profit": 90.0,
        }
        config = {"open_position": position}
        executor = ExitExecution(config)
        result = executor._calculate_trade_result(90.0)

        assert result is not None
        assert result["entry_type"] == "short"
        assert result["gross_pnl"] == pytest.approx(100.0)  # (100-90)*10
        assert result["pnl_percent"] == pytest.approx(10.0)  # (100-90)/100*100

    def test_calculate_trade_result_short_loss(self) -> None:
        """Test P&L calculation for losing short trade."""
        position = {
            "trade_id": "TRD-004",
            "entry_price": 100.0,
            "entry_type": "short",
            "position_size": 10.0,
            "stop_loss": 105.0,
            "take_profit": 90.0,
        }
        config = {"open_position": position}
        executor = ExitExecution(config)
        result = executor._calculate_trade_result(105.0)

        assert result is not None
        assert result["gross_pnl"] == pytest.approx(-50.0)  # (100-105)*10
        assert result["pnl_percent"] == pytest.approx(-5.0)  # (100-105)/100*100

    def test_calculate_trade_result_zero_entry_price(self) -> None:
        """Test calculation fails with zero entry price."""
        position = {
            "trade_id": "TRD-005",
            "entry_price": 0.0,
            "entry_type": "long",
            "position_size": 10.0,
            "stop_loss": 95.0,
            "take_profit": 110.0,
        }
        config = {"open_position": position}
        executor = ExitExecution(config)
        result = executor._calculate_trade_result(110.0)

        assert result is None

    def test_calculate_trade_result_zero_position_size(self) -> None:
        """Test calculation fails with zero position size."""
        position = {
            "trade_id": "TRD-006",
            "entry_price": 100.0,
            "entry_type": "long",
            "position_size": 0.0,
            "stop_loss": 95.0,
            "take_profit": 110.0,
        }
        config = {"open_position": position}
        executor = ExitExecution(config)
        result = executor._calculate_trade_result(110.0)

        assert result is None

    def test_calculate_trade_result_zero_exit_price(self) -> None:
        """Test calculation fails with zero exit price."""
        position = {
            "trade_id": "TRD-007",
            "entry_price": 100.0,
            "entry_type": "long",
            "position_size": 10.0,
            "stop_loss": 95.0,
            "take_profit": 110.0,
        }
        config = {"open_position": position}
        executor = ExitExecution(config)
        result = executor._calculate_trade_result(0.0)

        assert result is None

    def test_calculate_trade_result_has_required_fields(self) -> None:
        """Test trade result has all required fields."""
        position = {
            "trade_id": "TRD-008",
            "entry_price": 100.0,
            "entry_type": "long",
            "position_size": 10.0,
            "stop_loss": 95.0,
            "take_profit": 110.0,
        }
        config = {"open_position": position}
        executor = ExitExecution(config)
        result = executor._calculate_trade_result(110.0)

        required_fields = [
            "trade_id",
            "entry_price",
            "exit_price",
            "position_size",
            "entry_type",
            "exit_reason",
            "gross_pnl",
            "pnl_percent",
            "exit_time",
        ]
        for field in required_fields:
            assert field in result


class TestExitReasonDetermination:
    """Test exit reason determination."""

    def test_determine_exit_reason_take_profit_hit(self) -> None:
        """Test exit reason when take profit is hit."""
        position = {
            "take_profit": 110.0,
            "stop_loss": 95.0,
        }
        config = {
            "open_position": position,
            "exit_reason": "manual",
        }
        executor = ExitExecution(config)
        reason = executor._determine_exit_reason(110.0)

        assert reason == "Take Profit Hit"

    def test_determine_exit_reason_stop_loss_hit(self) -> None:
        """Test exit reason when stop loss is hit."""
        position = {
            "take_profit": 110.0,
            "stop_loss": 95.0,
        }
        config = {
            "open_position": position,
            "exit_reason": "manual",
        }
        executor = ExitExecution(config)
        reason = executor._determine_exit_reason(95.0)

        assert reason == "Stop Loss Hit"

    def test_determine_exit_reason_exit_signal(self) -> None:
        """Test exit reason when exit signal is triggered."""
        position = {
            "take_profit": 110.0,
            "stop_loss": 95.0,
        }
        config = {
            "open_position": position,
            "exit_reason": "manual",
            "exit_signal_detected": True,
        }
        executor = ExitExecution(config)
        reason = executor._determine_exit_reason(105.0)

        assert reason == "Exit Signal - Technical Reversal"

    def test_determine_exit_reason_manual_exit(self) -> None:
        """Test exit reason for manual exit."""
        position = {
            "take_profit": 110.0,
            "stop_loss": 95.0,
        }
        config = {
            "open_position": position,
            "exit_reason": "manual",
            "exit_signal_detected": False,
        }
        executor = ExitExecution(config)
        reason = executor._determine_exit_reason(105.0)

        assert reason == "Manual Exit"

    def test_determine_exit_reason_preset_reason(self) -> None:
        """Test exit reason returns preset value."""
        position = {
            "take_profit": 110.0,
            "stop_loss": 95.0,
        }
        config = {
            "open_position": position,
            "exit_reason": "Forced Liquidation",
        }
        executor = ExitExecution(config)
        reason = executor._determine_exit_reason(105.0)

        assert reason == "Forced Liquidation"

    def test_determine_exit_reason_tolerance_tp(self) -> None:
        """Test exit reason recognizes TP within tolerance."""
        position = {
            "take_profit": 110.0,
            "stop_loss": 95.0,
        }
        config = {
            "open_position": position,
            "exit_reason": "manual",
        }
        executor = ExitExecution(config)
        reason = executor._determine_exit_reason(110.005)

        assert reason == "Take Profit Hit"

    def test_determine_exit_reason_tolerance_sl(self) -> None:
        """Test exit reason recognizes SL within tolerance."""
        position = {
            "take_profit": 110.0,
            "stop_loss": 95.0,
        }
        config = {
            "open_position": position,
            "exit_reason": "manual",
        }
        executor = ExitExecution(config)
        reason = executor._determine_exit_reason(95.005)

        assert reason == "Stop Loss Hit"


class TestIntegrationScenarios:
    """Test integration scenarios with realistic data."""

    @pytest.mark.asyncio
    async def test_full_exit_execution_long_profit(self) -> None:
        """Test complete exit execution for profitable long trade."""
        position = {
            "trade_id": "TRD-LONG-001",
            "entry_price": 3500.0,
            "entry_time": "2025-01-01T10:00:00",
            "stop_loss": 3450.0,
            "take_profit": 3650.0,
            "position_size": 0.1,
            "position_value": 350.0,
            "entry_type": "long",
            "setup_type": "TST",
            "risk_reward_ratio": 3.0,
        }
        config = {
            "open_position": position,
            "current_price": 3650.0,
        }
        executor = ExitExecution(config)
        result = await executor.execute()

        assert result["execution_complete"] is True
        assert result["exit_successful"] is True
        assert result["trade_result"] is not None
        assert result["trade_result"]["gross_pnl"] == pytest.approx(15.0)
        assert result["trade_result"]["pnl_percent"] == pytest.approx(4.29, abs=0.1)
        assert "Take Profit Hit" in result["exit_message"]

    @pytest.mark.asyncio
    async def test_full_exit_execution_long_loss(self) -> None:
        """Test complete exit execution for losing long trade."""
        position = {
            "trade_id": "TRD-LONG-002",
            "entry_price": 3500.0,
            "entry_time": "2025-01-01T10:00:00",
            "stop_loss": 3450.0,
            "take_profit": 3650.0,
            "position_size": 0.1,
            "position_value": 350.0,
            "entry_type": "long",
            "setup_type": "BOF",
            "risk_reward_ratio": 2.0,
        }
        config = {
            "open_position": position,
            "current_price": 3450.0,
        }
        executor = ExitExecution(config)
        result = await executor.execute()

        assert result["execution_complete"] is True
        assert result["exit_successful"] is True
        assert result["trade_result"] is not None
        assert result["trade_result"]["gross_pnl"] == pytest.approx(-5.0)
        assert result["trade_result"]["pnl_percent"] == pytest.approx(-1.43, abs=0.1)
        assert "Stop Loss Hit" in result["exit_message"]

    @pytest.mark.asyncio
    async def test_full_exit_execution_short_profit(self) -> None:
        """Test complete exit execution for profitable short trade."""
        position = {
            "trade_id": "TRD-SHORT-001",
            "entry_price": 3500.0,
            "entry_time": "2025-01-01T10:00:00",
            "stop_loss": 3550.0,
            "take_profit": 3350.0,
            "position_size": 0.1,
            "position_value": 350.0,
            "entry_type": "short",
            "setup_type": "BPB",
            "risk_reward_ratio": 2.5,
        }
        config = {
            "open_position": position,
            "current_price": 3350.0,
        }
        executor = ExitExecution(config)
        result = await executor.execute()

        assert result["execution_complete"] is True
        assert result["exit_successful"] is True
        assert result["trade_result"] is not None
        assert result["trade_result"]["gross_pnl"] == pytest.approx(15.0)
        assert result["trade_result"]["pnl_percent"] == pytest.approx(4.29, abs=0.1)
        assert "Take Profit Hit" in result["exit_message"]

    @pytest.mark.asyncio
    async def test_full_exit_execution_short_loss(self) -> None:
        """Test complete exit execution for losing short trade."""
        position = {
            "trade_id": "TRD-SHORT-002",
            "entry_price": 3500.0,
            "entry_time": "2025-01-01T10:00:00",
            "stop_loss": 3550.0,
            "take_profit": 3350.0,
            "position_size": 0.1,
            "position_value": 350.0,
            "entry_type": "short",
            "setup_type": "CPB",
            "risk_reward_ratio": 2.0,
        }
        config = {
            "open_position": position,
            "current_price": 3550.0,
        }
        executor = ExitExecution(config)
        result = await executor.execute()

        assert result["execution_complete"] is True
        assert result["exit_successful"] is True
        assert result["trade_result"] is not None
        assert result["trade_result"]["gross_pnl"] == pytest.approx(-5.0)
        assert result["trade_result"]["pnl_percent"] == pytest.approx(-1.43, abs=0.1)
        assert "Stop Loss Hit" in result["exit_message"]

    @pytest.mark.asyncio
    async def test_full_exit_execution_manual_exit(self) -> None:
        """Test complete exit execution with manual exit."""
        position = {
            "trade_id": "TRD-MAN-001",
            "entry_price": 100.0,
            "entry_time": "2025-01-01T10:00:00",
            "stop_loss": 95.0,
            "take_profit": 110.0,
            "position_size": 10.0,
            "position_value": 1000.0,
            "entry_type": "long",
            "setup_type": "PB",
            "risk_reward_ratio": 2.0,
        }
        config = {
            "open_position": position,
            "current_price": 105.0,
            "exit_signal_detected": False,
        }
        executor = ExitExecution(config)
        result = await executor.execute()

        assert result["execution_complete"] is True
        assert result["exit_successful"] is True
        assert result["trade_result"] is not None
        assert result["trade_result"]["gross_pnl"] == pytest.approx(50.0)
        assert "Manual Exit" in result["exit_message"]

    @pytest.mark.asyncio
    async def test_full_exit_execution_exit_signal(self) -> None:
        """Test complete exit execution with exit signal."""
        position = {
            "trade_id": "TRD-SIG-001",
            "entry_price": 100.0,
            "entry_time": "2025-01-01T10:00:00",
            "stop_loss": 95.0,
            "take_profit": 110.0,
            "position_size": 10.0,
            "position_value": 1000.0,
            "entry_type": "long",
            "setup_type": "TST",
            "risk_reward_ratio": 2.0,
        }
        config = {
            "open_position": position,
            "current_price": 105.0,
            "exit_signal_detected": True,
        }
        executor = ExitExecution(config)
        result = await executor.execute()

        assert result["execution_complete"] is True
        assert result["exit_successful"] is True
        assert result["trade_result"] is not None
        assert "Exit Signal - Technical Reversal" in result["exit_message"]


class TestEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.asyncio
    async def test_execute_with_invalid_position_data(self) -> None:
        """Test execute with invalid position data."""
        position = {
            "trade_id": "TRD-BAD-001",
            "entry_price": 100.0,
            "entry_type": "long",
            "position_size": 0.0,  # Invalid
            "stop_loss": 95.0,
            "take_profit": 110.0,
        }
        config = {
            "open_position": position,
            "current_price": 110.0,
        }
        executor = ExitExecution(config)
        result = await executor.execute()

        assert result["execution_complete"] is True
        assert result["exit_successful"] is False
        assert result["trade_result"] is None

    def test_calculate_breakeven_exit(self) -> None:
        """Test exit at breakeven price."""
        position = {
            "trade_id": "TRD-BE-001",
            "entry_price": 100.0,
            "entry_type": "long",
            "position_size": 10.0,
            "stop_loss": 95.0,
            "take_profit": 110.0,
        }
        config = {"open_position": position}
        executor = ExitExecution(config)
        result = executor._calculate_trade_result(100.0)

        assert result is not None
        assert result["gross_pnl"] == pytest.approx(0.0)
        assert result["pnl_percent"] == pytest.approx(0.0)

    def test_large_position_pnl_calculation(self) -> None:
        """Test P&L calculation with large position."""
        position = {
            "trade_id": "TRD-LARGE-001",
            "entry_price": 100.0,
            "entry_type": "long",
            "position_size": 1000.0,  # Large position
            "stop_loss": 95.0,
            "take_profit": 110.0,
        }
        config = {"open_position": position}
        executor = ExitExecution(config)
        result = executor._calculate_trade_result(110.0)

        assert result is not None
        assert result["gross_pnl"] == pytest.approx(10000.0)  # (110-100)*1000
        assert result["pnl_percent"] == pytest.approx(10.0)

    def test_small_position_pnl_calculation(self) -> None:
        """Test P&L calculation with small position."""
        position = {
            "trade_id": "TRD-SMALL-001",
            "entry_price": 100.0,
            "entry_type": "long",
            "position_size": 0.001,  # Small position
            "stop_loss": 95.0,
            "take_profit": 110.0,
        }
        config = {"open_position": position}
        executor = ExitExecution(config)
        result = executor._calculate_trade_result(110.0)

        assert result is not None
        assert result["gross_pnl"] == pytest.approx(0.01)  # (110-100)*0.001
        assert result["pnl_percent"] == pytest.approx(10.0)

    @pytest.mark.asyncio
    async def test_high_leverage_scenario(self) -> None:
        """Test exit with high leverage trade (large position value)."""
        position = {
            "trade_id": "TRD-LEV-001",
            "entry_price": 100.0,
            "entry_type": "long",
            "position_size": 100.0,
            "position_value": 10000.0,
            "stop_loss": 99.0,
            "take_profit": 101.0,
        }
        config = {
            "open_position": position,
            "current_price": 101.0,
        }
        executor = ExitExecution(config)
        result = await executor.execute()

        assert result["execution_complete"] is True
        assert result["exit_successful"] is True
        assert result["trade_result"]["gross_pnl"] == pytest.approx(100.0)


class TestHummingbotIntegration:
    """Test Hummingbot integration for exit execution."""

    @pytest.mark.asyncio
    async def test_update_current_price_with_client(self) -> None:
        """Test price update from Hummingbot client."""
        mock_client = MagicMock()
        position = {
            "trade_id": "TRD-HB-001",
            "entry_price": 100.0,
            "entry_type": "long",
            "position_size": 10.0,
            "stop_loss": 95.0,
            "take_profit": 110.0,
        }
        config = {
            "open_position": position,
            "current_price": 100.0,
            "hummingbot_client": mock_client,
            "trading_pair": "ETH-USDT",
            "exchange": "binance_perpetual_testnet",
        }
        executor = ExitExecution(config)

        # Mock the fetch_current_price to return a new price
        with pytest.mock.patch(
            "agent.agents.exit_execution.fetch_current_price",
            new_callable=AsyncMock,
            return_value=105.0,
        ):
            await executor._update_current_price()

        assert executor.current_price == 105.0

    @pytest.mark.asyncio
    async def test_update_current_price_without_client(self) -> None:
        """Test price update skipped when no client."""
        position = {
            "trade_id": "TRD-HB-002",
            "entry_price": 100.0,
            "entry_type": "long",
            "position_size": 10.0,
            "stop_loss": 95.0,
            "take_profit": 110.0,
        }
        config = {
            "open_position": position,
            "current_price": 100.0,
        }
        executor = ExitExecution(config)
        initial_price = executor.current_price

        await executor._update_current_price()

        assert executor.current_price == initial_price

    @pytest.mark.asyncio
    async def test_place_exit_order_long_position(self) -> None:
        """Test placing exit order for long position (sell side)."""
        mock_client = MagicMock()
        position = {
            "trade_id": "TRD-HB-003",
            "entry_price": 100.0,
            "entry_type": "long",
            "position_size": 10.0,
            "stop_loss": 95.0,
            "take_profit": 110.0,
        }
        config = {
            "open_position": position,
            "current_price": 110.0,
            "hummingbot_client": mock_client,
            "trading_pair": "ETH-USDT",
            "exchange": "binance_perpetual_testnet",
        }
        executor = ExitExecution(config)
        trade_result: TradeResult = {
            "trade_id": "TRD-HB-003",
            "entry_price": 100.0,
            "exit_price": 110.0,
            "position_size": 10.0,
            "entry_type": "long",
            "exit_reason": "Take Profit Hit",
            "gross_pnl": 100.0,
            "pnl_percent": 10.0,
            "exit_time": "2025-01-01T11:00:00",
        }

        with pytest.mock.patch(
            "agent.agents.exit_execution.place_order",
            new_callable=AsyncMock,
            return_value={"order_id": "ORD-123", "status": "pending"},
        ) as mock_place_order:
            result = await executor._place_exit_order(trade_result)

            # Verify order was placed with correct side (sell for long)
            mock_place_order.assert_called_once()
            call_args = mock_place_order.call_args
            assert call_args.kwargs["side"] == "sell"
            assert call_args.kwargs["quantity"] == 10.0
            assert call_args.kwargs["price"] == 110.0
            assert result is not None
            assert result["order_id"] == "ORD-123"

    @pytest.mark.asyncio
    async def test_place_exit_order_short_position(self) -> None:
        """Test placing exit order for short position (buy side)."""
        mock_client = MagicMock()
        position = {
            "trade_id": "TRD-HB-004",
            "entry_price": 100.0,
            "entry_type": "short",
            "position_size": 10.0,
            "stop_loss": 105.0,
            "take_profit": 90.0,
        }
        config = {
            "open_position": position,
            "current_price": 90.0,
            "hummingbot_client": mock_client,
            "trading_pair": "ETH-USDT",
            "exchange": "binance_perpetual_testnet",
        }
        executor = ExitExecution(config)
        trade_result: TradeResult = {
            "trade_id": "TRD-HB-004",
            "entry_price": 100.0,
            "exit_price": 90.0,
            "position_size": 10.0,
            "entry_type": "short",
            "exit_reason": "Take Profit Hit",
            "gross_pnl": 100.0,
            "pnl_percent": 10.0,
            "exit_time": "2025-01-01T11:00:00",
        }

        with pytest.mock.patch(
            "agent.agents.exit_execution.place_order",
            new_callable=AsyncMock,
            return_value={"order_id": "ORD-124", "status": "pending"},
        ) as mock_place_order:
            result = await executor._place_exit_order(trade_result)

            # Verify order was placed with correct side (buy for short)
            mock_place_order.assert_called_once()
            call_args = mock_place_order.call_args
            assert call_args.kwargs["side"] == "buy"
            assert call_args.kwargs["quantity"] == 10.0
            assert call_args.kwargs["price"] == 90.0
            assert result is not None

    @pytest.mark.asyncio
    async def test_place_exit_order_without_client(self) -> None:
        """Test exit order placement skipped when no client."""
        position = {
            "trade_id": "TRD-HB-005",
            "entry_price": 100.0,
            "entry_type": "long",
            "position_size": 10.0,
            "stop_loss": 95.0,
            "take_profit": 110.0,
        }
        config = {
            "open_position": position,
            "current_price": 110.0,
        }
        executor = ExitExecution(config)
        trade_result: TradeResult = {
            "trade_id": "TRD-HB-005",
            "entry_price": 100.0,
            "exit_price": 110.0,
            "position_size": 10.0,
            "entry_type": "long",
            "exit_reason": "Manual",
            "gross_pnl": 100.0,
            "pnl_percent": 10.0,
            "exit_time": "2025-01-01T11:00:00",
        }

        result = await executor._place_exit_order(trade_result)

        assert result is None
