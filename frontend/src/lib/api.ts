export interface Candidate {
  id: string;
  name: string;
}

export interface Feedback {
  summary: string;
  strengths: string[];
  gaps: string[];
  next: string;
}

export interface InterviewResponse {
  reply: string;
  done: boolean;
  feedback: Feedback | null;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function startInterview(sessionId: string, candidate: Candidate): Promise<InterviewResponse> {
  const response = await fetch(`${API_BASE_URL}/api/interview`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      sessionId,
      candidate,
    }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to start interview');
  }
  
  return response.json();
}

export async function sendAnswer(sessionId: string, message: string): Promise<InterviewResponse> {
  const response = await fetch(`${API_BASE_URL}/api/interview`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      sessionId,
      message,
    }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to send answer');
  }
  
  return response.json();
}
