import json
import uuid
from typing import Optional, Dict, Any, cast

from person1.contracts import InterviewState


def create_initial_state(candidate: Optional[dict] = None, session_id: Optional[str] = None) -> InterviewState:
    """
    creates a valid initial InterviewState
    """
    if session_id is None:
        session_id = str(uuid.uuid4())
        
    candidate_id = ""
    candidate_name = ""
    if candidate:
        candidate_id = candidate.get("id", "")
        candidate_name = candidate.get("name", "")
        
    # Cast to InterviewState is used to bypass type checker complaints if fields aren't completely exact 
    # but they will be exact.
    return {
        "session_id": session_id,
        "candidate_id": candidate_id,
        "candidate_name": candidate_name,
        "phase": "intro",
        "competency_map": {},
        "question_count": 0,
        "probe_count": 0,
        "retry_count": 0,
        "covered_days": [],
        "asked_question_ids": [],
        "current_question": None,
        "last_user_answer": None,
        "last_answer_quality": 0.0,
        "last_evaluation": None,
        "difficulty_level": 2,
        "conversation_history": [],
        "summary_memory": "",
        "strengths": [],
        "gaps": [],
        "feedback": None,
        "done": False,
        "reply": "",
        "error": None,
    }


def append_message(state: InterviewState, role: str, content: str, turn_type: str = "message") -> InterviewState:
    """
    appends to conversation_history
    """
    new_state = state.copy()
    history = list(new_state.get("conversation_history", []))
    history.append({
        "role": role,
        "content": content,
        "turn_type": turn_type
    })
    new_state["conversation_history"] = history
    return cast(InterviewState, new_state)


def trim_history(state: InterviewState, max_turns: int = 4) -> InterviewState:
    """
    keeps only the latest 4 conversation turns in conversation_history
    older context should be compressed into summary_memory
    """
    new_state = state.copy()
    history = list(new_state.get("conversation_history", []))
    
    if len(history) > max_turns:
        old_messages = history[:-max_turns]
        kept_messages = history[-max_turns:]
        
        # update_summary_memory compresses old messages
        summary_add = " ".join([f"{msg['role']}: {msg['content']}" for msg in old_messages])
        new_state = update_summary_memory(new_state, summary_add)
        new_state["conversation_history"] = kept_messages
        
    return cast(InterviewState, new_state)


def update_summary_memory(state: InterviewState, new_information: str) -> InterviewState:
    """
    appends concise information to summary_memory
    avoids making summary_memory too long
    """
    new_state = state.copy()
    current_summary = new_state.get("summary_memory", "")
    if current_summary:
        new_summary = current_summary + "\n" + new_information
    else:
        new_summary = new_information
        
    # truncate if it gets too long
    if len(new_summary) > 2000:
        new_summary = "..." + new_summary[-1997:]
        
    new_state["summary_memory"] = new_summary
    return cast(InterviewState, new_state)


def serialize_state(state: InterviewState) -> dict:
    """
    returns JSON serializable dict
    """
    return json.loads(json.dumps(state))


def deserialize_state(data: dict) -> InterviewState:
    """
    reconstructs state from dict safely
    fills missing fields with defaults
    """
    # use create_initial_state to get all defaults
    state = create_initial_state()
    # update with given data
    state.update(data)
    return cast(InterviewState, state)


# Backward compatibility aliases
make_initial_state = create_initial_state
state_add_message = append_message
state_to_dict = serialize_state

