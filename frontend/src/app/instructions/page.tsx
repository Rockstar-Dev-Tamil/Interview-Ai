"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, ShieldCheck, FileText, AlertCircle, Camera } from "lucide-react";
import { motion } from "framer-motion";
import FocusCamera, { FocusStatus } from "@/components/ui/FocusCamera";

export default function InstructionsPage() {
  const router = useRouter();
  
  const [agreed, setAgreed] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [proctorStatus, setProctorStatus] = useState<FocusStatus>("OFFLINE");
  const [proctorMessage, setProctorMessage] = useState("Proctoring Offline");
  const [isStarting, setIsStarting] = useState(false);
  const [loadingText, setLoadingText] = useState("Connecting to server...");

  const handleProceed = () => {
    // Validate inputs
    if (!agreed) {
      setError("Please agree to the interview guidelines before proceeding.");
      return;
    }

    if (proctorStatus === "INITIALIZING" || proctorStatus === "ERROR") {
      setError("Please wait for the proctoring camera to initialize successfully.");
      return;
    }

    setError(null);
    setIsStarting(true);
    
    // Save a flag indicating they passed verification (optional)
    localStorage.setItem("idVerified", "true");
    
    // Simulate connection delay and sequence
    setTimeout(() => setLoadingText("Initializing AI agent..."), 1200);
    setTimeout(() => setLoadingText("Generating curriculum..."), 2400);
    setTimeout(() => setLoadingText("Starting session..."), 3600);
    
    // Redirect after delay
    setTimeout(() => {
      router.push("/interview");
    }, 4500);
  };

  return (
    <>
      {isStarting && (
        <div className="fixed inset-0 z-50 bg-bg/95 backdrop-blur-md flex flex-col items-center justify-center">
          <div className="flex flex-col items-center space-y-6 max-w-sm w-full p-8 rounded-2xl border border-primary/20 bg-surface/50 shadow-[0_0_50px_rgba(59,130,246,0.1)]">
            <div className="relative w-16 h-16 flex items-center justify-center">
              <div className="absolute inset-0 rounded-full border-t-2 border-primary animate-spin"></div>
              <div className="absolute inset-2 rounded-full border-r-2 border-cyan-400 animate-spin" style={{ animationDirection: 'reverse', animationDuration: '1.5s' }}></div>
              <div className="w-8 h-8 bg-primary/20 rounded-full animate-pulse"></div>
            </div>
            
            <div className="text-center space-y-2">
              <h3 className="text-xl font-bold text-white tracking-wide uppercase">Preparing Terminal</h3>
              <p className="text-sm font-mono text-cyan-400 animate-pulse">{loadingText}</p>
            </div>
            
            {/* Fake progress bar */}
            <div className="w-full h-1 bg-surface-2 rounded-full overflow-hidden">
              <motion.div 
                className="h-full bg-primary"
                initial={{ width: "0%" }}
                animate={{ width: "100%" }}
                transition={{ duration: 4.5, ease: "easeInOut" }}
              />
            </div>
          </div>
        </div>
      )}

      <div className="flex-1 flex flex-col items-center p-6 md:p-12 relative min-h-full overflow-y-auto">
        {/* Radial Gradient Background */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_50%_0%,rgba(59,130,246,0.08),transparent_60%)] pointer-events-none" />
        
        <div className="relative z-10 w-full max-w-3xl flex flex-col space-y-8 my-auto py-8">
          
          {/* Header Section */}
          <div className="space-y-4 text-center">
            <div className="flex items-center justify-center gap-2 mb-2">
              <ShieldCheck size={28} className="text-primary" />
            </div>
            <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-text">
              Interview Instructions
            </h1>
            <p className="text-lg text-text-secondary max-w-xl mx-auto">
              Please read the rules carefully before starting.
            </p>
          </div>

          <div className="bg-surface border border-border rounded-xl p-6 md:p-8 space-y-6">
            
            <div className="space-y-4">
              <h2 className="text-xl font-semibold flex items-center gap-2">
                <FileText size={20} className="text-text-secondary" />
                Interview Guidelines
              </h2>
              <ul className="space-y-3 text-text-secondary list-disc pl-5">
                <li>Ensure you have a stable and reliable internet connection.</li>
                <li>The AI will ask technical questions based on your background. Explain your thought process clearly.</li>
                <li>Do not use external assistance, additional devices, or seek help from others during the interview.</li>
                <li>You may be asked follow-up questions if your initial answer needs more depth.</li>
                <li>Once you start, do not close or refresh the browser window until the interview completes.</li>
              </ul>
            </div>

            <div className="h-px w-full bg-border" />

            {error && (
              <motion.div 
                initial={{ opacity: 0, y: -10 }} 
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center gap-2 text-error text-sm mt-4"
              >
                <AlertCircle size={16} />
                <span>{error}</span>
              </motion.div>
            )}

            <div className="space-y-4">
              <h2 className="text-xl font-semibold flex items-center gap-2">
                <Camera size={20} className="text-text-secondary" />
                Camera & Focus Check
              </h2>
              <p className="text-sm text-text-tertiary">
                Your interview requires active monitoring. Please ensure you are centered in the frame. The camera starts automatically.
              </p>
              
              <div className="max-w-[320px] mx-auto bg-surface-2 p-4 rounded-xl border border-border">
                <FocusCamera onStatusChange={(s, m) => { setProctorStatus(s); setProctorMessage(m); }} />
                
                {proctorStatus !== "OFFLINE" && (
                  <div className={`mt-3 p-2 rounded text-xs uppercase font-mono tracking-wider text-center border ${
                      proctorStatus === "FOCUSED" ? "text-cyan-400 border-cyan-400/50 bg-cyan-900/20 shadow-[0_0_10px_rgba(34,211,238,0.2)]" :
                      proctorStatus === "DISTRACTED" || proctorStatus === "ABSENT" ? "text-red-500 border-red-500/50 bg-red-900/20 shadow-[0_0_10px_rgba(239,68,68,0.3)] animate-pulse" :
                      "text-text-secondary border-border bg-surface"
                  }`}>
                    {proctorMessage}
                  </div>
                )}
              </div>
            </div>

            <div className="pt-6">
              <label className="flex items-start gap-3 cursor-pointer group">
                <div className="relative flex items-center justify-center mt-0.5">
                  <input 
                    type="checkbox" 
                    checked={agreed}
                    onChange={(e) => setAgreed(e.target.checked)}
                    className="appearance-none w-5 h-5 border-2 border-border rounded bg-surface checked:bg-primary checked:border-primary transition-colors cursor-pointer"
                  />
                  {agreed && (
                    <ShieldCheck size={14} className="absolute text-white pointer-events-none" />
                  )}
                </div>
                <span className="text-sm text-text-secondary group-hover:text-text transition-colors">
                  I have read and understood the interview guidelines and I agree to proceed with the assessment.
                </span>
              </label>
            </div>

          </div>

          {/* Action Section */}
          <div className="flex flex-col items-center pt-4">
            <button
              onClick={handleProceed}
              disabled={isStarting}
              className="group relative flex items-center justify-center gap-2 w-full max-w-sm bg-primary hover:bg-primary-hover text-white font-medium py-3 px-6 rounded-lg shadow-lg shadow-primary-glow transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span>{isStarting ? "Connecting..." : "Proceed to Interview"}</span>
              {!isStarting && <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />}
            </button>
          </div>

        </div>
      </div>
    </>
  );
}
