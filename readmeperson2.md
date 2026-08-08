# Data, Retrieval & Evaluation Pipeline (Person 2)

This package contains the pre-computed intelligence databases and the LangChain pipeline functions needed by the Conversational Agent (Person 1) and the API server (Person 3).

## 1. Setup & Installation

Before importing `pipeline.py`, you must install the required Machine Learning and evaluation dependencies in your local Python environment:

```bash
pip install faiss-cpu sentence-transformers deepeval langchain-google-genai
```

You must also configure your Gemini API key in your `.env` file (or environment variables) for the live evaluation functions to work:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

## 2. Directory Structure

Please ensure these files are placed in the correct directories in your backend:

- `app/pipeline.py` (The main logic)
- `data/curriculum.db` (Pre-computed SQLite cache for 31 days)
- `data/faiss_index.bin` (BGE-small vector embeddings)
- `data/faiss_index.bin.meta` (Vector metadata)

## 3. Available Functions (API)

You can import these functions directly from `pipeline.py`:

```python
from app.pipeline import build_competency_map, retrieve_question, evaluate_answer, validate_feedback_hallucination
```

### `build_competency_map(candidate_id: str) -> dict`
Reads the `candidates.json` file and returns a dictionary mapping each curriculum day to the candidate's competency level (`Strong`, `Medium`, `Weak`, `Critical`).

### `retrieve_question(state: dict) -> dict`
Takes the LangGraph state (must include `competency_map` and `covered_days`) and pulls a highly relevant interview question from the local FAISS index. It strictly prioritizes `Weak` and `Critical` areas. Returns a dictionary perfectly matching Person 1's `QuestionArtifact` contract.

### `evaluate_answer(question: dict, answer: str, state: dict = None) -> dict`
Uses Gemini 3.5 Flash to grade the candidate's raw answer. Returns a dictionary perfectly matching Person 1's `EvaluationResult` contract:
- `quality` (float 0.0 to 1.0)
- `matched_concepts` (List[str])
- `missing_concepts` (List[str])
- `rationale` (String)
- `recommended_action` (String)

### `validate_feedback_hallucination(question: dict, answer: str, feedback: dict) -> bool`
Uses the DeepEval library to check the LLM's feedback against the candidate's raw answer to ensure the AI did not hallucinate fake weaknesses. Returns `True` if the feedback is grounded (score >= 0.5), or `False` if hallucinated.
