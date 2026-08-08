"""
utils.py — Shared utility functions for Person 1.

Stateless helpers used by the graph nodes, mock pipeline, and tests.
"""

from __future__ import annotations

import json
from typing import Any


# ───────────────────────────────────────────────────────────────────────────
# JSON safety
# ───────────────────────────────────────────────────────────────────────────

def is_json_serializable(obj: Any) -> bool:
    """Return True if *obj* can be round-tripped through json.dumps/loads."""
    try:
        json.dumps(obj)
        return True
    except (TypeError, ValueError, OverflowError):
        return False


def safe_dump(obj: Any) -> str:
    """Dump *obj* to a compact JSON string, or repr() on failure."""
    try:
        return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    except (TypeError, ValueError):
        return repr(obj)


# ───────────────────────────────────────────────────────────────────────────
# State helpers
# ───────────────────────────────────────────────────────────────────────────

def append_message(
    conversation_history: list[dict],
    role: str,
    content: str,
) -> list[dict]:
    """Return a *new* list with an appended message dict (immutable style)."""
    return conversation_history + [{"role": role, "content": content}]


def add_unique(items: list, value) -> list:
    """Return a *new* list with *value* appended only if not already present."""
    if value in items:
        return items
    return items + [value]


# ───────────────────────────────────────────────────────────────────────────
# Text helpers
# ───────────────────────────────────────────────────────────────────────────

def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp *value* to [lo, hi]."""
    return max(lo, min(hi, value))


def day_key(day_number: int) -> str:
    """Convert day number → competency map key.  2 → 'day_02', 12 → 'day_12'."""
    return f"day_{day_number:02d}"
