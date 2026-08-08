"""
integration.py — The single public entry point for Person 1.

run_turn(session_state, message, candidate=None)
    → reply (str), new_state (dict), done (bool), feedback (dict | None)

Design:
  - First call (phase="intro"): initialise state, run the intro → select → ask chain.
  - Subsequent calls: inject user message, continue from node_evaluate_answer.
  - The LangGraph graph is driven manually (invoke with thread config) to preserve
    state across calls without a persistent backend.
  - All state is kept in the dict returned as new_state; callers (Person 3)
    must pass it back on the next call.
"""

from __future__ import annotations

import copy
import uuid
from typing import Any

from .state import make_initial_state, state_add_message
from .nodes import (
    node_intro,
    node_select_question,
    node_ask_question,
    node_evaluate_answer,
    node_handle_probe_answer,
    node_probe,
    node_wrap,
    node_feedback,
)
from .routing import route_after_evaluate


# ---------------------------------------------------------------------------
# Core turn runner (graph-less implementation for maximum compatibility)
# ---------------------------------------------------------------------------
# We implement the state machine directly rather than through LangGraph's
# .invoke() because LangGraph's human-in-the-loop requires async or
# interrupt mechanisms that add complexity.  The graph.py still defines
# the canonical topology for visualisation / integration tests.

def _apply(state: dict, updates: dict) -> dict:
    """Shallow-merge updates into state, return new dict."""
    return {**state, **updates}


def run_turn(
    session_state: dict | None,
    message: str,
    candidate: dict | None = None,
) -> tuple[str, dict, bool, dict | None]:
    """
    Execute one turn of the interview.

    Args:
        session_state : The state dict from the previous turn, or None for turn 0.
        message       : The candidate's text input for this turn.
                        On turn 0 (phase="intro"), any message triggers the greeting.
        candidate     : Optional dict with "name", "role", etc.
                        Only used on turn 0 to initialise state.

    Returns:
        reply     : The agent's reply text.
        new_state : Updated state dict (JSON-serializable).
        done      : True when the interview is complete.
        feedback  : The feedback dict (or None if not yet done).
    """

    # ── Turn 0: initialise state ─────────────────────────────────────────
    if session_state is None or session_state.get("phase") == "intro":
        state = make_initial_state(candidate=candidate or {})
        if candidate:
            state = {**state, "candidate": candidate}
        state = state_add_message(state, "user", message)

        # Run intro → select → ask
        state = _apply(state, node_intro(state))
        state = _apply(state, node_select_question(state))
        state = _apply(state, node_ask_question(state))

        reply = state["pending_message"]
        return reply, dict(state), False, None

    # ── Subsequent turns ─────────────────────────────────────────────────
    state = copy.deepcopy(session_state)

    # If already done, return the existing feedback
    if state.get("done"):
        return (
            "The interview has already concluded.",
            dict(state),
            True,
            state.get("feedback"),
        )

    # Inject user message
    state = state_add_message(state, "user", message)

    # ── Phase: probe ─────────────────────────────────────────────────────
    if state.get("phase") == "probe" and state.get("pending_probe"):
        state = _apply(state, node_handle_probe_answer(state))
        # Now select next question
        state = _apply(state, node_select_question(state))
        if state.get("phase") == "wrap":
            state = _apply(state, node_wrap(state))
            state = _apply(state, node_feedback(state))
            return state["pending_message"], dict(state), True, state["feedback"]
        state = _apply(state, node_ask_question(state))
        reply = state["pending_message"]
        return reply, dict(state), False, None

    # ── Phase: question ───────────────────────────────────────────────────
    state = _apply(state, node_evaluate_answer(state))

    # Routing decision
    next_node = route_after_evaluate(state)

    if next_node == "node_probe":
        state = _apply(state, node_probe(state))
        reply = state["pending_message"]
        return reply, dict(state), False, None

    if next_node == "node_wrap":
        state = _apply(state, node_wrap(state))
        state = _apply(state, node_feedback(state))
        return state["pending_message"], dict(state), True, state["feedback"]

    # next_node == "node_select_question"
    state = _apply(state, node_select_question(state))
    if state.get("phase") == "wrap":
        state = _apply(state, node_wrap(state))
        state = _apply(state, node_feedback(state))
        return state["pending_message"], dict(state), True, state["feedback"]

    state = _apply(state, node_ask_question(state))
    reply = state["pending_message"]
    return reply, dict(state), False, None
