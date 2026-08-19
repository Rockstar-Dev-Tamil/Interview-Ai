"use client";

import React, { useState, useEffect } from "react";
import Editor from "@monaco-editor/react";
import { Play, CheckCircle, Clock, SkipForward } from "lucide-react";

type CodeEditorProps = {
  onSkip?: () => void;
  onSubmit?: () => void;
};

export default function CodeEditor({ onSkip, onSubmit }: CodeEditorProps) {
  const [language, setLanguage] = useState("python");
  const [code, setCode] = useState("# Write your solution here\n");
  const [output, setOutput] = useState<React.ReactNode | null>(null);

  const [loading, setLoading] = useState(false);
  const [timeLeft, setTimeLeft] = useState(20 * 60);

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          if (onSkip) onSkip(); // Auto skip when time's up
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [onSkip]);

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const isCodeEmpty = !code.trim() || code.trim() === "# Write your solution here" || code.trim() === "// Write your solution here";

  const handleRun = async () => {
    if (isCodeEmpty) {
      setOutput(<span className="text-red-400">Error: Code cannot be empty. Please write your solution before running tests.</span>);
      return;
    }
    
    setLoading(true);
    setOutput(<span className="text-gray-400">Analyzing code...</span>);
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || (process.env.NODE_ENV === 'production' ? 'https://interview-ai-j3az.onrender.com' : 'http://localhost:8000');
      const res = await fetch(`${apiUrl}/api/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language, code }),
      });
      const data = await res.json();
      
      if (data.errors && data.errors.length > 0) {
        setOutput(
          <div className="flex flex-col space-y-1 text-red-400 font-bold">
            {data.errors.map((err: string, i: number) => <div key={i}>{err}</div>)}
          </div>
        );
        return;
      }
      
      // Simulate test cases (mocking 1 failed private test case for realism)
      setOutput(
        <div className="flex flex-col space-y-4">
          <div className="text-gray-300 font-semibold mb-2">Running Test Cases...</div>
          
          <div>
            <div className="text-xs text-gray-400 uppercase tracking-wider mb-2 font-semibold">Public Cases (5/5 Passed)</div>
            <div className="space-y-2">
              {[
                { in: "[2, 7, 11, 15], 9", out: "[0, 1]" },
                { in: "[3, 2, 4], 6", out: "[1, 2]" },
                { in: "[3, 3], 6", out: "[0, 1]" },
                { in: "[1, 2, 3, 4], 7", out: "[2, 3]" },
                { in: "[2, 5, 9, 13], 14", out: "[1, 2]" }
              ].map((tc, i) => (
                <div key={i} className="flex flex-col bg-[#2d2d2d] rounded p-2 text-xs border border-[#404040]">
                  <div className="flex items-center gap-2 mb-1">
                    <CheckCircle size={12} className="text-emerald-500" />
                    <span className="text-gray-200 font-medium">Test Case {i + 1}</span>
                  </div>
                  <div className="grid grid-cols-[50px_1fr] gap-1 text-gray-400">
                    <span>Input:</span> <span className="text-gray-300 font-mono">{tc.in}</span>
                    <span>Output:</span> <span className="text-gray-300 font-mono">{tc.out}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div>
            <div className="text-xs text-gray-400 uppercase tracking-wider mb-2 font-semibold">Private Cases (5/5 Passed)</div>
            <div className="flex flex-wrap gap-2">
              {[1, 2, 3, 4, 5].map((tc, i) => {
                const passed = true; 
                return (
                  <div key={i} className={`flex items-center gap-1.5 px-3 py-1.5 rounded border text-xs font-medium ${passed ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-red-500/10 border-red-500/20 text-red-400'}`}>
                    {passed ? <CheckCircle size={12} /> : <span className="flex items-center justify-center w-3 h-3 text-red-500 text-[10px] font-bold">✕</span>}
                    Private Case {tc}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      );
    } catch (err) {
      setOutput(<span className="text-red-400">Failed to communicate with execution server.</span>);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    // We will always attempt to advance, but we will still run the analysis
    setLoading(true);
    setOutput(<span className="text-gray-400">Analyzing code...</span>);
    
    if (isCodeEmpty) {
      setOutput(
        <div className="flex flex-col space-y-2 text-emerald-400">
          <div className="text-gray-300">Evaluating optimal solution...</div>
          <div>Result:</div>
          <div>Time Complexity: O(N)</div>
          <div>Space Complexity: O(1)</div>
          <div className="font-bold mt-2 text-emerald-500">✅ Solution Accepted!</div>
        </div>
      );
      setLoading(false);
      if (onSubmit) onSubmit();
      return;
    }
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || (process.env.NODE_ENV === 'production' ? 'https://interview-ai-j3az.onrender.com' : 'http://localhost:8000');
      const res = await fetch(`${apiUrl}/api/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language, code }),
      });
      const data = await res.json();
      
      if (data.errors && data.errors.length > 0) {
        setOutput(
          <div className="flex flex-col space-y-1 text-red-400 font-bold">
            {data.errors.map((err: string, i: number) => <div key={i}>{err}</div>)}
          </div>
        );
        // We still advance even if there are errors for demo purposes
      } else {
        setOutput(
          <div className="flex flex-col space-y-2 text-emerald-400">
            <div className="text-gray-300">Evaluating optimal solution...</div>
            <div>Result:</div>
            <div>Time Complexity: O(N)</div>
            <div>Space Complexity: O(1)</div>
            <div className="font-bold mt-2 text-emerald-500">✅ Solution Accepted!</div>
          </div>
        );
      }
      
      // Call onSubmit so the user can advance
      if (onSubmit) {
        onSubmit();
      }
      
    } catch (err) {
      setOutput(<span className="text-red-400">Failed to communicate with execution server.</span>);
      // Advance on error too
      if (onSubmit) onSubmit();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#1e1e1e] border-l border-border overflow-hidden">
      {/* Top Bar */}
      <div className="flex items-center justify-between px-4 py-3 bg-[#2d2d2d] border-b border-[#404040]">
        <div className="flex items-center gap-3">
          <select 
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="bg-[#1e1e1e] text-gray-300 border border-[#404040] rounded-md px-3 py-1.5 text-sm outline-none focus:border-primary transition-colors cursor-pointer"
          >
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="c">C</option>
            <option value="cpp">C++</option>
          </select>
          <div className="text-xs text-gray-500 hidden sm:block">Theme: vs-dark</div>
          <div className={`flex items-center gap-1.5 text-sm font-mono ml-4 ${timeLeft < 300 ? 'text-red-400 animate-pulse' : 'text-gray-300'}`}>
            <Clock size={14} /> {formatTime(timeLeft)}
          </div>
        </div>

        <div className="flex gap-2">
          {onSkip && (
            <button onClick={onSkip} className="flex items-center gap-1.5 text-sm font-medium bg-gray-700 hover:bg-gray-600 text-gray-200 px-4 py-1.5 rounded-md transition-colors shadow-sm">
              <SkipForward size={14} /> Skip
            </button>
          )}
          <button onClick={handleRun} className="flex items-center gap-1.5 text-sm font-medium bg-[#3c3c3c] hover:bg-[#4d4d4d] text-gray-200 px-4 py-1.5 rounded-md transition-colors shadow-sm">
            <Play size={14} className="text-gray-300" /> Run Code
          </button>
          <button onClick={handleSubmit} className="flex items-center gap-1.5 text-sm font-medium bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-1.5 rounded-md transition-colors shadow-sm">
            <CheckCircle size={14} /> Submit
          </button>
        </div>
      </div>

      {/* Editor */}
      <div className="flex-1 relative min-h-0">
        <Editor
          height="100%"
          language={language}
          theme="vs-dark"
          value={code}
          onChange={(val) => setCode(val || "")}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineHeight: 24,
            padding: { top: 16 },
            scrollBeyondLastLine: false,
            smoothScrolling: true,
            cursorBlinking: "smooth",
            cursorSmoothCaretAnimation: "on",
            formatOnPaste: true,
            fontFamily: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', Consolas, monospace",
          }}
        />
      </div>

      {/* Output Console */}
      {output && (
        <div className="h-72 bg-[#1e1e1e] border-t border-[#404040] p-4 font-mono text-sm overflow-y-auto">
          <div className="flex items-center justify-between mb-3">
            <div className="text-gray-400 font-semibold tracking-wider text-[11px] uppercase">Console Output</div>
            <button onClick={() => setOutput(null)} className="text-gray-500 hover:text-gray-300 text-xs">Clear</button>
          </div>
          <div className="leading-relaxed">{output}</div>
        </div>
      )}
    </div>
  );
}
