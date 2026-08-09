from person1.graph import run_turn
import json

candidate = {"id": "CAND-001", "name": "Alex Turner", "role": "Software Engineer"}
print("Turn 1...")
result1 = run_turn(session_state=None, message="hi", candidate=candidate)
print("Turn 1 complete. Replying with an answer...")

state = result1["state"]
result2 = run_turn(session_state=state, message="Because it isolates dependencies!")
print("Turn 2 complete:", result2)
