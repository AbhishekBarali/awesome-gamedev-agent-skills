#!/usr/bin/env python3
"""preToolUse guard for the gamedev-skills-builder agent.

Reads the hook payload as JSON from stdin and inspects the proposed shell command
(``tool_input.command``). If the command matches a destructive git pattern, it prints
a warning to stderr and exits 2 to block the call. Otherwise it exits 0.

This is a safety net, not a policy engine: it only blocks the clearly destructive,
hard-to-reverse git operations. Non-git commands and ordinary git usage pass through.
"""

from __future__ import annotations

import json
import re
import sys

# Patterns for destructive / hard-to-reverse git operations.
DESTRUCTIVE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("force push", re.compile(r"\bgit\b.*\bpush\b.*(--force\b|--force-with-lease\b|(?<!\w)-f\b)")),
    ("hard reset", re.compile(r"\bgit\b.*\breset\b.*--hard\b")),
    ("force clean", re.compile(r"\bgit\b.*\bclean\b.*(?:-[a-eg-z]*f|--force)")),
    ("force branch delete", re.compile(r"\bgit\b.*\bbranch\b.*(?<!\w)-D\b")),
    ("force checkout delete", re.compile(r"\bgit\b.*\bcheckout\b.*-B\b")),
    ("rebase", re.compile(r"\bgit\b.*\brebase\b")),
    ("recursive git rm", re.compile(r"\bgit\b.*\brm\b.*-[a-z]*r[a-z]*f|\bgit\b.*\brm\b.*-[a-z]*f[a-z]*r")),
    ("update-ref delete", re.compile(r"\bgit\b.*\bupdate-ref\b.*-d\b")),
]


def main() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        return 0
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        # Can't parse — don't block, just allow.
        return 0

    tool_input = payload.get("tool_input") or payload.get("toolInput") or {}
    command = ""
    if isinstance(tool_input, dict):
        command = tool_input.get("command") or tool_input.get("cmd") or ""
    if not isinstance(command, str) or not command.strip():
        return 0

    lowered = command.lower()
    for label, pattern in DESTRUCTIVE_PATTERNS:
        if pattern.search(lowered):
            sys.stderr.write(
                f"[guard] Blocked a potentially destructive git operation ({label}): "
                f"{command.strip()}\n"
                "[guard] If this is intentional, run it yourself outside the agent.\n"
            )
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
