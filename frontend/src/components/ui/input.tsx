import * as React from "react";
import { cn } from "@/lib/utils";

function Input({ className, type, ...props }: React.ComponentProps<"input">) {
  return (
    <input
      type={type}
      className={cn(
        "placeholder:text-slate-400 flex h-9 w-full min-w-0 rounded-md border border-slate-200 bg-white px-3 py-1 text-base transition-colors outline-none disabled:pointer-events-none disabled:opacity-50 md:text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500",
        className,
      )}
      {...props}
    />
  );
}

export { Input };
