#!/usr/bin/env python3
"""Load Kessandra's narrative understanding of the user."""

import os
from pathlib import Path

CONTEXT_FILE = Path(os.environ.get(
    "HUMOP_CONTEXT_FILE",
    str(Path.home() / ".humop" / "context.md")
))


def main():
    if not CONTEXT_FILE.exists():
        print("No context yet. This is a new relationship. Get to know them.")
        return

    content = CONTEXT_FILE.read_text().strip()
    if not content:
        print("No context yet. This is a new relationship. Get to know them.")
        return

    print(content)


if __name__ == "__main__":
    main()
