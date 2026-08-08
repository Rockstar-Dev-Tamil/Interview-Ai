# AI-Assisted Development Prompts

This file documents the AI prompts used to generate the Person 3 backend and frontend implementations.

## Initial Request
```markdown
# PERSON 3 — BACKEND + SESSION + FRONTEND IMPLEMENTATION PROMPT
...
(The massive prompt provided by the user)
...
```

## Backend and Database
- "Implement a FastAPI backend based on the Person 3 prompt."
- "Create Pydantic models in `schemas.py` that match the contracts exactly."
- "Implement a SQLite session store in `session_store.py` with parameterized queries to persist the `InterviewState` JSON."
- "Write `test_api.py` covering the 10 requested edge cases, and `test_personas.py` for E2E testing of weak, average, and expert candidates."

## Frontend
- "Create a Next.js application with Tailwind CSS."
- "Create a landing page with candidate information and a Start Interview button."
- "Create the main chat UI that dynamically updates with agent replies, handles empty answers, loading states, and disabled input states."
- "Create a dynamic feedback dashboard rendering the FinalFeedback JSON object."

## Infrastructure
- "Generate a Dockerfile and .dockerignore for the FastAPI backend, exposing port 8000 and persisting the SQLite DB."
- "Update README.md with architecture, local setup instructions, environment variables, and API examples."

## Final Polish & API Refinements
- "Remove hardcoded check for question marks in `person1/nodes.py` to allow the LLM to naturally handle candidate questions."
- "Handle React StrictMode double-mounting by returning the existing state rather than appending an empty message."
- "Update `person2/pipeline.py` to use `gemini-flash-latest` instead of hardcoded older models."
- "Create `/api/candidates` endpoint to securely serve candidate profiles from `candidates.json`."
- "Implement dynamic candidate selection on the start screen with professional styling and experience metrics."
- "Refine Interview UI with Question Count progress, animated typing indicators, and robust error recovery states."
- "Polish Feedback Dashboard to strictly match the requested visual hierarchy (Overview, Strengths, Areas to Improve, Next Steps)."
