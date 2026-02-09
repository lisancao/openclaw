# HUMOP Event Schema Reference

## Event Envelope

Every event follows this structure:

```json
{
  "event_id": "uuid-v4",
  "event_type": "category.action",
  "user_id": "string",
  "timestamp": "ISO 8601 UTC",
  "source": "openclaw | apollo-discord | apollo-cli | apollo-web",
  "payload": { }
}
```

## Payload Schemas by Event Type

### checkin.mood

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| mood | int (1-10) | yes | Self-reported mood score |
| energy | int (1-10) | no | Self-reported energy level |
| notes | string | no | Free-text context |

### checkin.domain

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| domain | string | yes | Health domain (sleep, exercise, mindfulness, nutrition, etc.) |
| value | float | yes | Domain-specific score |
| notes | string | no | Free-text context |

### conversation.started

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| domain | string | no | Primary conversation domain |
| interaction_mode | string | no | supportive, direct, coaching, curious |

### conversation.ended

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| domain | string | no | Primary conversation domain |
| message_count | int | yes | Total messages in conversation |
| duration_seconds | int | yes | Conversation duration |

### goal.created

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| domain | string | yes | Health domain |
| title | string | yes | Goal title |
| target_value | float | no | Numeric target |
| target_date | string | no | ISO 8601 date |

### goal.progress

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| goal_id | uuid | yes | Reference to goal |
| old_value | float | yes | Previous value |
| new_value | float | yes | Updated value |

### goal.status_changed

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| goal_id | uuid | yes | Reference to goal |
| old_status | string | yes | active, paused, completed, abandoned |
| new_status | string | yes | active, paused, completed, abandoned |

### daily_goal.created

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | yes | Goal title |
| priority | int (1-5) | yes | 1 = highest priority |
| date | string | yes | ISO 8601 date |
| description | string | no | Additional context |

### daily_goal.stuck

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| goal_id | uuid | yes | Reference to daily goal |
| stuck_type | string | yes | perfectionist, operational, emotional, overwhelm |

### daily_goal.completed

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| goal_id | uuid | yes | Reference to daily goal |
| duration_minutes | int | no | Time spent on goal |

### habit.completed

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| habit_id | uuid | yes | Reference to habit |
| habit_name | string | yes | Habit name |
| domain | string | yes | Health domain |
| notes | string | no | Free-text context |

### habit.missed

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| habit_id | uuid | yes | Reference to habit |
| habit_name | string | yes | Habit name |
| domain | string | yes | Health domain |
| days_since_last | int | yes | Days since last completion |

### session.morning

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| mood_start | int (1-10) | no | Starting mood score |
| goal_count | int | yes | Number of goals set |

### session.evening

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| mood_end | int (1-10) | no | Ending mood score |
| goals_completed | int | yes | Goals completed today |
| goals_total | int | yes | Total goals for today |
| reflection | string | no | Free-text reflection |

### schedule.triggered

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| schedule_id | uuid | yes | Reference to schedule |
| call_type | string | yes | morning_check_in, goal_check_in, evening_reflection, reminder |

### schedule.response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| schedule_id | uuid | yes | Reference to schedule |
| call_type | string | yes | Type of scheduled call |
| response | string | yes | answered, missed, declined, snoozed |
| response_time_seconds | int | no | Time to respond |

## Domains

Standard HUMOP health domains:

- `sleep`
- `exercise`
- `mindfulness`
- `nutrition`
- `social`
- `financial`
- `creative`
- `professional`

Custom domains are allowed.
