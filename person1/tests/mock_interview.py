"""
mock_interview.py — Local mock interview test script.

Runs a fully automated simulation of an interview session using pre-scripted
answers so no human input or network calls are required.

Usage:
    python -m person1.tests.mock_interview
    python person1/tests/mock_interview.py

Output:
    Prints a full interview transcript with scores, probes, and final feedback.
    Validates all constraints at the end and exits 0 on success, 1 on failure.
"""

from __future__ import annotations

import json
import sys
import os

# Force UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Allow running as a script from the repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from person1.integration import run_turn

# ---------------------------------------------------------------------------
# Scripted answers — designed to trigger all constraint scenarios
# ---------------------------------------------------------------------------

CANDIDATE = {
    "name": "Arjun Sharma",
    "role": "Senior ML Engineer",
}

# Alternating weak/strong answers to trigger probes and cover difficulty scaling
SCRIPTED_ANSWERS = [
    # Turn 1: strong
    (
        "I understand this thoroughly. The reason behind this design is because "
        "of memory efficiency and lazy evaluation. For example, generators yield "
        "one item at a time, therefore they don't store everything in memory. "
        "In practice this is critical for large datasets. The trade-off however "
        "is slightly higher overhead per item."
    ),
    # Turn 2: weak → triggers probe
    "i don't know, not sure about this, maybe it has something to do with caching.",
    # Turn 3: probe answer (medium)
    (
        "Ah, I see. The follow-up makes sense now. The implementation involves "
        "a specific approach to avoid the problem you described. For example, "
        "you would use a different data structure to handle this case."
    ),
    # Turn 4: strong
    (
        "The bias-variance tradeoff is fundamental. High bias means the model "
        "is too simple and underfits — for example, a linear model on non-linear "
        "data. High variance means it overfits to training noise. Therefore we use "
        "cross-validation to diagnose this. In practice regularisation helps "
        "specifically by penalising large weights, because it constrains model "
        "complexity."
    ),
    # Turn 5: strong
    (
        "Self-attention computes query-key-value dot products. The scaling by √d_k "
        "prevents gradients from vanishing in deep models because without it the "
        "dot products grow large. For example, with d_k=512 the raw scores would be "
        "~512 magnitude, therefore the softmax saturates. Multi-head attention "
        "specifically allows the model to attend to different representation subspaces "
        "simultaneously. In practice this captures both syntactic and semantic "
        "relationships."
    ),
    # Turn 6: weak → triggers second probe
    "Not sure, maybe something with cache or a proxy server.",
    # Turn 7: probe answer
    (
        "Right, so cache invalidation specifically requires a TTL-based approach. "
        "For example, you would use write-through or write-behind patterns. "
        "Therefore when the origin changes, the cache is updated immediately "
        "or asynchronously. In practice write-through has higher write latency "
        "because every write hits both cache and storage."
    ),
    # Turn 8: strong
    (
        "For a URL shortener at 1 billion URLs: storage requires roughly 500GB "
        "with a ~500 byte average record. The hashing approach uses base62 encoding "
        "of a counter or MD5 prefix. For scaling specifically, reads are 100x more "
        "common than writes, therefore a CDN + Redis cache handles 99% of reads. "
        "In practice, write scaling uses sharded databases because a single node "
        "would bottleneck at ~10k QPS."
    ),
    # Turn 9+: strong filler to ensure we hit 8+ questions across 4+ days
    (
        "K-fold cross-validation is preferred because it uses all data for both "
        "training and validation. For example with k=5, each fold serves as validation "
        "once. Stratified k-fold specifically maintains class distribution in each fold. "
        "Therefore for imbalanced datasets you must use stratified CV because "
        "random splits might have folds with no minority class samples."
    ),
    (
        "BFS explores level by level using a queue, therefore it finds shortest paths "
        "in unweighted graphs. DFS uses a stack and explores depth-first, for example "
        "to detect cycles. In practice I'd choose BFS for shortest path problems "
        "specifically because it guarantees optimality on unweighted edges."
    ),
    (
        "Gradient descent updates weights by subtracting the gradient times learning "
        "rate. Adam specifically uses adaptive learning rates per parameter because "
        "different parameters have different gradient magnitudes. Therefore Adam "
        "converges faster in practice, for example on sparse features. However the "
        "trade-off is higher memory usage due to moment estimates."
    ),
    # Extra strong answers for safety buffer
    (
        "REST is resource-oriented and stateless, for example it maps well to CRUD. "
        "GraphQL allows flexible queries because the client specifies exactly what fields "
        "it needs, therefore reducing over-fetching. gRPC uses Protocol Buffers specifically "
        "for high-performance internal services. In practice I'd use REST for public APIs "
        "because of tooling ecosystem, and gRPC internally because of streaming support."
    ),
]


# ---------------------------------------------------------------------------
# Run the mock interview
# ---------------------------------------------------------------------------

