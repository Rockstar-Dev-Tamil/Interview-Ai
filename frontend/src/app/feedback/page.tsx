"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { CheckCircle } from "lucide-react";
import { motion } from "framer-motion";
import { Feedback } from "@/lib/api";
import StrengthCard from "@/components/ui/StrengthCard";
import GapItem from "@/components/ui/GapItem";
import NextStepItem from "@/components/ui/NextStepItem";
import LoadingState from "@/components/ui/LoadingState";

export default function FeedbackPage() {
  const router = useRouter();
  const [feedback, setFeedback] = useState<Feedback | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem("feedback");
    if (stored) {
      try {
        setFeedback(JSON.parse(stored));
      } catch (e) {
        console.error("Failed to parse feedback", e);
        router.push("/");
      }
    } else {
      router.push("/");
    }
  }, [router]);

  const handleStartNew = () => {
    localStorage.removeItem("sessionId");
    localStorage.removeItem("feedback");
    router.push("/");
  };

  if (!feedback) {
    return <LoadingState icon="loader" title="Generating your report..." subtitle="Please wait while we finalize the evaluation" />;
  }

  // Parse next steps into an array if it's a string with newlines or numbered lists
  const nextStepsList = feedback.next
    .split(/\n+/)
    .filter((step) => step.trim().length > 0);

  return (
    <div className="flex-1 overflow-y-auto bg-bg p-6 md:p-12 lg:px-20 py-12">
      <div className="max-w-5xl mx-auto flex flex-col space-y-16">
        
        {/* Hero Section */}
        <motion.div 
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="space-y-4"
        >
          <div className="flex items-center gap-2">
            <CheckCircle size={16} className="text-success" />
            <span className="text-xs font-medium text-text-tertiary uppercase tracking-wider">
              Interview Complete
            </span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-text">
            Your Technical Interview Report
          </h1>
          <p className="text-lg text-text-secondary max-w-2xl">
            You completed your personalized AI engineering assessment.
          </p>
        </motion.div>

        {/* Overview Card */}
        <motion.div 
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
          className="bg-surface border border-border rounded-xl p-6 md:p-8"
        >
          <h2 className="text-xs font-medium text-text-tertiary uppercase tracking-wider mb-4">
            Overview
          </h2>
          <p className="text-text text-base leading-relaxed whitespace-pre-wrap">
            {feedback.summary}
          </p>
        </motion.div>

        {/* Strengths */}
        {feedback.strengths && feedback.strengths.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-xs font-medium text-text-tertiary uppercase tracking-wider">
              Strengths
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {feedback.strengths.map((s, i) => (
                <StrengthCard key={i} strength={s} delay={0.2 + i * 0.1} />
              ))}
            </div>
          </div>
        )}

        {/* Areas to Improve */}
        {feedback.gaps && feedback.gaps.length > 0 && (
          <div className="space-y-6">
            <h2 className="text-xs font-medium text-text-tertiary uppercase tracking-wider">
              Areas to Improve
            </h2>
            <div className="flex flex-col space-y-6">
              {feedback.gaps.map((g, i) => (
                <GapItem key={i} index={i + 1} gap={g} delay={0.4 + i * 0.1} />
              ))}
            </div>
          </div>
        )}

        {/* Next Steps */}
        <div className="space-y-6">
          <h2 className="text-xs font-medium text-text-tertiary uppercase tracking-wider">
            Your Next Steps
          </h2>
          <div className="flex flex-col space-y-3">
            {nextStepsList.map((step, i) => (
              <NextStepItem key={i} index={i + 1} step={step} delay={0.6 + i * 0.1} />
            ))}
          </div>
        </div>

        {/* Action Button */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 1 }}
          className="pt-8 flex justify-center border-t border-border/50"
        >
          <button
            onClick={handleStartNew}
            className="bg-surface border border-border hover:border-border-hover text-text-secondary hover:text-text font-medium py-3 px-8 rounded-lg transition-colors shadow-sm"
          >
            Start New Interview
          </button>
        </motion.div>
        
      </div>
    </div>
  );
}
