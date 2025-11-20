"""YTC Trading Assistant using Pinecone Assistant and OpenAI-compatible interface."""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class YTCTradingAssistant:
    """Chat interface for YTC trading method using Pinecone Assistant.

    Provides access to YTC strategy knowledge through OpenAI-compatible API
    endpoint via Pinecone Assistant.

    Features:
    - Query YTC trading patterns and rules
    - Get strategy recommendations based on current market conditions
    - Retrieve entry/exit rules for specific setups
    - Access historical performance data
    """

    def __init__(self, use_openai_client: bool = True):
        """Initialize YTC Trading Assistant.

        Args:
            use_openai_client: Use OpenAI Python client (if False, use raw requests)
        """
        self.assistant_name = os.getenv("PINECONE_ASSISTANT_NAME", "ytc-trading-assistant")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")

        self.use_openai_client = use_openai_client
        self.client = None
        self.assistant_id = None

        if self.openai_api_key and use_openai_client:
            try:
                from openai import OpenAI
                # Initialize OpenAI client pointing to Pinecone Assistant endpoint
                self.client = OpenAI(
                    api_key=self.openai_api_key,
                    base_url=f"https://api.pinecone.io/v1",
                )
                logger.info(f"Connected to Pinecone Assistant: {self.assistant_name}")
            except ImportError:
                logger.warning("OpenAI client not available, install with: pip install openai")
                self.client = None
        else:
            logger.warning("OpenAI API key not found, assistant disabled")

    def query_ytc_method(
        self,
        question: str,
        market_context: Optional[dict] = None,
    ) -> str:
        """Query YTC trading method knowledge base.

        Args:
            question: Question about YTC trading method
            market_context: Optional current market data for context

        Returns:
            Response from the assistant with YTC trading guidance.
        """
        if not self.client:
            logger.error("Assistant client not initialized")
            return "Assistant not available. Please set OPENAI_API_KEY."

        try:
            # Build context message if market data provided
            context_msg = ""
            if market_context:
                context_msg = self._format_market_context(market_context)

            full_message = f"{context_msg}\n\n{question}" if context_msg else question

            # Query using chat completions (OpenAI-compatible interface)
            response = self.client.chat.completions.create(
                model=self.assistant_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in YTC (Your Trading Coach) trading methodology. "
                        "Provide accurate guidance based on YTC principles including "
                        "support/resistance analysis, swing point detection, and trade setup identification.",
                    },
                    {
                        "role": "user",
                        "content": full_message,
                    },
                ],
                temperature=0.3,  # Lower temperature for more consistent methodology adherence
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error querying assistant: {e}")
            return f"Error: Unable to process query - {str(e)}"

    def get_pattern_analysis(
        self,
        pattern_type: str,
        trend: str,
        price_data: dict,
    ) -> str:
        """Get analysis of a specific YTC pattern in current market conditions.

        Args:
            pattern_type: Type of pattern (3_swing_trap, pullback, breakout, etc.)
            trend: Current market trend (uptrend, downtrend, sideways)
            price_data: Dict with current_price, recent_high, recent_low, etc.

        Returns:
            Pattern analysis and trading recommendation.
        """
        question = (
            f"Analyze a {pattern_type} pattern in a {trend}. "
            f"Current price: ${price_data.get('current_price')}, "
            f"Recent high: ${price_data.get('recent_high')}, "
            f"Recent low: ${price_data.get('recent_low')}. "
            f"What are the YTC entry rules and recommended stop loss?"
        )

        return self.query_ytc_method(question, market_context=price_data)

    def get_entry_rules(
        self,
        setup_type: str,
        direction: str,
    ) -> str:
        """Get detailed entry rules for a specific YTC setup.

        Args:
            setup_type: Type of setup (pullback, 3-swing-trap, etc.)
            direction: Trade direction (long, short)

        Returns:
            Entry rules specific to the setup and direction.
        """
        question = (
            f"What are the precise YTC entry rules for a {direction} "
            f"{setup_type} setup? Include entry triggers, entry zones, "
            f"and key levels to monitor."
        )

        return self.query_ytc_method(question)

    def get_fibonacci_strategy(self) -> str:
        """Get Fibonacci retracement strategy from YTC methodology.

        Returns:
            Detailed Fibonacci strategy including levels and entry points.
        """
        question = (
            "Explain the YTC approach to Fibonacci retracements for entry. "
            "What levels are most important (38.2%, 50%, 61.8%)? "
            "How do we use them in different market structures?"
        )

        return self.query_ytc_method(question)

    def get_stop_loss_guidance(
        self,
        setup_type: str,
        entry_price: float,
        structure: dict,
    ) -> str:
        """Get YTC-specific stop loss placement guidance.

        Args:
            setup_type: Type of trading setup
            entry_price: Planned entry price
            structure: Market structure data (support, resistance levels)

        Returns:
            Stop loss placement recommendation based on YTC methodology.
        """
        question = (
            f"For a {setup_type} entry at ${entry_price}, "
            f"where should I place my stop loss according to YTC principles? "
            f"Structure has support at ${structure.get('support')} "
            f"and resistance at ${structure.get('resistance')}."
        )

        return self.query_ytc_method(question, market_context=structure)

    def get_risk_management_rules(self) -> str:
        """Get YTC risk management and position sizing rules.

        Returns:
            Risk management guidelines including position sizing and R:R ratios.
        """
        question = (
            "What are the core YTC risk management rules? "
            "How do we determine position size based on stop loss distance? "
            "What are ideal risk-to-reward ratios?"
        )

        return self.query_ytc_method(question)

    def validate_setup(
        self,
        setup_data: dict,
    ) -> dict:
        """Validate a trading setup against YTC rules.

        Args:
            setup_data: Dictionary with setup details
              - pattern_type: str
              - trend: str
              - entry_price: float
              - stop_loss: float
              - targets: list[float]
              - supporting_factors: list[str]

        Returns:
            Validation result with confidence score and recommendations.
        """
        context_str = self._format_setup_data(setup_data)
        question = (
            f"Validate this trading setup against YTC principles: {context_str} "
            f"Is this a high-probability setup? What score (0-100) would you give it? "
            f"What improvements could be made?"
        )

        response = self.query_ytc_method(question, market_context=setup_data)

        return {
            "analysis": response,
            "validated": self._extract_validation_score(response) >= 70,
            "recommendations": response,
        }

    def _format_market_context(self, context: dict) -> str:
        """Format market context for the query.

        Args:
            context: Market context dictionary

        Returns:
            Formatted string for inclusion in query.
        """
        parts = ["Current Market Context:"]

        if "trend" in context:
            parts.append(f"- Trend: {context['trend']}")

        if "current_price" in context:
            parts.append(f"- Current Price: ${context['current_price']}")

        if "recent_high" in context and "recent_low" in context:
            parts.append(
                f"- Recent Range: ${context['recent_low']} - ${context['recent_high']}"
            )

        if "volatility" in context:
            parts.append(f"- Volatility: {context['volatility']}")

        if "confluence_factors" in context:
            factors = ", ".join(context["confluence_factors"])
            parts.append(f"- Confluence Factors: {factors}")

        return "\n".join(parts)

    def _format_setup_data(self, setup: dict) -> str:
        """Format setup data for validation query.

        Args:
            setup: Setup dictionary

        Returns:
            Formatted setup description.
        """
        parts = []

        if "pattern_type" in setup:
            parts.append(f"Pattern: {setup['pattern_type']}")

        if "trend" in setup:
            parts.append(f"Trend: {setup['trend']}")

        if "entry_price" in setup:
            parts.append(f"Entry: ${setup['entry_price']}")

        if "stop_loss" in setup:
            parts.append(f"Stop Loss: ${setup['stop_loss']}")

        if "targets" in setup:
            targets = ", ".join(f"${t}" for t in setup["targets"])
            parts.append(f"Targets: {targets}")

        if "supporting_factors" in setup:
            factors = ", ".join(setup["supporting_factors"])
            parts.append(f"Supporting Factors: {factors}")

        return " | ".join(parts)

    def _extract_validation_score(self, response: str) -> int:
        """Extract validation score from assistant response.

        Args:
            response: Response text from assistant

        Returns:
            Extracted score (0-100) or 50 as default.
        """
        import re

        # Look for patterns like "score of 75" or "75/100"
        match = re.search(r"(\d{1,3})\s*(?:/100|%|score)", response, re.IGNORECASE)
        if match:
            score = int(match.group(1))
            return min(100, max(0, score))

        # Default to 50 if no score found
        return 50
