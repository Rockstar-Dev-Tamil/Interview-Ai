import { useState, useRef, useEffect } from "react";
import { Send } from "lucide-react";

interface InterviewInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  initialValue?: string;
}

export default function InterviewInput({ onSend, disabled = false, initialValue = "" }: InterviewInputProps) {
  const [value, setValue] = useState(initialValue);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    setValue(initialValue);
  }, [initialValue]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(Math.max(textareaRef.current.scrollHeight, 80), 200)}px`;
    }
  }, [value]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (value.trim() && !disabled) {
        onSend(value.trim());
        setValue("");
      }
    }
  };

  const handleSend = () => {
    if (value.trim() && !disabled) {
      onSend(value.trim());
      setValue("");
    }
  };

  return (
    <div className={`flex flex-col space-y-2 ${disabled ? "opacity-50" : ""}`}>
      <div className="relative flex flex-col bg-surface border border-border rounded-xl focus-within:ring-2 focus-within:ring-primary/50 transition-shadow">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder="Explain your approach..."
          className="w-full bg-transparent p-4 min-h-[80px] max-h-[200px] resize-none outline-none text-text text-base disabled:cursor-not-allowed placeholder:text-text-tertiary"
          rows={3}
        />
        <div className="absolute top-2 right-4">
          <span className="text-xs text-text-tertiary">{value.length} chars</span>
        </div>
        <div className="flex justify-between items-center px-4 pb-3 pt-1 border-t border-border/50">
          <span className="text-xs text-text-tertiary hidden sm:block">
            Shift + Enter for newline
          </span>
          <button
            onClick={handleSend}
            disabled={disabled || !value.trim()}
            className="flex items-center gap-2 bg-primary hover:bg-primary-hover text-white font-medium py-2 px-4 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
          >
            <span>Send</span>
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
