"""
curriculum.py — Question bank across ≥5 curriculum days.

Each question:
  id           : unique str
  day          : curriculum day label
  topic        : sub-topic
  question     : the question text
  difficulty   : 1 (easy) – 5 (hard)
  probe_template : a follow-up template using {topic} and {answer_snippet}
"""

from __future__ import annotations

import random
from typing import Sequence

# ---------------------------------------------------------------------------
# Question Bank
# ---------------------------------------------------------------------------

QUESTION_BANK: list[dict] = [
    # ═══════════════════════════════════════════════════════════════════════
    # Day 1 — Python Fundamentals
    # ═══════════════════════════════════════════════════════════════════════
    {
        "id": "py_001",
        "day": "Day 1 – Python Fundamentals",
        "topic": "Mutability",
        "question": "Explain the difference between mutable and immutable objects in Python. Give a real-world example where mutability caused an unexpected bug.",
        "difficulty": 2,
        "probe_template": "You mentioned {topic}. Can you describe what happens to the object's identity (id()) when you rebind an immutable vs. mutate a mutable in place?",
    },
    {
        "id": "py_002",
        "day": "Day 1 – Python Fundamentals",
        "topic": "GIL",
        "question": "What is the Global Interpreter Lock (GIL) and how does it affect CPU-bound vs. I/O-bound multithreading in Python?",
        "difficulty": 3,
        "probe_template": "You touched on the GIL. How does using multiprocessing instead of threading circumvent GIL limitations for CPU-bound tasks?",
    },
    {
        "id": "py_003",
        "day": "Day 1 – Python Fundamentals",
        "topic": "Generators",
        "question": "How do Python generators differ from regular functions? Walk me through what happens step-by-step when you call next() on a generator.",
        "difficulty": 2,
        "probe_template": "You mentioned generators. Can you explain the difference between a generator expression and a list comprehension in terms of memory and lazy evaluation?",
    },
    {
        "id": "py_004",
        "day": "Day 1 – Python Fundamentals",
        "topic": "Decorators",
        "question": "Write a decorator that measures and prints execution time of any function. What does @functools.wraps do and why is it important?",
        "difficulty": 3,
        "probe_template": "You discussed decorators. How would you stack multiple decorators and what order do they apply in — bottom-up or top-down?",
    },

    # ═══════════════════════════════════════════════════════════════════════
    # Day 2 — Data Structures & Algorithms
    # ═══════════════════════════════════════════════════════════════════════
    {
        "id": "dsa_001",
        "day": "Day 2 – Data Structures & Algorithms",
        "topic": "Hash Tables",
        "question": "How does Python's dict handle hash collisions internally? What is the average and worst-case time complexity for lookups?",
        "difficulty": 3,
        "probe_template": "You mentioned hash collisions. Can you explain what a hash avalanche is and why it matters when designing hash functions?",
    },
    {
        "id": "dsa_002",
        "day": "Day 2 – Data Structures & Algorithms",
        "topic": "Big-O Notation",
        "question": "Given a nested loop that iterates n and m elements, derive the time complexity. When does O(n log n) beat O(n²) in practice?",
        "difficulty": 2,
        "probe_template": "You talked about Big-O. How does amortised analysis differ from worst-case analysis, and when should you use each?",
    },
    {
        "id": "dsa_003",
        "day": "Day 2 – Data Structures & Algorithms",
        "topic": "Binary Search",
        "question": "Implement binary search on a sorted list. What invariant must be maintained and why is it easy to introduce an off-by-one error?",
        "difficulty": 2,
        "probe_template": "You mentioned binary search invariants. How would you adapt binary search to find the first occurrence of a duplicate element in a sorted array?",
    },
    {
        "id": "dsa_004",
        "day": "Day 2 – Data Structures & Algorithms",
        "topic": "Graph Traversal",
        "question": "Compare BFS and DFS: when would you choose one over the other? How do you detect cycles in a directed graph using DFS?",
        "difficulty": 4,
        "probe_template": "You compared BFS and DFS. How does Dijkstra's algorithm extend BFS for weighted graphs, and what is its time complexity with a min-heap?",
    },

    # ═══════════════════════════════════════════════════════════════════════
    # Day 3 — Machine Learning Basics
    # ═══════════════════════════════════════════════════════════════════════
    {
        "id": "ml_001",
        "day": "Day 3 – Machine Learning Basics",
        "topic": "Bias-Variance Tradeoff",
        "question": "Explain the bias-variance tradeoff. How does model complexity affect each, and how do you diagnose them from training/validation curves?",
        "difficulty": 3,
        "probe_template": "You explained bias-variance. How does regularisation (L1 vs L2) specifically address each component, and what geometric intuition helps here?",
    },
    {
        "id": "ml_002",
        "day": "Day 3 – Machine Learning Basics",
        "topic": "Gradient Descent",
        "question": "Walk me through the gradient descent update rule. What problems arise with vanilla gradient descent that Adam optimizer solves?",
        "difficulty": 3,
        "probe_template": "You mentioned gradient descent updates. How does learning rate scheduling interact with Adam's adaptive rates — is a scheduler still necessary?",
    },
    {
        "id": "ml_003",
        "day": "Day 3 – Machine Learning Basics",
        "topic": "Cross-Validation",
        "question": "Why is k-fold cross-validation preferred over a single train/test split? What is stratified k-fold and when must you use it?",
        "difficulty": 2,
        "probe_template": "You discussed k-fold CV. How does time-series cross-validation differ and why can't you shuffle data the same way for sequential problems?",
    },
    {
        "id": "ml_004",
        "day": "Day 3 – Machine Learning Basics",
        "topic": "Feature Engineering",
        "question": "Describe three effective feature engineering techniques for tabular data. How do you handle categorical features with high cardinality?",
        "difficulty": 3,
        "probe_template": "You described feature engineering. How does target encoding differ from one-hot encoding and what data leakage risk must you guard against?",
    },

    # ═══════════════════════════════════════════════════════════════════════
    # Day 4 — LLMs & Agents
    # ═══════════════════════════════════════════════════════════════════════
    {
        "id": "llm_001",
        "day": "Day 4 – LLMs & Agents",
        "topic": "Transformer Architecture",
        "question": "Explain the self-attention mechanism in a transformer. Why is the attention score scaled by √d_k and what problem does this solve?",
        "difficulty": 4,
        "probe_template": "You explained self-attention scaling. How does multi-head attention allow the model to capture different types of relationships simultaneously?",
    },
    {
        "id": "llm_002",
        "day": "Day 4 – LLMs & Agents",
        "topic": "RAG Systems",
        "question": "How does Retrieval-Augmented Generation (RAG) work? Describe the retrieve-then-generate pipeline and its main failure modes.",
        "difficulty": 3,
        "probe_template": "You described RAG. What is the difference between naive RAG and advanced RAG with re-ranking, and when does re-ranking matter most?",
    },
    {
        "id": "llm_003",
        "day": "Day 4 – LLMs & Agents",
        "topic": "Prompt Engineering",
        "question": "Compare zero-shot, few-shot, and chain-of-thought prompting. In which scenario would you choose each, and what are their token-cost tradeoffs?",
        "difficulty": 2,
        "probe_template": "You compared prompting strategies. How does self-consistency prompting improve reliability and what is its computational cost?",
    },
    {
        "id": "llm_004",
        "day": "Day 4 – LLMs & Agents",
        "topic": "Agent Tool Use",
        "question": "Design a ReAct-style agent that can answer math questions using a calculator tool. What is the Thought→Action→Observation loop and how do you prevent infinite loops?",
        "difficulty": 4,
        "probe_template": "You discussed the ReAct loop. How would you add a memory component so the agent can reference earlier observations without exceeding context limits?",
    },

    # ═══════════════════════════════════════════════════════════════════════
    # Day 5 — System Design
    # ═══════════════════════════════════════════════════════════════════════
    {
        "id": "sys_001",
        "day": "Day 5 – System Design",
        "topic": "Scalability",
        "question": "Walk me through how you would design a URL shortener for 1 billion URLs. Cover storage, hashing, and read/write scaling strategies.",
        "difficulty": 4,
        "probe_template": "You described the URL shortener design. How would you handle cache invalidation if the destination URL for a short link changes?",
    },
    {
        "id": "sys_002",
        "day": "Day 5 – System Design",
        "topic": "API Design",
        "question": "What is the difference between REST, GraphQL, and gRPC? When would you choose each for an internal microservice vs. a public API?",
        "difficulty": 3,
        "probe_template": "You compared API paradigms. How does gRPC's streaming capability differ from WebSockets, and which would you use for a real-time leaderboard?",
    },
    {
        "id": "sys_003",
        "day": "Day 5 – System Design",
        "topic": "Distributed Caching",
        "question": "Compare Redis and Memcached for distributed caching. How do you handle cache stampede and what eviction policies matter for an AI inference system?",
        "difficulty": 4,
        "probe_template": "You mentioned cache stampede. Describe the probabilistic early expiration technique and how it reduces stampede probability compared to locking.",
    },
    {
        "id": "sys_004",
        "day": "Day 5 – System Design",
        "topic": "Message Queues",
        "question": "Why use a message queue (e.g., Kafka vs. RabbitMQ) in an ML pipeline? Describe at-least-once vs. exactly-once delivery semantics.",
        "difficulty": 4,
        "probe_template": "You explained delivery semantics. How does Kafka's consumer group model enable horizontal scaling while maintaining partition ordering guarantees?",
    },
]


