# AI-Assisted Development Prompts

This document contains all the AI prompts used to generate the Agent Brain, the Data/Retrieval/Evaluation Pipeline, and the Backend/Frontend implementations.

---

## 1. Person 1 (Agent Brain & Orchestration) Prompts

# PERSON1_PROMPTS.md
# Antigravity Prompt Pack — Person 1: Agent Brain & Orchestration
# ABTALKS AI Interview Agent Hackathon

## HOW TO USE
1. Work in Antigravity (agent mode).
2. Paste PROMPT 0 first. In every new chat, paste PROMPT 0 again.
3. Then paste PROMPT 1 → PROMPT 10 in order.
4. Move to the next prompt ONLY when the listed tests pass.
5. Never edit Person 2 or Person 3 files.
6. Keep everything JSON-serializable (Person 3 stores state in SQLite).

---

## PROMPT 0 — GLOBAL CONTEXT (paste first)

You are helping me build Person 1 (Agent Brain & Orchestration) for the ABTALKS AI Interview Agent hackathon.

My job: the stateful interview brain that reads candidate competency data, decides what to ask, evaluates answers, probes weak answers, raises difficulty on strong answers, remembers context, and ends with structured feedback.

Constraints:
- Python 3.11+, LangGraph
- All Person 1 code lives in person1/
- No FastAPI, no Person 3 files
- No live network calls in tests; use mocked Person 2 functions until real pipeline exists
- All state JSON-serializable
- Write and run tests after every phase

Frozen integration function (Person 3 will call this):
run_turn(session_state: Optional[dict], message: Optional[str], candidate: Optional[dict] = None)
returns: (reply, new_state, done, feedback)

Final feedback schema (EXACT keys):
summary: str, strengths: list[str], gaps: list[str], next: str

Hard requirements for the interview:
- Minimum 8 questions
- At least 4 different curriculum days covered
- At least one adaptive follow-up (probe) generated from a previous answer
- State survives across multiple run_turn calls
- Final turn returns done=True with valid feedback

Act as a senior AI engineer. Build step by step.

---

## PROMPT 1 — PHASE 0: CONTRACT FREEZE

Create a contract-first skeleton.

Files to create:
- CONTRACTS.md
- person1/__init__.py
- person1/contracts.py

No business logic yet. Only TypedDicts, stub signatures, and documentation.

Define exactly these shapes:

InterviewState:
session_id str, candidate_id str, candidate_name str,
phase str ("intro"|"question"|"probe"|"evaluate"|"feedback"|"done"),
competency_map dict, question_count int, probe_count int,
covered_days list[int], asked_question_ids list[str],
current_question dict|None, last_user_answer str|None,
last_answer_quality float (0-1), last_evaluation dict|None,
difficulty_level int (1-5), conversation_history list[dict],
summary_memory str, strengths list[str], gaps list[str],
feedback dict|None, done bool, reply str, error str|None

CompetencyEntry:
day int, module str, topic str,
status ("strong"|"medium"|"weak"|"critical"),
priority ("high"|"medium"|"low"),
difficulty_target int, evidence str
CompetencyMap = dict keyed like "day_02"

QuestionArtifact:
question_id ("day_XX_qY"), day int, module str, topic str,
difficulty int 1-5, question_text str,
expected_concepts list[str], follow_up_hints list[str], source str

EvaluationResult:
quality float 0-1, matched_concepts list[str],
missing_concepts list[str], rationale str,
recommended_action ("retry"|"probe"|"continue"|"increase_difficulty")

FinalFeedback:
summary str, strengths list[str], gaps list[str], next str

TurnResult:
reply str, state dict, done bool, feedback dict|None

Stub signatures:
retrieve_question(state) -> QuestionArtifact
evaluate_answer(question, answer, state) -> EvaluationResult
run_turn(session_state, message, candidate=None) -> TurnResult

Write CONTRACTS.md documenting all of this so I can share it with Person 2 and Person 3.
Verify: python -c "import person1.contracts" works.

