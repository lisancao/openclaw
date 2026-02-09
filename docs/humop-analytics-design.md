# HUMOP Analytics Architecture

Server-side analytics for Kessandra personalization, powered by the lakehouse-at-home stack and OpenClaw skills.

## Overview

HUMOP is a personal AI assistant for behavioral health optimization. **Kessandra** is its AI engine (Claude-backed). This design adds a server-side analytics layer so Kessandra can personalize based on long-term user patterns rather than just the current conversation.

```
┌──────────────────────────────────────────────────────────────────────┐
│  User Interaction Layer                                              │
│                                                                      │
│  OpenClaw (multi-platform)          Apollo (Discord voice, WASM)    │
│  └─ humop-checkin skill             └─ Rust native agent            │
│  └─ humop-events skill                                              │
│  └─ humop-insights skill                                            │
└────────────┬──────────────────────────────────────┬──────────────────┘
             │ events                               │ events
             ▼                                      ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Lakehouse Stack (lakehouse-at-home)                                 │
│                                                                      │
│  ┌────────────┐    ┌─────────────────────────────────────────────┐   │
│  │   Kafka    │───▶│              Spark 4.x                     │   │
│  │  :9092     │    │                                             │   │
│  │  topic:    │    │  ┌─────────┐  ┌──────────┐  ┌───────────┐  │   │
│  │  humop.    │    │  │ BRONZE  │─▶│  SILVER  │─▶│   GOLD    │  │   │
│  │  events    │    │  │raw JSON │  │ cleaned  │  │ insights  │  │   │
│  └────────────┘    │  └─────────┘  └──────────┘  └───────────┘  │   │
│                    └──────────────────────────────────┬──────────┘   │
│  ┌────────────┐                                      │              │
│  │  Airflow   │─── schedules Spark jobs ─────────────┘              │
│  │  :8085     │                                                     │
│  └────────────┘    ┌─────────────────────────────────────────────┐   │
│                    │  Iceberg Tables (SeaweedFS S3)              │   │
│                    │  PostgreSQL catalog metadata                │   │
│                    └─────────────────────────────────────────────┘   │
└──────────────────────────────────────┬───────────────────────────────┘
                                       │
                                       │ gold layer queries
                                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Kessandra (AI Engine)                                               │
│                                                                      │
│  system_context = default_humop_context()                            │
│                 + analytics_context()  ◀── from gold layer           │
│                                                                      │
│  Personalized responses informed by weeks/months of user data        │
└──────────────────────────────────────────────────────────────────────┘
```

## Design Goals

1. **Kessandra gets smarter over time** - Long-term patterns inform personalization, not just the current session.
2. **Two front-ends, one pipeline** - OpenClaw (prototyping, multi-platform) and Apollo (WASM, voice) both emit to the same event stream.
3. **Offline resilience** - Events queue locally when Kafka is unavailable. Check-ins work without the lakehouse.
4. **Privacy first** - All data stays on the user's infrastructure. No cloud dependencies.

## Event System

### Event Envelope

Every user interaction that matters for analytics is captured as a structured event:

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "checkin.mood",
  "user_id": "default",
  "timestamp": "2025-01-20T08:30:00Z",
  "source": "openclaw",
  "payload": {
    "mood": 7,
    "energy": 6,
    "notes": "slept well"
  }
}
```

### Event Types

| Category | Events | Purpose |
|----------|--------|---------|
| Check-ins | `checkin.mood`, `checkin.domain` | Track subjective well-being over time |
| Conversations | `conversation.started`, `conversation.ended` | Measure engagement and session patterns |
| Goals | `goal.created`, `goal.progress`, `goal.status_changed` | Track long-term goal pursuit |
| Daily Goals | `daily_goal.created`, `daily_goal.stuck`, `daily_goal.completed` | Daily productivity patterns |
| Habits | `habit.completed`, `habit.missed` | Habit consistency and streaks |
| Sessions | `session.morning`, `session.evening` | Structured check-in data |
| Scheduling | `schedule.triggered`, `schedule.response` | Engagement with scheduled interactions |

Full payload schemas: [`skills/humop-events/references/event-schema.md`](../skills/humop-events/references/event-schema.md)

### Event Flow

```
User interaction
  → OpenClaw skill calls emit_event.py
    → Kafka (humop.events topic)
      → Spark streaming job (bronze_ingest)
        → iceberg.bronze.humop_events

