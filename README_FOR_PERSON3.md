# Backend Integration Guide (For Person 3)

Hello Person 3! 

This folder contains the **fully integrated, tested, and working backend core** combining the efforts of Person 1 (LangGraph Orchestration) and Person 2 (Gemini AI Pipeline & Data).

We have already wired our systems together and verified that they communicate flawlessly with zero contract errors. Your job is to wrap this core logic into an API server (e.g. FastAPI, Express, or Next.js server actions) and build the frontend UI.

---

## 1. What's Inside This Folder?

- `person1/` - The LangGraph State Machine (Agent Brain).
- `person2/` - The Gemini AI Pipeline (Evaluation, Question Retrieval, Hallucination Checks).
- `data/` - Pre-computed SQLite databases containing the 31-day enriched curriculum and FAISS embeddings.
- `test_e2e.py` - A simulation script proving that the system works end-to-end.

---

## 2. Setup & Installation

You need to place these folders into the root of your Python backend server. 
You will also need to install the combined dependencies:

```bash
pip install langgraph langchain-google-genai pydantic faiss-cpu sentence-transformers deepeval
```

You must also set the Gemini API Key in your backend `.env` file for the LLM to function:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

---

## 3. How to Use This in Your Server

You **only need to import one function** to run the entire backend! Person 1's `run_turn` function acts as the single entry point. It automatically manages the state and talks to Person 2's AI pipeline under the hood.

```python
from person1 import run_turn

# On the very first turn (Initialization):
candidate_info = {"id": "CAND-001", "name": "Sarah"}
result = run_turn(session_state=None, message="hi", candidate=candidate_info)

print(result['reply']) # Send this to the frontend
current_state = result['state'] # Save this JSON object in your SQLite DB!

# On all subsequent turns:
# 1. Fetch current_state from your database
# 2. Get the candidate's answer from the frontend
user_answer = "I would use microservices..."

result = run_turn(session_state=current_state, message=user_answer)

print(result['reply']) # The agent's next question or probe
updated_state = result['state'] # Update your DB with this new state
```

### The `TurnResult` Object

Every time you call `run_turn`, it returns a dictionary with 4 keys:
- `reply` (String): The text you should display in the chat UI.
- `state` (Dictionary): The massive JSON state object. **You must save this in your database and pass it back in on the next turn.**
- `done` (Boolean): If `True`, the interview is over!
- `feedback` (Dictionary): The final performance review (only provided when `done=True`).

---

## 4. Testing

To verify everything is working on your machine before you build the server, simply run:

```bash
python test_e2e.py
```

If it prints "Zero crashes detected. Integration is flawless.", you are good to go! Good luck building the UI, make sure every screen has a "wow" moment!
