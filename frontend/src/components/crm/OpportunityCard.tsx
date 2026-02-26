import { DollarSign, Calendar, AlertCircle, TrendingUp, TrendingDown } from 'lucide-react';

export type Priority = 'HIGH' | 'MEDIUM' | 'LOW';

export interface Opportunity {
  id: string;
  name: string;
  priority: Priority;
  accountNumber: string;
  description: string;
  amount: number;
  dueDate: string;
  daysRemaining: number;
  icon: 'up' | 'down' | 'warning';
}

interface OpportunityCardProps {
  opportunity: Opportunity;
}

const priorityStyles = {
  HIGH: {
    bg: 'bg-[#ffe2e2]',
    border: 'border-[#ffa2a2]',
    text: 'text-[#c10007]',
  },
  MEDIUM: {
    bg: 'bg-[#fef3c6]',
    border: 'border-[#ffd230]',
    text: 'text-[#bb4d00]',
  },
  LOW: {
    bg: 'bg-[#e0f2fe]',
    border: 'border-[#7dd3fc]',
    text: 'text-[#0369a1]',
  },
};

const IconComponent = ({ icon }: { icon: 'up' | 'down' | 'warning' }) => {
  const iconClass = "w-5 h-5 text-[#155DFC]";
  
  switch (icon) {
    case 'up':
      return <TrendingUp className={iconClass} />;
    case 'down':
      return <TrendingDown className={iconClass} />;
    case 'warning':
      return <AlertCircle className={iconClass} />;
  }
};

export function OpportunityCard({ opportunity }: OpportunityCardProps) {
  const priorityStyle = priorityStyles[opportunity.priority];
  const isUrgent = opportunity.daysRemaining <= 10;

  return (
    <div className="border-b border-[#e2e8f0] px-6 py-5 hover:bg-gray-50/50 transition-colors">
      <div className="flex gap-4">
        {/* Icon */}
        <div className="pt-1">
          <IconComponent icon={opportunity.icon} />
        </div>

        {/* Content */}
        <div className="flex-1">
          {/* Header */}
          <div className="flex items-center gap-3 mb-2">
            <h3 className="font-semibold text-[18px] text-[#0f172b] tracking-[-0.4395px]">
              {opportunity.name}
            </h3>
            
            {/* Priority Badge */}
            <span
              className={`px-2 py-0.5 text-xs font-semibold rounded-lg border ${priorityStyle.bg} ${priorityStyle.border} ${priorityStyle.text}`}
            >
              {opportunity.priority}
            </span>
            
            {/* Account Number */}
            <span className="text-xs text-[#62748e]">
              #{opportunity.accountNumber}
            </span>
          </div>

          {/* Description */}
          <p className="text-sm text-[#45556c] mb-4 tracking-[-0.1504px]">
            {opportunity.description}
          </p>

          {/* Meta Information */}
          <div className="flex items-center gap-6 text-xs">
            {/* Amount */}
            <div className="flex items-center gap-1.5 text-[#314158]">
              <DollarSign className="w-3.5 h-3.5 text-[#62748e]" />
              <span className="font-medium">
                ${opportunity.amount.toLocaleString()}
              </span>
            </div>

            {/* Due Date */}
            <div className="flex items-center gap-1.5 text-[#62748e]">
              <Calendar className="w-3.5 h-3.5" />
              <span>Due: {opportunity.dueDate}</span>
            </div>

            {/* Days Remaining */}
            <div className="flex items-center gap-1.5">
              <AlertCircle className={`w-3.5 h-3.5 ${isUrgent ? 'text-[#E7000B]' : 'text-[#62748e]'}`} />
              <span className={`font-medium ${isUrgent ? 'text-[#e7000b]' : 'text-[#314158]'}`}>
                {opportunity.daysRemaining} days remaining
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
