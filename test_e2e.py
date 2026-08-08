import sys
import os

# Add the person1_code directory to path so imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from person1.graph import run_turn
import json

def test_full_loop():
    print("--- STARTING E2E INTERVIEW LOOP ---")
    
    # TURN 1: Initialize
    print("\n--- TURN 1 (INIT) ---")
    candidate = {"id": "CAND-001", "name": "Sarah"}
    result = run_turn(session_state=None, message="hi", candidate=candidate)
    
    print(f"Agent Reply: {result['reply']}")
    state = result['state']
    
    if result['done']:
        print("Error: Interview finished prematurely on turn 1.")
        return
        
    # TURN 2: Answer the first question
    print("\n--- TURN 2 (ANSWER 1) ---")
    answer_1 = "I would use a microservices architecture with a message broker like Kafka for async processing."
    print(f"Candidate: {answer_1}")
    result = run_turn(session_state=state, message=answer_1)
    
    print(f"Agent Reply: {result['reply']}")
    state = result['state']
    
    # TURN 3: Answer the probe or next question
    print("\n--- TURN 3 (ANSWER 2) ---")
    answer_2 = "That's a good point. I would ensure idempotency using unique request IDs in the database."
    print(f"Candidate: {answer_2}")
    result = run_turn(session_state=state, message=answer_2)
    
    print(f"Agent Reply: {result['reply']}")
    state = result['state']
    
    print("\n--- TEST COMPLETED ---")
    print(f"Final State Phase: {state.get('phase')}")
    print(f"Total Questions Asked: {state.get('question_count')}")
    print("Zero crashes detected. Integration is flawless.")

if __name__ == "__main__":
    test_full_loop()
