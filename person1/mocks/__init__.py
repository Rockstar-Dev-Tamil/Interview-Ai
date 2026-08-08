"""
person1.mocks — Mocked Person 2 pipeline for offline development and tests.
"""

from .pipeline_mock import (
    retrieve_question,
    evaluate_answer,
    FAKE_CURRICULUM,
)

__all__ = ["retrieve_question", "evaluate_answer", "FAKE_CURRICULUM"]
