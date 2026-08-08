import pytest
import os
import json
import sqlite3

# This is an E2E test. We will use the real run_turn but mock the LLM if no API key is present
# However, the project says Person 2 pipeline uses Gemini. 
# For true E2E persona tests, we should probably mock the pipeline or use a mock pipeline adapter if the project supports it.
# The `README_FOR_PERSON3.md` says test_e2e.py runs flawlessly. We can just invoke the real API backend.

from fastapi.testclient import TestClient
from app import app
import session_store
import person1

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_teardown():
    session_store.DB_PATH = "test_persona_sessions.db"
    if os.path.exists(session_store.DB_PATH):
        os.remove(session_store.DB_PATH)
    yield
    if os.path.exists(session_store.DB_PATH):
        os.remove(session_store.DB_PATH)


def run_persona_test(session_id, candidate_name, answers):
    print(f"\\n--- Starting Persona Test: {candidate_name} ---")
    
    # Init
    resp = client.post("/api/interview", json={
        "sessionId": session_id,
        "candidate": {"id": f"c_{session_id}", "name": candidate_name}
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["done"] == False
    
    turn = 1
    # Run through the answers
    for answer in answers:
        print(f"Turn {turn} Candidate: {answer}")
        resp = client.post("/api/interview", json={
            "sessionId": session_id,
            "message": answer
        })
        assert resp.status_code == 200
        data = resp.json()
        print(f"Turn {turn} Agent: {data['reply']}")
        
        if data["done"]:
            print(f"Interview finished at turn {turn}.")
            assert data["feedback"] is not None
            return data
            
        turn += 1
        
    # We should eventually hit done=True
    return data

@pytest.mark.skipif(not os.environ.get("GOOGLE_API_KEY"), reason="Requires GOOGLE_API_KEY for real E2E")
def test_weak_candidate():
    answers = [
        "I don't know.",
        "I'm not sure how to answer that.",
        "Maybe we can use a loop?",
        "I guess so.",
        "I have never heard of that concept.",
        "I don't know.",
        "I don't know.",
        "I don't know.",
        "I don't know.",
        "I don't know."
    ]
    data = run_persona_test("weak-1", "Weak Candidate", answers)
    assert data["done"] == True
    assert "gaps" in data["feedback"]
    assert len(data["feedback"]["gaps"]) > 0

@pytest.mark.skipif(not os.environ.get("GOOGLE_API_KEY"), reason="Requires GOOGLE_API_KEY for real E2E")
def test_average_candidate():
    answers = [
        "I would use a simple database table to store this.",
        "For optimization, maybe add an index.",
        "I'm not exactly sure about the deep details of the B-Tree, but it makes it faster.",
        "I'd write a script in Python.",
        "I would use unit tests.",
        "I think we can scale it by adding more servers.",
        "A load balancer helps distribute the traffic.",
        "I've used AWS before.",
        "Docker is for containers.",
        "That's all I know."
    ]
    data = run_persona_test("avg-1", "Average Candidate", answers)
    assert data["done"] == True

@pytest.mark.skipif(not os.environ.get("GOOGLE_API_KEY"), reason="Requires GOOGLE_API_KEY for real E2E")
def test_expert_candidate():
    answers = [
        "I would design a microservices architecture. We'd use Kafka for event sourcing and asynchronous processing between the services to ensure loose coupling.",
        "To guarantee exactly-once processing, I'd implement the transactional outbox pattern.",
        "For the database, considering the read-heavy workload, I'd use a distributed NoSQL store like Cassandra, with Redis for caching hot data.",
        "I would implement circuit breakers using resilience4j to prevent cascading failures.",
        "Observability would be handled via OpenTelemetry, exporting traces and metrics to Prometheus and Jaeger.",
        "To ensure zero downtime deployments, we'd use Kubernetes with rolling updates and readiness probes.",
        "For security, all inter-service communication would be encrypted via mTLS using a service mesh like Istio.",
        "We'd manage infrastructure as code using Terraform.",
        "That should cover the primary non-functional requirements.",
        "I'm ready for the next system design scenario."
    ]
    data = run_persona_test("expert-1", "Expert Candidate", answers)
    assert data["done"] == True
