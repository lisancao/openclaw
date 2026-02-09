# Check-In Session Flow Reference

## Event Emission Cheat Sheet

### Morning Session Events

```bash
# 1. Session start
python3 <humop-events>/scripts/emit_event.py --type session.morning \
  --payload '{"mood_start": <1-10>, "goal_count": <n>}'

# 2. For each goal
python3 <humop-events>/scripts/emit_event.py --type daily_goal.created \
  --payload '{"title": "<title>", "priority": <n>, "date": "<YYYY-MM-DD>"}'

# 3. Mood (always)
python3 <humop-events>/scripts/emit_event.py --type checkin.mood \
  --payload '{"mood": <1-10>, "energy": <1-10>}'
```

### Midday Session Events

```bash
# Goal completed
python3 <humop-events>/scripts/emit_event.py --type daily_goal.completed \
  --payload '{"goal_id": "<uuid>", "duration_minutes": <n>}'

# Goal stuck
python3 <humop-events>/scripts/emit_event.py --type daily_goal.stuck \
  --payload '{"goal_id": "<uuid>", "stuck_type": "<type>"}'
```

### Evening Session Events

```bash
# 1. Session end
python3 <humop-events>/scripts/emit_event.py --type session.evening \
  --payload '{"mood_end": <1-10>, "goals_completed": <n>, "goals_total": <n>, "reflection": "<text>"}'

# 2. Any remaining goal completions
python3 <humop-events>/scripts/emit_event.py --type daily_goal.completed \
  --payload '{"goal_id": "<uuid>"}'

# 3. Goal deferrals (status change)
python3 <humop-events>/scripts/emit_event.py --type goal.status_changed \
  --payload '{"goal_id": "<uuid>", "old_status": "in_progress", "new_status": "deferred"}'

# 4. Evening mood
python3 <humop-events>/scripts/emit_event.py --type checkin.mood \
  --payload '{"mood": <1-10>, "energy": <1-10>}'
```

## Insight Queries for Session Personalization

```bash
# Load full context at session start
python3 <humop-insights>/scripts/query_insights.py --query kessandra-context

# Check goal effectiveness (morning, to inform goal count)
python3 <humop-insights>/scripts/query_insights.py --query goal-effectiveness

# Check domain needing attention (evening, for domain question)
python3 <humop-insights>/scripts/query_insights.py --query domain-scores

# Check engagement profile (to adapt session length/style)
python3 <humop-insights>/scripts/query_insights.py --query engagement
```