---

## PROMPT 2 — PHASE 1: SCAFFOLD + MOCKED PERSON 2 PIPELINE

Build the dev scaffold and a mocked Person 2 pipeline so I can build without waiting.

Files:
- person1/types.py
- person1/mocks/__init__.py
- person1/mocks/pipeline_mock.py
- person1/utils.py
- tests/__init__.py
- tests/test_mock_pipeline.py
- requirements.txt (langgraph, pytest)

Mock pipeline behavior:

1. retrieve_question(state)
- selects by weakness, NOT random and NOT curriculum order
- prefers high-priority weak/critical days from competency_map
- never repeats question_id already in asked_question_ids
- must be able to cover at least 4 different days
- respects difficulty_level
- returns a valid QuestionArtifact

2. evaluate_answer(question, answer, state)
- deterministic, no LLM
- empty answer or "not sure" -> low quality
- answer containing several expected_concepts -> high quality
- partial answer -> medium quality
- returns quality 0-1, matched_concepts, missing_concepts, rationale, recommended_action

Fake curriculum: at least 10 questions across at least 6 days, using realistic topics:
Day 2 Python environments, Day 7 data cleaning, Day 12 embeddings,
Day 18 LLM fine-tuning, Day 22 chatbot memory, Day 26 agents and tools,
Day 29 monitoring, Day 31 capstone deployment.

Tests:
- retrieve_question returns valid artifact
- no repeated question ids
- quality within 0-1
- "not sure" gets low score
- concept-rich answer gets high score
Run tests and make them pass.

---

## PROMPT 3 — PHASE 2: STATE FACTORY + MEMORY HELPERS

Files:
- person1/state.py
- tests/test_state.py

Functions:

1. create_initial_state(candidate=None, session_id=None)
question_count=0, probe_count=0, covered_days=[], asked_question_ids=[],
difficulty_level=2, phase="intro", summary_memory="", strengths=[], gaps=[],
done=False. Use candidate name/id/job role if present. Generate session_id if missing.

2. append_message(state, role, content, turn_type="message")
role: interviewer|candidate. turn_type: question|answer|probe|system|feedback.

3. trim_history(state, max_turns=4)
keep only latest 4 turns in conversation_history; compress older context into summary_memory.

4. update_summary_memory(state, new_information)
append concise notes, keep bounded length.

5. serialize_state(state) / deserialize_state(data)
JSON-safe round trip; fill missing fields with defaults on load.

Rules: no datetime objects, no functions, no non-serializable values in state.

Tests: valid init; append works; trim keeps 4; round trip preserves fields; json.dumps(state) works.
Run tests and make them pass.

---

## PROMPT 4 — PHASE 3: ROUTING, DIFFICULTY, SOCRATIC PROBING, FEEDBACK

Files:
- person1/reasoning.py
- person1/feedback.py
- tests/test_reasoning.py
- tests/test_feedback.py

reasoning.py:

1. route_after_evaluation(state) -> one of "retry"|"probe"|"continue"|"increase_difficulty"|"feedback"
Rules:
- question_count >= 10 -> feedback
- question_count >= 8 AND unique covered_days >= 4 AND last_answer_quality >= 0.65 -> feedback
- last_answer_quality < 0.4 AND probe_count < 3 -> probe
- last_answer_quality > 0.8 -> increase_difficulty
- else continue

2. adjust_difficulty(state, evaluation)
quality > 0.8 -> +1 (max 5); quality < 0.3 -> -1 (min 1); else unchanged.

3. generate_socratic_probe(state, question, answer, evaluation)
Adaptive follow-up built from missing_concepts and the candidate's actual answer.
Examples: "You mentioned X — but how would that handle Y?", "What edge case breaks this approach?", "How does this scale under production load?"
If nothing missing, ask a deeper trade-off/scalability question. Never generic.

4. mark_day_covered(state, day) — add day if absent.

