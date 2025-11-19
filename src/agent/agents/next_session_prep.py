"""Next Session Preparation agent for goal setting and planning."""

from typing import Any, TypedDict
from datetime import datetime, timedelta


class GoalConfig(TypedDict):
    """Goals for next session."""

    process_goals: list[str]
    performance_targets: dict[str, Any]
    focus_areas: list[str]


class NextSessionConfig(TypedDict):
    """Configuration for next trading session."""

    date: str
    goals: GoalConfig
    strategy_updates: list[str]
    system_maintenance: list[str]


class NextSessionPrepOutput(TypedDict):
    """Output from next session preparation."""

    prep_complete: bool
    next_session_config: NextSessionConfig
    prep_timestamp: str


class NextSessionPrep:
    """Set goals and prepare for next trading session.

    Based on current performance and learning, prepares:
    - Process and performance goals
    - Strategy adjustments
    - System maintenance needs
    - Session checklists
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize next session prep agent.

        Args:
            config: Configuration with current session results and optimization.
                    Expected keys: win_rate, pnl, recommendations, etc.
        """
        self.config = config or {}
        self.win_rate = self.config.get("win_rate", 50.0)
        self.pnl = self.config.get("pnl", 0.0)
        self.recommendations = self.config.get("recommendations", [])
        self.improvement_goals = self.config.get("improvement_goals", [])

    def execute(self) -> NextSessionPrepOutput:
        """Execute next session preparation.

        Returns:
            NextSessionPrepOutput with session goals and configuration.
        """
        # Calculate next session date (next trading day)
        next_date = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")

        # Generate goals
        goals = self._generate_goals()

        # Generate strategy updates
        strategy_updates = self._generate_strategy_updates()

        # Generate maintenance checklist
        maintenance = self._generate_maintenance_checklist()

        config: NextSessionConfig = {
            "date": next_date,
            "goals": goals,
            "strategy_updates": strategy_updates,
            "system_maintenance": maintenance,
        }

        return {
            "prep_complete": True,
            "next_session_config": config,
            "prep_timestamp": datetime.utcnow().isoformat(),
        }

    def _generate_goals(self) -> GoalConfig:
        """Generate goals for next session.

        Returns:
            GoalConfig with process and performance targets.
        """
        process_goals = [
            "Execute only setups with >75% confidence",
            "Maintain position size discipline",
            "Exit at take-profit levels when hit",
            "Review each setup before entry",
            "Document all trade reasoning",
        ]

        # Adjust based on current performance
        if self.win_rate < 50:
            process_goals.insert(0, "Focus on setup validity - skip low-confidence setups")

        if self.pnl < 0:
            process_goals.insert(0, "Conservative session - max 2 trades, high quality only")

        performance_targets: dict[str, Any] = {
            "minimum_win_rate": 55.0,
            "target_avg_r": 1.5,
            "max_loss_per_trade": 100.0,
            "daily_loss_limit": 300.0,
            "profit_target": 200.0,
        }

        focus_areas = self.improvement_goals[:3] if self.improvement_goals else [
            "Pattern recognition accuracy",
            "Entry timing precision",
            "Risk management discipline",
        ]

        return {
            "process_goals": process_goals,
            "performance_targets": performance_targets,
            "focus_areas": focus_areas,
        }

    def _generate_strategy_updates(self) -> list[str]:
        """Generate strategy adjustments for next session.

        Returns:
            List of strategy updates to implement.
        """
        updates = [
            "Apply recommended parameter adjustments from optimization",
            "Use tighter stop losses per session learnings",
            "Implement momentum confirmation before entry",
        ]

        if self.win_rate > 65:
            updates.append("Scale up position size by 10% based on improved accuracy")

        if self.pnl > 500:
            updates.append("Consider taking more setups - edge is clear")

        if any("entry" in str(goal).lower() for goal in self.improvement_goals):
            updates.insert(0, "Practice entry timing on 2 historical charts before trading")

        return updates

    def _generate_maintenance_checklist(self) -> list[str]:
        """Generate system maintenance checklist.

        Returns:
            List of maintenance tasks for next session.
        """
        checklist = [
            "Verify data feed connectivity",
            "Check broker account status",
            "Confirm position sizing calculations",
            "Update market structure support/resistance levels",
            "Review economic calendar for upcoming events",
            "Clean up old log files",
            "Verify backup system access",
            "Test manual override procedures",
        ]

        return checklist
