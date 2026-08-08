import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from person1.graph import run_turn
from scripts.run_mock_interview import generate_candidate_answer


def run_simulation(persona: str):
    print(f"\n--- Running validation for persona: {persona.upper()} ---")
    candidate = {
        "id": f"cand_{persona}_01",
        "name": f"Alex ({persona.capitalize()} Candidate)",
        "role": "Software Engineer"
    }

    turn = run_turn(session_state=None, message="Hello, I am ready for the interview.", candidate=candidate)
    session_state = turn["state"]

    turn_number = 1

    while not turn["done"] and turn_number < 30:
        turn_number += 1
        candidate_message = generate_candidate_answer(persona, session_state)
        turn = run_turn(session_state=session_state, message=candidate_message)
        session_state = turn["state"]

    total_questions = session_state.get("question_count", 0)
    covered_days = session_state.get("covered_days", [])
    unique_days = len(set(covered_days))
    probe_count = session_state.get("probe_count", 0)
    final_feedback = turn.get("feedback")

    # Verifications
    print("Verifying minimum 8 questions...")
    assert total_questions >= 8, f"Expected >= 8 questions, got {total_questions}"

    print("Verifying at least 4 covered days...")
    assert unique_days >= 4, f"Expected >= 4 unique days, got {unique_days}"

    if persona == "weak":
        print("Verifying at least one probe for weak candidate...")
        assert probe_count >= 1, f"Expected >= 1 probe, got {probe_count}"

    print("Verifying final feedback schema...")
    assert final_feedback is not None, "Final feedback is missing"
    assert "summary" in final_feedback
    assert "strengths" in final_feedback
    assert "gaps" in final_feedback
    assert "next" in final_feedback

    print("Verifying state is JSON serializable...")
    try:
        json.dumps(session_state)
        print("JSON serialization passed.")
    except TypeError as e:
        assert False, f"State is not JSON serializable: {e}"

    print(f"Persona {persona.upper()} passed all validation checks.\n")


def main():
    print("Starting Person 1 Validation Suite...")
    
    # 1. import person1.graph - done at top of file
    
    # 2. run weak candidate mock interview
    run_simulation("weak")
    
    # 3. run average candidate mock interview
    run_simulation("average")
    
    # 4. run expert candidate mock interview
    run_simulation("expert")
    
    print("=========================================")
    print("ALL VALIDATION CHECKS PASSED SUCCESSFULLY")
    print("=========================================")


if __name__ == "__main__":
    main()
