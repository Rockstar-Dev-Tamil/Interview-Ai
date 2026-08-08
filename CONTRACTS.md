# ABTALKS AI Interview Agent — Contracts

> **Frozen data structures and function signatures.**
> Share this document with Person 2 and Person 3.
> Do NOT change any field name, type, or function signature without agreement from all three persons.

---

## 1. InterviewState

The single source of truth for one interview session.
All fields are **JSON-serializable** — Person 3 stores this in SQLite.

| Field | Type | Description |
|---|---|---|
| `session_id` | `str` | Unique session identifier |
| `candidate_id` | `str` | Candidate's unique ID |
| `candidate_name` | `str` | Candidate's display name |
| `phase` | `str` | One of `"intro"` · `"question"` · `"probe"` · `"evaluate"` · `"feedback"` · `"done"` |
| `competency_map` | `dict[str, CompetencyEntry]` | Tracks proficiency per curriculum day. Key format: `"day_02"`, `"day_07"`, etc. |
| `question_count` | `int` | Total questions asked so far |
| `probe_count` | `int` | Total probes asked so far |
| `covered_days` | `list[int]` | Curriculum day numbers already covered |
| `asked_question_ids` | `list[str]` | IDs of questions already asked |
| `current_question` | `dict \| None` | The active `QuestionArtifact`, or `None` between turns |
| `last_user_answer` | `str \| None` | Raw text of the candidate's latest answer |
| `last_answer_quality` | `float` | `0.0`–`1.0`, from latest evaluation |
| `last_evaluation` | `dict \| None` | The latest `EvaluationResult`, or `None` |
| `difficulty_level` | `int` | `1`–`5`, current adaptive difficulty |
| `conversation_history` | `list[dict]` | `[{"role": "user"\|"assistant", "content": str}, ...]` |
| `summary_memory` | `str` | Compressed summary of earlier turns |
| `strengths` | `list[str]` | Running list of observed strengths |
| `gaps` | `list[str]` | Running list of observed gaps |
| `feedback` | `dict \| None` | `FinalFeedback` dict when done, else `None` |
| `done` | `bool` | `True` when the interview is finished |
| `reply` | `str` | Agent's reply text for this turn |
| `error` | `str \| None` | Error message if something went wrong |

---

## 2. CompetencyEntry

Tracks the candidate's proficiency in one curriculum day/module.

| Field | Type | Description |
|---|---|---|
| `day` | `int` | Curriculum day number (1–30) |
| `module` | `str` | Module name, e.g. `"Python Basics"` |
| `topic` | `str` | Specific topic, e.g. `"List Comprehensions"` |
| `status` | `str` | One of `"strong"` · `"medium"` · `"weak"` · `"critical"` |
| `priority` | `str` | One of `"high"` · `"medium"` · `"low"` |
| `difficulty_target` | `int` | `1`–`5`, next difficulty to target for this area |
| `evidence` | `str` | Free-text evidence from the candidate's answers |

### CompetencyMap

```python
CompetencyMap = dict[str, CompetencyEntry]
# Key format: "day_02", "day_07", etc.
```

---

## 3. QuestionArtifact

A single interview question produced by Person 2 or pulled from the question bank.

| Field | Type | Description |
|---|---|---|
| `question_id` | `str` | Format `"day_XX_qY"`, e.g. `"day_03_q2"` |
| `day` | `int` | Curriculum day number |
| `module` | `str` | Module name |
| `topic` | `str` | Specific topic |
| `difficulty` | `int` | `1`–`5` |
| `question_text` | `str` | The question to ask the candidate |
| `expected_concepts` | `list[str]` | Concepts the answer should cover |
| `follow_up_hints` | `list[str]` | Hints for generating probes |
| `source` | `str` | Origin: `"bank"`, `"llm_generated"`, etc. |

---

## 4. EvaluationResult

Person 2's evaluation of a candidate answer against a question.

