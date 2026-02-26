import { ChevronDown } from 'lucide-react';

interface Policy {
  id: string;
  number: string;
  status: string;
}

const policies: Policy[] = [
  { id: '1', number: '#936982', status: 'Due for Annual Review' },
  { id: '2', number: '#889828', status: 'Due for Annual Review' },
  { id: '3', number: '#381810', status: 'Due for Annual Review' },
  { id: '4', number: '#653694', status: 'Due for Annual Review' },
  { id: '5', number: '#629249', status: 'Due for Annual Review' },
];

export function PoliciesSidebar() {
  return (
    <div className="bg-white rounded-[10px] border border-[#e2e8f0] shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-4 border-b border-[#e2e8f0]">
        <h2 className="font-semibold text-[20px] text-[#0f172b] tracking-[-0.4492px]">
          All Annuity Policies
        </h2>
        <button className="p-1 hover:bg-gray-50 rounded-lg transition-colors">
          <ChevronDown className="w-4 h-4" />
        </button>
      </div>

      {/* Policy List */}
      <div className="p-4 space-y-2">
        {policies.map((policy) => (
          <div
            key={policy.id}
            className="p-3 hover:bg-gray-50 rounded cursor-pointer transition-colors"
          >
            <p className="font-medium text-sm text-[#0f172b] tracking-[-0.1504px]">
              Policy {policy.number}
            </p>
            <p className="text-xs text-[#62748e] mt-1">
              {policy.status}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