5. update_strengths_and_gaps(state, question, evaluation)
quality >= 0.7 -> add strength (topic); quality < 0.4 -> add gap (missing concepts); no duplicates.

feedback.py:
generate_final_feedback(state) -> EXACT keys: summary, strengths, gaps, next.
summary mentions questions asked, days covered, overall performance.
next = concrete next learning step. Neutral wording if lists are empty.

Tests for every routing rule, difficulty up/down, probe mentions missing concept, feedback exact keys.
Run tests and make them pass.

---

## PROMPT 5 — PHASE 4: LANGGRAPH NODES

Files:
- person1/nodes.py
- tests/test_nodes.py

Design: nodes accept state and return partial state updates. Never mutate input state. Pipeline is injected; default = mock pipeline.

Nodes:

1. intro_node — first turn. Interviewer intro + first question via retrieve_question. Sets current_question, question_count += 1, covered_days, asked_question_ids, reply, phase="question".

2. evaluate_answer_node — if answer empty/None: reply politely asking to answer current question, no evaluation. Otherwise call evaluate_answer; store last_evaluation and last_answer_quality; update strengths/gaps; append brief note to summary_memory; phase="evaluate".

3. route_decision_node — sets next_route using route_after_evaluation.

4. probe_node — reply = generate_socratic_probe(...); probe_count += 1 (NOT question_count); log to history; phase="probe".

5. next_question_node — retrieve_question; question_count += 1; update current_question, covered_days, asked_question_ids; reply = question; phase="question".

6. feedback_node — generate_final_feedback; set feedback; done=True; phase="done"; closing reply.

Tests: intro asks first question; empty answer safe; quality stored; probe_count increments; question_count increments; feedback node returns done=True with exact schema.
Run tests and make them pass.

---

## PROMPT 6 — PHASE 5: graph.py + run_turn (MAIN DELIVERABLE)

Files:
- person1/graph.py
- tests/test_graph.py

Expose:
run_turn(session_state, message, candidate=None) -> TurnResult(reply, state, done, feedback)

Build a compiled LangGraph StateGraph:
START -> intro_node (if new session) OR evaluate_answer_node (if answer received)
-> route_decision_node -> conditional edge:
retry = re-ask current question
probe = probe_node
continue = next_question_node
increase_difficulty = adjust difficulty then next_question_node
feedback = feedback_node
-> END

Behavior:
- Turn 1: session_state None + candidate provided -> intro + first question, done=False, feedback=None.
- Later turns: store candidate message in history, evaluate, route, reply, return updated state.
- State must survive across calls (returned state is the next input).
- Enforce min 8 questions and 4 unique days before feedback.
- Safety cap max_questions = 12 -> force feedback.
- Invalid or partial state -> friendly error reply, never crash.
- Pipeline injectable; default mock.

Test (simulate full interview using ONLY run_turn):
start with candidate -> get first reply -> send 8+ answers including one weak answer that triggers a probe -> continue until done=True.
Assert: question_count >= 8; unique covered_days >= 4; probe_count >= 1; feedback has exact keys summary/strengths/gaps/next.
Run tests and make them pass.

---

## PROMPT 7 — PHASE 6: LOCAL MOCK INTERVIEW SCRIPT (DELIVERABLE #2)

File:
- scripts/run_mock_interview.py

Simulate a full interview with NO FastAPI, using run_turn only.
Print each interviewer reply and candidate answer. Run until done=True. Print final feedback.

Personas:
- weak: shallow answers, sometimes "not sure", MUST trigger at least one probe
- average: mixed partial and good answers
- expert: strong answers, should trigger difficulty increase

CLI:
python scripts/run_mock_interview.py --persona weak
python scripts/run_mock_interview.py --persona average
python scripts/run_mock_interview.py --persona expert
(default: average)

End summary printed: total questions, unique days covered, probe count, done status, final feedback.
Assertions: question_count >= 8; unique days >= 4; weak persona probe_count >= 1; done is True; feedback keys exact.

