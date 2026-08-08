import { ArrowRight } from "lucide-react";
import { motion } from "framer-motion";

interface NextStepItemProps {
  index: number;
  step: string;
  delay?: number;
}

export default function NextStepItem({ index, step, delay = 0 }: NextStepItemProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.3 }}
      className="bg-surface-2 border border-border rounded-lg p-4 flex items-start gap-3 hover:border-border-hover transition-colors"
    >
      <div className="text-text-tertiary font-mono text-sm mt-0.5 shrink-0">
        {index.toString().padStart(2, "0")}
      </div>
      <div className="shrink-0 mt-0.5">
        <ArrowRight size={16} className="text-text-secondary" />
      </div>
      <p className="text-text text-sm leading-relaxed">{step.replace(/^\d+[\.\)]\s*/, "")}</p>
    </motion.div>
  );
}
