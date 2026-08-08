# ABTALKS AI Interview Agent — Person 1
# Agent Brain & Orchestration

## Overview
Person 1 owns the interview state machine, LangGraph flow, routing logic,
memory strategy, and final feedback generation.

## Structure
```
person1/
├── __init__.py          # Public exports
├── state.py             # InterviewState TypedDict + helpers
├── curriculum.py        # Question bank (20 questions, 5 days)
├── mocks.py             # Mock Person 2 evaluation stubs
├── memory.py            # Rolling memory compression
├── feedback.py          # Final feedback generator
├── routing.py           # Edge routing (probe / next / wrap)
├── nodes.py             # All LangGraph node functions
├── graph.py             # LangGraph StateGraph definition
├── integration.py       # run_turn() public API
└── tests/
    ├── test_state.py
    ├── test_curriculum.py
    ├── test_routing.py
    ├── test_graph.py
    └── mock_interview.py
```

## Quick Start

### Run the mock interview (automated, no network required)
```bash
python -m person1.tests.mock_interview
```

### Run all unit tests
```bash
pytest person1/tests/ -v
```

### Use the integration function (for Person 3)
```python
from person1 import run_turn

# First turn — pass session_state=None
reply, state, done, feedback = run_turn(
    session_state=None,
    message="Hello, ready to start!",
    candidate={"name": "Alice", "role": "ML Engineer"},
)

# Subsequent turns — pass state back in
while not done:
    user_input = input("Your answer: ")
    reply, state, done, feedback = run_turn(state, user_input)
    print(reply)

# When done=True, feedback has the required shape:
# {
#   "summary": str,
#   "strengths": list[str],
#   "gaps": list[str],
#   "next": str
# }
print(feedback)
```

## Interview Constraints Satisfied
| Constraint | Value |
|---|---|
| Minimum questions asked | ≥ 8 |
| Curriculum days covered | ≥ 4 (of 5 available) |
| Adaptive probes generated | ≥ 1 |
| State JSON-serializable | ✅ (no sets, no datetimes) |
| Final turn done=True + feedback | ✅ |

## Environment Variables (for LLM integration)
```
OPENAI_API_KEY=sk-...    # Optional — mocks work without it
```

## Key Design Decisions
- **Mock-first**: All evaluation and probe generation uses heuristics. No LLM dependency for tests.
- **State-dict pattern**: State is a plain dict — Person 3 can JSON-serialize and store in SQLite.
- **Adaptive difficulty**: Scores ≥4 increase difficulty; scores ≤2 decrease it.
- **Probe logic**: Weak answers (score ≤2) trigger exactly one probe per question.
- **Memory compression**: Every 3 answers are compressed into a `memory_summary` string.
- **LangGraph topology**: graph.py defines the canonical flow for visualisation and LLM integration.

---

## Person 3: Backend & Frontend Architecture

The system is deployed as a FastAPI backend with a SQLite session store, integrating Person 1's orchestrator and Person 2's AI pipeline, and a Next.js frontend UI.

```text
Frontend (Next.js)
       ↓
FastAPI (app.py)
       ↓
SQLite Session Store (session_store.py)
       ↓
Person 1 run_turn()
       ↓
Person 2 Pipeline
```

## Local Setup

1. **Install Backend Dependencies:**
```bash
pip install -r requirements.txt
```

2. **Environment Variables:**
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your_gemini_api_key
FRONTEND_URL=http://localhost:3000
PORT=8000
```

3. **Run the Backend Server:**
```bash
uvicorn app:app --reload
```

4. **Run the Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## API Examples

### 1. Start an Interview Session
```bash
curl -X POST http://localhost:8000/api/interview \
-H "Content-Type: application/json" \
-d '{
  "sessionId": "session-uuid-123",
  "candidate": {
    "id": "cand-001",
    "name": "Jayabalaji"
  }
}'
```

### 2. Send an Answer
```bash
curl -X POST http://localhost:8000/api/interview \
-H "Content-Type: application/json" \
-d '{
  "sessionId": "session-uuid-123",
  "message": "I would use microservices with Kafka."
}'
```

### 3. Fetch Candidates
```bash
curl http://localhost:8000/api/candidates
```

### 4. Check Health
```bash
curl http://localhost:8000/health
```
