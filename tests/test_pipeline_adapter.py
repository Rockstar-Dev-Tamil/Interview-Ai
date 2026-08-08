import logging
from person1.pipeline_adapter import get_pipeline, wrap_real_pipeline
import person1.mocks.pipeline_mock as mock_pipeline


def test_get_pipeline_default_mock():
    pipeline = get_pipeline()
    assert pipeline is mock_pipeline


def test_get_pipeline_fallback_on_import_error(caplog):
    with caplog.at_level(logging.WARNING):
        pipeline = get_pipeline(use_real_pipeline=True)
        assert pipeline is mock_pipeline
        assert "Failed to load real Person 2 pipeline" in caplog.text


def test_wrap_real_pipeline():
    def mock_retrieve(state):
        return {"id": "1", "text": "mock Q"}
    
    def mock_eval(q, a, state):
        return {"quality": 0.9}

    wrapped = wrap_real_pipeline(mock_retrieve, mock_eval)
    
    q = wrapped.retrieve_question({"test": 1})
    assert q == {"id": "1", "text": "mock Q"}
    
    e = wrapped.evaluate_answer(q, "answer", {})
    assert e == {"quality": 0.9}
