#!/usr/bin/env python3
"""Query Pinecone for YTC trading strategy patterns and rules."""

import os
import json
from typing import Optional
from dotenv import load_dotenv
from pinecone import Pinecone

# Load environment variables
load_dotenv()


def initialize_pinecone() -> Pinecone:
    """Initialize Pinecone client with API key from environment.

    Returns:
        Pinecone client instance.

    Raises:
        ValueError: If PINECONE_API_KEY is not set.
    """
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        raise ValueError(
            "PINECONE_API_KEY not found in environment. "
            "Please set it in .env file or as environment variable."
        )

    return Pinecone(api_key=api_key)


def get_index_name() -> str:
    """Get Pinecone index name from environment or use default.

    Returns:
        Index name string.
    """
    return os.getenv("PINECONE_INDEX_NAME", "ytc-strategy-patterns")


def query_pattern(
    pattern_type: str,
    trend: str = "uptrend",
    top_k: int = 5,
    min_confidence: float = 0.7,
) -> list[dict]:
    """Query Pinecone for YTC strategy patterns.

    Args:
        pattern_type: Type of pattern (e.g., "3_swing_trap", "pullback", "breakout")
        trend: Market trend ("uptrend", "downtrend", "sideways")
        top_k: Number of results to return
        min_confidence: Minimum confidence score (0-1)

    Returns:
        List of pattern matches with metadata.
    """
    try:
        pc = initialize_pinecone()
        index_name = get_index_name()
        index = pc.Index(index_name)

        # Construct query metadata filter
        filter_dict = {
            "pattern_type": {"$eq": pattern_type},
            "trend": {"$eq": trend},
        }

        # Query the index
        results = index.query(
            vector=[0] * 1536,  # Placeholder vector (would be replaced with actual embedding)
            top_k=top_k,
            include_metadata=True,
            filter=filter_dict,
        )

        # Parse and format results
        patterns = []
        for match in results.get("matches", []):
            if match["score"] >= min_confidence:
                patterns.append(
                    {
                        "pattern_name": match["metadata"].get("pattern_name"),
                        "similarity_score": round(match["score"], 3),
                        "pattern_type": match["metadata"].get("pattern_type"),
                        "trend": match["metadata"].get("trend"),
                        "rules": match["metadata"].get("rules", []),
                        "entry_rules": match["metadata"].get("entry_rules", {}),
                        "stop_loss_pct": match["metadata"].get("stop_loss_pct"),
                        "profit_targets": match["metadata"].get("profit_targets", {}),
                        "historical_winrate": match["metadata"].get("historical_winrate"),
                        "avg_rrr": match["metadata"].get("avg_rrr"),
                        "min_score": match["metadata"].get("min_score"),
                        "confluence_factors": match["metadata"].get("confluence_factors", []),
                    }
                )

        return patterns

    except Exception as e:
        print(f"Error querying Pinecone: {e}")
        raise


def query_trend_rules(trend: str) -> dict:
    """Query structural rules for a specific trend.

    Args:
        trend: Market trend ("uptrend", "downtrend")

    Returns:
        Dictionary with trend-specific trading rules.
    """
    try:
        pc = initialize_pinecone()
        index_name = get_index_name()
        index = pc.Index(index_name)

        # Query for trend rules
        filter_dict = {
            "document_type": {"$eq": "trend_rules"},
            "trend": {"$eq": trend},
        }

        results = index.query(
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

        return {"trend": trend, "error": "No rules found"}

    except Exception as e:
        print(f"Error querying trend rules: {e}")
        raise


def query_fibonacci_strategy() -> dict:
    """Query Fibonacci retracement strategy from knowledge base.

    Returns:
        Dictionary with Fibonacci entry and exit strategy.
    """
    try:
        pc = initialize_pinecone()
        index_name = get_index_name()
        index = pc.Index(index_name)

        filter_dict = {"document_type": {"$eq": "fibonacci_strategy"}}

        results = index.query(
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
                "optimal_entry_levels": match["metadata"].get("optimal_entry_levels", []),
                "target_expansion_levels": match["metadata"].get("targets", []),
                "rules": match["metadata"].get("rules", []),
                "win_rate": match["metadata"].get("win_rate"),
            }

        return {"error": "Fibonacci strategy not found"}

    except Exception as e:
        print(f"Error querying Fibonacci strategy: {e}")
        raise


def list_all_patterns() -> list[dict]:
    """List all available patterns in the knowledge base.

    Returns:
        List of all available patterns with basic metadata.
    """
    try:
        pc = initialize_pinecone()
        index_name = get_index_name()
        index = pc.Index(index_name)

        # Get index stats
        stats = index.describe_index_stats()

        print(f"Index: {index_name}")
        print(f"Dimension: {stats.get('dimension')}")
        print(f"Total vectors: {stats.get('total_vector_count')}")
        print(f"Namespaces: {list(stats.get('namespaces', {}).keys())}")

        return stats

    except Exception as e:
        print(f"Error listing patterns: {e}")
        raise


if __name__ == "__main__":
    import sys

    # Example usage
    if len(sys.argv) < 2:
        print("YTC Strategy Pattern Query Tool")
        print("\nUsage:")
        print("  python query_ytc_strategy.py <command> [args]")
        print("\nCommands:")
        print("  pattern <type> [trend]     Query patterns by type (e.g., '3_swing_trap')")
        print("  trend <trend>              Query rules for a specific trend")
        print("  fibonacci                  Query Fibonacci retracement strategy")
        print("  list                       List all available patterns\n")
        print("Examples:")
        print("  python query_ytc_strategy.py pattern 3_swing_trap uptrend")
        print("  python query_ytc_strategy.py trend uptrend")
        print("  python query_ytc_strategy.py fibonacci")
        sys.exit(1)

    command = sys.argv[1]

    try:
        if command == "pattern":
            pattern_type = sys.argv[2] if len(sys.argv) > 2 else "pullback"
            trend = sys.argv[3] if len(sys.argv) > 3 else "uptrend"
            print(f"\nQuerying for {pattern_type} patterns in {trend}...\n")
            patterns = query_pattern(pattern_type, trend)
            print(json.dumps(patterns, indent=2))

        elif command == "trend":
            trend = sys.argv[2] if len(sys.argv) > 2 else "uptrend"
            print(f"\nQuerying rules for {trend}...\n")
            rules = query_trend_rules(trend)
            print(json.dumps(rules, indent=2))

        elif command == "fibonacci":
            print("\nQuerying Fibonacci retracement strategy...\n")
            strategy = query_fibonacci_strategy()
            print(json.dumps(strategy, indent=2))

        elif command == "list":
            print("\nListing all available patterns...\n")
            stats = list_all_patterns()
            print(json.dumps(stats, indent=2))

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
