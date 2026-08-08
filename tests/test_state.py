import pytest
import json
import sys
import os

# Add root to sys.path so we can import from person1
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from person1.state import (
    create_initial_state,
    append_message,
    trim_history,
    update_summary_memory,
    serialize_state,
    deserialize_state,
)


def test_create_initial_state():
    state = create_initial_state(candidate={"name": "Alice", "id": "123", "job role": "Engineer"})
    assert state["question_count"] == 0
    assert state["probe_count"] == 0
    assert state["covered_days"] == []
    assert state["asked_question_ids"] == []
    assert state["difficulty_level"] == 2
    assert state["phase"] == "intro"
    assert state["summary_memory"] == ""
    assert state["strengths"] == []
    assert state["gaps"] == []
    assert state["done"] is False
    assert state["candidate_name"] == "Alice"
    assert state["candidate_id"] == "123"
    assert "session_id" in state
    assert state["session_id"] is not None


def test_append_message():
    state = create_initial_state()
    state = append_message(state, "interviewer", "Hello there", turn_type="question")
    assert len(state["conversation_history"]) == 1
    assert state["conversation_history"][0]["role"] == "interviewer"
    assert state["conversation_history"][0]["content"] == "Hello there"
    assert state["conversation_history"][0]["turn_type"] == "question"


def test_trim_history():
    state = create_initial_state()
    for i in range(6):
        state = append_message(state, "candidate", f"Message {i}")
        
    state = trim_history(state, max_turns=4)
    assert len(state["conversation_history"]) == 4
    assert state["conversation_history"][-1]["content"] == "Message 5"
    assert state["conversation_history"][0]["content"] == "Message 2"
    assert "Message 0" in state["summary_memory"]
    assert "Message 1" in state["summary_memory"]


def test_update_summary_memory():
    state = create_initial_state()
    state = update_summary_memory(state, "New info")
    assert "New info" in state["summary_memory"]
    state = update_summary_memory(state, "More info")
    assert "New info" in state["summary_memory"]
    assert "More info" in state["summary_memory"]


def test_serialize_deserialize():
    state = create_initial_state()
    state["question_count"] = 5
    state["conversation_history"] = [{"role": "user", "content": "test", "turn_type": "message"}]
    
    serialized = serialize_state(state)
    assert isinstance(serialized, dict)
    
    json_str = json.dumps(serialized)
    assert isinstance(json_str, str)
    
    deserialized = deserialize_state(json.loads(json_str))
    assert deserialized["question_count"] == 5
    assert len(deserialized["conversation_history"]) == 1
    assert deserialized["conversation_history"][0]["content"] == "test"
    
    # Test missing fields
    partial = {"session_id": "test_id", "question_count": 10}
    deserialized_partial = deserialize_state(partial)
    assert deserialized_partial["question_count"] == 10
    assert deserialized_partial["difficulty_level"] == 2 # default from create_initial_state
    assert deserialized_partial["session_id"] == "test_id"
