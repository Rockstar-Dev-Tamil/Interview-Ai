import { Loader2, AlertCircle, type LucideIcon } from "lucide-react";

interface LoadingStateProps {
  icon: "loader" | "alert";
  title: string;
  subtitle: string;
}

export default function LoadingState({ icon, title, subtitle }: LoadingStateProps) {
  const IconComponent: LucideIcon = icon === "loader" ? Loader2 : AlertCircle;
  const isLoader = icon === "loader";

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8 text-center min-h-[50vh]">
      <div className={`mb-6 ${isLoader ? "text-primary" : "text-warning"}`}>
        <IconComponent size={48} className={isLoader ? "animate-spin" : ""} strokeWidth={1.5} />
      </div>
      <h2 className="text-xl font-semibold text-text mb-2">{title}</h2>
      <p className="text-sm text-text-tertiary">{subtitle}</p>
    </div>
  );
}
