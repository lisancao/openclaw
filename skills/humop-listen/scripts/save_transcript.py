#!/usr/bin/env python3
"""Save conversation transcripts for Kessandra's long-term memory."""

import argparse
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

LAKEHOUSE_DIR = Path(os.environ.get(
    "HUMOP_LAKEHOUSE_CONVERSATIONS",
    str(Path.home() / ".humop" / "conversations")
))
USER_ID = os.environ.get("HUMOP_USER_ID", "default")


def save_transcript(source: str, transcript: str) -> Path:
    """Save a conversation transcript to storage."""
    LAKEHOUSE_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)
    conversation = {
        "id": str(uuid.uuid4()),
        "user_id": USER_ID,
        "source": source,
        "timestamp": now.isoformat(),
        "date": now.strftime("%Y-%m-%d"),
        "time_of_day": _time_of_day(now),
        "transcript": transcript,
        "message_count": transcript.count("\nU:") + transcript.count("\nK:") + 1,
    }

    filename = f"{now.strftime('%Y-%m-%d_%H-%M')}_{conversation['id'][:8]}.json"
    filepath = LAKEHOUSE_DIR / filename
    filepath.write_text(json.dumps(conversation, indent=2))
    return filepath


def _time_of_day(dt: datetime) -> str:
    hour = dt.hour
    if hour < 6:
        return "night"
    elif hour < 12:
        return "morning"
    elif hour < 17:
        return "afternoon"
    elif hour < 21:
        return "evening"
    return "night"


def main():
    parser = argparse.ArgumentParser(description="Save conversation transcript")
    parser.add_argument("--source", default="openclaw", help="Source platform")
    parser.add_argument("--transcript", required=True, help="Conversation text")
    args = parser.parse_args()

    filepath = save_transcript(args.source, args.transcript)
    print(f"Saved to {filepath}")


if __name__ == "__main__":
    main()
