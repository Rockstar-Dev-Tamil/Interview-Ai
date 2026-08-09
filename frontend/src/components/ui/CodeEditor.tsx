"use client";

import { useState } from "react";
import Editor from "@monaco-editor/react";
import { Play, CheckCircle } from "lucide-react";

export default function CodeEditor() {
  const [language, setLanguage] = useState("python");
  const [code, setCode] = useState("# Write your solution here\n");
  const [output, setOutput] = useState("");

  const handleRun = () => {
    setOutput("Running tests...\n\nOutput:\nTest Case 1: Passed\nTest Case 2: Passed\n\nSuccess: All tests passed!");
  };

  const handleSubmit = () => {
    setOutput("Evaluating optimal solution...\n\nResult:\nTime Complexity: O(N)\nSpace Complexity: O(1)\n\nSolution Accepted!");
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
            <option value="typescript">TypeScript</option>
            <option value="javascript">JavaScript</option>
            <option value="c">C</option>
            <option value="cpp">C++</option>
          </select>
          <div className="text-xs text-gray-500 hidden sm:block">Theme: vs-dark</div>
        </div>

        <div className="flex gap-2">
          <button onClick={handleRun} className="flex items-center gap-1.5 text-sm font-medium bg-[#3c3c3c] hover:bg-[#4d4d4d] text-gray-200 px-4 py-1.5 rounded-md transition-colors shadow-sm">
            <Play size={14} className="text-gray-300" /> Run Code
          </button>
          <button onClick={handleSubmit} className="flex items-center gap-1.5 text-sm font-medium bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-1.5 rounded-md transition-colors shadow-sm">
            <CheckCircle size={14} /> Submit
          </button>
        </div>
      </div>

      {/* Editor */}
      <div className="flex-1 relative">
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
        <div className="h-64 bg-[#1e1e1e] border-t border-[#404040] p-4 font-mono text-sm overflow-y-auto">
          <div className="flex items-center justify-between mb-3">
            <div className="text-gray-400 font-semibold tracking-wider text-[11px] uppercase">Console Output</div>
            <button onClick={() => setOutput("")} className="text-gray-500 hover:text-gray-300 text-xs">Clear</button>
          </div>
          <pre className="text-emerald-400 leading-relaxed whitespace-pre-wrap">{output}</pre>
        </div>
      )}
    </div>
  );
}
