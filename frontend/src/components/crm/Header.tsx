import { Search, UserPlus } from 'lucide-react';

interface HeaderProps {
  onNavigateToDashboard?: () => void;
}

export function Header({ onNavigateToDashboard }: HeaderProps) {
  return (
    <div className="bg-white w-full h-[60px] border-b border-black/10 shadow-sm">
      <div className="content-stretch flex items-center justify-between h-full px-6">
        {/* Logo and Title */}
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">
            IRI
          </div>
          <h1 className="font-semibold text-[20px] text-[#0f172b] tracking-[-0.4492px]">
            CRM
          </h1>
        </div>

        {/* Search and New Client */}
        <div className="flex items-center gap-3">
          {/* Search Input */}
          <div className="relative w-[320px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#90A1B9]" />
            <input
              type="text"
              placeholder="Search..."
              className="w-full h-9 pl-9 pr-3 bg-[#f8fafc] border border-[#cad5e2] rounded-lg text-sm text-[#0f172b] placeholder:text-[#717182] focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* New Client Button */}
          <button 
            onClick={onNavigateToDashboard}
            className="flex items-center gap-2 h-8 px-3 text-sm font-medium text-[#45556c] hover:bg-gray-50 rounded-lg transition-colors"
          >
            <UserPlus className="w-4 h-4" />
            New Client
          </button>
        </div>
      </div>
    </div>
  );
}
