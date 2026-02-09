---
name: humop-listen
description: Save conversation transcripts for Kessandra's long-term memory. Use AFTER every meaningful conversation to preserve what was discussed. This is how Kessandra remembers across sessions.
metadata:
  {
    "openclaw":
      {
        "emoji": "📝",
        "requires": { "bins": ["python3"] },
      },
  }
---

# HUMOP Listen

After a conversation, save the transcript so Kessandra can remember it later. This is the foundation of long-term memory.

## When to use

After every conversation that has substance. Skip trivial exchanges ("hey" / "hey" / "bye").

## How to save

```bash
python3 {baseDir}/scripts/save_transcript.py --source openclaw --transcript '<conversation text>'
```

The transcript should be the natural conversation as it happened. Include both sides. Don't summarize or filter - the raw conversation is the source of truth.

Example:

```bash
python3 {baseDir}/scripts/save_transcript.py --source openclaw --transcript 'K: morning. how'\''s today looking?
U: not great honestly. barely slept
K: rough night. want to talk about it or just sit here?
U: i keep waking up at like 3am. third time this week
K: that'\''s a pattern. anything on your mind when you wake up?
U: work stuff. that project is just... a lot
K: yeah. sounds like it'\''s following you to bed. has anything helped before?
U: honestly when i stopped looking at slack after dinner it was better for a while
K: that worked once. might be worth trying again. no pressure though.
U: yeah maybe'
```

## Rules

- Save after the conversation ends, not during.
- Include the full conversation. Don't cherry-pick.
- Use K: for Kessandra and U: for the user.
- The script handles timestamps, IDs, and storage location.
- If the lakehouse is unavailable, transcripts save locally to `~/.humop/conversations/`.
