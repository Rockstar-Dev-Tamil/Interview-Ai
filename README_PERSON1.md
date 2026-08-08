# Person 1: Interview Engine

This module contains the core LangGraph-based state machine for conducting technical interviews. It handles the interview lifecycle, including introductions, question traversal, answer evaluation, Socratic probing, adaptive difficulty, and final feedback generation.

## How to Run Locally

You can test the interview flow directly using the local mock scripts. Ensure you are in the project root:

```bash
# Run a mock interview with an average candidate persona
python scripts/run_mock_interview.py --persona average

# Run a full suite of automated end-to-end validation checks
python scripts/validate_person1.py
```

## How to Run Tests

All unit tests are written using `pytest`. They cover state transitions, edge case handling, and pipeline adapter integration.

```bash
# Run all tests
pytest tests/ person1/tests/
```

## How Person 3 Integrates (`run_turn`)

Person 3 (the Backend/API layer) interfaces with Person 1 through a single stateless function:

```python
from person1.graph import run_turn

turn_result = run_turn(
    session_state=current_state,  # dict or None
    message=user_input,           # str or None
    candidate=candidate_info      # dict or None
)
```

### Example Request/Response Flow

1. **Initial Turn (Start Interview)**:
   - Call `run_turn(session_state=None, message=None, candidate={"name": "Alice"})`
   - Returns a `TurnResult` containing the `reply` (the intro + first question), a newly initialized JSON-serializable `state`, and `done=False`.
   - **Person 3 Action**: Store the returned `state` in the database. Send the `reply` to the user via WebSocket/HTTP.

2. **Subsequent Turns (Answering Questions)**:
   - Retrieve the stored `state` from the database.
   - Call `run_turn(session_state=stored_state, message="I would use pip install -e.")`
   - Returns a new `TurnResult` with the agent's next `reply` (a probe or the next question), the updated `state`, and `done=False`.
   - **Person 3 Action**: Update the database with the new `state`. Send the `reply` to the user.

3. **End of Interview**:
   - Once curriculum constraints (or maximum turns) are reached, `run_turn` will return a `TurnResult` where `done=True`.
   - The result will contain a generated `feedback` dictionary containing strengths, gaps, and professional recommendations.
   - **Person 3 Action**: Update the database, send the final feedback, and close the session.

### State Persistence Shape

The `state` returned by `run_turn` is **strictly JSON-serializable**. Person 3 must persist it (e.g., in Postgres, MongoDB, or Redis) between requests. Do not modify the state directly outside of `run_turn`.

```json
{
    "session_id": "uuid",
    "candidate_name": "Alice",
    "question_count": 4,
    "probe_count": 1,
    "covered_days": [2, 10, 15],
    "asked_question_ids": ["day_02_q1", "day_10_q2"],
    "current_question": { ... },
    "last_answer_quality": 0.8,
    "difficulty_level": 3,
    "phase": "question",
    "conversation_history": [ ... ],
    "strengths": [ ... ],
    "gaps": [ ... ]
}
```

## How Person 2 Pipeline is Injected

By default, Person 1 uses a local mock pipeline (`person1/mocks/pipeline_mock.py`). 
Once Person 2 completes the real curriculum generation and LLM-based evaluation pipeline, Person 1 will automatically attempt to use it via the adapter in `person1/pipeline_adapter.py`.

If you need to explicitly inject the real pipeline during a run (e.g., in production):

```python
from person1.pipeline_adapter import get_pipeline
from person1.graph import run_turn

# Returns the real pipeline if available, otherwise safely falls back to the mock
production_pipeline = get_pipeline(use_real_pipeline=True)

turn_result = run_turn(
    session_state=state,
    message=user_input,
    pipeline=production_pipeline
)
```
