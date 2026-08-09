from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from schemas import InterviewRequest, InterviewResponse, FeedbackModel, CandidateProfileResponse
from typing import List
from session_store import create_session, get_session, save_session
import logging
import os
from dotenv import load_dotenv

import json

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# We need to import run_turn from person1
# Using absolute imports relative to project root
from person1.graph import run_turn

app = FastAPI(title="ABTALKS AI Interview API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/api/candidates", response_model=List[CandidateProfileResponse])
async def get_candidates():
    candidates_file = os.path.join(os.path.dirname(__file__), "data", "candidates.json")
    try:
        with open(candidates_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        profiles = []
        for cand in data.get("candidates", []):
            member = cand.get("member", {})
            missions = cand.get("missions", [])
            skills = [m["title"] for m in missions if m.get("passed")][:4]
            if not skills:
                skills = ["Python", "FastAPI"]
            
            profiles.append(CandidateProfileResponse(
                id=member.get("id", ""),
                name=member.get("name", ""),
                jobRole=member.get("jobRole", ""),
                yearsExperience=member.get("yearsExperience", 0),
                skills=skills
            ))
        return profiles
    except Exception as e:
        logger.error(f"Failed to load candidates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load candidates."
        )

@app.post("/api/interview", response_model=InterviewResponse)
async def interview_turn(request: InterviewRequest):
    try:
        session_id = request.sessionId
        message = request.message
        candidate = request.candidate
        
        # Load state
        state = get_session(session_id)
        
        # Determine if this is a new session
        if state is None:
            if candidate is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Candidate information is required to start a new interview session."
                )
            # Create session
            # We don't have the initial state yet, we get it from the first run_turn call
            logger.info(f"Starting new session {session_id} for candidate {candidate.id}")
            result = run_turn(session_state=None, message="hi", candidate=candidate.model_dump())
            state = result["state"]
            create_session(session_id, candidate.id, state)
            
            feedback = None
            if result.get("feedback"):
                feedback = FeedbackModel(**result["feedback"])
                
            return InterviewResponse(
                reply=result["reply"],
                done=result["done"],
                feedback=feedback,
                deliberation=state.get("last_deliberation"),
                answerDiff=state.get("last_answer_diff")
            )
            
        # Ongoing session
        if not message or not message.strip():
            # Handle empty message (e.g. page reload or React StrictMode double-mount)
            # by returning the last known reply from the state.
            return InterviewResponse(
                reply=state.get("reply", "Take your time — please explain your approach before we move on."),
                done=state.get("done", False),
                feedback=FeedbackModel(**state["feedback"]) if state.get("feedback") else None
            )
            
        # Proceed with run_turn
        logger.info(f"Processing turn for session {session_id}")
        result = run_turn(session_state=state, message=message)
        
        # Save updated state
        save_session(session_id, result["state"])
        
        feedback = None
        if result.get("feedback"):
            feedback = FeedbackModel(**result["feedback"])
            
        return InterviewResponse(
            reply=result["reply"],
            done=result["done"],
            feedback=feedback,
            deliberation=result["state"].get("last_deliberation"),
            answerDiff=result["state"].get("last_answer_diff")
        )
        
    except Exception as e:
        logger.error(f"Error processing interview turn: {e}", exc_info=True)
        # We don't expose stack traces.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred while processing your request."
        )

from schemas import InterruptRequest, InterruptResponse
from person1.pipeline_adapter import get_pipeline

@app.post("/api/interrupt", response_model=InterruptResponse)
async def check_interruption(request: InterruptRequest):
    try:
        session_id = request.sessionId
        partial_answer = request.partialAnswer
        
        state = get_session(session_id)
        if state is None:
            return InterruptResponse(interrupt=False)
            
        # Basic heuristic: if the answer is getting too long without substance, or includes certain phrases
        # Here we do a lightweight LLM call to decide if we should interrupt.
        pipeline = get_pipeline()
        
        if not hasattr(pipeline, '_call_llm'):
            # Heuristic fallback for MockPipeline
            words = partial_answer.lower().split()
            word_count = len(words)
            if word_count > 40:
                return InterruptResponse(interrupt=True, reply="Hold on, let's keep it concise. What is the core idea?")
            
            weak_phrases = ["not sure", "i don't know", "maybe", "i guess", "so yeah", "like", "um", "uh", "stuff", "things"]
            weak_count = sum(1 for phrase in weak_phrases if phrase in partial_answer.lower())
            
            if word_count >= 10 and weak_count >= 2:
                 return InterruptResponse(interrupt=True, reply="Wait, let me stop you there. Can you be more specific?")
                 
            return InterruptResponse(interrupt=False)
        
        system_prompt = (
            "You are a strict technical interviewer. The candidate is currently typing their answer to the following question:\n"
            f"Question: {state.get('current_question', {}).get('question_text', 'Unknown')}\n\n"
            "Here is what they have typed so far:\n"
            f"\"{partial_answer}\"\n\n"
            "If the candidate is rambling, being extremely vague, or dodging the question, you should interrupt them. "
            "Reply with 'INTERRUPT: <your interruption message>' if you want to interrupt. "
            "Reply with 'CONTINUE' if they should keep going."
        )
        
        try:
            # Try to use the underlying langchain llm
            from langchain_core.messages import SystemMessage
            response = pipeline.llm.invoke([SystemMessage(content=system_prompt)])
        except Exception:
            # Fallback to heuristic
            words = partial_answer.lower().split()
            if len(words) > 40:
                return InterruptResponse(interrupt=True, reply="Hold on, let's keep it concise. What is the core idea?")
            return InterruptResponse(interrupt=False)
        
        response_text = response.content.strip()
        if response_text.startswith("INTERRUPT:"):
            msg = response_text.replace("INTERRUPT:", "").strip()
            return InterruptResponse(interrupt=True, reply=msg)
            
        return InterruptResponse(interrupt=False)
        
    except Exception as e:
        logger.error(f"Error in interrupt check: {e}", exc_info=True)
        return InterruptResponse(interrupt=False)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