| Field | Type | Description |
|---|---|---|
| `quality` | `float` | `0.0`–`1.0`, overall answer quality |
| `matched_concepts` | `list[str]` | Concepts the candidate demonstrated |
| `missing_concepts` | `list[str]` | Concepts the candidate missed |
| `rationale` | `str` | Explanation of the score |
| `recommended_action` | `str` | One of `"retry"` · `"probe"` · `"continue"` · `"increase_difficulty"` |

---

## 5. FinalFeedback

The feedback object returned on the final turn. **Must match this exact shape** for Person 3 to render.

```json
{
  "summary": "string",
  "strengths": ["string", "..."],
  "gaps": ["string", "..."],
  "next": "string"
}
```

| Field | Type | Description |
|---|---|---|
| `summary` | `str` | Overall performance summary |
| `strengths` | `list[str]` | What the candidate did well |
| `gaps` | `list[str]` | Areas to improve |
| `next` | `str` | Recommended next steps |

---

## 6. TurnResult

The return value of `run_turn()`. Person 3 unpacks this to drive the frontend and persist state.

| Field | Type | Description |
|---|---|---|
| `reply` | `str` | Agent's reply text |
| `state` | `InterviewState` | Updated state dict |
| `done` | `bool` | `True` on the final turn |
| `feedback` | `FinalFeedback \| None` | Non-`None` only when `done=True` |

---

## 7. Function Signatures

### `run_turn` — Person 1 public entry point

```python
def run_turn(
    session_state: Optional[dict] = None,
    message: Optional[str] = None,
    candidate: Optional[dict] = None,
) -> TurnResult:
```

| Scenario | `session_state` | `message` | `candidate` |
|---|---|---|---|
| **First call** | `None` | `"hi"` | `{"id": "...", "name": "..."}` |
| **Subsequent calls** | previous `state` dict | candidate's answer | omitted |
| **Final return** | — | — | — |

Returns `TurnResult` with `done=True` and `feedback != None` on the final turn.

---

### `retrieve_question` — Question selection

```python
def retrieve_question(state: InterviewState) -> QuestionArtifact:
```

Uses `competency_map`, `covered_days`, `asked_question_ids`, and `difficulty_level` to pick an adaptive question.

- **Called by:** Person 1 (graph nodes)
- **Depends on:** Person 2 (question bank / LLM generation)

---

### `evaluate_answer` — Answer evaluation

```python
def evaluate_answer(
    question: QuestionArtifact,
    answer: str,
    state: InterviewState,
) -> EvaluationResult:
```

Scores the answer quality and recommends a routing action.

- **Called by:** Person 1 (graph nodes)
- **Depends on:** Person 2 (evaluation pipeline)

---

## 8. Integration Flow

```
Person 3 (Backend)                   Person 1 (Agent Brain)                    Person 2 (AI Pipeline)
       │                                      │                                        │
       │──── run_turn(None, msg, cand) ──────>│                                        │
       │                                      │──── retrieve_question(state) ─────────>│
       │                                      │<──── QuestionArtifact ─────────────────│
       │<──── TurnResult (reply, state) ──────│                                        │
       │                                      │                                        │
       │──── run_turn(state, answer) ────────>│                                        │
       │                                      │──── evaluate_answer(q, ans, st) ──────>│
       │                                      │<──── EvaluationResult ─────────────────│
       │                                      │                                        │
       │                                      │  [routing: probe / next Q / wrap]      │
       │                                      │                                        │
       │<──── TurnResult (reply, state) ──────│                                        │
       │         ...repeats...                │                                        │
       │                                      │                                        │
       │<──── TurnResult (done=True, fb) ─────│                                        │
       │                                      │                                        │
```

---

## 9. Constraints

| Constraint | Value |
|---|---|
| Minimum questions asked | ≥ 8 |
| Curriculum days covered | ≥ 4 |
| Adaptive probes generated | ≥ 1 |
| State JSON-serializable | ✅ (for SQLite) |
| Final turn `done=True` + valid feedback | ✅ |
| Python version | 3.11+ |

---

> [!IMPORTANT]
> All changes to these contracts require sign-off from Person 1, Person 2, and Person 3.
