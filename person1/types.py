"""
types.py — Re-exports and factory helpers for the frozen contracts.

All TypedDicts live in contracts.py.  This module adds:
  - make_initial_state()  — build a blank InterviewState
  - make_competency_entry() — build a CompetencyEntry with defaults
  - Convenience re-exports so downstream code can do:
        from person1.types import InterviewState, make_initial_state
"""

from __future__ import annotations

import uuid
from typing import Optional

from .contracts import (
    InterviewState,
    CompetencyEntry,
    CompetencyMap,
    QuestionArtifact,
    EvaluationResult,
    FinalFeedback,
    TurnResult,
)

__all__ = [
    "InterviewState",
    "CompetencyEntry",
    "CompetencyMap",
    "QuestionArtifact",
    "EvaluationResult",
    "FinalFeedback",
    "TurnResult",
    "make_initial_state",
    "make_competency_entry",
]


# ───────────────────────────────────────────────────────────────────────────
# Factories
# ───────────────────────────────────────────────────────────────────────────

def make_initial_state(
    candidate_id: str = "",
    candidate_name: str = "",
    session_id: Optional[str] = None,
) -> InterviewState:
    """Return a fresh InterviewState with every field initialised."""
    return InterviewState(
        session_id=session_id or str(uuid.uuid4()),
        candidate_id=candidate_id,
        candidate_name=candidate_name,
        phase="intro",
        competency_map={},
        question_count=0,
        probe_count=0,
        covered_days=[],
        asked_question_ids=[],
        current_question=None,
        last_user_answer=None,
        last_answer_quality=0.0,
        last_evaluation=None,
        difficulty_level=2,
        conversation_history=[],
        summary_memory="",
        strengths=[],
        gaps=[],
        feedback=None,
        done=False,
        reply="",
        error=None,
    )


def make_competency_entry(
    day: int,
    module: str,
    topic: str,
    *,
    status: str = "weak",
    priority: str = "medium",
    difficulty_target: int = 2,
    evidence: str = "",
) -> CompetencyEntry:
    """Build a CompetencyEntry with sensible defaults."""
    return CompetencyEntry(
        day=day,
        module=module,
        topic=topic,
        status=status,
        priority=priority,
        difficulty_target=difficulty_target,
        evidence=evidence,
    )
