'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Feedback } from '@/lib/api';

export default function FeedbackPage() {
  const router = useRouter();
  const [feedback, setFeedback] = useState<Feedback | null>(null);

  useEffect(() => {
    const data = localStorage.getItem('feedback');
    if (!data) {
      router.push('/');
      return;
    }
    
    try {
      setFeedback(JSON.parse(data));
    } catch (e) {
      router.push('/');
    }
  }, [router]);

  if (!feedback) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-gray-500">Loading feedback...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto space-y-8">
        
        <div className="text-center">
          <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">Interview Complete</h1>
          <p className="mt-2 text-lg text-gray-500">Thank you for completing the technical interview.</p>
        </div>

        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6 bg-blue-600">
            <h3 className="text-lg leading-6 font-medium text-white flex items-center">
              <svg className="w-6 h-6 text-white mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
              Overview
            </h3>
          </div>
          <div className="border-t border-gray-200 px-4 py-5 sm:p-6 bg-blue-50">
            <p className="text-gray-800 text-lg">{feedback.summary}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
          <div className="bg-white shadow overflow-hidden sm:rounded-lg border-t-4 border-green-500">
            <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
              <h3 className="text-lg leading-6 font-medium text-gray-900 flex items-center">
                <svg className="w-6 h-6 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                Strengths
              </h3>
            </div>
            <ul className="divide-y divide-gray-200">
              {feedback.strengths.map((item, idx) => (
                <li key={idx} className="px-4 py-4 sm:px-6 flex items-start text-sm text-gray-700">
                  <span className="text-green-500 mr-2 text-lg leading-none">&bull;</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="bg-white shadow overflow-hidden sm:rounded-lg border-t-4 border-yellow-500">
            <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
              <h3 className="text-lg leading-6 font-medium text-gray-900 flex items-center">
                <svg className="w-6 h-6 text-yellow-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                Areas to Improve
              </h3>
            </div>
            <ul className="divide-y divide-gray-200">
              {feedback.gaps.map((item, idx) => (
                <li key={idx} className="px-4 py-4 sm:px-6 flex items-start text-sm text-gray-700">
                  <span className="text-yellow-500 mr-2 text-lg leading-none">&bull;</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="bg-white shadow overflow-hidden sm:rounded-lg border-t-4 border-purple-500">
          <div className="px-4 py-5 sm:px-6 bg-gray-50 border-b border-gray-200">
            <h3 className="text-lg leading-6 font-medium text-gray-900 flex items-center">
              <svg className="w-6 h-6 text-purple-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path></svg>
              Recommended Next Steps
            </h3>
          </div>
          <div className="border-t border-gray-200 px-4 py-5 sm:p-6 text-gray-800 whitespace-pre-wrap">
            {feedback.next}
          </div>
        </div>

        <div className="text-center pt-8">
          <button
            onClick={() => {
              localStorage.removeItem('sessionId');
              localStorage.removeItem('feedback');
              router.push('/');
            }}
            className="inline-flex justify-center py-2 px-6 border border-transparent shadow-sm text-base font-medium rounded-md text-white bg-gray-800 hover:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-900"
          >
            Start New Interview
          </button>
        </div>

      </div>
    </div>
  );
}
