import asyncio
from person1.graph import run_turn

state = {
    "session_id": "test",
    "candidate_id": "1",
    "candidate_name": "Test",
    "phase": "intro",
    "current_question": {"question_text": "hello?"},
    "question_count": 1
}

res = run_turn(session_state=state, message="my answer")
print("REPLY:", res.get('reply'))
print("ERROR:", res.get('state', {}).get('error'))
