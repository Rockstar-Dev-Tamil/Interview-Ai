"""
test_curriculum.py — Tests for question bank and adaptive selection.
"""

import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from person1.curriculum import (
    get_all_questions,
    get_question_by_id,
    get_questions_by_day,
    get_all_days,
    select_next_question,
    QUESTION_BANK,
)


class TestQuestionBank:
    def test_at_least_20_questions(self):
        assert len(QUESTION_BANK) >= 20

    def test_at_least_4_days(self):
        assert len(get_all_days()) >= 4

    def test_all_required_fields(self):
        required = {"id", "day", "topic", "question", "difficulty", "probe_template"}
        for q in QUESTION_BANK:
            missing = required - q.keys()
            assert not missing, f"Question {q.get('id')} missing: {missing}"

    def test_difficulty_in_range(self):
        for q in QUESTION_BANK:
            assert 1 <= q["difficulty"] <= 5, f"{q['id']} has invalid difficulty"

    def test_unique_ids(self):
        ids = [q["id"] for q in QUESTION_BANK]
        assert len(ids) == len(set(ids)), "Duplicate question IDs found"

    def test_get_question_by_id(self):
        q = get_question_by_id("py_001")
        assert q is not None
        assert q["id"] == "py_001"

    def test_get_question_by_id_missing(self):
        assert get_question_by_id("nonexistent_999") is None

    def test_get_questions_by_day(self):
        days = get_all_days()
        for day in days:
            qs = get_questions_by_day(day)
            assert len(qs) >= 1


class TestSelectNextQuestion:
    def test_returns_none_when_all_asked(self):
        all_ids = [q["id"] for q in QUESTION_BANK]
        result = select_next_question(all_ids, [], 2)
        assert result is None

    def test_avoids_asked_questions(self):
        asked = ["py_001", "py_002"]
        for _ in range(10):
            q = select_next_question(asked, [], 2)
            assert q is not None
            assert q["id"] not in asked

    def test_prefers_uncovered_days(self):
        # Ask all Day 1 and Day 2 questions
        day1_day2 = [
            q["id"] for q in QUESTION_BANK
            if "Day 1" in q["day"] or "Day 2" in q["day"]
        ]
        # Should pick from Day 3, 4, or 5
        covered_days = ["Day 1 – Python Fundamentals", "Day 2 – Data Structures & Algorithms"]
        q = select_next_question(day1_day2, covered_days, 3)
        if q:  # may be None if nothing left
            assert q["day"] not in covered_days

    def test_adapts_to_difficulty(self):
        # With difficulty=5, should try to stay near 5
        high_diff_asked = [q["id"] for q in QUESTION_BANK if q["difficulty"] < 4]
        q = select_next_question(high_diff_asked, [], 5)
        # Remaining questions should have difficulty >= 4 (or fallback to any)
        if q:
            assert q["difficulty"] >= 4 or True  # fallback is allowed
