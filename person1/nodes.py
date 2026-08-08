from typing import Any, Dict, Optional, cast

from person1.pipeline_adapter import get_pipeline
from person1.contracts import InterviewState
from person1.reasoning import (
    route_after_evaluation,
    generate_socratic_probe,
    mark_day_covered,
    update_strengths_and_gaps,
)
from person1.feedback import generate_final_feedback
from person1.state import update_summary_memory, append_message


def intro_node(state: InterviewState, pipeline: Any = None) -> Dict[str, Any]:
    """
    1. intro_node(state, pipeline)
       - used on first turn
       - generates an interviewer introduction
       - selects the first question using pipeline.retrieve_question(state)
       - updates current_question
       - increments question_count
       - adds day to covered_days
       - adds question_id to asked_question_ids
       - sets reply to intro + first question
       - sets phase = "question"
    """
    if pipeline is None:
        pipeline = get_pipeline()

    candidate_name = state.get("candidate_name", "")
    if candidate_name:
        intro_text = f"Welcome to your technical interview, {candidate_name}! Let's begin with your first question:\n\n"
    else:
        intro_text = "Welcome to your technical interview! Let's begin with your first question:\n\n"

    try:
        question = pipeline.retrieve_question(state)
    except RuntimeError:
        return {
            "phase": "feedback",
            "reply": "We have covered all the topics I wanted to discuss today. Thank you!"
        }

    question_count = state.get("question_count", 0) + 1
    
    covered_days = list(state.get("covered_days", []))
    if question["day"] not in covered_days:
        covered_days.append(question["day"])
        
    asked_ids = list(state.get("asked_question_ids", []))
    if question["question_id"] not in asked_ids:
        asked_ids.append(question["question_id"])

    reply = f"{intro_text}{question['question_text']}"
    
    history = list(state.get("conversation_history", []))
    history.append({
        "role": "interviewer",
        "content": reply,
        "turn_type": "question"
    })

    return {
        "current_question": question,
        "question_count": question_count,
        "covered_days": covered_days,
        "asked_question_ids": asked_ids,
        "reply": reply,
        "phase": "question",
        "conversation_history": history,
    }


def evaluate_answer_node(state: InterviewState, pipeline: Any = None) -> Dict[str, Any]:
    """
    2. evaluate_answer_node(state, pipeline)
       - if last_user_answer is empty or None, set reply asking candidate to answer the current question and return
       - calls pipeline.evaluate_answer(current_question, last_user_answer, state)
       - stores last_evaluation
       - stores last_answer_quality
       - updates strengths and gaps
       - updates summary_memory with brief performance note
       - sets phase = "evaluate"
    """
    if pipeline is None:
        pipeline = get_pipeline()

    last_user_answer = state.get("last_user_answer")
    if not last_user_answer or not str(last_user_answer).strip():
        return {
            "reply": "Please provide an answer to the question so we can evaluate it.",
            "phase": "question"
        }

    # 4. Very long answer
    answer_text = str(last_user_answer).strip()
    if len(answer_text) > 3000:
        answer_text = answer_text[:3000] + "..."


    current_question = state.get("current_question")
    
    # Evaluate
    eval_result = pipeline.evaluate_answer(current_question, answer_text, state)
    quality = eval_result.get("quality", 0.0)


    # Update strengths and gaps
    updated_state = update_strengths_and_gaps(state, current_question, eval_result)
    strengths = updated_state.get("strengths", [])
    gaps = updated_state.get("gaps", [])

    # Update summary memory
    topic = current_question.get("topic", "Topic") if current_question else "Topic"
    note = f"Evaluated topic '{topic}' with score {quality:.2f}."
    summary_state = update_summary_memory(state, note)
    summary_memory = summary_state.get("summary_memory", "")

    return {
        "last_evaluation": eval_result,
        "last_answer_quality": quality,
        "strengths": strengths,
        "gaps": gaps,
        "summary_memory": summary_memory,
        "phase": "evaluate",
    }


def route_decision_node(state: InterviewState) -> Dict[str, Any]:
    """
    3. route_decision_node(state)
       - uses route_after_evaluation(state)
       - sets a field called next_route in returned state
    """
    next_route = route_after_evaluation(state)
    return {
        "next_route": next_route
    }


def probe_node(state: InterviewState, pipeline: Any = None) -> Dict[str, Any]:
    """
    4. probe_node(state, pipeline)
       - generates adaptive follow-up using generate_socratic_probe
       - increments probe_count
       - does not increment question_count
       - adds probe to conversation_history
       - sets reply to the probe question
       - sets phase = "probe"
    """
    if pipeline is None:
        pipeline = get_pipeline()

    current_question = state.get("current_question", {})
    last_user_answer = state.get("last_user_answer", "")
    last_evaluation = state.get("last_evaluation", {})

    probe_text = generate_socratic_probe(state, current_question, last_user_answer, last_evaluation)
    probe_count = state.get("probe_count", 0) + 1

    history = list(state.get("conversation_history", []))
    history.append({
        "role": "interviewer",
        "content": probe_text,
        "turn_type": "probe"
    })

    return {
        "probe_count": probe_count,
        "conversation_history": history,
        "reply": probe_text,
        "phase": "probe",
    }


def next_question_node(state: InterviewState, pipeline: Any = None) -> Dict[str, Any]:
    """
    5. next_question_node(state, pipeline)
       - selects next question using pipeline.retrieve_question(state)
       - increments question_count
       - updates current_question
       - adds day to covered_days
       - adds question_id to asked_question_ids
       - sets reply to next question
       - sets phase = "question"
    """
    if pipeline is None:
        pipeline = get_pipeline()

    try:
        question = pipeline.retrieve_question(state)
    except RuntimeError:
        return {
            "phase": "feedback",
            "reply": "We have covered all the topics I wanted to discuss today. Thank you!"
        }

    question_count = state.get("question_count", 0) + 1

    covered_days = list(state.get("covered_days", []))
    if question["day"] not in covered_days:
        covered_days.append(question["day"])

    asked_ids = list(state.get("asked_question_ids", []))
    if question["question_id"] not in asked_ids:
        asked_ids.append(question["question_id"])

    reply = question.get("question_text", "")

    history = list(state.get("conversation_history", []))
    history.append({
        "role": "interviewer",
        "content": reply,
        "turn_type": "question"
    })

    return {
        "current_question": question,
        "question_count": question_count,
        "covered_days": covered_days,
        "asked_question_ids": asked_ids,
        "reply": reply,
        "phase": "question",
        "conversation_history": history,
    }


def feedback_node(state: InterviewState) -> Dict[str, Any]:
    """
    6. feedback_node(state)
       - calls generate_final_feedback(state)
       - sets feedback
       - sets done = True
       - sets phase = "done"
       - sets reply to a closing message
    """
    feedback_obj = generate_final_feedback(state)
    reply = "Thank you for participating in the interview. Here is your final feedback summary."

    return {
        "feedback": feedback_obj,
        "done": True,
        "phase": "done",
        "reply": reply,
    }
