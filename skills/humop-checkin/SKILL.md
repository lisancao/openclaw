---
name: humop-checkin
description: Run structured HUMOP check-in sessions (morning, midday, evening). Use when the user wants to do a check-in, set daily goals, review progress, or do an evening reflection. Combines the humop-events and humop-insights skills for a complete session.
user-invocable: true
metadata:
  {
    "openclaw":
      {
        "emoji": "🌅",
        "requires": { "bins": ["python3"] },
      },
  }
---

# HUMOP Check-In Sessions

Structured check-in sessions that capture user state, set/review goals, and emit analytics events. This skill orchestrates `humop-events` (to emit) and `humop-insights` (to personalize).

## Session Types

### Morning Check-In (`/humop-checkin morning`)

**Flow:**

1. **Load context** - Query `humop-insights --query kessandra-context` silently. Note any priority insights.
2. **Greet and ask about mood** - "How are you feeling this morning?" Capture mood (1-10) and energy (1-10).
3. **Review yesterday** (if data exists) - Briefly mention yesterday's goal completion rate. Don't dwell on misses.
4. **Set daily goals** - Ask what they want to accomplish today. For each goal:
   - Capture title and optional description
   - Assign priority (1 = most important)
   - Check against `goal-effectiveness` optimal count. If they're setting too many, gently suggest focusing.
5. **Emit events** - Emit `session.morning` and `daily_goal.created` for each goal.
6. **Close** - Brief, encouraging close. Mention one relevant insight if appropriate.

**Tone:** Warm, brief, energizing. Don't over-explain. Match the user's energy.

### Midday Check-In (`/humop-checkin midday`)

**Flow:**

1. **Load context** silently.
2. **Ask about progress** - "How's the day going? Any updates on your goals?"
3. **For each goal mentioned:**
   - If completed: emit `daily_goal.completed`, celebrate briefly.
   - If stuck: identify stuck type (perfectionist/operational/emotional/overwhelm), emit `daily_goal.stuck`, offer the appropriate help prompt.
   - If in progress: acknowledge and move on.
4. **Quick mood check** - Only if user seems different from morning. Emit `checkin.mood` if captured.
5. **Close** - Short and actionable.

**Tone:** Casual check-in, not an interrogation. If everything's fine, keep it short.

### Evening Reflection (`/humop-checkin evening`)

**Flow:**

1. **Load context** silently.
2. **Review the day** - "How did today go overall?"
3. **Goal review** - Go through each daily goal:
   - Completed: acknowledge
   - Not done: ask if defer to tomorrow or drop. No judgment.
4. **Mood and energy** - Capture evening mood. Compare to morning if available.
5. **Domain check** (optional) - If a domain is flagged as `needs_attention`, ask one simple question about it. Don't force multiple domains.
6. **Reflection** - "Anything you want to note about today?" Free-text capture.
7. **Emit events** - `session.evening`, any remaining `daily_goal.completed` or status changes, `checkin.mood`.
8. **Close** - Calm, brief. Mention tomorrow's schedule if one exists.

**Tone:** Reflective, calm, non-judgmental. Evening is wind-down time.

## Stuck Type Responses

When a user reports being stuck on a goal, identify the type and respond:

| Type | Signal | Response |
|------|--------|----------|
| Perfectionist | "It's not good enough" | "What would 'good enough' look like? Let's define the minimum viable version." |
| Operational | "I don't know how" | "What's the very first tiny step? Something you could do in 5 minutes?" |
| Emotional | "I don't want to" | "What feeling comes up when you think about this? Let's sit with that for a moment." |
| Overwhelm | "There's too much" | "Let's pick just ONE piece of this. What's the smallest slice we could tackle?" |

## Rules

- Never skip the mood/energy capture in morning and evening sessions. These are key analytics signals.
- Always emit events for goals and mood. The pipeline depends on consistent data.
- Use insights to personalize but don't lead with "your data says..." Be natural.
- If the user is in a rush, compress the session. A 30-second check-in is better than a skipped one.
- If `humop-insights` is unavailable (no lakehouse running), the session still works - just skip the personalization.
- Respect the `avoid_topics` list from Kessandra context. Don't push domains the user is overwhelmed by.
- Track goal IDs across sessions. Reference previous goals by name, not UUID.
