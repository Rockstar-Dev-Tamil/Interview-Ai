"""
memory.py — Memory extraction and rolling compression utilities.
"""

from __future__ import annotations

COMPRESS_EVERY = 3


def should_compress(answers: list[dict]) -> bool:
    return len(answers) > 0 and len(answers) % COMPRESS_EVERY == 0


def compress_answers(answers: list[dict], questions_map: dict[str, dict]) -> str:
    if not answers:
        return ""
    lines = ["=== Interview Progress Summary ==="]
    for idx, ans in enumerate(answers, 1):
        qid = ans["question_id"]
        q = questions_map.get(qid, {})
        topic = q.get("topic", "Unknown topic")
        day = q.get("day", "Unknown day")
        score = ans["score"]
        flags = ", ".join(ans.get("flags", []))
        probe_note = " [follow-up given]" if ans.get("probe_used") else ""
        lines.append(f"Q{idx} [{day} — {topic}]  Score: {score}/5  Flags: {flags}{probe_note}")
        raw_snippet = ans["raw"][:100] + ("..." if len(ans["raw"]) > 100 else "")
        lines.append(f"  Answer: {raw_snippet}")
    lines.append("=== End of Summary ===")
    return "\n".join(lines)


def build_prompt_context(memory_summary: str, candidate: dict) -> str:
    name = candidate.get("name", "the candidate")
    role = candidate.get("role", "a software engineering role")
    ctx_parts = [
        f"You are an AI technical interviewer evaluating {name} for {role}.",
        "Be concise, professional, and encouraging.",
    ]
    if memory_summary:
        ctx_parts.append("")
        ctx_parts.append(memory_summary)
    return "\n".join(ctx_parts)
