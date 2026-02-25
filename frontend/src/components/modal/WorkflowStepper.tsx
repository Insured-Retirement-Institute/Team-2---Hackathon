import { cn } from "@/lib/utils";
import { User, Scale, CheckCircle2 } from "lucide-react";

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
  onStepClick,
}: WorkflowStepperProps) {
  return (
    <div className="bg-gradient-to-b from-slate-50 to-white border-b border-slate-200">
      <div className="px-8 pt-6 pb-0">
        <div className="flex items-end gap-2">
          {STEPS.map((step, idx) => {
            const isCurrent = currentStep === step.id;
            const Icon = step.icon;

            return (
              <button
                key={step.id}
                onClick={() => onStepClick(step.id)}
                className={cn(
                  "group relative flex items-center gap-3 px-6 py-4 rounded-t-xl transition-all min-w-[220px] cursor-pointer",
                  isCurrent &&
                    "bg-white border-2 border-b-0 border-blue-500 shadow-xl shadow-blue-100 -translate-y-1 z-10",
                  !isCurrent &&
                    "bg-white border-2 border-b-0 border-slate-200 hover:border-slate-300 hover:shadow-md",
                )}
              >
                <div
                  className={cn(
                    "h-10 w-10 rounded-full flex items-center justify-center shrink-0 transition-all",
                    isCurrent && "bg-blue-600",
                    !isCurrent && "bg-slate-200",
                  )}
                >
                  <Icon
                    className={cn(
                      "h-5 w-5",
                      isCurrent ? "text-white" : "text-slate-500",
                    )}
                  />{" "}
                </div>
                <div className="text-left flex-1">
                  <div
                    className={cn(
                      "font-bold text-sm",
                      isCurrent && "text-blue-900",
                      !isCurrent && "text-slate-500",
                    )}
                  >
                    {step.label}
                  </div>
                  <div
                    className={cn(
                      "text-xs font-medium",
                      isCurrent && "text-blue-600",
                      !isCurrent && "text-slate-400",
                    )}
                  >
                    {step.sublabel}
                  </div>
                </div>
                <div
                  className={cn(
                    "h-6 w-6 rounded-full flex items-center justify-center text-xs font-bold shrink-0",
                    isCurrent &&
                      "bg-blue-100 text-blue-700 border border-blue-300",
                    !isCurrent &&
                      "bg-slate-100 text-slate-400 border border-slate-300",
                  )}
                >
                  {idx + 1}
                </div>
                {isCurrent && (
                  <div className="absolute bottom-0 left-0 right-0 h-1 rounded-t-sm bg-gradient-to-r from-blue-500 to-blue-600" />
                )}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
