"""
contracts.py — Frozen data structures and function signatures for Person 1.

These TypedDicts and stubs define the contract between Person 1 (Agent Brain),
Person 2 (AI Pipeline), and Person 3 (Backend/Frontend).

Do NOT change field names, types, or function signatures without agreement
from all three persons.
"""

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict


# ═══════════════════════════════════════════════════════════════════════════
# Data Contracts
# ═══════════════════════════════════════════════════════════════════════════


class CompetencyEntry(TypedDict):
    """
    Tracks the candidate's proficiency in one curriculum day/module.

    key format in CompetencyMap: "day_02", "day_07", etc.
    """
    day: int                    # curriculum day number (1–30)
    module: str                 # module name, e.g. "Python Basics"
    topic: str                  # specific topic, e.g. "List Comprehensions"
    status: str                 # one of "strong" | "medium" | "weak" | "critical"
    priority: str               # one of "high" | "medium" | "low"
    difficulty_target: int      # 1–5, next difficulty to target for this area
    evidence: str               # free-text evidence from the candidate's answers


# CompetencyMap: dict mapping "day_XX" keys → CompetencyEntry
CompetencyMap = dict[str, CompetencyEntry]


class QuestionArtifact(TypedDict):
    """
    A single interview question produced by Person 2 or pulled from the bank.
    """
    question_id: str            # format "day_XX_qY", e.g. "day_03_q2"
    day: int                    # curriculum day number
    module: str                 # module name
    topic: str                  # specific topic
    difficulty: int             # 1–5
    question_text: str          # the question to ask the candidate
    expected_concepts: list[str]  # concepts the answer should cover
    follow_up_hints: list[str]  # hints for generating probes
    source: str                 # origin: "bank", "llm_generated", etc.


class EvaluationResult(TypedDict):
    """
    Person 2's evaluation of a candidate answer against a question.
    """
    quality: float              # 0.0–1.0, overall answer quality
    matched_concepts: list[str] # concepts the candidate demonstrated
    missing_concepts: list[str] # concepts the candidate missed
    rationale: str              # explanation of the score
    recommended_action: str     # one of "retry" | "probe" | "continue" | "increase_difficulty"


class FinalFeedback(TypedDict):
    """
    The feedback object returned on the final turn.
    Must match this exact shape for Person 3 to render.
    """
    summary: str                # overall performance summary
    strengths: list[str]        # what the candidate did well
    gaps: list[str]             # areas to improve
    next: str                   # recommended next steps


class InterviewState(TypedDict):
    """
    The single source of truth for one interview session.
    All fields are JSON-serializable — Person 3 stores this in SQLite.
    """
    # ── Identity ──────────────────────────────────────────────────────────
    session_id: str
    candidate_id: str
    candidate_name: str

    # ── Phase control ─────────────────────────────────────────────────────
    phase: str                          # "intro" | "question" | "probe" | "evaluate" | "feedback" | "done"

    # ── Competency tracking ───────────────────────────────────────────────
    competency_map: CompetencyMap       # dict[str, CompetencyEntry]

    # ── Question tracking ─────────────────────────────────────────────────
    question_count: int                 # total questions asked so far
    probe_count: int                    # total probes asked so far
    covered_days: list[int]             # curriculum day numbers covered
    asked_question_ids: list[str]       # IDs of questions already asked

    # ── Current turn ──────────────────────────────────────────────────────
    current_question: dict | None       # the active QuestionArtifact or None
    last_user_answer: str | None        # raw text of the candidate's latest answer
    last_answer_quality: float          # 0.0–1.0, from latest evaluation
    last_evaluation: dict | None        # the latest EvaluationResult or None

    # ── Difficulty ────────────────────────────────────────────────────────
    difficulty_level: int               # 1–5, current adaptive difficulty

    # ── Memory ────────────────────────────────────────────────────────────
    conversation_history: list[dict]    # [{"role": "user"|"assistant", "content": str}, ...]
    summary_memory: str                 # compressed summary of earlier turns

    # ── Feedback accumulation ─────────────────────────────────────────────
    strengths: list[str]                # running list of observed strengths
    gaps: list[str]                     # running list of observed gaps

    # ── Completion ────────────────────────────────────────────────────────
    feedback: dict | None               # FinalFeedback dict when done, else None
    done: bool                          # True when interview is finished
    reply: str                          # agent's reply text for this turn
    error: str | None                   # error message if something went wrong


class TurnResult(TypedDict):
    """
    The return value of run_turn().
    Person 3 unpacks this to drive the frontend and persist state.
    """
    reply: str                          # agent's reply text
    state: InterviewState               # updated state dict
    done: bool                          # True on final turn
    feedback: FinalFeedback | None      # non-None only when done=True


# ═══════════════════════════════════════════════════════════════════════════
# Function Contracts (stubs — no business logic yet)
# ═══════════════════════════════════════════════════════════════════════════


def retrieve_question(state: InterviewState) -> QuestionArtifact:
    """
    Select the next question to ask based on the current interview state.

    Uses competency_map, covered_days, asked_question_ids, and
    difficulty_level to pick an adaptive question.

    Called by:  Person 1 (graph nodes)
    Depends on: Person 2 (question bank / LLM generation)

    Args:
        state: Current InterviewState.

    Returns:
        A QuestionArtifact with the next question.

    Raises:
        RuntimeError: If no suitable question can be found.
    """
    raise NotImplementedError("retrieve_question is a stub — implement in Phase 2")


def evaluate_answer(
    question: QuestionArtifact,
    answer: str,
    state: InterviewState,
) -> EvaluationResult:
    """
    Evaluate the candidate's answer against the question's expected concepts.

    Uses Person 2's LLM pipeline (or mock heuristics in tests) to score
    the answer quality and recommend a routing action.

    Called by:  Person 1 (graph nodes)
    Depends on: Person 2 (evaluation pipeline)

    Args:
        question: The QuestionArtifact that was asked.
        answer:   The candidate's raw answer text.
        state:    Current InterviewState (for context/memory).

    Returns:
        An EvaluationResult with quality score, concept matching, and action.
    """
    raise NotImplementedError("evaluate_answer is a stub — implement in Phase 2")


def run_turn(
    session_state: Optional[dict] = None,
    message: Optional[str] = None,
    candidate: Optional[dict] = None,
) -> TurnResult:
    """
    Execute one turn of the interview state machine.

    This is the single public entry point for Person 1.
    Person 3 calls this on every user interaction.

    First call:
        session_state=None, message="hi", candidate={"id": ..., "name": ...}
        → initialises state, runs intro, selects first question.

    Subsequent calls:
        session_state=<previous state dict>, message=<candidate's answer>
        → evaluates answer, routes, emits next question or probe or feedback.

    Final call:
        Returns TurnResult with done=True and feedback != None.

    Args:
        session_state: The state dict from the previous turn, or None for turn 0.
        message:       The candidate's text input.
        candidate:     Dict with "id" and "name" keys. Only used on turn 0.

    Returns:
        TurnResult with reply, updated state, done flag, and optional feedback.
    """
    raise NotImplementedError("run_turn is a stub — implement in Phase 2")
