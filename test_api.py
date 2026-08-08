import pytest
from fastapi.testclient import TestClient
from app import app
import os
import sqlite3
import json

# Setup Test DB
os.environ["DB_PATH"] = "test_sessions.db"
# But we used hardcoded path in session_store.py. Let's patch session_store db path for tests.
import session_store
session_store.DB_PATH = "test_sessions.db"

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_teardown():
    # Setup
    if os.path.exists(session_store.DB_PATH):
        os.remove(session_store.DB_PATH)
    yield
    # Teardown
    if os.path.exists(session_store.DB_PATH):
        os.remove(session_store.DB_PATH)

# We will patch person1.run_turn to not hit the real LLM for fast API tests
import person1
from unittest.mock import patch

def mock_run_turn_generator():
    yield {
        "reply": "Welcome to the interview! Let's start with question 1.",
        "state": {"phase": "intro", "question_count": 0, "done": False},
        "done": False,
        "feedback": None
    }
    yield {
        "reply": "Good answer. Here is question 2.",
        "state": {"phase": "question", "question_count": 1, "done": False},
        "done": False,
        "feedback": None
    }
    yield {
        "reply": "Interview completed.",
        "state": {"phase": "done", "question_count": 2, "done": True},
        "done": True,
        "feedback": {
            "summary": "Good job.",
            "strengths": ["Python"],
            "gaps": ["Go"],
            "next": "Learn Go"
        }
    }

mock_generator = mock_run_turn_generator()

def side_effect_run_turn(session_state=None, message=None, candidate=None):
    # Depending on what we need, we can return dynamic mock responses.
    # For a simple test, we can just return a static dictionary or state based on input.
    if session_state is None:
        return {
            "reply": "Welcome to the interview!",
            "state": {"phase": "intro", "done": False},
            "done": False,
            "feedback": None
        }
    if message == "trigger_done":
        return {
            "reply": "Interview completed.",
            "state": {"phase": "done", "done": True},
            "done": True,
            "feedback": {
                "summary": "Good job.",
                "strengths": ["Python"],
                "gaps": ["Go"],
                "next": "Learn Go"
            }
        }
    
    return {
        "reply": "Next question.",
        "state": {"phase": "question", "done": False},
        "done": False,
        "feedback": None
    }

@patch("app.run_turn", side_effect=side_effect_run_turn)
def test_1_new_session(mock_run):
    response = client.post("/api/interview", json={
        "sessionId": "test-session-1",
        "candidate": {"id": "c1", "name": "John Doe"}
    })
    assert response.status_code == 200
    data = response.json()
    assert data["reply"] == "Welcome to the interview!"
    assert data["done"] == False
    assert session_store.get_session("test-session-1") is not None

@patch("app.run_turn", side_effect=side_effect_run_turn)
def test_2_continue_session(mock_run):
    # Setup session first
    client.post("/api/interview", json={
        "sessionId": "test-session-2",
        "candidate": {"id": "c2", "name": "Jane Doe"}
    })
    # Continue
    response = client.post("/api/interview", json={
        "sessionId": "test-session-2",
        "message": "My answer is..."
    })
    assert response.status_code == 200
    data = response.json()
    assert data["reply"] == "Next question."

def test_4_unknown_session():
    # Without candidate info, a new session can't start
    response = client.post("/api/interview", json={
        "sessionId": "unknown-session",
        "message": "Answer to unknown"
    })
    assert response.status_code == 422

@patch("app.run_turn", side_effect=side_effect_run_turn)
def test_5_empty_answer(mock_run):
    # Setup session first
    client.post("/api/interview", json={
        "sessionId": "test-session-5",
        "candidate": {"id": "c5", "name": "Empty"}
    })
    
    response = client.post("/api/interview", json={
        "sessionId": "test-session-5",
        "message": "   "
    })
    assert response.status_code == 200
    data = response.json()
    assert "Take your time" in data["reply"]

def test_6_malformed_request():
    response = client.post("/api/interview", json={
        "wrong_field": "value"
    })
    assert response.status_code == 422

@patch("app.run_turn", side_effect=side_effect_run_turn)
def test_7_interview_completion(mock_run):
    # Setup session first
    client.post("/api/interview", json={
        "sessionId": "test-session-7",
        "candidate": {"id": "c7", "name": "Finisher"}
    })
    
    response = client.post("/api/interview", json={
        "sessionId": "test-session-7",
        "message": "trigger_done"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["done"] == True
    assert data["feedback"]["summary"] == "Good job."

@patch("app.run_turn", side_effect=side_effect_run_turn)
def test_10_server_restart_simulation(mock_run):
    # Start session
    client.post("/api/interview", json={
        "sessionId": "test-session-10",
        "candidate": {"id": "c10", "name": "Restarter"}
    })
    
    # Simulate restart by clearing Python memory caches if any.
    # Because session_store uses sqlite on disk, the state is there.
    state = session_store.get_session("test-session-10")
    assert state is not None
    
    # Make a new client request, which simulates a fresh API hitting the DB
    response = client.post("/api/interview", json={
        "sessionId": "test-session-10",
        "message": "After restart"
    })
    assert response.status_code == 200
