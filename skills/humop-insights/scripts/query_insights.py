#!/usr/bin/env python3
"""Query HUMOP lakehouse gold layer for user insights."""

import argparse
import json
import os
import sys

LAKEHOUSE_HOST = os.environ.get("HUMOP_LAKEHOUSE_HOST", "localhost")
SPARK_THRIFT_PORT = os.environ.get("HUMOP_SPARK_THRIFT_PORT", "10000")
USER_ID = os.environ.get("HUMOP_USER_ID", "default")

# Queries against the Iceberg gold layer
QUERIES = {
    "kessandra-context": """
        SELECT context_json, context_summary, priority_insights,
               suggested_topics, avoid_topics, recommended_mode
        FROM iceberg.gold.kessandra_context
        WHERE user_id = '{user_id}'
        ORDER BY computed_at DESC
        LIMIT 1
    """,
    "domain-scores": """
        SELECT domain, current_score, score_7d_avg, score_30d_avg,
               trend_direction, trend_magnitude, days_since_update, needs_attention
        FROM iceberg.gold.user_domain_scores
        WHERE user_id = '{user_id}'
        {domain_filter}
        ORDER BY needs_attention DESC, current_score ASC
    """,
    "patterns": """
        SELECT pattern_type, description, confidence, actionable, recommended_action
        FROM iceberg.gold.user_patterns
        WHERE user_id = '{user_id}'
        AND confidence >= {min_confidence}
        ORDER BY confidence DESC
    """,
    "goal-effectiveness": """
        SELECT completion_rate_overall, completion_rate_by_domain,
               avg_goals_per_day, optimal_goal_count, common_stuck_types,
               stuck_recovery_rate, best_completion_time, deferral_rate
        FROM iceberg.gold.goal_effectiveness
        WHERE user_id = '{user_id}'
        ORDER BY computed_at DESC
        LIMIT 1
    """,
    "engagement": """
        SELECT preferred_check_in_time, avg_session_duration,
               preferred_interaction_mode, response_rate,
               best_response_days, worst_response_days,
               streak_sensitivity, overwhelm_indicators
        FROM iceberg.gold.user_engagement_profile
        WHERE user_id = '{user_id}'
        ORDER BY computed_at DESC
        LIMIT 1
    """,
    "trend": """
        SELECT recorded_at, score, previous_score, score_delta
        FROM iceberg.silver.domain_health
        WHERE user_id = '{user_id}'
        AND domain = '{domain}'
        AND recorded_at >= current_timestamp - INTERVAL '{days}' DAY
        ORDER BY recorded_at ASC
    """,
    "correlations": """
        SELECT p.description, p.confidence, p.supporting_data
        FROM iceberg.gold.user_patterns p
        WHERE p.user_id = '{user_id}'
        AND p.pattern_type = 'domain_correlation'
        AND p.confidence >= 0.6
        ORDER BY p.confidence DESC
    """,
}


def execute_query(query: str) -> list[dict]:
    """Execute a query against the Spark Thrift Server via PyHive."""
    try:
        from pyhive import hive

        conn = hive.connect(
            host=LAKEHOUSE_HOST,
            port=int(SPARK_THRIFT_PORT),
            username="humop",
        )
        cursor = conn.cursor()
        cursor.execute(query)

        columns = [desc[0] for desc in cursor.description]
        rows = []
        for row in cursor.fetchall():
            rows.append(dict(zip(columns, row)))

        cursor.close()
        conn.close()
        return rows

    except ImportError:
        print(
            "pyhive not installed. Install with: pip install pyhive[hive]",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as e:
        print(f"Query failed: {e}", file=sys.stderr)
        # Fall back to reading from local cache
        return read_local_cache(query)


def read_local_cache(query: str) -> list[dict]:
    """Read from local JSON cache if lakehouse is unavailable."""
    from pathlib import Path

    cache_dir = Path.home() / ".humop" / "insights_cache"
    if not cache_dir.exists():
        print("No local cache available.", file=sys.stderr)
        return []

    # Find most recent cache file
    files = sorted(cache_dir.glob("*.json"), reverse=True)
    if not files:
        return []

    data = json.loads(files[0].read_text())
    print(f"Using cached insights from {files[0].name}", file=sys.stderr)
    return data if isinstance(data, list) else [data]


def main():
    parser = argparse.ArgumentParser(description="Query HUMOP lakehouse insights")
    parser.add_argument(
        "--query",
        required=True,
        choices=list(QUERIES.keys()),
        help="Query type",
    )
    parser.add_argument("--domain", default=None, help="Filter by domain")
    parser.add_argument("--days", default="30", help="Lookback period in days")
    parser.add_argument(
        "--min-confidence", default="0.5", help="Minimum pattern confidence"
    )
    parser.add_argument("--format", default="json", choices=["json", "text"])
    args = parser.parse_args()

    query_template = QUERIES[args.query]

    domain_filter = f"AND domain = '{args.domain}'" if args.domain else ""

    query = query_template.format(
        user_id=USER_ID,
        domain=args.domain or "",
        domain_filter=domain_filter,
        days=args.days,
        min_confidence=args.min_confidence,
    )

    results = execute_query(query.strip())

    if args.format == "json":
        print(json.dumps(results, indent=2, default=str))
    else:
        if not results:
            print("No data available.")
            return
        for row in results:
            for key, value in row.items():
                print(f"  {key}: {value}")
            print()


if __name__ == "__main__":
    main()
