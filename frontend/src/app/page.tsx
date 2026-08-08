'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface CandidateProfile {
  id: string;
  name: string;
  jobRole: string;
  yearsExperience: number;
}

export default function Home() {
  const router = useRouter();
  const [candidates, setCandidates] = useState<CandidateProfile[]>([]);
  const [selectedCandidateId, setSelectedCandidateId] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchCandidates() {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/candidates`);
        if (res.ok) {
          const data = await res.json();
          setCandidates(data);
          if (data.length > 0) {
            setSelectedCandidateId(data[0].id);
          }
        }
      } catch (err) {
        console.error("Failed to fetch candidates", err);
      } finally {
        setLoading(false);
      }
    }
    fetchCandidates();
  }, []);

  const startInterview = () => {
    if (!selectedCandidateId) return;
    
    const selectedCandidate = candidates.find(c => c.id === selectedCandidateId);
    if (!selectedCandidate) return;

    const sessionId = crypto.randomUUID();
    localStorage.setItem('sessionId', sessionId);
    localStorage.setItem('candidateId', selectedCandidate.id);
    localStorage.setItem('candidateName', selectedCandidate.name);
    
    router.push('/interview');
  };

  const selectedCandidate = candidates.find(c => c.id === selectedCandidateId);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
      <div className="max-w-xl w-full bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-extrabold text-gray-900 mb-2 tracking-tight">ABTALKS AI</h1>
          <h2 className="text-xl font-semibold text-gray-700 mb-1">Technical Interview Agent</h2>
          <p className="text-sm text-gray-500">
            Personalized technical interview based on your 31-day AI Engineering journey.
          </p>
        </div>
        
        {loading ? (
          <div className="text-center text-gray-500 py-8">Loading candidates...</div>
        ) : (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Select Candidate</label>
              <select 
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 bg-gray-50 text-base"
                value={selectedCandidateId}
                onChange={(e) => setSelectedCandidateId(e.target.value)}
              >
                {candidates.map(c => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>
            
            {selectedCandidate && (
              <div className="bg-blue-50 rounded-lg p-5 border border-blue-100">
                <div className="grid grid-cols-3 gap-4">
                  <div className="col-span-1 text-sm font-medium text-blue-800">Name</div>
                  <div className="col-span-2 text-sm text-gray-900 font-semibold">{selectedCandidate.name}</div>
                  
                  <div className="col-span-1 text-sm font-medium text-blue-800">Role</div>
                  <div className="col-span-2 text-sm text-gray-900">{selectedCandidate.jobRole}</div>
                  
                  <div className="col-span-1 text-sm font-medium text-blue-800">Experience</div>
                  <div className="col-span-2 text-sm text-gray-900">{selectedCandidate.yearsExperience} {selectedCandidate.yearsExperience === 1 ? 'year' : 'years'}</div>
                </div>
              </div>
            )}

            <div className="pt-4">
              <button 
                onClick={startInterview}
                disabled={!selectedCandidateId}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-bold py-3 px-4 rounded-lg shadow-sm transition duration-150 ease-in-out"
              >
                Start Interview
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
