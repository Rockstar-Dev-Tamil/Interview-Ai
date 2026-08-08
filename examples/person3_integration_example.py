"""
Person 3 Integration Example

This script demonstrates how Person 3 (the backend/API layer) should 
interact with the Person 1 interview engine.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from person1.graph import run_turn


def main():
    print("--- Person 3 Integration Simulation ---\n")

    # 1. Call run_turn with no state, no message, but candidate object
    candidate_profile = {
        "id": "c_123",
        "name": "Jane Doe",
        "role": "Backend Developer"
    }
    
    print("1. Starting interview session...")
    turn_result = run_turn(session_state=None, message=None, candidate=candidate_profile)
    
    # 2. Store returned state
    # (In reality, Person 3 will serialize this dictionary and save it to a database)
    db_stored_state = turn_result["state"]
    
    print(f"Interviewer: {turn_result['reply']}\n")

    # 3. Call run_turn with stored state and candidate answer
    # 4. Repeat until done
    simulated_answers = [
        "I would use pip install -e to install it in editable mode for development, modifying setup.py.",
        "I'd write unit tests with pytest and mock any external dependencies to ensure isolation.",
        "A dictionary has O(1) lookup time, whereas a list is O(n). I'd use a dict for fast access.",
        "I would optimize the SQL query and add indexes to the database schema.",
        "I use Docker to containerize the application to ensure environments match.",
        "A load balancer distributes traffic across multiple instances to ensure high availability.",
        "I'd use Redis for caching frequent database queries to improve read times.",
        "I always prioritize integration testing for all core modules."
    ]

    for i, answer in enumerate(simulated_answers):
        if turn_result["done"]:
            break
            
        print(f"Candidate: {answer}")
        
        # Load state from DB
        current_state = db_stored_state
        
        # Run next turn
        turn_result = run_turn(session_state=current_state, message=answer)
        
        # Update state in DB
        db_stored_state = turn_result["state"]
        
        print(f"Interviewer: {turn_result['reply']}\n")

    # 5. Print final feedback
    if turn_result["done"]:
        print("--- Interview Finished ---")
        print("Final Feedback Generated:")
        feedback = turn_result["feedback"]
        for key, value in feedback.items():
            print(f"  {key.capitalize()}: {value}")
    else:
        print("--- End of simulated answers (Interview not fully completed yet) ---")


if __name__ == "__main__":
    main()
