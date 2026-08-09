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
      className={`flex flex-col w-full ${isAI ? "items-start" : "items-end"}`}
    >
      {/* AI Message */}
      {isAI ? (
        <div className="flex flex-col space-y-3 max-w-[90%] md:max-w-[85%]">
          <div className="flex flex-col items-start gap-1">
            {isProbe && (
              <div className="text-[10px] text-primary font-semibold uppercase tracking-widest flex items-center gap-1 mb-1">
                ✦ Adaptive follow-up
              </div>
            )}
            <div className="flex items-center gap-2 mb-1">
              <Sparkles size={12} className="text-text-tertiary" />
              <span className="text-[10px] font-bold text-text-tertiary uppercase tracking-wider">
                AI INTERVIEWER
              </span>
            </div>
          </div>
          
          <div className="p-6 rounded-2xl rounded-tl-sm bg-surface border border-border shadow-sm">
            <p className="text-text text-[15px] leading-relaxed whitespace-pre-wrap">
              {content}
            </p>
          </div>
        </div>
      ) : (
        /* User Message */
        <div className="flex flex-col items-end max-w-[90%] md:max-w-[85%] mt-4">
          <div className="p-5 px-6 rounded-[28px] rounded-tr-sm bg-primary shadow-sm min-w-[100px] flex flex-col items-center justify-center gap-3">
            <span className="text-white font-bold text-[11px] uppercase tracking-wider">
              YOU
            </span>
            <p className="text-white font-medium text-[15px] leading-relaxed whitespace-pre-wrap text-center">
              {content}
            </p>
          </div>
        </div>
      )}
    </motion.div>
  );
}
