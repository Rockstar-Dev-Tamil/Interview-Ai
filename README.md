# ABTALKS AI Interview Agent

![ABTALKS AI Interview Agent](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)

Welcome to the **ABTALKS AI Interview Agent** — a fully autonomous, adaptive technical interview platform built for the hackathon. 

This repository contains the complete, integrated solution combining the work of **Person 1 (LangGraph Orchestration)**, **Person 2 (Gemini AI Pipeline & RAG)**, and **Person 3 (FastAPI Backend & Next.js Frontend)**.

## 🚀 Features

- **Dynamic Candidate Selection:** Automatically fetches candidate profiles from the enriched curriculum database.
- **Adaptive Interview Flow:** Driven by a LangGraph state machine, the interview dynamically adjusts difficulty (drilling deeper on weak answers, moving to new topics on strong ones).
- **Semantic Evaluation:** Uses Gemini (via `gemini-flash-latest`) to evaluate answers, verify against hallucination guardrails, and generate context-aware follow-up questions.
- **Polished Next.js Frontend:** Provides a premium user experience with typing indicators, progress tracking, and robust error recovery.
- **Actionable Feedback Dashboard:** Generates a comprehensive summary, strengths, areas to improve, and recommended next steps at the end of the session.

---

## 🏗️ Architecture

The system is deployed as a FastAPI backend with a SQLite session store, integrating the LangGraph orchestrator and Gemini AI pipeline, consumed by a Next.js frontend UI.

```text
Frontend (Next.js)
       ↓
FastAPI (app.py)
       ↓
SQLite Session Store (session_store.py)
       ↓
LangGraph State Machine (person1)
       ↓
Gemini Evaluation Pipeline (person2)
```

---

## 🛠️ Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- A Google Gemini API Key

### 1. Backend Setup

1. **Install Python Dependencies:**
```bash
pip install -r requirements.txt
```

2. **Environment Variables:**
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your_gemini_api_key
FRONTEND_URL=http://localhost:3000
PORT=8000
```

3. **Run the FastAPI Server:**
```bash
uvicorn app:app --reload
```

### 2. Frontend Setup

1. **Install Node Dependencies:**
```bash
cd frontend
npm install
```

2. **Run the Next.js App:**
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`.

---

## 🔌 API Documentation

### 1. Fetch Available Candidates
Retrieves a list of candidate profiles to populate the start screen.
```bash
curl http://localhost:8000/api/candidates
```

### 2. Start an Interview Session
Initializes a new session for a selected candidate.
```bash
curl -X POST http://localhost:8000/api/interview \
-H "Content-Type: application/json" \
-d '{
  "sessionId": "session-uuid-123",
  "candidate": {
    "id": "CAND-001",
    "name": "Sarah Johnson"
  }
}'
```

### 3. Send an Answer
Submits the candidate's answer and receives the AI's evaluation and next question.
```bash
curl -X POST http://localhost:8000/api/interview \
-H "Content-Type: application/json" \
-d '{
  "sessionId": "session-uuid-123",
  "message": "I would use microservices with Kafka for event streaming."
}'
```

---

## 🐳 Docker Deployment

A `Dockerfile` is included for easy deployment of the backend server. 

```bash
docker build -t abtalks-interview-ai .
docker run -p 8000:8000 -e GOOGLE_API_KEY=your_api_key abtalks-interview-ai
```

---

## 📝 Key Design Decisions

- **State-dict pattern:** LangGraph state is kept as a plain JSON-serializable dict, allowing the FastAPI layer to trivially persist active interviews in SQLite.
- **Robustness:** React StrictMode double-mounting is gracefully handled by returning the existing state instead of pushing empty messages to the graph.
- **Adaptive Probing:** Weak answers (score ≤2) trigger exactly one probe per question, ensuring the agent digs deeper without getting stuck in infinite loops.
- **Memory Compression:** Every 3 answers are compressed into a `memory_summary` string to keep the LLM context window clean and efficient.