Run the weak persona end-to-end successfully.

---

## PROMPT 8 — PHASE 7: PERSON 2 INTEGRATION ADAPTER

Files:
- person1/pipeline_adapter.py
- tests/test_pipeline_adapter.py

Implement:
get_pipeline(use_real_pipeline=False)
- default: mock pipeline
- if True: try importing Person 2's retrieve_question and evaluate_answer
- on import failure: fall back to mock with a warning, never crash

wrap_real_pipeline(retrieve_fn, evaluate_fn)
- returns an object exposing retrieve_question and evaluate_answer

Do not break existing tests.
Tests: default is mock; wrapping custom functions works; graceful fallback works.
Run tests and make them pass.

---

## PROMPT 9 — PHASE 8: EDGE CASE HARDENING

Update: person1/graph.py, person1/nodes.py
Add: tests/test_edge_cases.py

Handle safely:
1. Empty answer -> polite re-ask; do NOT increment question_count
2. Very short answer -> low/medium quality; may trigger probe
3. Off-topic answer -> redirect back to the current question
4. Very long answer -> truncate/summarize before evaluating; keep state small
5. Candidate asks a question instead of answering -> acknowledge briefly, then re-ask current question
6. Corrupted or partial state -> rebuild safe defaults; sanitize non-serializable values before returning
7. max_questions = 12 reached -> generate feedback and finish
8. retrieve_question finds no new question -> gracefully go to feedback

Add one test per case. Run all tests and make them pass.

---

## PROMPT 10 — PHASE 9: VALIDATION + PERSON 3 HANDOFF

Files:
- README_PERSON1.md
- scripts/validate_person1.py
- examples/person3_integration_example.py

README_PERSON1.md: how to run locally, how to run tests, how Person 3 calls run_turn, example request/response flow, state shape to persist, how Person 2 pipeline is injected.

validate_person1.py runs all checks:
import graph; run weak, average, expert mock interviews; verify 8+ questions; 4+ days; 1+ probe for weak; feedback schema; state JSON-serializable.

examples/person3_integration_example.py simulates Person 3 (no FastAPI):
1. run_turn(None, None, candidate)
2. store returned state
3. loop run_turn(state, answer) until done
4. print final feedback

Run: python scripts/validate_person1.py — must pass.

---

## DEBUG PROMPT (use when anything fails)

The last change failed or misbehaved.
1. Show the exact failing command and output.
2. Identify root cause.
3. Fix only the smallest necessary part.
4. Re-run the relevant tests.
5. No unrelated refactors.
6. Keep state JSON-serializable.
7. Keep the run_turn signature unchanged.

---

## EMERGENCY SCOPE-CUT PROMPT (if running out of time)

We are short on time. Reduce Person 1 to the minimum viable version:
keep run_turn signature unchanged; keep mock pipeline; keep LangGraph simple;
ensure 8+ questions, 4+ covered days, 1+ probe, feedback keys summary/strengths/gaps/next;
lightweight but passing tests. Prioritize a working end-to-end mock interview over perfect architecture.

---

## TEAM CONTRACT MESSAGES (copy to group chat)

To Person 2:
Person 1 needs these two functions from you:
retrieve_question(state) -> QuestionArtifact(question_id, day, module, topic, difficulty, question_text, expected_concepts, follow_up_hints, source)
evaluate_answer(question, answer, state) -> EvaluationResult(quality 0-1, matched_concepts, missing_concepts, rationale, recommended_action)
I will build against mocks until your real functions exist.

To Person 3:
Integration point:
from person1.graph import run_turn
reply, new_state, done, feedback = run_turn(session_state, message, candidate)
Turn 1: session_state=None, message=None, candidate=<candidate json>
Later: session_state=<previous returned state>, message=<candidate answer>, candidate=None
Persist new_state in SQLite by sessionId. State is JSON-serializable.
Return to HTTP: {"reply": reply, "done": done, "feedback": feedback}

---

