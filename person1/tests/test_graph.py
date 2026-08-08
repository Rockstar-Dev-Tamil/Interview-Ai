import pytest
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from person1.graph import run_turn
from person1.state import create_initial_state


def test_full_mock_interview_flow():
    candidate = {"id": "cand_001", "name": "Sarah Chen", "role": "Senior ML Engineer"}
    
    # 1. Start interview
    turn1 = run_turn(session_state=None, message="Hello!", candidate=candidate)
    
    assert turn1["done"] is False
    assert turn1["feedback"] is None
    assert turn1["state"]["question_count"] == 1
    assert "Sarah Chen" in turn1["reply"]
    assert turn1["state"]["candidate_name"] == "Sarah Chen"
    
    current_state = turn1["state"]
    probe_triggered = False
    
    # Loop until completion
    for _ in range(25):
        if current_state.get("question_count", 0) == 2 and not probe_triggered:
            # Trigger a probe on turn 2 by giving a weak answer
            answer = "I don't know, not sure about this topic."
            probe_triggered = True
        else:
            # Give a strong answer (>40 words to pass word count check in mock pipeline)
            q = current_state.get("current_question", {})
            expected = q.get("expected_concepts", [])
            concepts_str = " ".join(expected) if expected else "best practices"
            answer = (
                f"I apply {concepts_str} with isolation and comprehensive standards across all production services. "
                "We maintain rigorous unit tests, integration testing, CI/CD pipelines, containerization, "
                "detailed logging, metrics collection, and automated deployment strategies to ensure high availability, "
                "scalability, resilience, and maintainability in enterprise systems."
            )

        turn = run_turn(session_state=current_state, message=answer)
        current_state = turn["state"]
        
        # Verify JSON serializability at each step
        json_str = json.dumps(current_state)
        assert isinstance(json_str, str)

        if turn["done"]:
            # Check final outputs
            assert turn["feedback"] is not None
            fb = turn["feedback"]
            assert "summary" in fb
            assert "strengths" in fb
            assert "gaps" in fb
            assert "next" in fb
            
            assert current_state["question_count"] >= 8
            assert len(set(current_state["covered_days"])) >= 4
            assert current_state["probe_count"] >= 1
            break

    assert current_state["done"] is True


def test_empty_message_handling():
    candidate = {"id": "c1", "name": "Alice"}
    turn1 = run_turn(session_state=None, message="Hi", candidate=candidate)
    
    # Send empty message
    turn2 = run_turn(session_state=turn1["state"], message="")
    assert turn2["done"] is False
    assert "Please provide" in turn2["reply"] or "substantive" in turn2["reply"]
    
    # Send None message
    turn3 = run_turn(session_state=turn1["state"], message=None)
    assert turn3["done"] is False


def test_corrupted_state_recovery():
    # Pass an invalid state dict
    corrupted_state = {"invalid_key": 123}
    res = run_turn(session_state=corrupted_state, message="Test")
    
    assert res["done"] is False
    assert res["state"] is not None
    assert "reply" in res
