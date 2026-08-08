"""
pipeline_mock.py — Mocked Person 2 pipeline.

Provides deterministic, offline implementations of:
  - retrieve_question(state)  → QuestionArtifact
  - evaluate_answer(question, answer, state)  → EvaluationResult

Uses a built-in FAKE_CURRICULUM of ≥ 10 questions across ≥ 6 curriculum days.
No LLM calls, no network — suitable for unit tests and local development.
"""

from __future__ import annotations

import random
from typing import Any

from person1.contracts import (
    InterviewState,
    QuestionArtifact,
    EvaluationResult,
    CompetencyEntry,
)
from person1.utils import clamp, day_key


# ═══════════════════════════════════════════════════════════════════════════
# Fake Curriculum — ≥ 10 questions, ≥ 6 days
# ═══════════════════════════════════════════════════════════════════════════

FAKE_CURRICULUM: list[QuestionArtifact] = [
    # ── Day 2: Python Environments ─────────────────────────────────────
    QuestionArtifact(
        question_id="day_02_q1",
        day=2,
        module="Python Environments",
        topic="Virtual Environments",
        difficulty=1,
        question_text="Explain the purpose of a Python virtual environment. How does `venv` differ from `conda`?",
        expected_concepts=["isolation", "dependencies", "venv", "conda", "reproducibility"],
        follow_up_hints=["How would you share your environment with a teammate?"],
        source="bank",
    ),
    QuestionArtifact(
        question_id="day_02_q2",
        day=2,
        module="Python Environments",
        topic="Package Management",
        difficulty=2,
        question_text="What is the difference between `pip install` and `pip install -e`? When would you use editable mode?",
        expected_concepts=["pip", "editable", "development", "setup.py", "pyproject.toml"],
        follow_up_hints=["How does editable mode interact with version pinning?"],
        source="bank",
    ),

    # ── Day 7: Data Cleaning ───────────────────────────────────────────
    QuestionArtifact(
        question_id="day_07_q1",
        day=7,
        module="Data Cleaning",
        topic="Missing Values",
        difficulty=2,
        question_text="You receive a dataset where 30% of a column is NaN. Walk me through your strategy for handling it.",
        expected_concepts=["imputation", "mean", "median", "drop", "domain knowledge", "missing at random"],
        follow_up_hints=["How would your approach change for time-series data?"],
        source="bank",
    ),
    QuestionArtifact(
        question_id="day_07_q2",
        day=7,
        module="Data Cleaning",
        topic="Outlier Detection",
        difficulty=3,
        question_text="Compare IQR-based and Z-score-based outlier detection. When might each give misleading results?",
        expected_concepts=["IQR", "Z-score", "normal distribution", "skewed data", "robust statistics"],
        follow_up_hints=["What about isolation forests for high-dimensional data?"],
        source="bank",
    ),

    # ── Day 12: Embeddings ─────────────────────────────────────────────
    QuestionArtifact(
        question_id="day_12_q1",
        day=12,
        module="Embeddings",
        topic="Word Embeddings",
        difficulty=3,
        question_text="Explain how Word2Vec learns word embeddings. What is the key insight behind the skip-gram model?",
        expected_concepts=["context window", "skip-gram", "CBOW", "cosine similarity", "distributed representation"],
        follow_up_hints=["How do contextual embeddings (BERT) differ from Word2Vec?"],
        source="bank",
    ),

    # ── Day 18: LLM Fine-Tuning ───────────────────────────────────────
    QuestionArtifact(
        question_id="day_18_q1",
        day=18,
        module="LLM Fine-Tuning",
        topic="LoRA",
        difficulty=4,
        question_text="Explain LoRA (Low-Rank Adaptation). Why is it more memory-efficient than full fine-tuning?",
        expected_concepts=["low-rank", "weight matrices", "adapter", "parameter efficient", "frozen weights"],
        follow_up_hints=["How does QLoRA extend LoRA with quantisation?"],
        source="bank",
    ),
    QuestionArtifact(
        question_id="day_18_q2",
        day=18,
        module="LLM Fine-Tuning",
        topic="RLHF",
        difficulty=5,
        question_text="Describe the RLHF pipeline. What role does the reward model play and how is PPO used to update the policy?",
        expected_concepts=["reward model", "PPO", "human preferences", "policy gradient", "KL divergence"],
        follow_up_hints=["What is DPO and why do some teams prefer it over PPO?"],
        source="bank",
    ),

    # ── Day 22: Chatbot Memory ─────────────────────────────────────────
    QuestionArtifact(
        question_id="day_22_q1",
        day=22,
        module="Chatbot Memory",
        topic="Conversation Memory",
        difficulty=3,
        question_text="Compare buffer memory, summary memory, and vector-store-backed memory for a chatbot. Trade-offs?",
        expected_concepts=["buffer", "summary", "vector store", "token limit", "retrieval", "context window"],
        follow_up_hints=["How would you handle multi-session memory across days?"],
        source="bank",
    ),

    # ── Day 26: Agents and Tools ───────────────────────────────────────
    QuestionArtifact(
        question_id="day_26_q1",
        day=26,
        module="Agents and Tools",
        topic="ReAct Pattern",
        difficulty=4,
        question_text="Describe the ReAct (Reasoning + Acting) pattern. How does it differ from a simple chain-of-thought approach?",
        expected_concepts=["thought", "action", "observation", "tool use", "loop termination", "grounding"],
        follow_up_hints=["How do you prevent infinite tool-call loops?"],
        source="bank",
    ),
    QuestionArtifact(
        question_id="day_26_q2",
        day=26,
        module="Agents and Tools",
        topic="Tool Binding",
        difficulty=3,
        question_text="How do you expose a Python function as a tool for an LLM agent? Walk me through the function-calling API flow.",
        expected_concepts=["function schema", "JSON schema", "tool binding", "structured output", "argument parsing"],
        follow_up_hints=["How do you handle tool errors gracefully?"],
        source="bank",
    ),

    # ── Day 29: Monitoring ─────────────────────────────────────────────
    QuestionArtifact(
        question_id="day_29_q1",
        day=29,
        module="Monitoring",
        topic="LLM Observability",
        difficulty=3,
        question_text="What metrics would you track in production for an LLM-powered application? How do you detect drift?",
        expected_concepts=["latency", "token usage", "hallucination rate", "user feedback", "embedding drift"],
        follow_up_hints=["How would you set up alerting thresholds?"],
        source="bank",
    ),

    # ── Day 31: Capstone Deployment ────────────────────────────────────
    QuestionArtifact(
        question_id="day_31_q1",
        day=31,
        module="Capstone Deployment",
        topic="End-to-End Pipeline",
        difficulty=4,
        question_text="Walk me through deploying an LLM-based chatbot to production. Cover infrastructure, CI/CD, and rollback strategy.",
        expected_concepts=["containerisation", "CI/CD", "load balancer", "model versioning", "rollback", "canary deploy"],
        follow_up_hints=["How do you handle model updates without downtime?"],
        source="bank",
    ),
    QuestionArtifact(
        question_id="day_31_q2",
        day=31,
        module="Capstone Deployment",
        topic="Cost Optimisation",
        difficulty=5,
        question_text="Your LLM API costs $50k/month. Propose three concrete strategies to reduce costs without degrading quality.",
        expected_concepts=["caching", "smaller model", "batching", "prompt compression", "distillation", "routing"],
        follow_up_hints=["How would you measure quality degradation after switching models?"],
        source="bank",
    ),
]