If Kafka unavailable:
  → ~/.humop/event_queue/*.json
    → emit_event.py --replay (when Kafka returns)
```

## Lakehouse Tables

### Bronze (Raw Ingest)

| Table | Partitioning | Description |
|-------|-------------|-------------|
| `iceberg.bronze.humop_events` | `days(event_timestamp), event_type` | Raw Kafka events, JSON payload |

### Silver (Cleaned & Enriched)

| Table | Key Enrichments |
|-------|----------------|
| `iceberg.silver.mood_entries` | Day of week, hour, is_weekend flags |
| `iceberg.silver.domain_health` | Previous score, score delta |
| `iceberg.silver.conversations` | User/assistant message counts, avg response length, sentiment |
| `iceberg.silver.daily_goals` | Final status, time to complete, was_deferred flag |
| `iceberg.silver.habit_tracking` | Streak count, on-time flag |
| `iceberg.silver.schedule_interactions` | Response time, day/hour breakdown |

### Gold (Kessandra Insights)

| Table | Update Frequency | What It Provides |
|-------|-----------------|------------------|
| `iceberg.gold.user_domain_scores` | Daily | Rolling 7d/30d averages, trend direction, needs_attention flag |
| `iceberg.gold.user_patterns` | Daily | Behavioral patterns with confidence scores and recommended actions |
| `iceberg.gold.user_engagement_profile` | Daily | Preferred times, response rates, overwhelm indicators |
| `iceberg.gold.goal_effectiveness` | Daily | Completion rates by domain, optimal goal count, stuck recovery rate |
| `iceberg.gold.kessandra_context` | Hourly | Pre-computed context blob for prompt injection |

## Kessandra Context Injection

The `kessandra_context` table produces a JSON blob that gets injected into Kessandra's system prompt:

```json
{
  "domain_status": {
    "sleep": { "score": 45, "trend": "declining", "days_tracked": 14 },
    "exercise": { "score": 72, "trend": "improving", "days_tracked": 21 }
  },
  "active_patterns": [
    {
      "insight": "Mood improves 40% on days following exercise",
      "confidence": 0.85,
      "actionable": true
    }
  ],
  "engagement": {
    "preferred_time": "morning",
    "response_rate": 0.78,
    "overwhelm_risk": "low"
  },
  "goals": {
    "completion_rate_7d": 0.65,
    "optimal_daily_count": 3
  },
  "priority_insights": [
    "Sleep has declined 20% over 2 weeks",
    "Exercise streak is at 5 days - positive momentum"
  ],
  "suggested_approach": {
    "mode": "steady_presence",
    "focus_domain": "sleep",
    "avoid": ["adding new habits", "long task lists"]
  }
}
```

This replaces raw data dumps with actionable context. Kessandra uses this to:
- Know which domain needs attention without asking
- Reinforce positive momentum
- Avoid overwhelming the user with topics they're struggling with
- Adapt interaction style based on engagement patterns

## OpenClaw Skills

Three skills handle the integration:

### humop-events

Emits structured events to Kafka. Called by the model whenever a trackable interaction occurs (mood report, goal update, habit completion, etc.).

- **Script**: `scripts/emit_event.py`
- **Requires**: `python3`, `KAFKA_BOOTSTRAP_SERVERS`
- **Fallback**: Queues to `~/.humop/event_queue/` when Kafka is down

### humop-insights

Queries the lakehouse gold layer via Spark Thrift Server. Seven query types: `kessandra-context`, `domain-scores`, `patterns`, `goal-effectiveness`, `engagement`, `trend`, `correlations`.

- **Script**: `scripts/query_insights.py`
- **Requires**: `python3`, `HUMOP_LAKEHOUSE_HOST`
- **Fallback**: Reads from `~/.humop/insights_cache/` when lakehouse is down

### humop-checkin

User-invocable skill (`/humop-checkin morning|midday|evening`) that orchestrates structured check-in sessions. Combines insights (for personalization) and events (for capture).

- **Morning**: Mood capture, daily goal setting, context-informed suggestions
- **Midday**: Goal progress check, stuck-type identification and support
- **Evening**: Day review, mood capture, reflection, domain health check

## Spark Jobs

| Job | Schedule | Input | Output |
|-----|----------|-------|--------|
| `bronze_ingest` | Streaming | Kafka `humop.events` | `bronze.humop_events` |
| `silver_transform` | Hourly | Bronze tables | All silver tables |
| `gold_domain_scores` | Daily | `silver.mood_entries`, `silver.domain_health` | `gold.user_domain_scores` |
| `gold_patterns` | Daily | All silver tables | `gold.user_patterns` |
| `gold_engagement` | Daily | `silver.conversations`, `silver.schedule_interactions` | `gold.user_engagement_profile` |
| `gold_goal_effectiveness` | Daily | `silver.daily_goals` | `gold.goal_effectiveness` |
| `gold_kessandra_context` | Hourly | All gold tables | `gold.kessandra_context` |

These will be scheduled via Airflow DAGs in lakehouse-at-home.

## Apollo Integration (Future)

The same event schema works for Apollo (the Rust-native agent). A `humop-events` Rust crate would:

1. Serialize events to the same JSON format
2. Produce to the same Kafka topic (`humop.events`)
3. Fall back to SQLite queue (via Hyacinth) when offline
4. Query the gold layer via HTTP/Thrift for Kessandra context

This ensures both OpenClaw and Apollo feed the same analytics pipeline.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `KAFKA_BOOTSTRAP_SERVERS` | `localhost:9092` | Kafka broker address |
| `HUMOP_KAFKA_TOPIC` | `humop.events` | Kafka topic for events |
| `HUMOP_USER_ID` | `default` | User identifier |
| `HUMOP_SOURCE` | `openclaw` | Event source identifier |
| `HUMOP_LAKEHOUSE_HOST` | `localhost` | Spark Thrift Server host |
| `HUMOP_SPARK_THRIFT_PORT` | `10000` | Spark Thrift Server port |

## Status

- [x] Event schema design
- [x] OpenClaw skills (humop-events, humop-insights, humop-checkin)
- [ ] Spark job implementations (PySpark in lakehouse-at-home)
- [ ] Airflow DAG definitions
- [ ] Iceberg table DDL scripts
- [ ] Apollo Rust crate (`humop-events`)
- [ ] End-to-end testing
