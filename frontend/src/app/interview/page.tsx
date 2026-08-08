"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { startInterview, sendAnswer } from "@/lib/api";
import InterviewMessage from "@/components/ui/InterviewMessage";
import InterviewInput from "@/components/ui/InterviewInput";
import ThinkingIndicator from "@/components/ui/ThinkingIndicator";
import ErrorState from "@/components/ui/ErrorState";
import LoadingState from "@/components/ui/LoadingState";

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
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize session
  useEffect(() => {
    const init = async () => {
      const sessionId = localStorage.getItem("sessionId");
      const candidateId = localStorage.getItem("candidateId");
      const candidateName = localStorage.getItem("candidateName");

      if (!sessionId || !candidateId || !candidateName) {
        router.push("/");
        return;
      }

      try {
        const res = await startInterview(sessionId, { id: candidateId, name: candidateName });
        setMessages([{ role: "ai", content: res.reply }]);
        setLoading(false);
      } catch (err) {
        console.error(err);
        setError("Failed to start the interview. Please try again.");
        setLoading(false);
      }
    };

    init();
  }, [router]);

  // Auto-scroll
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
      
      // Check if it's a probe (doesn't increment question count)
      // The old logic used "Take your time" check, we can refine this or just assume 
      // if it's a follow-up it might be a probe. For now we use the existing heuristic.
      const isProbe = res.reply.includes("Take your time") || res.reply.includes("explain your approach");
      if (!isProbe && !res.done) {
        setQuestionCount((c) => c + 1);
      }

      setMessages((prev) => [...prev, { role: "ai", content: res.reply, isProbe }]);

      if (res.done) {
        localStorage.setItem("feedback", JSON.stringify(res.feedback));
        router.push("/feedback");
      }
    } catch (err) {
      console.error(err);
      setError("Failed to send your answer. Please try again.");
      // Rollback optimistic message and restore input
      setMessages((prev) => prev.slice(0, -1));
      setInput(messageText);
    } finally {
      setLoading(false);
    }
  };

  if (error && messages.length === 0) {
    return <LoadingState icon="alert" title="Session Error" subtitle="Failed to start the session. Returning home..." />;
  }

  return (
    <div className="flex-1 flex flex-col bg-bg">
      {/* Header Area */}
      <div className="sticky top-0 z-40 bg-bg/90 backdrop-blur-sm border-b border-border py-4 px-6 md:px-12 lg:px-20">
        <div className="max-w-5xl mx-auto flex justify-between items-center">
          <span className="text-xs font-medium text-text-tertiary uppercase tracking-wider">
            Technical Interview
          </span>
          <span className="text-sm font-medium text-text-secondary">
            Question {questionCount.toString().padStart(2, "0")}
          </span>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 overflow-y-auto px-6 md:px-12 lg:px-20 py-8">
        <div className="max-w-5xl mx-auto flex flex-col space-y-12">
          {messages.map((m, i) => (
            <InterviewMessage key={i} role={m.role} content={m.content} isProbe={m.isProbe} />
          ))}
          
          {loading && <ThinkingIndicator />}
          
          {error && messages.length > 0 && (
            <div className="mt-8">
              <ErrorState onRetry={() => handleSend(input)} />
            </div>
          )}
          
          <div ref={messagesEndRef} className="h-4" />
        </div>
      </div>

      {/* Input Area */}
      <div className="shrink-0 bg-bg border-t border-border p-6 md:px-12 lg:px-20 pb-8 md:pb-12">
        <div className="max-w-5xl mx-auto">
          <InterviewInput onSend={handleSend} disabled={loading} initialValue={input} />
        </div>
      </div>
    </div>
  );
}
