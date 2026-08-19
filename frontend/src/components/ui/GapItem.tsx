import { motion } from "framer-motion";

interface GapItemProps {
  index: number;
  gap: string;
  delay?: number;
}

export default function GapItem({ index, gap, delay = 0 }: GapItemProps) {
  // Try to parse out a title if there's a colon, otherwise just use the text
  const parts = gap.split(":");
  const title = parts.length > 1 ? parts[0] : gap;
  const description = parts.length > 1 ? parts.slice(1).join(":").trim() : "";

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.3 }}
      className="flex gap-4 border-l-2 border-warning pl-4 py-1 print:gap-2 print:pl-3 print:py-0"
    >
      <div className="text-text-tertiary font-mono text-sm mt-0.5 shrink-0 print:text-[10px]">
        {index.toString().padStart(2, "0")}
      </div>
      <div>
        <h4 className="text-text font-medium text-base mb-1 print:text-xs print:mb-0 print:text-black">{title}</h4>
        {description && (
          <p className="text-text-secondary text-sm leading-relaxed print:text-[10px] print:text-gray-600">{description}</p>
        )}
      </div>
    </motion.div>
  );
}
