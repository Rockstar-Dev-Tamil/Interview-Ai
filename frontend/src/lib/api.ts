export interface Candidate {
  id: string;
  name: string;
  jobRole?: string;
  yearsExperience?: number;
  skills?: string[];
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

const getApiBaseUrl = () => {
  if (typeof window !== 'undefined') {
    return `http://${window.location.hostname}:8000`;
  }
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
};

export async function getCandidates(): Promise<Candidate[]> {
  const response = await fetch(`${getApiBaseUrl()}/api/candidates`);
  if (!response.ok) {
    throw new Error('Failed to fetch candidates');
  }
  return response.json();
}

export async function startInterview(sessionId: string, candidate: Candidate): Promise<InterviewResponse> {
  const response = await fetch(`${getApiBaseUrl()}/api/interview`, {
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
  const response = await fetch(`${getApiBaseUrl()}/api/interview`, {
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

export interface InterruptResponse {
  interrupt: boolean;
  reply: string | null;
}

export async function checkInterruption(sessionId: string, partialAnswer: string): Promise<InterruptResponse> {
  const response = await fetch(`${getApiBaseUrl()}/api/interrupt`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      sessionId,
      partialAnswer,
    }),
  });
  
  if (!response.ok) {
    return { interrupt: false, reply: null };
  }
  
  return response.json();
}
