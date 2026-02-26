import { cn } from "@/lib/utils";
import { User, Scale, CheckCircle2, Check, ChevronLeft, ChevronRight } from "lucide-react";

export type WorkflowStep = "overview" | "compare" | "action";

const STEPS: {
  id: WorkflowStep;
  label: string;
  sublabel: string;
  icon: React.ComponentType<{ className?: string }>;
}[] = [
  {
    id: "overview",
    label: "Overview",
    sublabel: "Policy features & benefits",
    icon: User,
  },
  {
    id: "compare",
    label: "Compare",
    sublabel: "Evaluate recommended options",
    icon: Scale,
  },
  {
    id: "action",
    label: "Take Action",
    sublabel: "Confirm, disclose, submit",
    icon: CheckCircle2,
  },
];

interface WorkflowStepperProps {
  currentStep: WorkflowStep;
  completedSteps: Set<WorkflowStep>;
  onStepClick: (step: WorkflowStep) => void;
}

export function WorkflowStepper({
  currentStep,
  completedSteps,
  onStepClick,
}: WorkflowStepperProps) {
  const currentIdx = STEPS.findIndex((s) => s.id === currentStep);
  const canGoBack = currentIdx > 0;
  const canGoForward = currentIdx < STEPS.length - 1;

  const handlePrevious = () => {
    if (canGoBack) onStepClick(STEPS[currentIdx - 1].id);
  };

  const handleNext = () => {
    if (canGoForward) onStepClick(STEPS[currentIdx + 1].id);
  };

  return (
    <div className="bg-gradient-to-b from-slate-50 to-white border-b border-slate-200">
      <div className="px-8 py-8">
        <div className="flex items-center gap-4 max-w-4xl mx-auto">
          {/* Previous Button */}
          <button
            onClick={handlePrevious}
            disabled={!canGoBack}
            className={cn(
              "h-10 w-10 rounded-full flex items-center justify-center transition-all border-2",
              canGoBack
                ? "bg-white border-slate-300 hover:border-blue-500 hover:bg-blue-50 text-slate-700"
                : "bg-slate-100 border-slate-200 text-slate-300 cursor-not-allowed",
            )}
          >
            <ChevronLeft className="h-5 w-5" />
          </button>

          <div className="flex items-center justify-between flex-1">{STEPS.map((step, idx) => {
            const isCurrent = currentStep === step.id;
            const isCompleted = completedSteps.has(step.id);
            const isPast = idx < currentIdx;
            const canClick = isPast || isCurrent || isCompleted;
            const Icon = step.icon;

            return (
              <div key={step.id} className="flex items-center">
                <button
                  onClick={() => canClick && onStepClick(step.id)}
                  disabled={!canClick}
                  className={cn(
                    "flex flex-col items-center gap-2 transition-all",
                    canClick ? "cursor-pointer" : "cursor-not-allowed opacity-50",
                  )}
                >
                  <div
                    className={cn(
                      "h-14 w-14 rounded-full flex items-center justify-center transition-all border-2",
                      isCurrent &&
                        "bg-blue-600 border-blue-600 shadow-lg shadow-blue-200",
                      isCompleted &&
                        !isCurrent &&
                        "bg-green-500 border-green-500",
                      !isCurrent &&
                        !isCompleted &&
                        "bg-slate-100 border-slate-300",
                    )}
                  >
                    {isCompleted && !isCurrent ? (
                      <Check className="h-6 w-6 text-white" />
                    ) : (
                      <Icon
                        className={cn(
                          "h-6 w-6",
                          isCurrent || isCompleted
                            ? "text-white"
                            : "text-slate-400",
                        )}
                      />
                    )}
                  </div>
                  <div className="text-center">
                    <div
                      className={cn(
                        "font-bold text-sm",
                        isCurrent && "text-blue-900",
                        isCompleted && !isCurrent && "text-green-700",
                        !isCurrent && !isCompleted && "text-slate-500",
                      )}
                    >
                      {step.label}
                    </div>
                    <div
                      className={cn(
                        "text-xs",
                        isCurrent && "text-blue-600",
                        isCompleted && !isCurrent && "text-green-600",
                        !isCurrent && !isCompleted && "text-slate-400",
                      )}
                    >
                      {step.sublabel}
                    </div>
                  </div>
                </button>
                {idx < STEPS.length - 1 && (
                  <div className="w-32 h-0.5 mx-4 bg-slate-200 relative">
                    <div
                      className={cn(
                        "absolute inset-0 bg-gradient-to-r transition-all",
                        idx < currentIdx
                          ? "from-green-500 to-green-500"
                          : "from-slate-200 to-slate-200",
                      )}
                    />
                  </div>
                )}
              </div>
            );
          })}</div>

          {/* Next Button */}
          <button
            onClick={handleNext}
            disabled={!canGoForward}
            className={cn(
              "h-10 w-10 rounded-full flex items-center justify-center transition-all border-2",
              canGoForward
                ? "bg-blue-600 border-blue-600 hover:bg-blue-700 text-white"
                : "bg-slate-100 border-slate-200 text-slate-300 cursor-not-allowed",
            )}
          >
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
