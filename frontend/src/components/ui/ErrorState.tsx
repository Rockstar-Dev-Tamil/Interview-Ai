import { AlertCircle } from "lucide-react";

interface ErrorStateProps {
  onRetry: () => void;
}

export default function ErrorState({ onRetry }: ErrorStateProps) {
  return (
    <div role="alert" className="w-full max-w-md mx-auto bg-surface border border-error/30 rounded-xl p-6">
      <div className="flex flex-col items-center text-center">
        <div className="w-12 h-12 rounded-full bg-error/10 flex items-center justify-center mb-4">
          <AlertCircle className="text-error" size={24} />
        </div>
        <h3 className="text-lg font-semibold text-text mb-2">Something went wrong</h3>
        <p className="text-text-secondary text-sm mb-6">
          Your answer was preserved.<br />
          Your interview session is safe.
        </p>
        <button
          onClick={onRetry}
          className="w-full bg-error/10 hover:bg-error/20 text-error font-medium py-2.5 px-4 rounded-lg transition-colors"
        >
          Try Again
        </button>
      </div>
    </div>
  );
}
