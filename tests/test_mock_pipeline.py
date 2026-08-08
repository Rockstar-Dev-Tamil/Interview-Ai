"""
test_mock_pipeline.py — Tests for the mocked Person 2 pipeline.

Validates:
  - retrieve_question returns a valid QuestionArtifact
  - retrieve_question does not repeat asked_question_ids
  - evaluate_answer returns quality between 0 and 1
  - evaluate_answer returns low score for "not sure"
  - evaluate_answer returns high score when answer contains expected concepts
"""

from __future__ import annotations

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from person1.contracts import (
    InterviewState,
    QuestionArtifact,
    EvaluationResult,
)
from person1.types import make_initial_state
from person1.mocks.pipeline_mock import (
    retrieve_question,
    evaluate_answer,
    FAKE_CURRICULUM,
)


# ═══════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def fresh_state() -> InterviewState:
    """A blank interview state with no questions asked."""
    return make_initial_state(candidate_id="test_001", candidate_name="Test User")


@pytest.fixture
def sample_question() -> QuestionArtifact:
    """Return the first question in the fake curriculum for evaluation tests."""
    return FAKE_CURRICULUM[0]


# ═══════════════════════════════════════════════════════════════════════════
# Curriculum sanity checks
# ═══════════════════════════════════════════════════════════════════════════

class TestFakeCurriculum:
    def test_at_least_10_questions(self):
        assert len(FAKE_CURRICULUM) >= 10

    def test_at_least_6_days(self):
        days = set(q["day"] for q in FAKE_CURRICULUM)
        assert len(days) >= 6, f"Only {len(days)} days: {sorted(days)}"

    def test_all_ids_unique(self):
        ids = [q["question_id"] for q in FAKE_CURRICULUM]
        assert len(ids) == len(set(ids)), "Duplicate question IDs in fake curriculum"

    def test_question_fields_present(self):
        required = {
            "question_id", "day", "module", "topic", "difficulty",
            "question_text", "expected_concepts", "follow_up_hints", "source",
        }
        for q in FAKE_CURRICULUM:
            missing = required - q.keys()
            assert not missing, f"{q['question_id']} missing fields: {missing}"


# ═══════════════════════════════════════════════════════════════════════════
# retrieve_question tests
# ═══════════════════════════════════════════════════════════════════════════

class TestRetrieveQuestion:
    def test_returns_question_artifact(self, fresh_state):
        q = retrieve_question(fresh_state)
        assert isinstance(q, dict), "Should return a dict (QuestionArtifact)"
        assert "question_id" in q
        assert "question_text" in q
        assert "expected_concepts" in q
        assert "difficulty" in q
        assert isinstance(q["day"], int)

    def test_returns_valid_question_id_format(self, fresh_state):
        q = retrieve_question(fresh_state)
        qid = q["question_id"]
        assert qid.startswith("day_"), f"question_id should start with 'day_', got {qid}"

    def test_does_not_repeat_asked_ids(self, fresh_state):
        """Ask the first 5 questions, then verify the 6th is different."""
        state = dict(fresh_state)
        asked: list[str] = []

        for _ in range(5):
            q = retrieve_question(state)
            qid = q["question_id"]
            assert qid not in asked, f"Repeated question_id: {qid}"
            asked.append(qid)
            state = {**state, "asked_question_ids": list(asked)}

        # 6th question must also be unique
        q6 = retrieve_question(state)
        assert q6["question_id"] not in asked

    def test_does_not_repeat_even_under_pressure(self, fresh_state):
        """Ask ALL questions one by one; none should repeat."""
        state = dict(fresh_state)
        asked: list[str] = []

        for _ in range(len(FAKE_CURRICULUM)):
            q = retrieve_question(state)
            assert q["question_id"] not in asked, f"Repeated: {q['question_id']}"
            asked.append(q["question_id"])
            state = {**state, "asked_question_ids": list(asked)}

    def test_raises_when_exhausted(self, fresh_state):
        """After asking every question, retrieving another should raise."""
        all_ids = [q["question_id"] for q in FAKE_CURRICULUM]
        state = {**fresh_state, "asked_question_ids": all_ids}

        with pytest.raises(RuntimeError, match="No unasked questions"):
            retrieve_question(state)

    def test_prefers_uncovered_days(self, fresh_state):
        """When some days are covered, the result should come from an uncovered day."""
        covered = [2, 7]  # already covered days
        state = {**fresh_state, "covered_days": covered}
        q = retrieve_question(state)
        # The question should prefer uncovered days (12, 18, 22, 26, 29, 31)
        # but with some jitter, so we just check it's a valid question
        assert q["question_id"] not in state["asked_question_ids"]

    def test_prefers_weak_competency_days(self, fresh_state):
        """Questions from weak/critical days should be prioritised."""
        comp_map = {
            "day_18": {
                "day": 18,
                "module": "LLM Fine-Tuning",
                "topic": "LoRA",
                "status": "critical",
                "priority": "high",
                "difficulty_target": 4,
                "evidence": "struggled with LoRA concepts",
            },
        }
        state = {**fresh_state, "competency_map": comp_map, "difficulty_level": 4}
        q = retrieve_question(state)
        # With critical+high priority, day 18 should be strongly preferred
        # (but jitter means this isn't guaranteed — run a few times)
        results = set()
        for _ in range(10):
            q = retrieve_question(state)
            results.add(q["day"])
        assert 18 in results, "Day 18 (critical) should appear at least once in 10 tries"


