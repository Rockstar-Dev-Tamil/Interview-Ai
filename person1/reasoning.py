from typing import Dict, Any, cast

from person1.contracts import InterviewState, EvaluationResult, QuestionArtifact


def route_after_evaluation(state: InterviewState) -> str:
    """
    Return one of: "retry", "probe", "continue", "increase_difficulty", "feedback"
    """
    last_user_answer = state.get("last_user_answer")
    if last_user_answer is not None and not str(last_user_answer).strip():
        return "retry"


    question_count = state.get("question_count", 0)
    unique_covered_days = len(set(state.get("covered_days", [])))
    last_answer_quality = state.get("last_answer_quality", 0.0)
    probe_count = state.get("probe_count", 0)

    if question_count >= 12:
        return "feedback"

    if question_count >= 8 and unique_covered_days >= 4 and last_answer_quality >= 0.65:
        return "feedback"

    last_eval = state.get("last_evaluation", {})
    recommended_action = last_eval.get("recommended_action")
    
    if recommended_action and recommended_action in ["retry", "probe", "continue", "increase_difficulty"]:
        if recommended_action == "probe" and probe_count >= 3:
            return "continue"
        return recommended_action

    if last_answer_quality < 0.4 and probe_count < 3:
        return "probe"

    if last_answer_quality > 0.8:
        return "increase_difficulty"

    return "continue"



def adjust_difficulty(state: InterviewState, evaluation_result: EvaluationResult) -> int:
    """
    Adjusts the difficulty level based on answer quality.
    """
    current_difficulty = state.get("difficulty_level", 2)
    quality = evaluation_result.get("quality", 0.0)
    
    if quality > 0.8:
        return min(5, current_difficulty + 1)
    elif quality < 0.3:
        return max(1, current_difficulty - 1)
    return current_difficulty


def generate_socratic_probe(state: InterviewState, question: QuestionArtifact, last_user_answer: str, evaluation_result: EvaluationResult) -> str:
    """
    Generates a follow-up probe based on what concepts the candidate missed.
    Uses hints from the question_artifact.
    """
    if evaluation_result is None:
        evaluation_result = {}
        
    missing_concepts = evaluation_result.get("missing_concepts", [])
    hints = question.get("follow_up_hints", [])
    
    if not missing_concepts:
        # no missing concepts, deeper scalability or tradeoff question
        topic = question.get("topic", "this concept")
        return f"You explained {topic} well. How would this approach scale under high production load, and what tradeoffs did you consider?"
        
    first_missing = missing_concepts[0]
    
    quality = evaluation_result.get("quality", 0.0)
    if quality < 0.3:
        return f"Let's break it down a bit. How would you handle {first_missing} in this scenario?"
        
    return f"You mentioned some good points, but how would you handle {first_missing} in this scenario?"


def mark_day_covered(state: InterviewState, day: int) -> InterviewState:
    """
    Adds day to covered_days if not already present.
    """
    new_state = state.copy()
    covered = list(new_state.get("covered_days", []))
    if day not in covered:
        covered.append(day)
    new_state["covered_days"] = covered
    return cast(InterviewState, new_state)


def update_strengths_and_gaps(state: InterviewState, question: QuestionArtifact, evaluation_result: EvaluationResult) -> InterviewState:
    """
    Updates strengths and gaps in the state based on the evaluation result.
    """
    new_state = state.copy()
    quality = evaluation_result.get("quality", 0.0)
    topic = question.get("topic", "General")
    
    strengths = list(new_state.get("strengths", []))
    gaps = list(new_state.get("gaps", []))
    
    if quality >= 0.7:
        strength = f"Strong understanding of {topic}"
        if strength not in strengths:
            strengths.append(strength)
            
    if quality < 0.4:
        missing = evaluation_result.get("missing_concepts", [])
        if missing:
            gap = f"Needs review on {missing[0]} in {topic}"
        else:
            gap = f"Needs improvement in {topic}"
            
        if gap not in gaps:
            gaps.append(gap)
            
    new_state["strengths"] = strengths
    new_state["gaps"] = gaps
    return cast(InterviewState, new_state)
