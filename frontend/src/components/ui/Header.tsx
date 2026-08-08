"use client";

import { useEffect, useState } from "react";
import { User } from "lucide-react";
import Link from "next/link";

export default function Header() {
  const [candidateName, setCandidateName] = useState<string | null>(null);

  useEffect(() => {
    // Only access localStorage on the client
    setCandidateName(localStorage.getItem("candidateName"));
  }, []);

  const getInitial = (name: string) => name.charAt(0).toUpperCase();

  return (
    <header className="sticky top-0 z-50 h-16 border-b border-border bg-bg/80 backdrop-blur-md">
      <div className="max-w-5xl mx-auto h-full px-6 md:px-12 lg:px-20 flex items-center justify-between">
        <Link href="/" className="font-semibold text-base md:text-lg text-text hover:text-primary transition-colors">
          ABTALKS AI
        </Link>
        <div className="flex items-center gap-3">
          {candidateName ? (
            <>
              <div className="hidden md:block text-sm text-text-secondary">
                {candidateName}
              </div>
              <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-white text-sm font-semibold shrink-0">
                {getInitial(candidateName)}
              </div>
            </>
          ) : (
            <div className="w-8 h-8 rounded-full bg-surface-2 border border-border flex items-center justify-center text-text-tertiary shrink-0">
              <User size={16} />
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
