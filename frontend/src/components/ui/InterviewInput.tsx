import { useState, useRef, useEffect } from "react";
import { Send, Mic, MicOff } from "lucide-react";

declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

interface InterviewInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  initialValue?: string;
  onPauseTyping?: (text: string) => void;
}

export default function InterviewInput({ onSend, disabled = false, initialValue = "", onPauseTyping }: InterviewInputProps) {
  const [value, setValue] = useState(initialValue);
  const [isRecording, setIsRecording] = useState(false);
  const [speechError, setSpeechError] = useState<string | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const recognitionRef = useRef<any>(null);
  const startTextRef = useRef("");
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // Initialize speech recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';
      recognitionRef.current.maxAlternatives = 1;

      recognitionRef.current.onresult = (event: any) => {
        const transcript = Array.from(event.results)
          .map((result: any) => result[0].transcript)
          .join("");
        setValue(startTextRef.current + (startTextRef.current && transcript ? " " : "") + transcript);
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error("Speech recognition error", event.error);
        if (event.error === 'network') {
          setSpeechError("Speech recognition failed due to network or browser restrictions. Please type your answer.");
        } else {
          setSpeechError(`Speech recognition error: ${event.error}`);
        }
        setIsRecording(false);
      };

      recognitionRef.current.onend = () => {
        // We keep it continuous, but if it ends naturally, update state
        setIsRecording(false);
      };
    }
  }, []);

  const toggleRecording = () => {
    setSpeechError(null);
    if (isRecording) {
      recognitionRef.current?.stop();
      setIsRecording(false);
    } else {
      startTextRef.current = value;
      try {
        recognitionRef.current?.start();
        setIsRecording(true);
      } catch (e) {
        console.error(e);
      }
    }
  };

  useEffect(() => {
    setValue(initialValue);
  }, [initialValue]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(Math.max(textareaRef.current.scrollHeight, 60), 200)}px`;
    }
    
    // Debounce typing for interruption check
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }
    
    if (value.length > 50 && !disabled && onPauseTyping) {
      debounceTimerRef.current = setTimeout(() => {
        onPauseTyping(value);
      }, 2000);
    }
    
    return () => {
      if (debounceTimerRef.current) clearTimeout(debounceTimerRef.current);
    };
  }, [value, disabled, onPauseTyping]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (value.trim() && !disabled) {
        if (isRecording) {
          recognitionRef.current?.stop();
          setIsRecording(false);
        }
        onSend(value.trim());
        setValue("");
      }
    }
  };

  const handleSend = () => {
    if (value.trim() && !disabled) {
      if (isRecording) {
        recognitionRef.current?.stop();
        setIsRecording(false);
      }
      onSend(value.trim());
      setValue("");
    }
  };

  return (
    <div className="w-full flex flex-col gap-2">
      <div className={`flex flex-col relative bg-surface border ${speechError ? "border-red-500/50" : "border-border"} rounded-2xl transition-shadow shadow-sm overflow-hidden ${disabled ? "opacity-50" : ""}`}>
        <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        placeholder="Type or speak your answer here..."
        className="w-full bg-transparent p-5 pr-28 min-h-[60px] max-h-[200px] resize-none outline-none text-text text-[15px] disabled:cursor-not-allowed placeholder:text-text-tertiary"
        rows={1}
      />
      <div className="absolute right-3 bottom-3 flex items-center gap-2">
        <button
          onClick={toggleRecording}
          disabled={disabled || !recognitionRef.current}
          className={`flex items-center justify-center p-2.5 rounded-xl transition-colors ${
            isRecording 
              ? "bg-red-500/20 text-red-500 hover:bg-red-500/30 animate-pulse" 
              : "bg-surface-2 hover:bg-border text-text-secondary hover:text-text disabled:opacity-50 disabled:cursor-not-allowed"
          }`}
          title={isRecording ? "Stop recording" : "Start recording"}
        >
          {isRecording ? <MicOff size={18} /> : <Mic size={18} />}
        </button>
        <button
          onClick={handleSend}
          disabled={disabled || !value.trim()}
          className="flex items-center justify-center bg-surface-2 hover:bg-border text-text-secondary hover:text-text p-2.5 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <Send size={18} />
        </button>
      </div>
    </div>
    {speechError && (
      <span className="text-red-500 text-xs px-2">{speechError}</span>
    )}
    </div>
  );
}
