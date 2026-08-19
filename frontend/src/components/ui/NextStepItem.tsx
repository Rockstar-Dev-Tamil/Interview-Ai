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
      className="bg-surface-2 border border-border rounded-lg p-4 flex items-start gap-3 hover:border-border-hover transition-colors print:p-2 print:border-none print:bg-transparent print:gap-2"
    >
      <div className="text-text-tertiary font-mono text-sm mt-0.5 shrink-0 print:text-[10px]">
        {index.toString().padStart(2, "0")}
      </div>
      <div className="shrink-0 mt-0.5">
        <ArrowRight size={16} className="text-text-secondary print:w-3 print:h-3" />
      </div>
      <p className="text-text text-sm leading-relaxed print:text-xs print:text-black">{step.replace(/^\d+[\.\)]\s*/, "")}</p>
    </motion.div>
  );
}
