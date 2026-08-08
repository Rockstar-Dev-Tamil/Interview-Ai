'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { startInterview, sendAnswer } from '@/lib/api';

interface Message {
  role: 'agent' | 'candidate';
  text: string;
}

export default function InterviewPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [questionCount, setQuestionCount] = useState(0);
  const [candidateName, setCandidateName] = useState('Candidate');
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    const init = async () => {
      try {
        const sessionId = localStorage.getItem('sessionId');
        const candidateId = localStorage.getItem('candidateId');
        const storedName = localStorage.getItem('candidateName');
        
        if (storedName) {
          setCandidateName(storedName);
        }
        if (!sessionId || !candidateId || !storedName) {
          router.push('/');
          return;
        }

        const res = await startInterview(sessionId, { id: candidateId, name: storedName });
        setMessages([{ role: 'agent', text: res.reply }]);
        setQuestionCount(1);
        
        if (res.done) {
          localStorage.setItem('feedback', JSON.stringify(res.feedback));
          router.push('/feedback');
        }
      } catch (err: any) {
        setError(err.message || 'Failed to start interview');
      } finally {
        setLoading(false);
      }
    };
    init();
  }, [router]);

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || loading) return;
    
    const sessionId = localStorage.getItem('sessionId');
    if (!sessionId) return;
    
    const userMessage = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'candidate', text: userMessage }]);
    setLoading(true);
    setError(null);
    
    try {
      const res = await sendAnswer(sessionId, userMessage);
      setMessages(prev => [...prev, { role: 'agent', text: res.reply }]);
      
      if (!res.reply.includes("Take your time")) {
         setQuestionCount(prev => prev + 1);
      }
      
      if (res.done) {
        localStorage.setItem('feedback', JSON.stringify(res.feedback));
        router.push('/feedback');
      }
    } catch (err: any) {
      setError(err.message || 'Error sending answer. Please try again.');
      setInput(userMessage);
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center py-8 px-4">
      <div className="w-full max-w-3xl bg-white shadow-xl rounded-xl overflow-hidden flex flex-col h-[85vh]">
        
        <div className="bg-slate-800 text-white p-4 flex justify-between items-center shrink-0">
          <div>
            <h2 className="font-bold text-lg">ABTALKS AI Interview Agent</h2>
            <p className="text-slate-300 text-sm">Candidate: {candidateName}</p>
          </div>
          <div className="text-slate-300 text-sm bg-slate-700 px-3 py-1 rounded-full">
            Question {questionCount} &middot; Adaptive Interview
          </div>
        </div>
        
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-3 flex justify-between items-center shrink-0">
            <div className="text-red-700 text-sm font-medium">{error}</div>
            <button onClick={() => setError(null)} className="text-red-600 hover:text-red-800 text-sm font-semibold">Dismiss</button>
          </div>
        )}
        
        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === 'candidate' ? 'justify-end' : 'justify-start'}`}>
              <div 
                className={`max-w-[80%] p-4 rounded-2xl ${
                  msg.role === 'candidate' 
                  ? 'bg-blue-600 text-white rounded-br-none shadow-md' 
                  : 'bg-white border border-gray-200 text-gray-800 rounded-bl-none shadow-sm'
                }`}
              >
                <div className="text-xs font-semibold mb-1 opacity-75">
                  {msg.role === 'candidate' ? 'You' : 'AI Interviewer'}
                </div>
                <div className="whitespace-pre-wrap">{msg.text}</div>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 p-4 rounded-2xl rounded-bl-none shadow-sm flex space-x-2 items-center h-12">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        
        <div className="p-4 bg-white border-t border-gray-200 shrink-0">
          <form onSubmit={handleSubmit} className="relative">
            <textarea
              className="w-full border border-gray-300 rounded-lg pl-4 pr-24 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none bg-gray-50 text-gray-900"
              rows={3}
              placeholder="Type your answer here... (Press Enter to submit, Shift+Enter for newline)"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit();
                }
              }}
            />
            <button 
              type="submit"
              disabled={loading || !input.trim()}
              className="absolute right-3 bottom-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-md transition duration-150"
            >
              Submit
            </button>
          </form>
        </div>
        
      </div>
    </div>
  );
}
