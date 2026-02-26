interface Stat {
  id: string;
  label: string;
  value: string | number;
  color?: string;
}

const stats: Stat[] = [
  {
    id: '1',
    label: 'Open Opportunities',
    value: 5,
  },
  {
    id: '2',
    label: 'High Priority',
    value: 2,
    color: 'text-[#e7000b]',
  },
  {
    id: '3',
    label: 'Total Value',
    value: '$995K',
    color: 'text-[#16a34a]',
  },
];

export function QuickStats() {
  return (
    <div className="bg-white rounded-[10px] border border-[#e2e8f0] shadow-sm p-6">
      <h2 className="font-semibold text-[18px] text-[#0f172b] tracking-[-0.4395px] mb-4">
        Quick Stats
      </h2>

      <div className="space-y-3">
        {stats.map((stat) => (
          <div key={stat.id} className="flex items-center justify-between">
            <span className="text-sm text-[#62748e] tracking-[-0.1504px]">
              {stat.label}
            </span>
            <span className={`text-sm font-semibold ${stat.color || 'text-[#0f172b]'}`}>
              {stat.value}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
