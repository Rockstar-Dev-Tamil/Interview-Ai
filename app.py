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
            profiles.append(CandidateProfileResponse(
                id=member.get("id", ""),
                name=member.get("name", ""),
                jobRole=member.get("jobRole", ""),
                yearsExperience=member.get("yearsExperience", 0)
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
                feedback=feedback
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
            feedback=feedback
        )
        
    except Exception as e:
        logger.error(f"Error processing interview turn: {e}", exc_info=True)
        # We don't expose stack traces.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred while processing your request."
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
