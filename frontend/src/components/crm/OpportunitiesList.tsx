import { useState } from 'react';
import { OpportunityCard, type Opportunity } from './OpportunityCard';

interface OpportunitiesListProps {
  onViewAll?: () => void;
}

const mockOpportunities: Opportunity[] = [
  {
    id: '1',
    name: 'Robert Chen',
    priority: 'HIGH',
    accountNumber: '000000311837',
    description: 'CD maturing in 8 days - urgent reinvestment decision required',
    amount: 245000,
    dueDate: '2026-03-06',
    daysRemaining: 8,
    icon: 'up',
  },
  {
    id: '2',
    name: 'Jennifer Martinez',
    priority: 'HIGH',
    accountNumber: '000000239784',
    description: 'Significant excess cash in low-yield account - substantial opportunity to improve returns',
    amount: 180000,
    dueDate: '2026-02-28',
    daysRemaining: 2,
    icon: 'up',
  },
  {
    id: '3',
    name: 'Sarah Williams',
    priority: 'MEDIUM',
    accountNumber: '000000154992',
    description: 'Current product underperforming - replacement opportunity available',
    amount: 325000,
    dueDate: '2026-03-15',
    daysRemaining: 17,
    icon: 'warning',
  },
  {
    id: '4',
    name: 'David Thompson',
    priority: 'MEDIUM',
    accountNumber: '000000276381',
    description: 'Annuity renewal in 45 days - rate drop from 5.2% to 3.8%',
    amount: 150000,
    dueDate: '2026-04-12',
    daysRemaining: 45,
    icon: 'down',
  },
  {
    id: '5',
    name: 'Emily Rodriguez',
    priority: 'MEDIUM',
    accountNumber: '000000298453',
    description: 'CD maturing soon - client may need to reinvest funds or take distribution',
    amount: 95000,
    dueDate: '2026-03-30',
    daysRemaining: 32,
    icon: 'up',
  },
];

export function OpportunitiesList({ onViewAll }: OpportunitiesListProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterPriority, setFilterPriority] = useState<string>('all');

  const filteredOpportunities = mockOpportunities.filter((opp) => {
    const matchesSearch = 
      opp.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      opp.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      opp.accountNumber.includes(searchQuery);
    
    const matchesPriority = filterPriority === 'all' || opp.priority === filterPriority;
    
    return matchesSearch && matchesPriority;
  });

  return (
    <div className="bg-white rounded-[10px] border border-[#e2e8f0] shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-5 border-b border-[#e2e8f0]">
        <h2 className="font-semibold text-[18px] text-[#0f172b] tracking-[-0.4395px]">
          Today's Opportunities
        </h2>
        
        <div className="flex items-center gap-3">
          {/* Priority Filter */}
          <select
            value={filterPriority}
            onChange={(e) => setFilterPriority(e.target.value)}
            className="h-9 px-3 bg-[#f3f3f5] border-0 rounded-lg text-sm text-[#0f172b] focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Priorities</option>
            <option value="HIGH">High Priority</option>
            <option value="MEDIUM">Medium Priority</option>
            <option value="LOW">Low Priority</option>
          </select>

          {/* Search Input */}
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search opportunities..."
            className="w-64 h-9 px-3 bg-[#f3f3f5] border-0 rounded-lg text-sm text-[#0f172b] placeholder:text-[#717182] focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Opportunities List */}
      <div>
        {filteredOpportunities.length > 0 ? (
          <>
            {filteredOpportunities.map((opportunity) => (
              <OpportunityCard key={opportunity.id} opportunity={opportunity} />
            ))}
          </>
        ) : (
          <div className="px-6 py-12 text-center">
            <p className="text-sm text-[#62748e]">No opportunities found matching your criteria.</p>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-[#e2e8f0] text-center">
        <button 
          onClick={onViewAll}
          className="text-sm text-[#155DFC] font-medium hover:underline"
        >
          View All Opportunities
        </button>
      </div>
    </div>
  );
}
