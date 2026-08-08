from typing import Dict, Any

from person1.contracts import InterviewState, FinalFeedback


def generate_final_feedback(state: InterviewState) -> FinalFeedback:
    """
    Returns exact keys: summary, strengths, gaps, next.
    """
    question_count = state.get("question_count", 0)
    covered_days = state.get("covered_days", [])
    unique_days = len(set(covered_days))
    strengths = state.get("strengths", [])
    gaps = state.get("gaps", [])
    
    summary = f"The candidate answered {question_count} questions across {unique_days} days of the curriculum. Overall performance was solid."
    
    if not strengths:
        strengths = ["The candidate participated fully in the interview."]
        
    if not gaps:
        gaps = ["No major gaps identified. The candidate showed consistent knowledge."]
        
    next_step = "Review specific topics mentioned in gaps to improve depth."
    if not state.get("gaps", []):
        next_step = "Continue building on current knowledge and explore advanced architectures."

    return {
        "summary": summary,
        "strengths": strengths,
        "gaps": gaps,
        "next": next_step
    }
