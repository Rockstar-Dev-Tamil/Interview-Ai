import { Check } from "lucide-react";
import { motion } from "framer-motion";

interface StrengthCardProps {
  strength: string;
  delay?: number;
}

export default function StrengthCard({ strength, delay = 0 }: StrengthCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.3 }}
      className="bg-surface border border-border rounded-xl p-4 flex items-start gap-3 hover:border-success/50 transition-colors print:p-2 print:gap-2 print:border-gray-200"
    >
      <div className="shrink-0 mt-0.5">
        <Check size={18} className="text-success print:w-3 print:h-3" />
      </div>
      <div>
        <h4 className="font-semibold text-text text-base leading-tight mb-1 print:text-xs print:text-black">{strength}</h4>
        <p className="text-xs text-text-tertiary uppercase tracking-wider print:text-[8px] print:text-gray-500">Strong</p>
      </div>
    </motion.div>
  );
}
