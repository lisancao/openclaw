---
name: humop-insights
description: Query the HUMOP lakehouse gold layer for user analytics and Kessandra context. Use when the user asks about their patterns, trends, domain health scores, goal effectiveness, or when you need personalized context to give better advice.
metadata:
  {
    "openclaw":
      {
        "emoji": "🔮",
        "requires": { "bins": ["python3"], "env": ["HUMOP_LAKEHOUSE_HOST"] },
        "primaryEnv": "HUMOP_LAKEHOUSE_HOST",
      },
  }
---

# HUMOP Insights (Lakehouse Gold Layer)

Query the HUMOP analytics pipeline for user insights. Data flows from user interactions through Kafka -> Spark -> Iceberg tables in a Bronze/Silver/Gold medallion architecture. This skill reads from the Gold layer.

## Available queries

### Full Kessandra context

Get the pre-computed context blob with all insights. Use this at the start of sessions to personalize your responses.

```bash
python3 {baseDir}/scripts/query_insights.py --query kessandra-context
```

Returns domain scores, active patterns, engagement profile, priority insights, and suggested interaction approach.

### Domain health scores

```bash
python3 {baseDir}/scripts/query_insights.py --query domain-scores
python3 {baseDir}/scripts/query_insights.py --query domain-scores --domain sleep
```

### Behavioral patterns

```bash
python3 {baseDir}/scripts/query_insights.py --query patterns
python3 {baseDir}/scripts/query_insights.py --query patterns --min-confidence 0.7
```

### Goal effectiveness

```bash
python3 {baseDir}/scripts/query_insights.py --query goal-effectiveness
```

### Engagement profile

```bash
python3 {baseDir}/scripts/query_insights.py --query engagement
```

### Trend for a domain over time

```bash
python3 {baseDir}/scripts/query_insights.py --query trend --domain sleep --days 30
```

### Correlations between domains

```bash
python3 {baseDir}/scripts/query_insights.py --query correlations
```

## When to query

- **Session start**: Run `kessandra-context` to load personalized context. Silently incorporate insights - don't dump raw data at the user.
- **User asks "how am I doing"**: Use `domain-scores` and `patterns`.
- **User asks about a specific domain**: Use `domain-scores --domain X` and `trend --domain X`.
- **User sets goals**: Use `goal-effectiveness` to inform realistic goal-setting.
- **User seems overwhelmed**: Check `engagement` for overwhelm indicators.

## How to use insights

- Weave insights naturally into conversation. Don't say "according to your analytics..."
- Use patterns to proactively suggest helpful actions.
- If a domain is declining, gently bring attention to it.
- If you detect positive momentum, reinforce it.
- Respect the `suggested_approach.avoid` list - don't push topics the user is overwhelmed by.
- Never fabricate insights. If the query returns no data, say so.
