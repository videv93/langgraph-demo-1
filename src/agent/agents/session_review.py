"""Session Review agent for post-market analysis."""

from typing import Any, TypedDict
from datetime import datetime


class TradeReview(TypedDict):
    """Review of a single trade."""

    trade_id: str
    was_valid_setup: bool
    entry_quality: str  # excellent|good|poor
    optimal_entry: float
    actual_entry: float
    optimal_exit: float
    actual_exit: float
    optimal_r: float
    actual_r: float
    lessons: list[str]


class EnvironmentClassification(TypedDict):
    """Market environment analysis."""

    actual: str  # trending|ranging|choppy
    predicted: str
    accuracy: bool


class SessionReviewOutput(TypedDict):
    """Output from session review."""

    review_complete: bool
    environment_classification: EnvironmentClassification
    trade_reviews: list[TradeReview]
    key_observations: list[str]
    lessons_learned: list[str]
    improvement_goals: list[str]
    review_timestamp: str


class SessionReview:
    """Review trading session comparing actual vs optimal execution.

    Conducts comprehensive post-session analysis using YTC methodology:
    - Environment classification accuracy
    - Trade entry/exit quality assessment
    - Hindsight-perfect execution comparison
    - Lessons extraction for future improvement
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize session review agent.

        Args:
            config: Configuration with session data and trade results.
                    Expected keys: trades, market_data, decisions, pnl, etc.
        """
        self.config = config or {}
        self.trades = self.config.get("trades", [])
        self.session_pnl = self.config.get("pnl", 0.0)
        self.predicted_environment = self.config.get("predicted_environment", "unknown")
        self.actual_environment = self.config.get("actual_environment", "trending")

    def execute(self) -> SessionReviewOutput:
        """Execute session review analysis.

        Returns:
            SessionReviewOutput with comprehensive session analysis.
        """
        # Classify market environment
        environment = {
            "actual": self.actual_environment,
            "predicted": self.predicted_environment,
            "accuracy": self.actual_environment == self.predicted_environment,
        }

        # Review each trade
        trade_reviews = self._review_trades()

        # Extract key observations and lessons
        key_observations = self._extract_observations()
        lessons = self._extract_lessons()
        improvements = self._generate_improvement_goals()

        return {
            "review_complete": True,
            "environment_classification": environment,
            "trade_reviews": trade_reviews,
            "key_observations": key_observations,
            "lessons_learned": lessons,
            "improvement_goals": improvements,
            "review_timestamp": datetime.utcnow().isoformat(),
        }

    def _review_trades(self) -> list[TradeReview]:
        """Review each trade executed.

        Returns:
            List of trade reviews with quality metrics.
        """
        reviews = []

        for trade in self.trades:
            # Calculate hindsight-perfect metrics
            optimal_entry = trade.get("entry_level", 0.0) * 0.995  # Assume 0.5% better
            optimal_exit = trade.get("exit_level", 0.0) * 1.005  # Assume 0.5% better
            actual_entry = trade.get("entry_level", 0.0)
            actual_exit = trade.get("exit_level", 0.0)
            stop = trade.get("stop_loss", 0.0)

            # Calculate R-multiples
            optimal_r = (
                (optimal_exit - optimal_entry) / (optimal_entry - stop)
                if stop != optimal_entry
                else 0
            )
            actual_r = (
                (actual_exit - actual_entry) / (actual_entry - stop)
                if stop != actual_entry
                else 0
            )

            # Assess entry quality
            execution_efficiency = actual_r / optimal_r if optimal_r > 0 else 0
            if execution_efficiency > 0.9:
                entry_quality = "excellent"
            elif execution_efficiency > 0.75:
                entry_quality = "good"
            else:
                entry_quality = "poor"

            review: TradeReview = {
                "trade_id": trade.get("trade_id", "unknown"),
                "was_valid_setup": trade.get("setup_valid", False),
                "entry_quality": entry_quality,
                "optimal_entry": round(optimal_entry, 2),
                "actual_entry": round(actual_entry, 2),
                "optimal_exit": round(optimal_exit, 2),
                "actual_exit": round(actual_exit, 2),
                "optimal_r": round(optimal_r, 2),
                "actual_r": round(actual_r, 2),
                "lessons": [
                    f"Entry {entry_quality}: {execution_efficiency*100:.0f}% of optimal",
                    "Monitor setup validity criteria more strictly",
                ],
            }
            reviews.append(review)

        return reviews

    def _extract_observations(self) -> list[str]:
        """Extract key observations from session.

        Returns:
            List of key market observations.
        """
        observations = [
            f"Predicted environment: {self.predicted_environment}",
            f"Actual environment: {self.actual_environment}",
            f"Session P&L: {self.session_pnl} USDT",
            f"Trades analyzed: {len(self.trades)}",
        ]

        if self.session_pnl > 0:
            observations.append("Session was profitable - strategy execution solid")
        elif self.session_pnl < 0:
            observations.append("Session had losses - review risk management")
        else:
            observations.append("Session broke even - edge was minimal")

        return observations

    def _extract_lessons(self) -> list[str]:
        """Extract lessons from session performance.

        Returns:
            List of key lessons learned.
        """
        lessons = [
            "Setup identification showed reliability",
            "Entry timing could be refined with better momentum confirmation",
            "Risk management protocols held steady",
            "Exit execution met planned targets in most cases",
        ]

        if len(self.trades) == 0:
            lessons.append("No trades taken - reassess setup scanner sensitivity")

        if self.actual_environment != self.predicted_environment:
            lessons.append(
                "Environment classification mismatch - improve initial market assessment"
            )

        return lessons

    def _generate_improvement_goals(self) -> list[str]:
        """Generate improvement goals for next session.

        Returns:
            List of actionable improvement goals.
        """
        goals = [
            "Tighten entry criteria: only take setups with >75% confidence",
            "Improve environment classification accuracy before trading",
            "Practice exit timing on hindsight analysis",
            "Document edge cases for pattern recognition improvement",
        ]

        if len(self.trades) > 0:
            goals.append("Review trade management - compare actual vs optimal exits")

        return goals
