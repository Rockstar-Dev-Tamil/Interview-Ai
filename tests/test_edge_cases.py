import pytest
from person1.graph import run_turn
from person1.state import create_initial_state

def test_empty_answer():
    turn1 = run_turn(session_state=None, message="Ready")
    state = turn1["state"]

    turn2 = run_turn(session_state=state, message="   ")
    assert "Please provide an answer" in turn2["reply"]
    # Question count should not increment
    assert turn2["state"]["question_count"] == 1


def test_very_short_answer():
    turn1 = run_turn(session_state=None, message="Ready")
    state = turn1["state"]

    # Very short answer that isn't off-topic
    turn2 = run_turn(session_state=state, message="not sure")
    # Low score usually triggers probe
    assert turn2["state"]["probe_count"] == 1


def test_off_topic_answer():
    turn1 = run_turn(session_state=None, message="Ready")
    state = turn1["state"]

    turn2 = run_turn(session_state=state, message="I love eating pizza on Fridays.")
    assert "off-topic" in turn2["reply"]


def test_candidate_asks_question():
    turn1 = run_turn(session_state=None, message="Ready")
    state = turn1["state"]

    turn2 = run_turn(session_state=state, message="What do you think about it?")
    assert "Good question" in turn2["reply"]


def test_long_answer():
    turn1 = run_turn(session_state=None, message="Ready")
    state = turn1["state"]

    long_message = "word " * 4000
    turn2 = run_turn(session_state=state, message=long_message)
    # Shouldn't crash, should truncate
    assert turn2["state"]["last_answer_quality"] is not None


def test_max_questions():
    state = create_initial_state({})
    state["question_count"] = 12
    state["phase"] = "question"
    state["current_question"] = {"expected_concepts": ["test"]}
    # Mocking that 12 questions were asked
    turn = run_turn(session_state=state, message="Good answer with full concepts and a test.")
    assert turn["done"] is True
    assert turn["feedback"] is not None


def test_corrupted_state_missing_fields():
    state = {"session_id": "123"} # Missing all lists and counts
    turn = run_turn(session_state=state, message="Hi")
    assert turn["state"]["question_count"] == 1
    assert "conversation_history" in turn["state"]
