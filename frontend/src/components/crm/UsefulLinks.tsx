import { ExternalLink, LayoutDashboard } from 'lucide-react';

const links = [
  {
    id: '1',
    name: 'IBA Metrics Dashboard',
    url: '#',
    icon: LayoutDashboard,
  },
  {
    id: '2',
    name: 'My 3D Dashboards',
    url: '#',
    icon: ExternalLink,
  },
];

export function UsefulLinks() {
  return (
    <div className="bg-white rounded-[10px] border border-[#e2e8f0] shadow-sm p-6">
      <h2 className="font-semibold text-[18px] text-[#0f172b] tracking-[-0.4395px] mb-4">
        Useful Links
      </h2>

      <div className="space-y-2">
        {links.map((link) => (
          <a
            key={link.id}
            href={link.url}
            className="flex items-center gap-2 text-sm text-[#155dfc] hover:underline tracking-[-0.1504px]"
          >
            <link.icon className="w-4 h-4" />
            {link.name}
          </a>
        ))}
      </div>
    </div>
  );
}
