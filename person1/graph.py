import logging
from typing import Any, Dict, Optional, cast

from langgraph.graph import StateGraph, END

from person1.contracts import InterviewState, TurnResult, FinalFeedback
from person1.state import (
    create_initial_state,
    append_message,
    serialize_state,
    deserialize_state,
)
from person1.reasoning import route_after_evaluation, adjust_difficulty
from person1.nodes import (
    intro_node,
    evaluate_answer_node,
    route_decision_node,
    probe_node,
    next_question_node,
    feedback_node,
)
from person1.pipeline_adapter import get_pipeline

logger = logging.getLogger(__name__)


def retry_node(state: InterviewState) -> Dict[str, Any]:
    """
    Asks the candidate to answer the current question again if answer was empty/invalid.
    """
    current_q = state.get("current_question")
    if current_q and "question_text" in current_q:
        reply = f"Please provide a substantive answer to the question:\n\n{current_q['question_text']}"
    else:
        reply = "Please provide an answer to the question so we can evaluate it."
    return {
        "reply": reply,
        "phase": "question",
        "retry_count": state.get("retry_count", 0) + 1
    }


def adjust_diff_node(state: InterviewState, pipeline: Any = None) -> Dict[str, Any]:
    """
    Adjusts state difficulty level based on evaluation results before advancing to next question.
    """
    last_eval = state.get("last_evaluation", {})
    new_diff = adjust_difficulty(state, last_eval)
    return {
        "difficulty_level": new_diff
    }


def build_graph(pipeline: Any = None) -> Any:
    """
    Builds and compiles the LangGraph StateGraph for Person 1 interview workflow.
    """
    if pipeline is None:
        pipeline = get_pipeline()

    builder = StateGraph(InterviewState)

    # Define nodes
    builder.add_node("start_node", lambda state: {})
    builder.add_node("intro_node", lambda state: intro_node(state, pipeline))
    builder.add_node("evaluate_answer_node", lambda state: evaluate_answer_node(state, pipeline))
    builder.add_node("retry_node", retry_node)
    builder.add_node("probe_node", lambda state: probe_node(state, pipeline))
    builder.add_node("adjust_diff_node", lambda state: adjust_diff_node(state, pipeline))
    builder.add_node("next_question_node", lambda state: next_question_node(state, pipeline))
    builder.add_node("feedback_node", lambda state: feedback_node(state, pipeline))

    # Set entry point
    builder.set_entry_point("start_node")

    # Conditional entry routing
    def _select_entry(state: InterviewState) -> str:
        if state.get("phase") == "intro" or state.get("question_count", 0) == 0:
            return "intro_node"
        return "evaluate_answer_node"

    builder.add_conditional_edges(
        "start_node",
        _select_entry,
        {
            "intro_node": "intro_node",
            "evaluate_answer_node": "evaluate_answer_node",
        }
    )

    # Intro or Next Question -> END or Feedback
    def _after_question_node(state: InterviewState) -> str:
        if state.get("phase") == "feedback":
            return "feedback_node"
        return END

    builder.add_conditional_edges(
        "intro_node",
        _after_question_node,
        {"feedback_node": "feedback_node", END: END}
    )

    # Evaluate -> Route Decision
    def _route_decision(state: InterviewState) -> str:
        if state.get("phase") == "question":
            return END
            
        last_user_answer = state.get("last_user_answer")
        if not last_user_answer or not str(last_user_answer).strip():
            return "retry"
        return route_after_evaluation(state)

    builder.add_conditional_edges(
        "evaluate_answer_node",
        _route_decision,
        {
            "retry": "retry_node",
            "probe": "probe_node",
            "continue": "next_question_node",
            "increase_difficulty": "adjust_diff_node",
            "feedback": "feedback_node",
            END: END,
        }
    )

    # Edges after action nodes
    builder.add_edge("retry_node", END)
    builder.add_edge("probe_node", END)
    builder.add_edge("adjust_diff_node", "next_question_node")
    builder.add_conditional_edges(
        "next_question_node",
        _after_question_node,
        {"feedback_node": "feedback_node", END: END}
    )
    builder.add_edge("feedback_node", END)

    return builder.compile()



# Cache graph instance per pipeline for performance
_GRAPH_CACHE = {}

def get_graph(pipeline: Any = None) -> Any:
    pipe_key = id(pipeline) if pipeline is not None else "default"
    if pipe_key not in _GRAPH_CACHE:
        _GRAPH_CACHE[pipe_key] = build_graph(pipeline)
    return _GRAPH_CACHE[pipe_key]


def run_turn(
    session_state: Optional[dict] = None,
    message: Optional[str] = None,
    candidate: Optional[dict] = None,
    pipeline: Optional[Any] = None,
) -> TurnResult:
    """
    Public entry point for running a turn of the interview engine.
    """
    try:
        if pipeline is None:
            pipeline = get_pipeline()

        # Check if new session
        if session_state is None:
            state = create_initial_state(candidate=candidate)
            if hasattr(pipeline, "build_competency_map") and candidate and "id" in candidate:
                try:
                    state["competency_map"] = pipeline.build_competency_map(candidate["id"])
                except Exception as e:
                    logger.error(f"Failed to build competency map: {e}")
        else:
            state = deserialize_state(session_state)

        # Check if already completed
        if state.get("done"):
            return {
                "reply": state.get("reply") or "The interview has already been completed.",
                "state": serialize_state(state),
                "done": True,
                "feedback": state.get("feedback"),
            }

        # If user provided a message on a non-intro turn (or turn 0 answer), attach it
        if message is not None and state.get("question_count", 0) > 0:
            state["last_user_answer"] = message
            state = append_message(state, "candidate", message, turn_type="answer")
        elif message is not None and session_state is None:
            # Turn 0 message optional recording
            state["last_user_answer"] = None

        # Execute the graph
        graph = get_graph(pipeline)
        result_state = graph.invoke(state)

        # 6. State corruption handling
        # Attempt to serialize, if not json serializable, sanitize it
        try:
            safe_state = serialize_state(result_state)
        except Exception:
            # Fallback sanitization
            import json
            def _sanitize(obj):
                if isinstance(obj, dict):
                    return {k: _sanitize(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [_sanitize(v) for v in obj]
                elif isinstance(obj, (str, int, float, bool, type(None))):
                    return obj
                else:
                    return str(obj)
            safe_state = _sanitize(result_state)

        is_done = result_state.get("done", False)

        return {
            "reply": result_state.get("reply", "An error occurred."),
            "state": safe_state,
            "done": is_done,
            "feedback": result_state.get("feedback"),
        }
    except Exception as e:
        logger.error(f"Error in run_turn: {e}", exc_info=True)
        fallback_state = serialize_state(session_state or create_initial_state(candidate=candidate))
        fallback_state["error"] = str(e)
        return {
            "reply": "I'm sorry, our interview system encountered a temporary error. Let's try to proceed.",
            "state": fallback_state,
            "done": False,
            "feedback": None,
        }
