"""
test_routing.py — Tests for routing edge logic.
"""

import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from person1.routing import route_after_evaluate, MIN_QUESTIONS, MIN_DAYS, MAX_TURNS


def _base_state(**overrides) -> dict:
    state = {
        "turn_count": 5,
        "questions_asked_count": 5,
        "days_covered": ["Day 1", "Day 2", "Day 3"],
        "answers": [{"question_id": "py_001", "score": 3, "flags": [], "raw": "ok", "probe_used": False}],
        "probes_used": [],
        "current_question": {"id": "py_001", "topic": "GIL", "day": "Day 1"},
        "pending_probe": None,
    }
    state.update(overrides)
    return state


class TestRouteAfterEvaluate:
    def test_weak_answer_triggers_probe(self):
        state = _base_state(
            answers=[{"question_id": "py_001", "score": 1, "flags": [], "raw": "i don't know", "probe_used": False}],
        )
        result = route_after_evaluate(state)
        assert result == "node_probe"

    def test_probe_not_repeated_for_same_question(self):
        state = _base_state(
            answers=[{"question_id": "py_001", "score": 1, "flags": [], "raw": "dunno", "probe_used": False}],
            probes_used=["py_001"],  # already probed
        )
        result = route_after_evaluate(state)
        assert result != "node_probe"

    def test_strong_answer_selects_next_question(self):
        state = _base_state(
            answers=[{"question_id": "py_001", "score": 5, "flags": [], "raw": "great answer", "probe_used": False}],
        )
        result = route_after_evaluate(state)
        assert result == "node_select_question"

    def test_max_turns_forces_wrap(self):
        state = _base_state(turn_count=MAX_TURNS + 1)
        result = route_after_evaluate(state)
        assert result == "node_wrap"

    def test_constraints_met_wraps_after_enough_questions(self):
        probes = ["q1"]
        answers = [{"question_id": "q1", "score": 3, "flags": [], "raw": "ok", "probe_used": False}]
        state = _base_state(
            questions_asked_count=MIN_QUESTIONS + 3,
            days_covered=["D1", "D2", "D3", "D4"],
            probes_used=probes,
            answers=answers,
        )
        result = route_after_evaluate(state)
        assert result == "node_wrap"

    def test_not_enough_days_continues(self):
        probes = ["q1"]
        answers = [{"question_id": "q1", "score": 3, "flags": [], "raw": "ok", "probe_used": False}]
        state = _base_state(
            questions_asked_count=MIN_QUESTIONS + 3,
            days_covered=["D1", "D2"],  # only 2 days — below MIN_DAYS=4
            probes_used=probes,
            answers=answers,
        )
        result = route_after_evaluate(state)
        assert result == "node_select_question"
