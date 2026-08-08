import { Sparkles } from "lucide-react";
import { motion } from "framer-motion";

interface InterviewMessageProps {
  role: "ai" | "user";
  content: string;
  isProbe?: boolean;
}

export default function InterviewMessage({ role, content, isProbe = false }: InterviewMessageProps) {
  const isAI = role === "ai";

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className="flex flex-col space-y-4"
    >
      {/* Label & Indicator Area */}
      <div className="flex flex-col items-start gap-1">
        {isProbe && isAI && (
          <div className="text-xs text-primary font-medium flex items-center gap-1">
            ✦ Adaptive follow-up
          </div>
        )}
        <div className="flex items-center gap-2">
          {isAI && <Sparkles size={12} className="text-text-tertiary" />}
          <span className="text-xs font-medium text-text-tertiary uppercase tracking-wider">
            {isAI ? "AI INTERVIEWER" : "YOUR ANSWER"}
          </span>
        </div>
        <div className="w-8 h-px bg-border mt-1" />
      </div>

      {/* Message Content */}
      <div 
        className={`max-w-2xl p-6 rounded-xl border ${
          isAI ? "bg-surface border-border" : "bg-surface-2 border-border"
        }`}
      >
        <p className="text-text text-base leading-relaxed whitespace-pre-wrap">
          {content}
        </p>
      </div>
    </motion.div>
  );
}
