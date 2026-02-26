import { useState } from 'react';
import { OpportunityCard, type Opportunity } from './OpportunityCard';
import policyDataFile from '../../../.iri/context/policyData.json';

interface OpportunitiesListProps {
  onViewAll?: () => void;
}

// Generate opportunities from real policy data
function generateOpportunitiesFromPolicyData(): Opportunity[] {
  const opportunities: Opportunity[] = [];

  policyDataFile.policyData.forEach((policy) => {
    // Calculate days until renewal
    const parts = policy.renewalDate.split("/");
    const renewal = new Date(parseInt(parts[2]), parseInt(parts[0]) - 1, parseInt(parts[1]));
    const today = new Date();
    const daysRemaining = Math.ceil((renewal.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));

    // Only include eligible policies renewing within 90 days
    if (daysRemaining > 0 && daysRemaining <= 90 && policy.eligibilityStatus === "eligible") {
      const currentRate = parseFloat(policy.currentRate.replace("%", ""));
      const renewalRate = parseFloat(policy.renewalRate.replace("%", ""));
      const rateDrop = currentRate - renewalRate;
      
      let description = '';
      let priority: 'HIGH' | 'MEDIUM' | 'LOW' = 'MEDIUM';
      let icon: 'up' | 'down' | 'warning' = 'warning';

      if (policy.isMinRateRenewal) {
        description = `Renewal at minimum rate ${policy.renewalRate} - replacement analysis recommended`;
        priority = 'HIGH';
        icon = 'down';
      } else if (rateDrop > 0.5) {
        description = `Annuity renewal in ${daysRemaining} days - rate drop from ${policy.currentRate} to ${policy.renewalRate}`;
        priority = daysRemaining <= 30 ? 'HIGH' : 'MEDIUM';
        icon = 'down';
      } else {
        description = `Renewal opportunity - current rate ${policy.currentRate} renewing at ${policy.renewalRate}`;
        priority = daysRemaining <= 30 ? 'HIGH' : 'MEDIUM';
        icon = 'up';
      }

      opportunities.push({
        id: policy.contractId,
        name: policy.clientName,
        priority,
        accountNumber: policy.contractId,
        description,
        amount: parseFloat(policy.currentValue.replace(/[$,]/g, '')),
        dueDate: policy.renewalDate,
        daysRemaining,
        icon,
      });
    }
  });

  return opportunities.sort((a, b) => a.daysRemaining - b.daysRemaining).slice(0, 5);
}

const mockOpportunities: Opportunity[] = generateOpportunitiesFromPolicyData();

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
