#!/usr/bin/env python3
"""Emit structured HUMOP events to Kafka or local queue."""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

KAFKA_TOPIC = os.environ.get("HUMOP_KAFKA_TOPIC", "humop.events")
BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
USER_ID = os.environ.get("HUMOP_USER_ID", "default")
SOURCE = os.environ.get("HUMOP_SOURCE", "openclaw")
QUEUE_DIR = Path.home() / ".humop" / "event_queue"

VALID_EVENT_TYPES = {
    "checkin.mood",
    "checkin.domain",
    "conversation.started",
    "conversation.ended",
    "goal.created",
    "goal.progress",
    "goal.status_changed",
    "daily_goal.created",
    "daily_goal.stuck",
    "daily_goal.completed",
    "habit.completed",
    "habit.missed",
    "session.morning",
    "session.evening",
    "schedule.triggered",
    "schedule.response",
}


def build_event(event_type: str, payload: dict) -> dict:
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "user_id": USER_ID,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": SOURCE,
        "payload": payload,
    }


def send_to_kafka(event: dict) -> bool:
    try:
        from kafka import KafkaProducer

        producer = KafkaProducer(
            bootstrap_servers=BOOTSTRAP_SERVERS.split(","),
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            acks="all",
            retries=3,
            request_timeout_ms=5000,
        )
        future = producer.send(
            KAFKA_TOPIC,
            key=event["user_id"],
            value=event,
        )
        future.get(timeout=5)
        producer.flush(timeout=5)
        producer.close(timeout=5)
        return True
    except Exception as e:
        print(f"Kafka unavailable ({e}), falling back to local queue", file=sys.stderr)
        return False


def queue_locally(event: dict) -> Path:
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{event['timestamp'].replace(':', '-')}_{event['event_type']}_{event['event_id'][:8]}.json"
    filepath = QUEUE_DIR / filename
    filepath.write_text(json.dumps(event, indent=2))
    return filepath


def replay_queue() -> int:
    if not QUEUE_DIR.exists():
        print("No queued events.")
        return 0

    files = sorted(QUEUE_DIR.glob("*.json"))
    if not files:
        print("No queued events.")
        return 0

    sent = 0
    for f in files:
        event = json.loads(f.read_text())
        if send_to_kafka(event):
            f.unlink()
            sent += 1
        else:
            print(f"Failed to replay, stopping. {sent}/{len(files)} sent.")
            return sent

    print(f"Replayed {sent}/{len(files)} events.")
    return sent


def main():
    parser = argparse.ArgumentParser(description="Emit HUMOP events")
    parser.add_argument("--type", required=True, help="Event type")
    parser.add_argument("--payload", required=True, help="JSON payload")
    parser.add_argument("--replay", action="store_true", help="Replay queued events")
    args = parser.parse_args()

    if args.replay:
        replay_queue()
        return

    if args.type not in VALID_EVENT_TYPES:
        print(f"Unknown event type: {args.type}", file=sys.stderr)
        print(f"Valid types: {', '.join(sorted(VALID_EVENT_TYPES))}", file=sys.stderr)
        sys.exit(1)

    try:
        payload = json.loads(args.payload)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON payload: {e}", file=sys.stderr)
        sys.exit(1)

    event = build_event(args.type, payload)

    if send_to_kafka(event):
        print(f"Sent {args.type} event {event['event_id'][:8]} to Kafka")
    else:
        filepath = queue_locally(event)
        print(f"Queued {args.type} event to {filepath}")


if __name__ == "__main__":
    main()
