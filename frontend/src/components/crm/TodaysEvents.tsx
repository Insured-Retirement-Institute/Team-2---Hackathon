import { Calendar } from 'lucide-react';

export function TodaysEvents() {
  return (
    <div className="bg-white rounded-[10px] border border-[#e2e8f0] shadow-sm p-6">
      <h2 className="font-semibold text-[18px] text-[#0f172b] tracking-[-0.4395px] mb-6">
        Today's Events
      </h2>

      {/* Empty State */}
      <div className="flex flex-col items-center justify-center py-12">
        <div className="w-16 h-16 mb-4 flex items-center justify-center">
          <Calendar className="w-12 h-12 text-[#90A1B9]" strokeWidth={1.5} />
        </div>
        <p className="text-sm text-[#62748e] mb-6">
          Looks like you're free and clear the rest of the day.
        </p>
        <button className="text-sm text-[#155DFC] font-medium hover:underline">
          View Calendar
        </button>
      </div>
    </div>
  );
}
