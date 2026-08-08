from pydantic import BaseModel, Field
from typing import Optional, List

class CandidateProfileResponse(BaseModel):
    id: str = Field(..., description="Candidate ID")
    name: str = Field(..., description="Candidate Name")
    jobRole: str = Field(..., description="Candidate Job Role")
    yearsExperience: int = Field(..., description="Candidate Years of Experience")


class CandidateModel(BaseModel):
    id: str = Field(..., description="Candidate's unique ID")
    name: str = Field(..., description="Candidate's display name")


class InterviewRequest(BaseModel):
    sessionId: str = Field(..., description="Unique session identifier")
    message: Optional[str] = Field(None, description="Candidate's answer text")
    candidate: Optional[CandidateModel] = Field(None, description="Candidate details, required on first turn")


class FeedbackModel(BaseModel):
    summary: str = Field(..., description="Overall performance summary")
    strengths: List[str] = Field(..., description="What the candidate did well")
    gaps: List[str] = Field(..., description="Areas to improve")
    next: str = Field(..., description="Recommended next steps")


class InterviewResponse(BaseModel):
    reply: str = Field(..., description="Interviewer's next message")
    done: bool = Field(..., description="True if the interview is complete")
    feedback: Optional[FeedbackModel] = Field(None, description="Final feedback, populated when done=True")
