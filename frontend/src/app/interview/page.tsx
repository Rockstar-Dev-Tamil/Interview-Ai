"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { startInterview, sendAnswer, checkInterruption } from "@/lib/api";
import InterviewMessage from "@/components/ui/InterviewMessage";
import InterviewInput from "@/components/ui/InterviewInput";
import ThinkingIndicator from "@/components/ui/ThinkingIndicator";
import ErrorState from "@/components/ui/ErrorState";
import LoadingState from "@/components/ui/LoadingState";
import FocusCamera, { FocusStatus } from "@/components/ui/FocusCamera";

type Message = {
  role: "ai" | "user";
  content: string;
  isProbe?: boolean;
};

export default function InterviewPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [questionCount, setQuestionCount] = useState(1);
  const [candidateName, setCandidateName] = useState("");
  const [candidateSkills, setCandidateSkills] = useState<string[]>([]);
  const [input, setInput] = useState("");
  const [interruptCount, setInterruptCount] = useState(0);
  const [timeLeft, setTimeLeft] = useState(30 * 60); // 30 mins
  const [proctorStatus, setProctorStatus] = useState<FocusStatus>("OFFLINE");
  const [proctorMessage, setProctorMessage] = useState("Proctoring Offline");
  const [hasStarted, setHasStarted] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(true);
  const [focusViolations, setFocusViolations] = useState(0);
  const [showWarning, setShowWarning] = useState(false);
  const [isTimeUp, setIsTimeUp] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const speakText = (text: string) => {
    if (typeof window !== "undefined" && window.speechSynthesis) {
      window.speechSynthesis.cancel(); // Stop any ongoing speech
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.05; // Slightly faster for a more natural conversational pace
      window.speechSynthesis.speak(utterance);
    }
  };

  // Timer countdown
  useEffect(() => {
    if (!hasStarted) return;
    if (timeLeft <= 0) {
      setIsTimeUp(true);
      return;
    }
    
    const interval = setInterval(() => {
      setTimeLeft((prev) => prev - 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [timeLeft, router]);

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60).toString().padStart(2, "0");
    const s = (seconds % 60).toString().padStart(2, "0");
    return `${m}:${s}`;
  };

  // Initialize session
  useEffect(() => {
    if (!hasStarted) return;
    const init = async () => {
      const sessionId = localStorage.getItem("sessionId");
      const cId = localStorage.getItem("candidateId");
      const cName = localStorage.getItem("candidateName");
      const skillsStr = localStorage.getItem("candidateSkills");
      
      if (!sessionId || !cId || !cName) {
        router.push("/");
        return;
      }
      
      setCandidateName(cName);
      if (skillsStr) {
        try {
          setCandidateSkills(JSON.parse(skillsStr));
        } catch (e) {
          console.error(e);
        }
      }

      try {
        const res = await startInterview(sessionId, { id: cId, name: cName });
        setMessages([{ role: "ai", content: res.reply }]);
        speakText(res.reply);
        setLoading(false);
      } catch (err) {
        console.error(err);
        setError("Failed to start session. Please try again.");
        setLoading(false);
      }
    };

    init();
  }, [router]);

  // Navigate to coding phase on question 14
  useEffect(() => {
    if (questionCount >= 14) {
      router.push("/coding");
    }
  }, [questionCount, router]);

  // Scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async (messageText: string) => {
    if (!messageText.trim() || loading) return;

    const sessionId = localStorage.getItem("sessionId");
    if (!sessionId) return;

    // Optimistically add user message
    setMessages((prev) => [...prev, { role: "user", content: messageText }]);
    setLoading(true);
    setError(null);
    setInput(""); // Clear input on successful send trigger

    try {
      const res = await sendAnswer(sessionId, messageText);
      
      const isProbe = res.reply.includes("Take your time") || res.reply.includes("explain your approach");
      if (!isProbe && !res.done) {
        setQuestionCount((c) => c + 1);
      }

      setMessages((prev) => [...prev, { role: "ai", content: res.reply, isProbe }]);
      speakText(res.reply);

      if (res.done) {
        localStorage.setItem("feedback", JSON.stringify(res.feedback));
        router.push("/feedback");
      }
    } catch (err) {
      console.error(err);
      setError("Failed to send your answer. Please try again.");
      setMessages((prev) => prev.slice(0, -1));
      setInput(messageText);
    } finally {
      setLoading(false);
    }
  };

  const handlePauseTyping = async (partialText: string) => {
    const sessionId = localStorage.getItem("sessionId");
    if (!sessionId || loading || partialText.trim().length < 50) return;

    try {
      const res = await checkInterruption(sessionId, partialText);
      if (res.interrupt && res.reply) {
        // The AI has decided to interrupt!
        setMessages((prev) => [
          ...prev, 
          { role: "user", content: partialText },
          { role: "ai", content: res.reply as string, isProbe: true }
        ]);
        speakText(res.reply);
        
        // Force the input to remount and clear by incrementing key
        setInterruptCount((c) => c + 1);
      }
    } catch (e) {
      console.error("Interruption check failed", e);
    }
  };

  // Proctor status tracking for continuous unfocus
  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (hasStarted && (proctorStatus === "ABSENT" || proctorStatus === "DISTRACTED")) {
      timer = setTimeout(() => {
        setFocusViolations(prev => prev + 1);
        setShowWarning(true);
      }, 120 * 1000); // 2 mins
    }
    return () => clearTimeout(timer);
  }, [hasStarted, proctorStatus]);

  // Fullscreen & focus tracking
  useEffect(() => {
    if (!hasStarted) return;

    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    const handleFocusLost = () => {
      setFocusViolations(prev => prev + 1);
      setShowWarning(true);
    };

    const handleVisibilityChange = () => {
      if (document.hidden) handleFocusLost();
    };

    const handleBlur = () => {
      handleFocusLost();
    };

    document.addEventListener("fullscreenchange", handleFullscreenChange);
    document.addEventListener("visibilitychange", handleVisibilityChange);
    window.addEventListener("blur", handleBlur);

    return () => {
      document.removeEventListener("fullscreenchange", handleFullscreenChange);
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      window.removeEventListener("blur", handleBlur);
    };
  }, [hasStarted]);

  const enterFullscreenAndStart = async () => {
    try {
      await document.documentElement.requestFullscreen();
    } catch (err) {
      console.error("Error attempting to enable fullscreen:", err);
    } finally {
      setIsFullscreen(true);
      setHasStarted(true);
    }
  };

  const hasFailed = focusViolations >= 5;

  if (error && messages.length === 0) {
    return <LoadingState icon="alert" title="Session Error" subtitle="Failed to start the session. Returning home..." />;
  }

  return (
    <>
      {isTimeUp && (
        <div className="fixed inset-0 bg-red-950/90 backdrop-blur-md z-[120] flex flex-col items-center justify-center p-6 text-center">
          <div className="bg-black/50 border border-red-500/50 p-8 rounded-2xl max-w-md w-full shadow-[0_0_50px_rgba(239,68,68,0.3)]">
            <h2 className="text-2xl font-bold text-red-500 mb-2 uppercase tracking-wider animate-pulse">Time's Up!</h2>
            <p className="text-text-secondary text-sm mb-6">
              Your 30-minute interview time limit has expired. The interview has been terminated.
            </p>
            <button 
              onClick={() => router.push("/")}
              className="w-full bg-red-500 text-white font-semibold py-3 rounded-xl hover:bg-red-600 transition-colors"
            >
              Return Home
            </button>
          </div>
        </div>
      )}

      {hasFailed && !isTimeUp && (
        <div className="fixed inset-0 bg-red-950/90 backdrop-blur-md z-[120] flex flex-col items-center justify-center p-6 text-center">
          <div className="bg-black/50 border border-red-500/50 p-8 rounded-2xl max-w-md w-full shadow-[0_0_50px_rgba(239,68,68,0.3)]">
            <h2 className="text-2xl font-bold text-red-500 mb-2 uppercase tracking-wider">Interview Terminated</h2>
            <p className="text-text-secondary text-sm mb-6">
              Your interview has been terminated due to excessive focus and cheating policy violations.
            </p>
            <button 
              onClick={() => router.push("/")}
              className="w-full bg-red-500 text-white font-semibold py-3 rounded-xl hover:bg-red-600 transition-colors"
            >
              Return Home
            </button>
          </div>
        </div>
      )}

      {!hasStarted && !hasFailed && !isTimeUp && (
        <div className="fixed inset-0 bg-bg/90 backdrop-blur-sm z-[100] flex flex-col items-center justify-center p-6 text-center">
          <div className="bg-surface border border-border p-8 rounded-2xl max-w-md w-full shadow-2xl">
            <h2 className="text-2xl font-bold text-white mb-2">Ready to Begin?</h2>
            <p className="text-text-secondary text-sm mb-6">
              This interview requires full-screen mode. Do not switch tabs or windows during the interview, as violations will be recorded.
            </p>
            <button 
              onClick={enterFullscreenAndStart}
              className="w-full bg-primary text-black font-semibold py-3 rounded-xl hover:bg-primary/90 transition-colors"
            >
              Start Interview
            </button>
          </div>
        </div>
      )}

      {hasStarted && !isFullscreen && !hasFailed && !isTimeUp && (
        <div className="fixed inset-0 bg-red-950/90 backdrop-blur-md z-[100] flex flex-col items-center justify-center p-6 text-center">
          <div className="bg-black/50 border border-red-500/50 p-8 rounded-2xl max-w-md w-full shadow-[0_0_50px_rgba(239,68,68,0.3)]">
            <h2 className="text-2xl font-bold text-red-500 mb-2 uppercase tracking-wider animate-pulse">Fullscreen Exited</h2>
            <p className="text-text-secondary text-sm mb-6">
              You have exited full-screen mode. Please return to full-screen to continue your interview.
            </p>
            <button 
              onClick={enterFullscreenAndStart}
              className="w-full bg-red-500 text-white font-semibold py-3 rounded-xl hover:bg-red-600 transition-colors"
            >
              Return to Full Screen
            </button>
          </div>
        </div>
      )}

      {showWarning && !hasFailed && !isTimeUp && (
        <div className="fixed inset-0 bg-red-950/90 backdrop-blur-md z-[110] flex flex-col items-center justify-center p-6 text-center">
          <div className="bg-black/50 border border-red-500/50 p-8 rounded-2xl max-w-md w-full shadow-[0_0_50px_rgba(239,68,68,0.3)]">
            <h2 className="text-2xl font-bold text-red-500 mb-2 uppercase tracking-wider">Focus Lost</h2>
            <p className="text-text-secondary text-sm mb-4">
              Switching tabs or windows is strictly prohibited during the interview. 
            </p>
            <p className="text-red-400 font-mono text-xs mb-6 bg-red-950 p-2 rounded border border-red-500/30">
              Violations recorded: {focusViolations}
            </p>
            <button 
              onClick={() => {
                setShowWarning(false);
                if (!document.fullscreenElement) enterFullscreenAndStart();
              }}
              className="w-full bg-red-500 text-white font-semibold py-3 rounded-xl hover:bg-red-600 transition-colors"
            >
              I Understand
            </button>
          </div>
        </div>
      )}

      <div className={`flex-1 flex min-h-[100dvh] bg-bg ${!hasStarted || !isFullscreen || showWarning || hasFailed || isTimeUp ? 'blur-sm pointer-events-none overflow-hidden' : ''}`}>
      {/* Left Sidebar */}
      <div className="hidden md:flex w-[300px] flex-col border-r border-border bg-surface-2 overflow-y-auto fixed left-0 top-0 bottom-0 z-10">
        <div className="p-8 pb-4">
          <h1 className="text-xl font-bold text-white tracking-wide uppercase">ABTALKS AI</h1>
          <p className="text-[10px] text-text-tertiary uppercase tracking-widest mt-1">Interview Terminal</p>
        </div>
        
        <div className="px-8 py-6">
          <h2 className="text-[10px] font-semibold text-text-tertiary uppercase tracking-wider mb-4">Candidate Profile</h2>
          <div className="bg-surface rounded-xl p-4 border border-border mb-3 shadow-sm">
            <p className="text-[10px] text-text-tertiary mb-1">Name</p>
            <p className="text-sm font-semibold text-text">{candidateName || "Candidate"}</p>
          </div>
          <div className="bg-surface rounded-xl p-4 border border-border shadow-sm">
            <p className="text-[10px] text-text-tertiary mb-1">Session ID</p>
            <p className="text-sm font-semibold text-primary">Active Session</p>
          </div>
        </div>

        <div className="px-8 py-4">
          <h2 className="text-[10px] font-semibold text-text-tertiary uppercase tracking-wider mb-4">Key Competencies</h2>
          <div className="flex flex-wrap gap-2">
            {(candidateSkills.length > 0 ? candidateSkills : ["Python", "LangChain", "FastAPI", "RAG pipelines", "Vector DBs"]).map((skill, index) => (
              <span key={`${skill}-${index}`} className="px-3 py-1.5 text-xs text-text-secondary bg-surface border border-border rounded-lg shadow-sm">
                {skill}
              </span>
            ))}
          </div>
        </div>

        <div className="px-8 py-4">
          <FocusCamera onStatusChange={(s, m) => { setProctorStatus(s); setProctorMessage(m); }} />
          {proctorStatus !== "OFFLINE" && (
            <div className={`mt-3 p-2 rounded text-[10px] uppercase font-mono tracking-wider text-center border ${
                proctorStatus === "FOCUSED" ? "text-cyan-400 border-cyan-400/50 bg-cyan-900/20 shadow-[0_0_10px_rgba(34,211,238,0.2)]" :
                proctorStatus === "DISTRACTED" || proctorStatus === "ABSENT" ? "text-red-500 border-red-500/50 bg-red-900/20 shadow-[0_0_10px_rgba(239,68,68,0.3)] animate-pulse" :
                "text-text-secondary border-border bg-surface"
            }`}>
              {proctorMessage}
            </div>
          )}
        </div>

        <div className="px-8 py-6 mt-auto">
          <h2 className="text-[10px] font-semibold text-text-tertiary uppercase tracking-wider mb-4">Interview Progress</h2>
          <div className="bg-surface border border-border rounded-xl p-5 flex items-center gap-5 shadow-sm">
            <span className="text-3xl font-bold text-primary">{questionCount}</span>
            <div className="flex flex-col">
              <span className="text-sm font-semibold text-text">Questions</span>
              <span className="text-xs text-text-tertiary">Asked</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex flex-col relative h-[100dvh] bg-bg transition-all duration-300 md:ml-[300px] flex-1">
        {/* Timer UI */}
        <div className="absolute top-6 right-6 md:right-12 lg:right-20 bg-surface-2 border border-border px-4 py-2 rounded-xl shadow-sm flex items-center gap-2 z-20">
          <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
          <span className="text-text-secondary font-mono text-sm tracking-widest">{formatTime(timeLeft)}</span>
        </div>

        <div className="flex-1 overflow-y-auto px-6 md:px-12 lg:px-20 py-8 scroll-smooth pb-32">
          <div className="max-w-5xl mx-auto flex flex-col space-y-10">
            {messages.map((m, i) => (
              <InterviewMessage key={i} role={m.role} content={m.content} isProbe={m.isProbe} />
            ))}
            
            {loading && (
              <div className="flex justify-start">
                <ThinkingIndicator />
              </div>
            )}
            
            {error && messages.length > 0 && (
              <div className="mt-8">
                <ErrorState onRetry={() => handleSend(input)} />
              </div>
            )}
            
            <div ref={messagesEndRef} className="h-32" />
          </div>
        </div>

        {/* Input Area - Fixed at bottom */}
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-bg via-bg/90 to-transparent pt-20 pb-8 px-6 md:px-12 lg:px-20">
          <div className="max-w-5xl mx-auto">
            <InterviewInput 
              key={`input-${interruptCount}`}
              onSend={handleSend} 
              disabled={loading} 
              onPauseTyping={handlePauseTyping}
            />
          </div>
        </div>
      </div>
    </div>
    </>
  );
}
