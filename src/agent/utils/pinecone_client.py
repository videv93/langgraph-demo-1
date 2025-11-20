"""Pinecone client for querying YTC strategy patterns and rules."""

import os
from typing import Optional
import logging
from dotenv import load_dotenv
from pinecone import Pinecone

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class PineconeStrategyClient:
    """Client for querying YTC trading strategy patterns from Pinecone.

    Handles:
    - Pattern matching (3-swing trap, pullback, breakout, etc.)
    - Trend-specific rules and requirements
    - Fibonacci retracement strategies
    - Entry/exit rule validation
    """

    def __init__(self):
        """Initialize Pinecone client with environment variables."""
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "ytc-strategy-patterns")
        self.environment = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")

        if not self.api_key:
            logger.warning("PINECONE_API_KEY not found in environment variables")
            self.client = None
            self.index = None
        else:
            try:
                self.client = Pinecone(api_key=self.api_key)
                self.index = self.client.Index(self.index_name)
                logger.info(f"Connected to Pinecone index: {self.index_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Pinecone: {e}")
                self.client = None
                self.index = None

    def is_connected(self) -> bool:
        """Check if Pinecone client is connected.

        Returns:
            True if connected, False otherwise.
        """
        return self.client is not None and self.index is not None

    def query_patterns(
        self,
        pattern_type: str,
        trend: str = "uptrend",
        top_k: int = 5,
        min_confidence: float = 0.7,
    ) -> list[dict]:
        """Query Pinecone for strategy patterns.

        Args:
            pattern_type: Type of pattern (3_swing_trap, pullback, breakout, etc.)
            trend: Market trend (uptrend, downtrend, sideways)
            top_k: Number of results to return
            min_confidence: Minimum confidence score threshold

        Returns:
            List of matching patterns with metadata.
        """
        if not self.is_connected():
            logger.warning("Pinecone not connected, returning empty patterns")
            return []

        try:
            # Query with metadata filter
            filter_dict = {
                "pattern_type": {"$eq": pattern_type},
                "trend": {"$eq": trend},
            }

            # Use placeholder vector (would be replaced with actual embeddings)
            results = self.index.query(
                vector=[0] * 1536,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict,
            )

            patterns = []
            for match in results.get("matches", []):
                if match["score"] >= min_confidence:
                    patterns.append({
                        "pattern_id": match.get("id"),
                        "pattern_name": match["metadata"].get("pattern_name"),
                        "similarity": round(match["score"], 3),
                        "pattern_type": match["metadata"].get("pattern_type"),
                        "trend": match["metadata"].get("trend"),
                        "rules": match["metadata"].get("rules", []),
                        "entry_rules": match["metadata"].get("entry_rules", {}),
                        "stop_loss_pct": match["metadata"].get("stop_loss_pct"),
                        "targets": match["metadata"].get("targets", {}),
                        "winrate": match["metadata"].get("winrate"),
                        "avg_rrr": match["metadata"].get("avg_rrr"),
                        "min_score": match["metadata"].get("min_score"),
                        "confluence": match["metadata"].get("confluence_factors", []),
                    })

            logger.info(f"Found {len(patterns)} matching patterns for {pattern_type}")
            return patterns

        except Exception as e:
            logger.error(f"Error querying patterns: {e}")
            return []

    def get_trend_rules(self, trend: str) -> dict:
        """Get structural rules for a specific trend.

        Args:
            trend: Market trend (uptrend, downtrend)

        Returns:
            Dictionary with trend-specific rules and requirements.
        """
        if not self.is_connected():
            logger.warning("Pinecone not connected, returning empty rules")
            return {}

        try:
            filter_dict = {
                "document_type": {"$eq": "trend_rules"},
                "trend": {"$eq": trend},
            }

            results = self.index.query(
                vector=[0] * 1536,
                top_k=1,
                include_metadata=True,
                filter=filter_dict,
            )

            if results.get("matches"):
                match = results["matches"][0]
                return {
                    "trend": trend,
                    "rules": match["metadata"].get("rules", []),
                    "structural_requirements": match["metadata"].get("requirements", []),
                    "forbidden_actions": match["metadata"].get("forbidden_actions", []),
                    "ideal_conditions": match["metadata"].get("ideal_conditions", []),
                }

            logger.warning(f"No rules found for trend: {trend}")
            return {"trend": trend, "rules": []}

        except Exception as e:
            logger.error(f"Error getting trend rules: {e}")
            return {}

    def get_fibonacci_strategy(self) -> dict:
        """Get Fibonacci retracement entry/exit strategy.

        Returns:
            Dictionary with Fibonacci strategy details.
        """
        if not self.is_connected():
            logger.warning("Pinecone not connected, returning empty strategy")
            return {}

        try:
            filter_dict = {"document_type": {"$eq": "fibonacci_strategy"}}

            results = self.index.query(
                vector=[0] * 1536,
                top_k=1,
                include_metadata=True,
                filter=filter_dict,
            )

            if results.get("matches"):
                match = results["matches"][0]
                return {
                    "strategy_name": match["metadata"].get("strategy_name"),
                    "retracement_levels": match["metadata"].get("retracement_levels", {}),
                    "optimal_entries": match["metadata"].get("optimal_entry_levels", []),
                    "targets": match["metadata"].get("targets", []),
                    "rules": match["metadata"].get("rules", []),
                    "winrate": match["metadata"].get("win_rate"),
                }

            logger.warning("Fibonacci strategy not found")
            return {}

        except Exception as e:
            logger.error(f"Error getting Fibonacci strategy: {e}")
            return {}

    def validate_setup(self, setup_data: dict) -> dict:
        """Validate a trading setup against known patterns and rules.

        Args:
            setup_data: Setup data containing pattern_type, trend, price_levels, etc.

        Returns:
            Validation result with matching patterns and confidence.
        """
        if not self.is_connected():
            logger.warning("Pinecone not connected, skipping validation")
            return {"validated": False, "reason": "Pinecone not connected"}

        try:
            pattern_type = setup_data.get("pattern_type", "pullback")
            trend = setup_data.get("trend", "uptrend")

            patterns = self.query_patterns(pattern_type, trend, top_k=3)
            rules = self.get_trend_rules(trend)

            if not patterns:
                return {"validated": False, "reason": "No matching patterns found"}

            # Validate against rules
            setup_score = sum(p["similarity"] for p in patterns) / len(patterns) if patterns else 0

            return {
                "validated": setup_score >= 0.7,
                "confidence_score": round(setup_score, 3),
                "matching_patterns": len(patterns),
                "best_pattern": patterns[0] if patterns else None,
                "trend_rules": rules,
            }

        except Exception as e:
            logger.error(f"Error validating setup: {e}")
            return {"validated": False, "reason": str(e)}

    def get_index_stats(self) -> dict:
        """Get Pinecone index statistics.

        Returns:
            Index statistics including dimension and total vectors.
        """
        if not self.is_connected():
            return {}

        try:
            stats = self.index.describe_index_stats()
            return {
                "index_name": self.index_name,
                "dimension": stats.get("dimension"),
                "total_vectors": stats.get("total_vector_count"),
                "namespaces": list(stats.get("namespaces", {}).keys()),
            }

        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {}
