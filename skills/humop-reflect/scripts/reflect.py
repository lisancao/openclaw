#!/usr/bin/env python3
"""Process conversation transcripts into Kessandra's narrative understanding."""

import argparse
import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

CONVERSATIONS_DIR = Path(os.environ.get(
    "HUMOP_LAKEHOUSE_CONVERSATIONS",
    str(Path.home() / ".humop" / "conversations")
))
CONTEXT_FILE = Path(os.environ.get(
    "HUMOP_CONTEXT_FILE",
    str(Path.home() / ".humop" / "context.md")
))
USER_ID = os.environ.get("HUMOP_USER_ID", "default")
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = os.environ.get("HUMOP_REFLECT_MODEL", "claude-sonnet-4-5-20250929")

REFLECT_PROMPT = """You are the memory system for Kessandra, a mental health companion.
Your job is to read recent conversations and produce a narrative understanding of the user.

Core principles:
- This is qualitative, holistic understanding. Not metrics or scores.
- Track CHANGE over time. "Where were they, where are they now."
- Note what Kessandra offered that landed vs. what was deflected.
- Note self-initiated positives (things the user did on their own without prompting).
- Identify overwhelm signals specific to THIS person.
- Never judge. "They deflected" not "they're avoiding."

{existing_context}

Write the following sections:

## Where they are right now
(Current state. What's on their mind. How they're showing up in conversations.)

## What's shifting
(What's changing compared to earlier conversations. Progress, regression, or stasis - described without judgment.)

## What helps
(What Kessandra has said or suggested that actually landed. What the user responds to.)

## What to be careful about
(Topics they deflect. Things that increase shutdown. What NOT to do.)

## How they've changed (last 30 days)
(Concrete observations about trajectory. Not "they're doing better" but specific shifts.)

Here are the recent conversations, oldest first:

{conversations}"""


def load_conversations(days: int) -> list[dict]:
    """Load conversation transcripts from the last N days."""
    if not CONVERSATIONS_DIR.exists():
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    conversations = []

    for filepath in sorted(CONVERSATIONS_DIR.glob("*.json")):
        try:
            data = json.loads(filepath.read_text())
            ts = datetime.fromisoformat(data["timestamp"])
            if ts >= cutoff:
                conversations.append(data)
        except (json.JSONDecodeError, KeyError):
            continue

    return conversations


def format_conversations(conversations: list[dict]) -> str:
    """Format conversations for the LLM prompt."""
    parts = []
    for conv in conversations:
        date = conv.get("date", "unknown")
        time = conv.get("time_of_day", "")
        source = conv.get("source", "unknown")
        transcript = conv.get("transcript", "")
        parts.append(f"### {date} ({time}, via {source})\n\n{transcript}")
    return "\n\n---\n\n".join(parts)


def load_existing_context() -> str:
    """Load existing narrative context if it exists."""
    if CONTEXT_FILE.exists():
        content = CONTEXT_FILE.read_text().strip()
        if content:
            return f"Here is the EXISTING understanding from previous reflection. Update and evolve it based on new conversations:\n\n{content}"
    return "This is the first reflection. Build understanding from scratch."


def reflect(conversations: list[dict], incremental: bool) -> str:
    """Call Claude to produce narrative understanding."""
    import anthropic

    existing_context = load_existing_context() if incremental else "Build understanding from scratch."
    formatted = format_conversations(conversations)

    if not formatted.strip():
        return ""

    client = anthropic.Anthropic(api_key=API_KEY)
    message = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": REFLECT_PROMPT.format(
                existing_context=existing_context,
                conversations=formatted,
            ),
        }],
    )

    return message.content[0].text


def main():
    parser = argparse.ArgumentParser(description="Reflect on recent conversations")
    parser.add_argument("--days", type=int, default=30, help="Look back N days")
    parser.add_argument("--incremental", action="store_true",
                        help="Build on existing understanding")
    parser.add_argument("--output", type=str, default=None,
                        help="Output file path")
    args = parser.parse_args()

    output_path = Path(args.output) if args.output else CONTEXT_FILE

    conversations = load_conversations(args.days)
    if not conversations:
        print("No conversations found.")
        return

    print(f"Reflecting on {len(conversations)} conversations from the last {args.days} days...")

    context = reflect(conversations, args.incremental)
    if not context:
        print("No context generated.")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(context)
    print(f"Context written to {output_path}")


if __name__ == "__main__":
    main()
