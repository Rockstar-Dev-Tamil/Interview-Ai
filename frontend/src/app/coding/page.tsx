"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { sendAnswer } from "@/lib/api";
import InterviewMessage from "@/components/ui/InterviewMessage";
import InterviewInput from "@/components/ui/InterviewInput";
import ThinkingIndicator from "@/components/ui/ThinkingIndicator";
import ErrorState from "@/components/ui/ErrorState";
import LoadingState from "@/components/ui/LoadingState";
import CodeEditor from "@/components/ui/CodeEditor";
import dynamic from "next/dynamic";
import type { FocusStatus } from "@/components/ui/FocusCamera";

const FocusCamera = dynamic(() => import("@/components/ui/FocusCamera"), { ssr: false });

type Message = {
  role: "ai" | "user";
  content: string;
  isProbe?: boolean;
};

const CHALLENGES = [
  {
    title: "Coding Challenge 1/2",
    description: "You are given an array of integers and a target sum. Write a function to find two numbers in the array that add up to the target."
  },
  {
    title: "Coding Challenge 2/2",
    description: "Write a function to check if a given string is a valid palindrome, considering only alphanumeric characters and ignoring cases."
  }
];

export default function CodingPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [proctorStatus, setProctorStatus] = useState<FocusStatus>("OFFLINE");
  const [proctorMessage, setProctorMessage] = useState("Proctoring Offline");
  const [challengeIndex, setChallengeIndex] = useState(0);

  const handleStatusChange = (s: FocusStatus, m: string) => {
    setProctorStatus(s);
    setProctorMessage(m);
  };

  const speakText = (text: string) => {
    if (typeof window !== "undefined" && window.speechSynthesis) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.05;
      window.speechSynthesis.speak(utterance);
    }
  };

  useEffect(() => {
    // Generate a dummy session if none exists so we can directly test the page
    let sessionId = localStorage.getItem("sessionId");
    if (!sessionId) {
      sessionId = "test-session-" + Math.random().toString(36).substr(2, 9);
      localStorage.setItem("sessionId", sessionId);
    }
    
    // We add an initial message simulating the AI giving a coding problem
    setMessages([
      { role: "ai", content: "Great! Let's move on to the coding challenge. Take a look at the problem statement. When you're ready, write your solution in the editor on the right and explain your thought process to me." }
    ]);
  }, [router]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async (messageText: string) => {
    if (!messageText.trim() || loading) return;

    const sessionId = localStorage.getItem("sessionId");
    if (!sessionId) return;

    setMessages((prev) => [...prev, { role: "user", content: messageText }]);
    setLoading(true);
    setError(null);
    setInput("");

    try {
      const res = await sendAnswer(sessionId, messageText);
      
      const isProbe = res.reply.includes("Take your time") || res.reply.includes("explain your approach");
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
  
  const handleNextChallenge = () => {
    console.log("handleNextChallenge called with index:", challengeIndex);
    if (challengeIndex < CHALLENGES.length - 1) {
      setChallengeIndex(prev => prev + 1);
      setMessages((prev) => [...prev, { role: "ai", content: "Excellent! Let's move on to the next challenge." }]);
      speakText("Excellent! Let's move on to the next challenge.");
    } else {
      console.log("Last challenge completed, redirecting to feedback...");
      // Always ensure a valid feedback object exists when bypassing the AI
      const mockFeedback = {
        summary: "The candidate answered 13 questions across 8 days of the curriculum. Overall performance was solid. In addition, the coding challenges were completed successfully with strong algorithmic implementations.",
        strengths: [
          "The candidate participated fully in the interview.",
          "Demonstrated clean code structure in the coding assessment."
        ],
        gaps: [
          "Needs review on pip in Package Management",
          "Needs review on imputation in Missing Values",
          "Needs review on context window in Word Embeddings",
          "Needs review on buffer in Conversation Memory",
          "Needs review on function schema in Tool Binding",
          "Needs review on latency in LLM Observability",
          "Needs review on reward model in RLHF",
          "Needs review on containerisation in End-to-End Pipeline",
          "Needs review on handling edge cases in Coding Algorithms",
          "Needs review on space complexity optimization in Coding Challenges"
        ],
        next: "Review package management and deployment concepts.\nPractice more advanced data structures.\nTry optimizing space complexity in future coding solutions."
      };
      localStorage.setItem("feedback", JSON.stringify(mockFeedback));
      router.push("/feedback");
    }
  };

  if (error && messages.length === 0) {
    return <LoadingState icon="alert" title="Session Error" subtitle="Failed to start the session. Returning home..." />;
  }

  return (
    <div className="flex-1 flex min-h-[100dvh] bg-bg overflow-hidden">
      {/* Left Chat Area (Problem Discussion) */}
      <div className="flex flex-col relative h-[100dvh] w-1/2 border-r border-border bg-bg">
        <div className="flex-1 overflow-y-auto px-6 md:px-10 py-8 scroll-smooth pb-32">
          <div className="max-w-2xl mx-auto flex flex-col space-y-8">
            <div className="flex gap-4 mb-4">
              <div className="flex-1 bg-surface-2 p-6 rounded-xl border border-border shadow-sm">
                <h2 className="text-sm font-bold text-text mb-2 uppercase tracking-wide">{CHALLENGES[challengeIndex].title}</h2>
                <p className="text-sm text-text-secondary">
                  {CHALLENGES[challengeIndex].description}
                </p>
              </div>
              <div className="w-32 flex-shrink-0 flex flex-col">
                <FocusCamera onStatusChange={handleStatusChange} />
                {proctorStatus !== "OFFLINE" && (
                  <div className={`mt-2 p-1.5 rounded text-[9px] uppercase font-mono tracking-wider text-center border ${
                      proctorStatus === "FOCUSED" ? "text-cyan-400 border-cyan-400/50 bg-cyan-900/20 shadow-[0_0_10px_rgba(34,211,238,0.2)]" :
                      proctorStatus === "DISTRACTED" || proctorStatus === "ABSENT" ? "text-red-500 border-red-500/50 bg-red-900/20 shadow-[0_0_10px_rgba(239,68,68,0.3)] animate-pulse" :
                      "text-text-secondary border-border bg-surface"
                  }`}>
                    {proctorMessage}
                  </div>
                )}
              </div>
            </div>
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
            
            <div ref={messagesEndRef} className="h-16" />
          </div>
        </div>

        {/* Input Area */}
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-bg via-bg/90 to-transparent pt-16 pb-6 px-6 md:px-10">
          <div className="max-w-2xl mx-auto">
            <InterviewInput onSend={handleSend} disabled={loading} initialValue={input} />
          </div>
        </div>
      </div>

      {/* Right Code Editor Pane */}
      <div className="w-1/2 h-[100dvh] flex flex-col z-20">
        <CodeEditor 
          key={challengeIndex} // Force remount to reset code when challenge changes
          onSkip={handleNextChallenge}
          onSubmit={handleNextChallenge}
        />
      </div>
    </div>
  );
}
