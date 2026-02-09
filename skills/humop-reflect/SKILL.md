---
name: humop-reflect
description: Process recent conversations into Kessandra's narrative understanding of the user. Run periodically or after meaningful conversations to update long-term memory. This is how Kessandra tracks change over time.
metadata:
  {
    "openclaw":
      {
        "emoji": "🪞",
        "requires": { "bins": ["python3"], "env": ["ANTHROPIC_API_KEY"] },
        "primaryEnv": "ANTHROPIC_API_KEY",
      },
  }
---

# HUMOP Reflect

This is the intelligence layer. It reads recent conversation transcripts and produces Kessandra's evolving understanding of who this person is and how they're doing.

## What it does

Takes raw conversations and produces a **narrative context** - not metrics, not scores. A qualitative, holistic understanding that tracks change over time.

## How to run

```bash
python3 {baseDir}/scripts/reflect.py
```

Options:

```bash
# Process only the last N days of conversations
python3 {baseDir}/scripts/reflect.py --days 14

# Include the existing understanding (for incremental updates)
python3 {baseDir}/scripts/reflect.py --incremental

# Output to a specific file
python3 {baseDir}/scripts/reflect.py --output ~/.humop/context.md
```

## What it produces

A file at `~/.humop/context.md` that reads like a clinical note from a thoughtful therapist - but warmer:

```markdown
## Where they are right now

Sleep has been hard for about two weeks. Waking at 3am, mind on work.
They traced it to a new project that's "a lot." When asked what helped
before, they remembered that cutting off Slack after dinner made a
difference. They haven't tried it again yet but didn't shut down the
idea.

## What's shifting

Three weeks ago, most conversations were about feeling stuck and
overwhelmed by everything. Lately the overwhelm is more focused -
it's specifically work, specifically this project. That's actually
progress: diffuse anxiety narrowing to something identifiable.

They've mentioned going for walks a few times, unprompted. Didn't
frame it as exercise or a habit - just something they're doing. Don't
make it a thing.

## What helps

- Short, grounded responses when they're terse
- Asking "want to talk about it or just sit here?" - they choose
  both, depending on the day
- Reminding them of things they already know work (like the Slack
  boundary) rather than suggesting new things
- Not pushing when they give one-word answers

## What to be careful about

- Financial stuff - they've deflected twice. Not ready.
- Don't frame the walks as a "habit" or "streak"
- When work comes up, listen first. They tend to figure things out
  by talking, not by getting advice.

## How they've changed (last 30 days)

- Went from "everything is too much" to "this specific thing is hard"
- More willing to name what's bothering them
- Started doing small things for themselves (walks) without being told
- Still avoids some topics but engages more overall
```

## When to run

- After a meaningful conversation (use `--incremental`)
- Daily as a batch job (processes all new conversations since last run)
- When Kessandra needs fresh context

## Rules

- The output is NARRATIVE, not structured data.
- Track CHANGE over time. That's the whole point. "Where were they, where are they now."
- Note what interventions land and what doesn't. Kessandra needs to learn what works for THIS person.
- Never frame observations as judgments. "They deflected" not "they're avoiding."
- Note self-initiated positives specifically. Things the user does on their own matter more than prompted actions.
- Keep the overwhelm signals section practical - what does overwhelm look like for THIS person?