## 2. Person 2 (System Prompts)

This section contains the exact system prompts and LLM instructions used by the Data, Retrieval & Evaluation pipeline (`pipeline.py`).

These prompts were passed to the `gemini-3.5-flash-lite` model using LangChain's `PromptTemplate`.

### 2.1 Curriculum Enrichment Prompt
**Purpose:** Used internally by the pre-computation script (`build_index.py`) to analyze the raw JSON curriculum and autonomously generate interview questions, Socratic traps, and real-world scenarios.

**The Prompt:**
```text
You are an expert technical interviewer.
Analyze this curriculum day: Module: {module}, Title: {title}, Objectives: {objectives}.
Generate enriched interview metadata based on the schema.
```

**Structured Output Schema (Pydantic):**
- `key_concepts` (List of Strings)
- `interview_questions` (List of Strings)
- `follow_up_traps` (List of Strings)
- `real_world_scenarios` (List of Strings)
- `difficulty` (Integer 1-5)

### 2.2 Answer Evaluation Prompt
**Purpose:** Used by the conversational agent during the live interview to grade the candidate's raw answer against the target question.

**The Prompt:**
```text
You are evaluating a candidate's answer to the following technical question.
Question: {question}
Expected Concepts: {concepts}
Candidate's Answer: {answer}
Evaluate the technical depth, correctness, and completeness of the answer.
```

**Structured Output Schema (Pydantic):**
- `quality` (Float 0.0 to 1.0)
- `matched_concepts` (List of Strings)
- `missing_concepts` (List of Strings)
- `rationale` (String)
- `recommended_action` (String)

### 2.3 DeepEval Hallucination Metric
**Purpose:** An automated validation check that prevents the LLM from inventing fake weaknesses that contradict the candidate's actual answer.

**Configuration:**
- **Metric:** `HallucinationMetric`
- **Threshold:** `0.5` (Enforces high logical grounding)
- **Context Provided:** The candidate's raw answer is injected directly as the source of truth `context` to validate the generated `feedback`.

---

## 3. Person 3 (Backend + Frontend) Prompts

### Initial Request
```markdown
# PERSON 3 — BACKEND + SESSION + FRONTEND IMPLEMENTATION PROMPT
...
(The massive prompt provided by the user)
...
```

### Backend and Database
- "Implement a FastAPI backend based on the Person 3 prompt."
- "Create Pydantic models in `schemas.py` that match the contracts exactly."
- "Implement a SQLite session store in `session_store.py` with parameterized queries to persist the `InterviewState` JSON."
- "Write `test_api.py` covering the 10 requested edge cases, and `test_personas.py` for E2E testing of weak, average, and expert candidates."

### Frontend
- "Create a Next.js application with Tailwind CSS."
- "Create a landing page with candidate information and a Start Interview button."
- "Create the main chat UI that dynamically updates with agent replies, handles empty answers, loading states, and disabled input states."
- "Create a dynamic feedback dashboard rendering the FinalFeedback JSON object."

### Infrastructure
- "Generate a Dockerfile and .dockerignore for the FastAPI backend, exposing port 8000 and persisting the SQLite DB."
- "Update README.md with architecture, local setup instructions, environment variables, and API examples."

### Final Polish & API Refinements
- "Remove hardcoded check for question marks in `person1/nodes.py` to allow the LLM to naturally handle candidate questions."
- "Handle React StrictMode double-mounting by returning the existing state rather than appending an empty message."
- "Update `person2/pipeline.py` to use `gemini-flash-lite-latest` instead of hardcoded older models."
- "Create `/api/candidates` endpoint to securely serve candidate profiles from `candidates.json`."
- "Implement dynamic candidate selection on the start screen with professional styling and experience metrics."
- "Refine Interview UI with Question Count progress, animated typing indicators, and robust error recovery states."
- "Polish Feedback Dashboard to strictly match the requested visual hierarchy (Overview, Strengths, Areas to Improve, Next Steps)."
