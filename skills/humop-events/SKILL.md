---
name: humop-events
description: Emit structured HUMOP events to Kafka for the lakehouse analytics pipeline. Use when the user reports mood, completes habits, updates goals, finishes check-ins, or any trackable interaction that should be captured for Kessandra analytics.
metadata:
  {
    "openclaw":
      {
        "emoji": "📡",
        "requires": { "bins": ["python3"], "env": ["KAFKA_BOOTSTRAP_SERVERS"] },
        "primaryEnv": "KAFKA_BOOTSTRAP_SERVERS",
      },
  }
---

# HUMOP Event Emission

Capture user interactions as structured events and send them to Kafka for the lakehouse analytics pipeline. These events flow through Bronze -> Silver -> Gold layers and ultimately power Kessandra's personalization.

## When to emit events

Emit events whenever the user:

- Reports mood or energy levels
- Logs a health domain score (sleep, exercise, mindfulness, etc.)
- Creates, updates, or completes a goal
- Creates or completes a daily goal
- Reports being stuck on a goal
- Completes or misses a habit
- Starts or finishes a morning/evening session
- Responds to a scheduled check-in

## How to emit

```bash
python3 {baseDir}/scripts/emit_event.py --type <event_type> --payload '<json>'
```

## Event types and payloads

### Mood check-in

```bash
python3 {baseDir}/scripts/emit_event.py \
  --type checkin.mood \
  --payload '{"mood": 7, "energy": 6, "notes": "feeling good after a walk"}'
```

### Domain health entry

```bash
python3 {baseDir}/scripts/emit_event.py \
  --type checkin.domain \
  --payload '{"domain": "sleep", "value": 6.5, "notes": "woke up once"}'
```

### Goal created

```bash
python3 {baseDir}/scripts/emit_event.py \
  --type goal.created \
  --payload '{"domain": "exercise", "title": "Run 3x per week", "target_value": 3.0}'
```

### Goal progress

```bash
python3 {baseDir}/scripts/emit_event.py \
  --type goal.progress \
  --payload '{"goal_id": "<uuid>", "old_value": 1.0, "new_value": 2.0}'
```

### Goal status changed

```bash
python3 {baseDir}/scripts/emit_event.py \
  --type goal.status_changed \
  --payload '{"goal_id": "<uuid>", "old_status": "active", "new_status": "completed"}'
```

### Daily goal created

```bash
python3 {baseDir}/scripts/emit_event.py \
  --type daily_goal.created \
  --payload '{"title": "Finish report", "priority": 1, "date": "2025-01-20"}'
```

### Daily goal stuck

```bash
python3 {baseDir}/scripts/emit_event.py \
  --type daily_goal.stuck \
  --payload '{"goal_id": "<uuid>", "stuck_type": "operational"}'
```

Stuck types: `perfectionist`, `operational`, `emotional`, `overwhelm`

### Daily goal completed

```bash
python3 {baseDir}/scripts/emit_event.py \
  --type daily_goal.completed \
  --payload '{"goal_id": "<uuid>", "duration_minutes": 45}'
```

### Habit completed

```bash
python3 {baseDir}/scripts/emit_event.py \
  --type habit.completed \
  --payload '{"habit_id": "<uuid>", "habit_name": "meditation", "domain": "mindfulness", "notes": "10 min session"}'
```

### Habit missed

```bash
python3 {baseDir}/scripts/emit_event.py \
  --type habit.missed \
  --payload '{"habit_id": "<uuid>", "habit_name": "meditation", "domain": "mindfulness", "days_since_last": 2}'
```

### Morning session

```bash
python3 {baseDir}/scripts/emit_event.py \
  --type session.morning \
  --payload '{"mood_start": 6, "goal_count": 3}'
```

### Evening session

```bash
python3 {baseDir}/scripts/emit_event.py \
  --type session.evening \
  --payload '{"mood_end": 7, "goals_completed": 2, "goals_total": 3, "reflection": "productive day"}'
```

### Schedule response

```bash
python3 {baseDir}/scripts/emit_event.py \
  --type schedule.response \
  --payload '{"schedule_id": "<uuid>", "call_type": "morning_check_in", "response": "answered"}'
```

Response values: `answered`, `missed`, `declined`, `snoozed`

### Conversation ended

```bash
python3 {baseDir}/scripts/emit_event.py \
  --type conversation.ended \
  --payload '{"domain": "sleep", "message_count": 12, "duration_seconds": 300}'
```

## Rules

- Always include all required payload fields for the event type.
- Use ISO 8601 timestamps. The script adds `event_id`, `user_id`, `timestamp`, and `source` automatically.
- Emit events in the background - don't block the conversation waiting for confirmation.
- If Kafka is unavailable, the script writes events to `~/.humop/event_queue/` for later replay.
- Never fabricate event data. Only emit events based on actual user interactions.
