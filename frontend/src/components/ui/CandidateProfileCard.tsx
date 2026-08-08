import { Candidate } from "@/lib/api";

export interface ExtendedCandidate extends Candidate {
  jobRole?: string;
  yearsExperience?: number;
}

interface CandidateProfileCardProps {
  candidate: ExtendedCandidate;
  onClick?: () => void;
  isSelected?: boolean;
}

export default function CandidateProfileCard({ candidate, onClick, isSelected = false }: CandidateProfileCardProps) {
  const getInitial = (name: string) => name.charAt(0).toUpperCase();

  return (
    <div 
      onClick={onClick}
      className={`
        relative overflow-hidden w-full max-w-md mx-auto p-8 rounded-xl border bg-surface transition-all duration-200
        ${onClick ? "cursor-pointer hover:border-border-hover hover:shadow-lg hover:shadow-black/20" : ""}
        ${isSelected ? "border-primary ring-1 ring-primary" : "border-border"}
      `}
    >
      {/* Radial gradient background */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-primary/10 to-transparent opacity-50 pointer-events-none rounded-bl-full" />
      
      <div className="relative z-10 flex flex-col items-center text-center">
        <div className="w-16 h-16 rounded-full bg-primary flex items-center justify-center text-white text-2xl font-semibold mb-4 shadow-lg shadow-primary-glow">
          {getInitial(candidate.name)}
        </div>
        
        <h3 className="text-xl font-semibold text-text mb-1 tracking-tight">{candidate.name}</h3>
        {candidate.jobRole && (
          <p className="text-sm font-medium text-text-tertiary uppercase tracking-wider mb-6">
            {candidate.jobRole}
          </p>
        )}
        
        <div className="w-full h-px bg-border mb-6" />
        
        <div className="w-full grid grid-cols-2 gap-4 text-left">
          {candidate.yearsExperience !== undefined && (
            <div>
              <p className="text-xs font-medium text-text-tertiary uppercase tracking-wider mb-1">Experience</p>
              <p className="text-sm text-text-secondary">{candidate.yearsExperience} years</p>
            </div>
          )}
          {candidate.jobRole && (
            <div>
              <p className="text-xs font-medium text-text-tertiary uppercase tracking-wider mb-1">Role</p>
              <p className="text-sm text-text-secondary">{candidate.jobRole}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
