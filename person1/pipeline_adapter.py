import logging
from typing import Any, Callable

import person1.mocks.pipeline_mock as default_pipeline

logger = logging.getLogger(__name__)


class PipelineWrapper:
    """
    Wraps separate functions into an object with the required pipeline interface.
    """
    def __init__(self, retrieve_fn: Callable, evaluate_fn: Callable):
        self._retrieve_fn = retrieve_fn
        self._evaluate_fn = evaluate_fn

    def retrieve_question(self, state: dict) -> dict:
        return self._retrieve_fn(state)

    def evaluate_answer(self, question: dict, answer: str, state: dict) -> dict:
        return self._evaluate_fn(question, answer, state)


def wrap_real_pipeline(retrieve_question_fn: Callable, evaluate_answer_fn: Callable) -> Any:
    """
    Wraps custom functions into an object compatible with Person 1's expected pipeline interface.
    """
    return PipelineWrapper(retrieve_question_fn, evaluate_answer_fn)


_PIPELINE_CACHE = None

def get_pipeline(use_real_pipeline: bool = True) -> Any:
    """
    Returns the appropriate pipeline for the graph to use.
    Falls back to mock pipeline if the real pipeline fails to load.
    """
    global _PIPELINE_CACHE
    
    if not use_real_pipeline:
        return default_pipeline
        
    if _PIPELINE_CACHE is not None:
        return _PIPELINE_CACHE
    
    try:
        from person2 import pipeline as real_pipeline
        # Verify interface
        if not hasattr(real_pipeline, "retrieve_question") or not hasattr(real_pipeline, "evaluate_answer"):
            raise ValueError("Real pipeline is missing required retrieve_question or evaluate_answer functions.")
        _PIPELINE_CACHE = real_pipeline
        return real_pipeline
    except Exception as e:
        logger.warning(f"Failed to load real Person 2 pipeline: {e}. Falling back to mock pipeline.")
        _PIPELINE_CACHE = default_pipeline
        return default_pipeline
