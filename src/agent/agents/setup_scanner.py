"""Setup scanner agent for identifying trading setups and entry points."""

from enum import Enum
from typing import Any, TypedDict


class SetupType(str, Enum):
    """Types of trading setups."""

    BREAKOUT = "breakout"
    PULLBACK = "pullback"
    REVERSAL = "reversal"
    MOMENTUM = "momentum"
    NONE = "none"


class PriceLevel(TypedDict):
    """Price level for entry/stop."""

    level: float
    description: str


class TradingSetup(TypedDict):
    """Complete trading setup with entry and exit levels."""

    setup_type: SetupType
    setup_found: bool
    entry_level: float
    stop_loss_level: float
    take_profit_level: float
    risk_reward_ratio: float
    setup_confidence: float  # 0-100
    entry_strategy: str


class SetupScannerOutput(TypedDict):
    """Output from setup scanning."""

    scan_complete: bool
    setups_found: list[TradingSetup]
    best_setup: TradingSetup | None
    total_setups: int
    scan_timestamp: str


class SetupScanner:
    """Scan for trading setups based on technical analysis.

    Identifies:
    - Breakout setups (price breaking resistance/support)
    - Pullback setups (retracement to support in uptrend)
    - Reversal setups (divergence + price action)
    - Momentum setups (strong RSI + trend alignment)
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the setup scanner agent.

        Args:
            config: Configuration with market data and analysis results.
                    Expected keys: current_price, support, resistance, trend,
                                   trend_strength, momentum, rsi, etc.
        """
        self.config = config or {}
        self.current_price = self.config.get("current_price", 100.0)
        self.support = self.config.get("support", 95.0)
        self.resistance = self.config.get("resistance", 110.0)
        self.trend = self.config.get("trend", "uptrend")
        self.trend_strength = self.config.get("trend_strength", "strong")
        self.momentum = self.config.get("momentum", "strong_up")
        self.rsi = self.config.get("rsi", 70.0)
        self.entry_bias = self.config.get("entry_bias", "neutral")
        self.trading_probability = self.config.get("trading_probability", 75.0)

    def execute(self) -> SetupScannerOutput:
        """Execute setup scanning.

        Returns:
            SetupScannerOutput with identified trading setups.
        """
        from datetime import datetime

        setups = []

        # Scan for different setup types
        breakout_setup = self._scan_breakout()
        if breakout_setup["setup_found"]:
            setups.append(breakout_setup)

        pullback_setup = self._scan_pullback()
        if pullback_setup["setup_found"]:
            setups.append(pullback_setup)

        reversal_setup = self._scan_reversal()
        if reversal_setup["setup_found"]:
            setups.append(reversal_setup)

        momentum_setup = self._scan_momentum()
        if momentum_setup["setup_found"]:
            setups.append(momentum_setup)

        # Sort by confidence
        setups.sort(key=lambda x: x["setup_confidence"], reverse=True)

        best_setup = setups[0] if setups else None

        return {
            "scan_complete": True,
            "setups_found": setups,
            "best_setup": best_setup,
            "total_setups": len(setups),
            "scan_timestamp": datetime.utcnow().isoformat(),
        }

    def _scan_breakout(self) -> TradingSetup:
        """Scan for breakout setups.

        Returns:
            TradingSetup if breakout setup found, else no setup.
        """
        # Breakout: price near resistance in uptrend, or near support in downtrend
        if self.trend == "uptrend" and self.trend_strength in ["strong", "moderate"]:
            distance_to_resistance = (self.resistance - self.current_price) / self.current_price * 100

            # Entry within 1% of resistance
            if 0 < distance_to_resistance <= 1.0:
                entry = self.resistance * 1.001  # Breakout above resistance
                stop = self.support
                profit = self.resistance + (self.resistance - self.support)
                risk_reward = (profit - entry) / (entry - stop) if entry != stop else 0

                return {
                    "setup_type": SetupType.BREAKOUT,
                    "setup_found": True,
                    "entry_level": round(entry, 2),
                    "stop_loss_level": round(stop, 2),
                    "take_profit_level": round(profit, 2),
                    "risk_reward_ratio": round(risk_reward, 2),
                    "setup_confidence": min(85.0, self.trading_probability + 15),
                    "entry_strategy": "Buy breakout above resistance with stop below support",
                }

        if self.trend == "downtrend" and self.trend_strength in ["strong", "moderate"]:
            distance_to_support = (self.current_price - self.support) / self.current_price * 100

            if 0 < distance_to_support <= 1.0:
                entry = self.support * 0.999  # Breakout below support
                stop = self.resistance
                profit = self.support - (self.resistance - self.support)
                risk_reward = (entry - profit) / (stop - entry) if stop != entry else 0

                return {
                    "setup_type": SetupType.BREAKOUT,
                    "setup_found": True,
                    "entry_level": round(entry, 2),
                    "stop_loss_level": round(stop, 2),
                    "take_profit_level": round(profit, 2),
                    "risk_reward_ratio": round(risk_reward, 2),
                    "setup_confidence": min(85.0, self.trading_probability + 15),
                    "entry_strategy": "Sell breakout below support with stop above resistance",
                }

        return self._no_setup(SetupType.BREAKOUT)

    def _scan_pullback(self) -> TradingSetup:
        """Scan for pullback setups (retracement to support/resistance).

        Returns:
            TradingSetup if pullback setup found, else no setup.
        """
        # Pullback: price near support in uptrend (buying opportunity)
        if (
            self.trend == "uptrend"
            and self.trend_strength in ["strong", "moderate"]
            and self.momentum in ["moderate_up", "weak"]
        ):
            distance_to_support = (self.current_price - self.support) / self.current_price * 100

            if 0 < distance_to_support <= 1.5:
                entry = self.support * 1.001
                stop = self.support * 0.99
                profit = self.resistance

                risk_reward = (profit - entry) / (entry - stop) if entry != stop else 0

                return {
                    "setup_type": SetupType.PULLBACK,
                    "setup_found": True,
                    "entry_level": round(entry, 2),
                    "stop_loss_level": round(stop, 2),
                    "take_profit_level": round(profit, 2),
                    "risk_reward_ratio": round(risk_reward, 2),
                    "setup_confidence": min(80.0, self.trading_probability + 10),
                    "entry_strategy": "Buy pullback to support in uptrend",
                }

        # Pullback in downtrend (selling opportunity)
        if (
            self.trend == "downtrend"
            and self.trend_strength in ["strong", "moderate"]
            and self.momentum in ["moderate_down", "weak"]
        ):
            distance_to_resistance = (self.resistance - self.current_price) / self.current_price * 100

            if 0 < distance_to_resistance <= 1.5:
                entry = self.resistance * 0.999
                stop = self.resistance * 1.01
                profit = self.support

                risk_reward = (entry - profit) / (stop - entry) if stop != entry else 0

                return {
                    "setup_type": SetupType.PULLBACK,
                    "setup_found": True,
                    "entry_level": round(entry, 2),
                    "stop_loss_level": round(stop, 2),
                    "take_profit_level": round(profit, 2),
                    "risk_reward_ratio": round(risk_reward, 2),
                    "setup_confidence": min(80.0, self.trading_probability + 10),
                    "entry_strategy": "Sell pullback to resistance in downtrend",
                }

        return self._no_setup(SetupType.PULLBACK)

    def _scan_reversal(self) -> TradingSetup:
        """Scan for reversal setups (divergence + price action).

        Returns:
            TradingSetup if reversal setup found, else no setup.
        """
        # Reversal setups require divergence in market data (not in config here)
        # Placeholder: would need divergence_detected from config
        divergence = self.config.get("divergence_detected", False)
        divergence_type = self.config.get("divergence_type", "none")

        if divergence and divergence_type == "bullish" and self.trend == "downtrend":
            entry = self.current_price
            stop = self.support * 0.98
            profit = self.resistance

            risk_reward = (profit - entry) / (entry - stop) if entry != stop else 0

            return {
                "setup_type": SetupType.REVERSAL,
                "setup_found": True,
                "entry_level": round(entry, 2),
                "stop_loss_level": round(stop, 2),
                "take_profit_level": round(profit, 2),
                "risk_reward_ratio": round(risk_reward, 2),
                "setup_confidence": 75.0,
                "entry_strategy": "Buy on bullish divergence reversal signal",
            }

        if divergence and divergence_type == "bearish" and self.trend == "uptrend":
            entry = self.current_price
            stop = self.resistance * 1.02
            profit = self.support

            risk_reward = (entry - profit) / (stop - entry) if stop != entry else 0

            return {
                "setup_type": SetupType.REVERSAL,
                "setup_found": True,
                "entry_level": round(entry, 2),
                "stop_loss_level": round(stop, 2),
                "take_profit_level": round(profit, 2),
                "risk_reward_ratio": round(risk_reward, 2),
                "setup_confidence": 75.0,
                "entry_strategy": "Sell on bearish divergence reversal signal",
            }

        return self._no_setup(SetupType.REVERSAL)

    def _scan_momentum(self) -> TradingSetup:
        """Scan for momentum setups (strong momentum aligned with trend).

        Returns:
            TradingSetup if momentum setup found, else no setup.
        """
        # Momentum setup: strong upside momentum in uptrend
        if (
            self.trend == "uptrend"
            and self.momentum == "strong_up"
            and self.rsi > 60
        ):
            entry = self.current_price
            stop = self.support
            profit = self.resistance + (self.resistance - self.support) * 0.5

            risk_reward = (profit - entry) / (entry - stop) if entry != stop else 0

            return {
                "setup_type": SetupType.MOMENTUM,
                "setup_found": True,
                "entry_level": round(entry, 2),
                "stop_loss_level": round(stop, 2),
                "take_profit_level": round(profit, 2),
                "risk_reward_ratio": round(risk_reward, 2),
                "setup_confidence": min(90.0, self.trading_probability + 20),
                "entry_strategy": "Long momentum trade in strong uptrend",
            }

        # Momentum setup: strong downside momentum in downtrend
        if (
            self.trend == "downtrend"
            and self.momentum == "strong_down"
            and self.rsi < 40
        ):
            entry = self.current_price
            stop = self.resistance
            profit = self.support - (self.resistance - self.support) * 0.5

            risk_reward = (entry - profit) / (stop - entry) if stop != entry else 0

            return {
                "setup_type": SetupType.MOMENTUM,
                "setup_found": True,
                "entry_level": round(entry, 2),
                "stop_loss_level": round(stop, 2),
                "take_profit_level": round(profit, 2),
                "risk_reward_ratio": round(risk_reward, 2),
                "setup_confidence": min(90.0, self.trading_probability + 20),
                "entry_strategy": "Short momentum trade in strong downtrend",
            }

        return self._no_setup(SetupType.MOMENTUM)

    def _no_setup(self, setup_type: SetupType) -> TradingSetup:
        """Return no setup found template.

        Args:
            setup_type: Type of setup that wasn't found.

        Returns:
            TradingSetup with setup_found = False.
        """
        return {
            "setup_type": setup_type,
            "setup_found": False,
            "entry_level": 0.0,
            "stop_loss_level": 0.0,
            "take_profit_level": 0.0,
            "risk_reward_ratio": 0.0,
            "setup_confidence": 0.0,
            "entry_strategy": "",
        }
