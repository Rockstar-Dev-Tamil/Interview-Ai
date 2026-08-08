import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from person1.state import create_initial_state
from person1.nodes import (
    intro_node,
    evaluate_answer_node,
    route_decision_node,
    probe_node,
    next_question_node,
    feedback_node,
)


def test_intro_node_asks_first_question():
    state = create_initial_state(candidate={"name": "Alice"})
    res = intro_node(state)
    
    assert res["question_count"] == 1
    assert "current_question" in res
    assert res["current_question"] is not None
    assert res["phase"] == "question"
    assert res["current_question"]["question_text"] in res["reply"]
    assert "Alice" in res["reply"]


def test_evaluate_answer_node_handles_empty_answer():
    state = create_initial_state()
    state["last_user_answer"] = ""
    res = evaluate_answer_node(state)
    assert res["phase"] == "question"
    assert "Please provide an answer" in res["reply"]

    state["last_user_answer"] = None
    res_none = evaluate_answer_node(state)
    assert res_none["phase"] == "question"
    assert "Please provide an answer" in res_none["reply"]


def test_evaluate_answer_node_stores_quality():
    state = create_initial_state()
    question = {
        "question_id": "day_02_q1",
        "day": 2,
        "module": "Python Environments",
        "topic": "Virtual Environments",
        "difficulty": 1,
        "question_text": "Explain venv.",
        "expected_concepts": ["isolation", "dependencies"],
        "follow_up_hints": [],
        "source": "bank",
    }
    state["current_question"] = question
    state["last_user_answer"] = "I use virtual environment for isolation and managing dependencies."
    
    res = evaluate_answer_node(state)
    assert res["phase"] == "evaluate"
    assert "last_answer_quality" in res
    assert res["last_answer_quality"] > 0.0
    assert "last_evaluation" in res


def test_probe_node_increments_probe_count():
    state = create_initial_state()
    state["probe_count"] = 1
    state["current_question"] = {
        "topic": "Virtual Environments",
        "question_id": "day_02_q1",
        "day": 2,
        "module": "m",
        "difficulty": 1,
        "question_text": "q",
        "expected_concepts": [],
        "follow_up_hints": [],
        "source": "b",
    }
    state["last_user_answer"] = "some answer"
    state["last_evaluation"] = {"quality": 0.3, "missing_concepts": ["isolation"]}
    
    res = probe_node(state)
    assert res["probe_count"] == 2
    assert res["phase"] == "probe"
    assert "reply" in res
    assert "isolation" in res["reply"]


def test_next_question_node_increments_question_count():
    state = create_initial_state()
    state["question_count"] = 1
    state["asked_question_ids"] = ["day_02_q1"]
    
    res = next_question_node(state)
    assert res["question_count"] == 2
    assert res["phase"] == "question"
    assert res["current_question"]["question_id"] != "day_02_q1"


def test_feedback_node_returns_done_and_feedback():
    state = create_initial_state()
    state["question_count"] = 10
    state["covered_days"] = [2, 7, 12, 18]
    
    res = feedback_node(state)
    assert res["done"] is True
    assert res["phase"] == "done"
    assert "feedback" in res
    fb = res["feedback"]
    assert "summary" in fb
    assert "strengths" in fb
    assert "gaps" in fb
    assert "next" in fb
