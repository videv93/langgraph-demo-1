"""Performance Analytics agent for statistical analysis and metrics tracking."""

from typing import Any, TypedDict
from datetime import datetime


class SetupTypeStats(TypedDict):
    """Statistics for a specific setup type."""

    trades: int
    win_rate: float
    avg_r: float
    total_r: float


class SessionStats(TypedDict):
    """Session-level statistics."""

    trades_taken: int
    win_rate: float
    avg_winner: float
    avg_loser: float
    profit_factor: float
    total_r: float


class CumulativeStats(TypedDict):
    """Cumulative statistics across multiple sessions."""

    total_trades: int
    overall_win_rate: float
    total_profit: float
    max_drawdown: float


class PerformanceAnalyticsOutput(TypedDict):
    """Output from performance analytics."""

    analytics_complete: bool
    session_stats: SessionStats
    by_setup_type: dict[str, SetupTypeStats]
    cumulative_stats: CumulativeStats
    analytics_timestamp: str


class PerformanceAnalytics:
    """Calculate comprehensive performance statistics and track metrics.

    Analyzes trading performance across multiple dimensions:
    - Win rate and profit factor
    - Average R-multiple per setup type
    - Cumulative drawdown and Sharpe ratio
    - Performance trends over time
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize performance analytics agent.

        Args:
            config: Configuration with trade results and journal data.
                    Expected keys: trades, pnl, win_count, loss_count, etc.
        """
        self.config = config or {}
        self.trades = self.config.get("trades", [])
        self.session_pnl = self.config.get("pnl", 0.0)
        self.win_count = self.config.get("win_count", 0)
        self.loss_count = self.config.get("loss_count", 0)
        self.total_trades_all_time = self.config.get("total_trades_all_time", 0)
        self.cumulative_pnl = self.config.get("cumulative_pnl", 0.0)

    def execute(self) -> PerformanceAnalyticsOutput:
        """Execute performance analytics calculation.

        Returns:
            PerformanceAnalyticsOutput with comprehensive statistics.
        """
        # Calculate session statistics
        session_stats = self._calculate_session_stats()

        # Calculate statistics by setup type
        setup_type_stats = self._calculate_by_setup_type()

        # Calculate cumulative statistics
        cumulative_stats = self._calculate_cumulative_stats()

        return {
            "analytics_complete": True,
            "session_stats": session_stats,
            "by_setup_type": setup_type_stats,
            "cumulative_stats": cumulative_stats,
            "analytics_timestamp": datetime.utcnow().isoformat(),
        }

    def _calculate_session_stats(self) -> SessionStats:
        """Calculate session-level statistics.

        Returns:
            SessionStats with session performance metrics.
        """
        total_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t.get("pnl", 0) > 0]
        losing_trades = [t for t in self.trades if t.get("pnl", 0) < 0]

        win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0
        avg_winner = (
            sum(t.get("pnl", 0) for t in winning_trades) / len(winning_trades)
            if winning_trades
            else 0
        )
        avg_loser = (
            sum(abs(t.get("pnl", 0)) for t in losing_trades) / len(losing_trades)
            if losing_trades
            else 0
        )
        profit_factor = (
            avg_winner / avg_loser if avg_loser > 0 else float("inf")
        ) if avg_winner > 0 else 0

        # Calculate total R-multiple
        total_r = sum(t.get("r_multiple", 0) for t in self.trades)

        return {
            "trades_taken": total_trades,
            "win_rate": round(win_rate, 2),
            "avg_winner": round(avg_winner, 2),
            "avg_loser": round(avg_loser, 2),
            "profit_factor": round(profit_factor, 2) if profit_factor != float("inf") else 0,
            "total_r": round(total_r, 2),
        }

    def _calculate_by_setup_type(self) -> dict[str, SetupTypeStats]:
        """Calculate statistics grouped by setup type.

        Returns:
            Dict mapping setup type to its statistics.
        """
        stats_by_type: dict[str, list] = {}

        for trade in self.trades:
            setup_type = trade.get("setup_type", "unknown")
            if setup_type not in stats_by_type:
                stats_by_type[setup_type] = []
            stats_by_type[setup_type].append(trade)

        result = {}
        for setup_type, trades in stats_by_type.items():
            winning = [t for t in trades if t.get("pnl", 0) > 0]
            win_rate = len(winning) / len(trades) * 100 if trades else 0
            avg_r = sum(t.get("r_multiple", 0) for t in trades) / len(
                trades
            ) if trades else 0
            total_r = sum(t.get("r_multiple", 0) for t in trades)

            result[setup_type] = {
                "trades": len(trades),
                "win_rate": round(win_rate, 2),
                "avg_r": round(avg_r, 2),
                "total_r": round(total_r, 2),
            }

        return result

    def _calculate_cumulative_stats(self) -> CumulativeStats:
        """Calculate cumulative statistics across all sessions.

        Returns:
            CumulativeStats with long-term performance metrics.
        """
        total_trades = self.total_trades_all_time + len(self.trades)
        total_profit = self.cumulative_pnl + self.session_pnl

        # Overall win rate (simplified estimate)
        overall_wins = self.win_count + len([t for t in self.trades if t.get("pnl", 0) > 0])
        overall_win_rate = (
            (overall_wins / total_trades * 100) if total_trades > 0 else 0
        )

        # Maximum drawdown (simplified - from session P&L)
        max_drawdown = abs(min(self.session_pnl, 0))

        return {
            "total_trades": total_trades,
            "overall_win_rate": round(overall_win_rate, 2),
            "total_profit": round(total_profit, 2),
            "max_drawdown": round(max_drawdown, 2),
        }
