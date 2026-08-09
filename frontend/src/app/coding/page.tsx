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

type Message = {
  role: "ai" | "user";
  content: string;
  isProbe?: boolean;
};

export default function CodingPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const speakText = (text: string) => {
    if (typeof window !== "undefined" && window.speechSynthesis) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.05;
      window.speechSynthesis.speak(utterance);
    }
  };

  useEffect(() => {
    // Only start if they came from the interview with an active session
    const sessionId = localStorage.getItem("sessionId");
    if (!sessionId) {
      router.push("/");
      return;
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

  if (error && messages.length === 0) {
    return <LoadingState icon="alert" title="Session Error" subtitle="Failed to start the session. Returning home..." />;
  }

  return (
    <div className="flex-1 flex min-h-[100dvh] bg-bg overflow-hidden">
      {/* Left Chat Area (Problem Discussion) */}
      <div className="flex flex-col relative h-[100dvh] w-1/2 border-r border-border bg-bg">
        <div className="flex-1 overflow-y-auto px-6 md:px-10 py-8 scroll-smooth pb-32">
          <div className="max-w-2xl mx-auto flex flex-col space-y-8">
            <div className="mb-4 bg-surface-2 p-6 rounded-xl border border-border shadow-sm">
              <h2 className="text-sm font-bold text-text mb-2 uppercase tracking-wide">Coding Challenge</h2>
              <p className="text-sm text-text-secondary">
                You are given an array of integers and a target sum. Write a function to find two numbers in the array that add up to the target.
              </p>
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
        <CodeEditor />
      </div>
    </div>
  );
}
