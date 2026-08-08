"""
routing.py — Edge routing logic for the LangGraph state machine.

After each node completes, these functions decide which node runs next.
"""

from __future__ import annotations

# Interview constraints
MIN_QUESTIONS = 8          # must ask at least this many before wrap allowed
MAX_TURNS = 20             # hard ceiling on total turns
MIN_DAYS = 4               # must cover at least 4 curriculum days before wrap


def route_after_evaluate(state: dict) -> str:
    """
    Called after node_evaluate_answer.
    Decides: go to probe, select next question, or wrap up.

    Returns the name of the next node to run.
    """
    turn_count: int = state.get("turn_count", 0)
    questions_asked_count: int = state.get("questions_asked_count", 0)
    days_covered: list = state.get("days_covered", [])
    answers: list = state.get("answers", [])
    probes_used: list = state.get("probes_used", [])
    current_question: dict | None = state.get("current_question")
    pending_probe: dict | None = state.get("pending_probe")

    # Hard stop: exceeded turn limit
    if turn_count >= MAX_TURNS:
        return "node_wrap"

    # Minimum requirements check — only wrap if constraints are satisfied
    constraints_met = (
        questions_asked_count >= MIN_QUESTIONS
        and len(days_covered) >= MIN_DAYS
        and len(probes_used) >= 1
    )

    # Evaluate last answer quality
    last_answer = answers[-1] if answers else None
    last_score = last_answer["score"] if last_answer else 3
    last_qid = last_answer["question_id"] if last_answer else None

    # Decide whether to probe
    should_probe = (
        last_score <= 2                          # weak answer
        and last_qid not in probes_used          # no probe used yet for this Q
        and pending_probe is None                # not already in probe mode
        and current_question is not None
    )

    if should_probe:
        return "node_probe"

    # Check if we're in a probing state that just completed
    # (pending_probe was set — answer came in — clear it and select next)
    # This is handled by inspecting if the latest answer was a probe answer
    # (the question_id matches a probes_used entry)

    # Continue interviewing if constraints not yet met
    if not constraints_met:
        return "node_select_question"

    # All constraints met — let the agent decide if it wants to wrap
    # We use a simple heuristic: wrap after questions_asked_count >= MIN_QUESTIONS + 2
    if questions_asked_count >= MIN_QUESTIONS + 2:
        return "node_wrap"

    return "node_select_question"


def route_after_intro(state: dict) -> str:
    """After the intro node, always move to question selection."""
    return "node_select_question"


def route_after_ask(state: dict) -> str:
    """After asking a question, wait for the human input turn (END)."""
    return "__end__"


def route_after_wrap(state: dict) -> str:
    """After wrap, generate feedback."""
    return "node_feedback"


def route_after_feedback(state: dict) -> str:
    """After feedback generation, terminate the graph."""
    return "__end__"
