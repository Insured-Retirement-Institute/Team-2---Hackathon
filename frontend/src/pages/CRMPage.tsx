import { useNavigate } from "react-router-dom";
import { Header } from "@/components/crm/Header";
import { PoliciesSidebar } from "@/components/crm/PoliciesSidebar";
import { RecentRecords } from "@/components/crm/RecentRecords";
import { OpportunitiesList } from "@/components/crm/OpportunitiesList";
import { TodaysEvents } from "@/components/crm/TodaysEvents";
import { UsefulLinks } from "@/components/crm/UsefulLinks";
import { QuickStats } from "@/components/crm/QuickStats";

export default function CRMPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#f1f5f9] flex flex-col">
      <Header onNavigateToDashboard={() => navigate("/dashboard")} />

      <div className="flex-1 p-6">
        <div className="max-w-[1600px] mx-auto">
          <div className="grid grid-cols-12 gap-4">
            <div className="col-span-3 space-y-4">
              <PoliciesSidebar />
              <RecentRecords />
            </div>

            <div className="col-span-6 space-y-4">
              <OpportunitiesList onViewAll={() => navigate("/dashboard")} />
              <TodaysEvents />
            </div>

            <div className="col-span-3 space-y-4">
              <UsefulLinks />
              <QuickStats />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
