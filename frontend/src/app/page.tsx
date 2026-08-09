"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getCandidates } from "@/lib/api";
import { ArrowRight, ChevronLeft, ChevronRight } from "lucide-react";
import CandidateProfileCard, { ExtendedCandidate } from "@/components/ui/CandidateProfileCard";
import LoadingState from "@/components/ui/LoadingState";
import ErrorState from "@/components/ui/ErrorState";

export default function Home() {
  const router = useRouter();
  const [candidates, setCandidates] = useState<ExtendedCandidate[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchCandidates();
  }, []);

  const fetchCandidates = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await getCandidates();
      setCandidates(data);
    } catch (err) {
      console.error(err);
      setError("Failed to load candidates");
    } finally {
      setIsLoading(false);
    }
  };

  const handleStart = () => {
    if (candidates.length === 0) return;
    
    setIsStarting(true);
    const selected = candidates[selectedIndex];
    
    // Store in localStorage as expected by the existing contract
    const sessionId = crypto.randomUUID();
    localStorage.setItem("sessionId", sessionId);
    localStorage.setItem("candidateId", selected.id);
    localStorage.setItem("candidateName", selected.name);
    localStorage.setItem("candidateSkills", JSON.stringify(selected.skills || []));
    
    router.push("/instructions");
  };

  if (isLoading) {
    return <LoadingState icon="loader" title="Loading candidates..." subtitle="Please wait while we fetch the profiles" />;
  }

  if (error) {
    return <ErrorState onRetry={fetchCandidates} />;
  }

  const selectedCandidate = candidates[selectedIndex];

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6 md:p-12 relative min-h-full">
      {/* Radial Gradient Background */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_50%_0%,rgba(139,92,246,0.08),transparent_60%)] pointer-events-none" />
      
      <div className="relative z-10 w-full max-w-3xl flex flex-col items-center text-center space-y-12 my-auto">
        
        {/* Header Section */}
        <div className="space-y-4">
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-text">
            Your AI Technical Interview<br />Partner
          </h1>
          <p className="text-lg text-text-secondary max-w-xl mx-auto">
            A personalized interview based on your AI engineering journey.
          </p>
        </div>

        {/* Profile Card Section */}
        <div className="w-full flex items-center justify-center gap-4">
          {candidates.length > 1 && (
            <button 
              onClick={() => setSelectedIndex((prev) => (prev > 0 ? prev - 1 : candidates.length - 1))}
              className="p-2 rounded-full hover:bg-surface-2 text-text-tertiary hover:text-text transition-colors hidden sm:block"
            >
              <ChevronLeft size={24} />
            </button>
          )}
          
          {selectedCandidate && (
            <div className="w-full max-w-md">
              <CandidateProfileCard candidate={selectedCandidate} />
            </div>
          )}

          {candidates.length > 1 && (
            <button 
              onClick={() => setSelectedIndex((prev) => (prev < candidates.length - 1 ? prev + 1 : 0))}
              className="p-2 rounded-full hover:bg-surface-2 text-text-tertiary hover:text-text transition-colors hidden sm:block"
            >
              <ChevronRight size={24} />
            </button>
          )}
        </div>

        {/* Mobile Navigation Controls */}
        {candidates.length > 1 && (
          <div className="flex items-center gap-4 sm:hidden">
            <button 
              onClick={() => setSelectedIndex((prev) => (prev > 0 ? prev - 1 : candidates.length - 1))}
              className="p-2 rounded-full bg-surface border border-border text-text-secondary"
            >
              <ChevronLeft size={20} />
            </button>
            <span className="text-sm text-text-tertiary font-medium">
              {selectedIndex + 1} of {candidates.length}
            </span>
            <button 
              onClick={() => setSelectedIndex((prev) => (prev < candidates.length - 1 ? prev + 1 : 0))}
              className="p-2 rounded-full bg-surface border border-border text-text-secondary"
            >
              <ChevronRight size={20} />
            </button>
          </div>
        )}

        {/* Action Section */}
        <div className="flex flex-col items-center space-y-6 w-full">
          <button
            onClick={handleStart}
            disabled={isStarting || !selectedCandidate}
            className="group relative flex items-center justify-center gap-2 w-full max-w-xs bg-primary hover:bg-primary-hover text-white font-medium py-3 px-6 rounded-lg shadow-lg shadow-primary-glow transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isStarting ? (
              <span>Starting...</span>
            ) : (
              <>
                <span>Start Interview</span>
                <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
              </>
            )}
          </button>
          
          <div className="flex items-center gap-2 text-sm text-text-tertiary">
            <span>Personalized</span>
            <span>·</span>
            <span>Adaptive</span>
            <span>·</span>
            <span>Technical</span>
          </div>
        </div>
      </div>
    </div>
  );
}
