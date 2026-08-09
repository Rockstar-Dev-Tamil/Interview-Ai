import { Sparkles } from "lucide-react";
import { motion } from "framer-motion";
import { memo } from "react";

interface InterviewMessageProps {
  role: "ai" | "user";
  content: string;
  isProbe?: boolean;
  deliberation?: any[];
  answerDiff?: string;
}

export default memo(function InterviewMessage({ role, content, isProbe = false, deliberation, answerDiff }: InterviewMessageProps) {
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
          
          {deliberation && deliberation.length > 0 && (
            <div className="w-full bg-surface-2 border border-border rounded-xl p-4 mt-2 shadow-inner">
              <div className="text-[10px] text-text-tertiary font-bold uppercase tracking-wider mb-3">Live Deliberation Room</div>
              <div className="space-y-3">
                {deliberation.map((log, idx) => (
                  <div key={idx} className="flex gap-2 text-sm">
                    <span className="font-semibold text-primary min-w-[120px]">{log.persona}:</span>
                    <span className="text-text-secondary">{log.message}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {answerDiff && (
            <div className="w-full bg-surface-2 border border-border rounded-xl p-4 mt-2 shadow-inner">
              <div className="text-[10px] text-text-tertiary font-bold uppercase tracking-wider mb-2">Answer Optimization (Signal Density)</div>
              <div 
                className="text-[13px] text-text-secondary leading-relaxed prose prose-sm prose-del:text-red-500 prose-del:bg-red-500/10 prose-ins:text-green-500 prose-ins:bg-green-500/10 prose-ins:no-underline"
                dangerouslySetInnerHTML={{ __html: answerDiff }}
              />
            </div>
          )}

          <div className="p-6 rounded-2xl rounded-tl-sm bg-surface border border-border shadow-sm mt-2">
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
});