# Pre-compute useful lookups
_BY_ID: dict[str, QuestionArtifact] = {q["question_id"]: q for q in FAKE_CURRICULUM}
_ALL_DAYS: list[int] = sorted(set(q["day"] for q in FAKE_CURRICULUM))


# ═══════════════════════════════════════════════════════════════════════════
# retrieve_question
# ═══════════════════════════════════════════════════════════════════════════

def retrieve_question(state: InterviewState) -> QuestionArtifact:
    """
    Select the next question based on candidate weakness — not random order.

    Priority logic:
    1. Filter out already-asked question_ids.
    2. Prefer questions from weak/critical competency days with high priority.
    3. Prefer uncovered days to ensure ≥ 4 days are reached.
    4. Respect difficulty_level ± 1 when possible.
    5. Fall back to any remaining unasked question.

    Raises RuntimeError if no unasked questions remain.
    """
    asked: set[str] = set(state.get("asked_question_ids", []))
    unasked = [q for q in FAKE_CURRICULUM if q["question_id"] not in asked]

    if not unasked:
        raise RuntimeError("No unasked questions remain in the curriculum.")

    competency: dict[str, CompetencyEntry] = state.get("competency_map", {})
    covered: set[int] = set(state.get("covered_days", []))
    target_diff: int = state.get("difficulty_level", 2)

    # ── Scoring function ──────────────────────────────────────────────
    def _score(q: QuestionArtifact) -> float:
        """Higher score → higher selection priority."""
        s = 0.0
        key = day_key(q["day"])
        entry = competency.get(key)

        # Weakness bonus
        if entry:
            status = entry.get("status", "medium")
            if status == "critical":
                s += 40.0
            elif status == "weak":
                s += 30.0
            elif status == "medium":
                s += 10.0
            # Priority bonus
            pri = entry.get("priority", "medium")
            if pri == "high":
                s += 20.0
            elif pri == "medium":
                s += 5.0

        # Uncovered-day bonus (ensures ≥ 4 days are reached)
        if q["day"] not in covered:
            s += 25.0

        # Difficulty proximity bonus (prefer ± 1 of target)
        diff_gap = abs(q["difficulty"] - target_diff)
        if diff_gap == 0:
            s += 15.0
        elif diff_gap == 1:
            s += 8.0

        # Small jitter to break ties
        s += random.random() * 2.0

        return s

    # Pick the highest-scoring question
    unasked.sort(key=_score, reverse=True)
    return unasked[0]


