import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from person1.reasoning import (
    route_after_evaluation,
    adjust_difficulty,
    generate_socratic_probe,
    mark_day_covered,
    update_strengths_and_gaps
)
from person1.state import create_initial_state

def test_route_after_evaluation_feedback():
    # 1. if question_count >= 10, go to feedback
    state = create_initial_state({})
    state["question_count"] = 12
    assert route_after_evaluation(state) == "feedback"

    # 2. if question_count >= 8 and unique_covered_days >= 4 and quality >= 0.65 -> feedback
    state = create_initial_state()
    state["question_count"] = 8
    state["covered_days"] = [1, 2, 3, 4]
    state["last_answer_quality"] = 0.7
    assert route_after_evaluation(state) == "feedback"

def test_route_after_evaluation_probe():
    # if quality < 0.4 and probe_count < 3, probe
    state = create_initial_state()
    state["last_answer_quality"] = 0.3
    state["probe_count"] = 2
    assert route_after_evaluation(state) == "probe"

def test_route_after_evaluation_increase_difficulty():
    state = create_initial_state()
    state["last_answer_quality"] = 0.9
    assert route_after_evaluation(state) == "increase_difficulty"
    
def test_route_after_evaluation_continue():
    state = create_initial_state()
    state["last_answer_quality"] = 0.6
    assert route_after_evaluation(state) == "continue"

def test_adjust_difficulty():
    state = create_initial_state()
    state["difficulty_level"] = 3
    
    eval_high = {"quality": 0.9, "matched_concepts": [], "missing_concepts": [], "rationale": "", "recommended_action": ""}
    assert adjust_difficulty(state, eval_high) == 4
    
    eval_low = {"quality": 0.2, "matched_concepts": [], "missing_concepts": [], "rationale": "", "recommended_action": ""}
    assert adjust_difficulty(state, eval_low) == 2
    
    eval_mid = {"quality": 0.5, "matched_concepts": [], "missing_concepts": [], "rationale": "", "recommended_action": ""}
    assert adjust_difficulty(state, eval_mid) == 3

def test_generate_socratic_probe():
    state = create_initial_state()
    question = {"topic": "Databases", "question_id": "q1", "day": 1, "module": "m", "difficulty": 1, "question_text": "Q", "expected_concepts": [], "follow_up_hints": [], "source": "b"}
    eval_res = {"quality": 0.3, "missing_concepts": ["Transactions"], "matched_concepts": [], "rationale": "", "recommended_action": ""}
    probe = generate_socratic_probe(state, question, "ans", eval_res)
    assert "Transactions" in probe
    
    eval_no_missing = {"quality": 0.9, "missing_concepts": [], "matched_concepts": [], "rationale": "", "recommended_action": ""}
    probe_scale = generate_socratic_probe(state, question, "ans", eval_no_missing)
    assert "scale" in probe_scale or "production load" in probe_scale

def test_mark_day_covered():
    state = create_initial_state()
    state = mark_day_covered(state, 1)
    assert state["covered_days"] == [1]
    state = mark_day_covered(state, 1)
    assert state["covered_days"] == [1] # no duplicates
    state = mark_day_covered(state, 2)
    assert state["covered_days"] == [1, 2]

def test_update_strengths_and_gaps():
    state = create_initial_state()
    question = {"topic": "Networking", "question_id": "q1", "day": 1, "module": "m", "difficulty": 1, "question_text": "Q", "expected_concepts": [], "follow_up_hints": [], "source": "b"}
    
    eval_res_high = {"quality": 0.8, "missing_concepts": [], "matched_concepts": [], "rationale": "", "recommended_action": ""}
    state = update_strengths_and_gaps(state, question, eval_res_high)
    assert len(state["strengths"]) == 1
    assert "Networking" in state["strengths"][0]
    
    eval_res_low = {"quality": 0.2, "missing_concepts": ["TCP"], "matched_concepts": [], "rationale": "", "recommended_action": ""}
    state = update_strengths_and_gaps(state, question, eval_res_low)
    assert len(state["gaps"]) == 1
    assert "TCP" in state["gaps"][0]