DIVIDER = "─" * 70
BOLD = "\033[1m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
RESET = "\033[0m"


def print_header(text: str) -> None:
    print(f"\n{CYAN}{DIVIDER}")
    print(f"  {text}")
    print(f"{DIVIDER}{RESET}\n")


def print_agent(text: str) -> None:
    print(f"{GREEN}🤖 AGENT:{RESET}")
    for line in text.split("\n"):
        print(f"   {line}")
    print()


def print_candidate(text: str, score_hint: str = "") -> None:
    label = f"{YELLOW}👤 CANDIDATE{score_hint}:{RESET}"
    print(label)
    snippet = text[:200] + ("..." if len(text) > 200 else "")
    print(f"   {snippet}")
    print()


def main() -> int:
    print_header("ABTALKS AI Interview Agent — Mock Interview Demo")
    print(f"{BOLD}Candidate:{RESET} {CANDIDATE['name']}")
    print(f"{BOLD}Role:{RESET}      {CANDIDATE['role']}\n")

    state = None
    done = False
    feedback = None
    answer_idx = 0
    turn_num = 0

    # Turn 0: Start interview
    print_header("Turn 0 — Starting Interview")
    reply, state, done, feedback = run_turn(None, "Hello! Ready to start.", candidate=CANDIDATE)
    turn_num += 1
    print_agent(reply)

    while not done:
        if answer_idx >= len(SCRIPTED_ANSWERS):
            print(f"{RED}⚠️  Ran out of scripted answers at turn {turn_num}!{RESET}")
            break

        answer = SCRIPTED_ANSWERS[answer_idx]
        answer_idx += 1

        phase_label = state.get("phase", "?")
        q_count = state.get("questions_asked_count", 0)
        days = state.get("days_covered", [])
        probes = state.get("probes_used", [])

        print_header(
            f"Turn {turn_num} — Phase: {phase_label} | "
            f"Qs: {q_count} | Days: {len(days)} | Probes: {len(probes)}"
        )

        score_hint = f" (scripted answer #{answer_idx})"
        print_candidate(answer, score_hint)

        reply, state, done, feedback = run_turn(state, answer)
        turn_num += 1
        print_agent(reply)

    # Final summary
    print_header("Interview Complete — Constraint Validation")

    q_count = state.get("questions_asked_count", 0)
    days = state.get("days_covered", [])
    probes = state.get("probes_used", [])
    answers = state.get("answers", [])
    avg_score = sum(a["score"] for a in answers) / max(len(answers), 1)

    checks = [
        ("≥ 8 questions asked", q_count >= 8, f"{q_count} asked"),
        ("≥ 4 days covered", len(days) >= 4, f"{len(days)} covered: {', '.join(days[:4])}..."),
        ("≥ 1 probe generated", len(probes) >= 1, f"{len(probes)} probes used"),
        ("done=True on final turn", done is True, f"done={done}"),
        ("feedback is not None", feedback is not None, ""),
        ("feedback has correct shape", (
            feedback is not None and
            isinstance(feedback.get("summary"), str) and
            isinstance(feedback.get("strengths"), list) and
            isinstance(feedback.get("gaps"), list) and
            isinstance(feedback.get("next"), str)
        ), ""),
        ("state is JSON-serializable", _check_json(state), ""),
    ]

    all_pass = True
    for label, passed, detail in checks:
        icon = f"{GREEN}✅{RESET}" if passed else f"{RED}❌{RESET}"
        detail_str = f"  ({detail})" if detail else ""
        print(f"  {icon}  {label}{detail_str}")
        if not passed:
            all_pass = False

    print()
    print(f"  {BOLD}Average answer score:{RESET} {avg_score:.2f}/5")
    print(f"  {BOLD}Total turns:{RESET}         {turn_num}")

    # Print feedback
    if feedback:
        print_header("Final Feedback")
        print(f"{BOLD}Summary:{RESET}")
        print(f"  {feedback['summary']}\n")
        print(f"{BOLD}Strengths:{RESET}")
        for s in feedback["strengths"]:
            print(f"  ✅ {s}")
        print(f"\n{BOLD}Gaps:{RESET}")
        for g in feedback["gaps"]:
            print(f"  ⚠️  {g}")
        print(f"\n{BOLD}Next Steps:{RESET}")
        print(f"  {feedback['next']}")

        print(f"\n{BOLD}Raw Feedback JSON:{RESET}")
        print(json.dumps(feedback, indent=2))

    print()
    if all_pass:
        print(f"{GREEN}{BOLD}✅ ALL CONSTRAINTS SATISFIED — Person 1 is ready!{RESET}")
        return 0
    else:
        print(f"{RED}{BOLD}❌ SOME CONSTRAINTS FAILED — see above.{RESET}")
        return 1


def _check_json(obj) -> bool:
    try:
        json.dumps(obj)
        return True
    except (TypeError, ValueError):
        return False


if __name__ == "__main__":
    sys.exit(main())
