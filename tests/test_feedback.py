import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from person1.feedback import generate_final_feedback
from person1.state import create_initial_state

def test_generate_final_feedback():
    state = create_initial_state()
    state["question_count"] = 12
    state["covered_days"] = [1, 2, 3, 3, 4]
    state["strengths"] = ["Strong understanding of Python"]
    state["gaps"] = ["Needs review on SQL in Databases"]
    
    feedback = generate_final_feedback(state)
    
    assert "summary" in feedback
    assert "strengths" in feedback
    assert "gaps" in feedback
    assert "next" in feedback
    
    assert "12" in feedback["summary"]
    assert "4" in feedback["summary"] # 4 unique days
    
    assert len(feedback["strengths"]) == 1
    assert feedback["strengths"][0] == "Strong understanding of Python"
    
    assert len(feedback["gaps"]) == 1
    assert feedback["gaps"][0] == "Needs review on SQL in Databases"
    
    assert "SQL" in feedback["next"] or "gaps" in feedback["next"]

def test_generate_final_feedback_no_gaps_or_strengths():
    state = create_initial_state()
    feedback = generate_final_feedback(state)
    
    assert len(feedback["strengths"]) > 0
    assert "participated fully" in feedback["strengths"][0]
    
    assert len(feedback["gaps"]) > 0
    assert "No major gaps" in feedback["gaps"][0]
    
    assert "Continue building" in feedback["next"] or "advanced" in feedback["next"]