# ---------------------------------------------------------------------------
# Accessors
# ---------------------------------------------------------------------------

def get_all_questions() -> list[dict]:
    """Return the full question bank."""
    return list(QUESTION_BANK)


def get_question_by_id(question_id: str) -> dict | None:
    """Look up a question by its id."""
    for q in QUESTION_BANK:
        if q["id"] == question_id:
            return q
    return None


def get_questions_by_day(day: str) -> list[dict]:
    """Return all questions for a given curriculum day."""
    return [q for q in QUESTION_BANK if q["day"] == day]


def get_all_days() -> list[str]:
    """Return unique curriculum days in order."""
    seen: set[str] = set()
    result: list[str] = []
    for q in QUESTION_BANK:
        if q["day"] not in seen:
            seen.add(q["day"])
            result.append(q["day"])
    return result


def select_next_question(
    asked_ids: list[str],
    days_covered: list[str],
    current_difficulty: int,
) -> dict | None:
    """
    Select the next question using adaptive strategy:
    1. Prioritise uncovered days first.
    2. Within eligible questions, prefer those within ±1 difficulty of current.
    3. Fall back to any unasked question.

    Returns None when no unasked questions remain.
    """
    asked_set = set(asked_ids)
    unasked = [q for q in QUESTION_BANK if q["id"] not in asked_set]

    if not unasked:
        return None

    all_days = get_all_days()
    uncovered_days = [d for d in all_days if d not in days_covered]

    # Priority bucket: uncovered days within difficulty band
    priority = [
        q for q in unasked
        if q["day"] in uncovered_days
        and abs(q["difficulty"] - current_difficulty) <= 1
    ]
    if priority:
        return random.choice(priority)

    # Second: uncovered days (any difficulty)
    uncovered_bucket = [q for q in unasked if q["day"] in uncovered_days]
    if uncovered_bucket:
        return random.choice(uncovered_bucket)

    # Third: covered days within difficulty band
    difficulty_bucket = [
        q for q in unasked
        if abs(q["difficulty"] - current_difficulty) <= 1
    ]
    if difficulty_bucket:
        return random.choice(difficulty_bucket)

    # Fallback: any unasked
    return random.choice(unasked)
