import { useState, useEffect } from "react";
import { motion, Variants } from "framer-motion";
import { Sparkles } from "lucide-react";

export default function ThinkingIndicator() {
  const [phase, setPhase] = useState("Analyzing your answer...");

  useEffect(() => {
    const timer = setTimeout(() => {
      setPhase("Preparing your next question...");
    }, 2000);
    return () => clearTimeout(timer);
  }, []);

  const dotVariants: Variants = {
    animate: {
      scale: [0.5, 1, 0.5],
      opacity: [0.3, 1, 0.3],
      transition: {
        duration: 1,
        repeat: Infinity,
        ease: "easeInOut"
      }
    }
  };

  return (
    <div className="flex flex-col space-y-4" aria-busy="true">
      <div className="flex flex-col items-start gap-1">
        <div className="flex items-center gap-2">
          <Sparkles size={12} className="text-text-tertiary" />
          <span className="text-xs font-medium text-text-tertiary uppercase tracking-wider">
            AI INTERVIEWER
          </span>
        </div>
        <div className="w-8 h-px bg-border mt-1" />
      </div>

      <div className="max-w-2xl p-6 rounded-xl bg-surface border border-border flex flex-col gap-3">
        <div className="flex items-center gap-2">
          <motion.div variants={dotVariants} animate="animate" className="w-2 h-2 rounded-full bg-primary" />
          <motion.div variants={dotVariants} animate="animate" transition={{ delay: 0.2 }} className="w-2 h-2 rounded-full bg-primary" />
          <motion.div variants={dotVariants} animate="animate" transition={{ delay: 0.4 }} className="w-2 h-2 rounded-full bg-primary" />
        </div>
        <span className="text-sm text-text-tertiary" aria-live="polite">
          {phase}
        </span>
      </div>
    </div>
  );
}
