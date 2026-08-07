# Person 2: System Prompts

This document contains the exact system prompts and LLM instructions used by the Data, Retrieval & Evaluation pipeline (`pipeline.py`).

These prompts were passed to the `gemini-3.5-flash` model using LangChain's `PromptTemplate`.

---

## 1. Curriculum Enrichment Prompt
**Purpose:** Used internally by the pre-computation script (`build_index.py`) to analyze the raw JSON curriculum and autonomously generate interview questions, Socratic traps, and real-world scenarios.

**The Prompt:**
```text
You are an expert technical interviewer.
Analyze this curriculum day: Module: {module}, Title: {title}, Objectives: {objectives}.
Generate enriched interview metadata based on the schema.
```

**Structured Output Schema (Pydantic):**
- `key_concepts` (List of Strings)
- `interview_questions` (List of Strings)
- `follow_up_traps` (List of Strings)
- `real_world_scenarios` (List of Strings)
- `difficulty` (Integer 1-5)

---

## 2. Answer Evaluation Prompt
**Purpose:** Used by the conversational agent during the live interview to grade the candidate's raw answer against the target question.

**The Prompt:**
```text
You are evaluating a candidate's answer to the following technical question.
Question: {question}
Candidate's Answer: {answer}
Evaluate the technical depth, correctness, and completeness of the answer.
```

**Structured Output Schema (Pydantic):**
- `score` (Float 0.0 to 1.0)
- `strengths` (List of Strings)
- `weaknesses` (List of Strings)
- `recommendation` (String)

---

## 3. DeepEval Hallucination Metric
**Purpose:** An automated validation check that prevents the LLM from inventing fake weaknesses that contradict the candidate's actual answer.

**Configuration:**
- **Metric:** `HallucinationMetric`
- **Threshold:** `0.5` (Enforces high logical grounding)
- **Context Provided:** The candidate's raw answer is injected directly as the source of truth `context` to validate the generated `feedback`.