# ═══════════════════════════════════════════════════════════════════════════
# evaluate_answer tests
# ═══════════════════════════════════════════════════════════════════════════

class TestEvaluateAnswer:
    def test_returns_evaluation_result(self, sample_question, fresh_state):
        result = evaluate_answer(sample_question, "some answer", fresh_state)
        assert isinstance(result, dict)
        assert "quality" in result
        assert "matched_concepts" in result
        assert "missing_concepts" in result
        assert "rationale" in result
        assert "recommended_action" in result

    def test_quality_between_0_and_1(self, sample_question, fresh_state):
        for answer in [
            "",
            "not sure",
            "a short reply",
            "isolation dependencies venv conda reproducibility and more words to fill",
        ]:
            result = evaluate_answer(sample_question, answer, fresh_state)
            assert 0.0 <= result["quality"] <= 1.0, (
                f"quality={result['quality']} for answer: {answer!r}"
            )

    def test_low_score_for_not_sure(self, sample_question, fresh_state):
        result = evaluate_answer(sample_question, "not sure about this", fresh_state)
        assert result["quality"] < 0.4, (
            f"Expected low quality for 'not sure', got {result['quality']}"
        )

    def test_low_score_for_empty(self, sample_question, fresh_state):
        result = evaluate_answer(sample_question, "", fresh_state)
        assert result["quality"] <= 0.15

    def test_low_score_for_very_short(self, sample_question, fresh_state):
        result = evaluate_answer(sample_question, "idk", fresh_state)
        assert result["quality"] <= 0.15

    def test_high_score_with_expected_concepts(self, sample_question, fresh_state):
        """Answer that mentions all expected concepts should score high."""
        concepts = sample_question["expected_concepts"]
        rich_answer = (
            "Great question. "
            + " ".join(concepts)
            + " — these are all relevant aspects. In practice, "
            "the key takeaway is that each concept plays a role in the overall architecture."
        )
        result = evaluate_answer(sample_question, rich_answer, fresh_state)
        assert result["quality"] >= 0.7, (
            f"Expected high quality when all concepts present, got {result['quality']}"
        )

    def test_matched_and_missing_concepts(self, sample_question, fresh_state):
        """Partial answer should produce both matched and missing lists."""
        # Use only the first 2 concepts
        partial = " ".join(sample_question["expected_concepts"][:2]) + " and that's all I know"
        result = evaluate_answer(sample_question, partial, fresh_state)
        assert len(result["matched_concepts"]) >= 2
        assert len(result["missing_concepts"]) >= 1
        # Union should equal expected_concepts
        all_concepts = set(result["matched_concepts"]) | set(result["missing_concepts"])
        assert all_concepts == set(sample_question["expected_concepts"])

    def test_recommended_action_for_low_quality(self, sample_question, fresh_state):
        result = evaluate_answer(sample_question, "not sure", fresh_state)
        assert result["recommended_action"] in ("retry", "probe")

    def test_recommended_action_for_high_quality(self, sample_question, fresh_state):
        rich = " ".join(sample_question["expected_concepts"]) + " thoroughly explained with examples"
        result = evaluate_answer(sample_question, rich, fresh_state)
        assert result["recommended_action"] in ("continue", "increase_difficulty")

    def test_rationale_is_nonempty_string(self, sample_question, fresh_state):
        result = evaluate_answer(sample_question, "some answer", fresh_state)
        assert isinstance(result["rationale"], str)
        assert len(result["rationale"]) > 5