# ═══════════════════════════════════════════════════════════════════════════
# evaluate_answer
# ═══════════════════════════════════════════════════════════════════════════

# Signals that indicate a weak/uncertain answer
_WEAK_PHRASES: list[str] = [
    "not sure",
    "i don't know",
    "no idea",
    "i guess",
    "maybe",
    "don't remember",
    "skip",
]


def evaluate_answer(
    question: QuestionArtifact,
    answer: str,
    state: InterviewState,
) -> EvaluationResult:
    """
    Deterministic answer evaluator — no LLM needed.

    Scoring rules:
      - Empty or very short answers → quality ≈ 0.1
      - Contains weak phrases ("not sure", etc.) → quality penalty
      - Each matched expected_concept adds to quality
      - Quality is clamped to [0.0, 1.0]

    recommended_action logic:
      - quality < 0.25 → "retry"
      - quality < 0.45 → "probe"
      - quality < 0.70 → "continue"
      - quality >= 0.70 → "increase_difficulty"
    """
    text_lower = answer.strip().lower() if answer else ""
    expected: list[str] = question.get("expected_concepts", [])
    word_count = len(text_lower.split()) if text_lower else 0

    # ── Concept matching ──────────────────────────────────────────────
    matched: list[str] = []
    missing: list[str] = []
    for concept in expected:
        if concept.lower() in text_lower:
            matched.append(concept)
        else:
            missing.append(concept)

    # ── Base quality from concept coverage ────────────────────────────
    if len(expected) > 0:
        concept_ratio = len(matched) / len(expected)
    else:
        concept_ratio = 0.5   # no expectations → neutral

    quality = concept_ratio

    # ── Penalties ─────────────────────────────────────────────────────
    # Empty / very short
    if word_count <= 3:
        quality = 0.1

    # Weak phrases
    weak_hits = sum(1 for phrase in _WEAK_PHRASES if phrase in text_lower)
    if weak_hits > 0:
        quality -= 0.15 * weak_hits

    # ── Bonuses ───────────────────────────────────────────────────────
    # Longer, substantive answers
    if word_count > 40:
        quality += 0.05
    if word_count > 80:
        quality += 0.05

    quality = clamp(quality, 0.0, 1.0)

    # ── Rationale ─────────────────────────────────────────────────────
    rationale = (
        f"Matched {len(matched)}/{len(expected)} expected concepts. "
        f"Word count: {word_count}. Weak-phrase hits: {weak_hits}."
    )

    # ── Recommended action ────────────────────────────────────────────
    if quality < 0.25:
        action = "retry"
    elif quality < 0.45:
        action = "probe"
    elif quality < 0.70:
        action = "continue"
    else:
        action = "increase_difficulty"

    return EvaluationResult(
        quality=round(quality, 4),
        matched_concepts=matched,
        missing_concepts=missing,
        rationale=rationale,
        recommended_action=action,
    )
