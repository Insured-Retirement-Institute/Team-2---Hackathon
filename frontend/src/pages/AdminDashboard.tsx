import { AIAuditDashboard } from "@/components/AIAuditDashboard";
import { useNavigate } from "react-router-dom";

export function AdminDashboard() {
  const navigate = useNavigate();
  
  return <AIAuditDashboard onClose={() => navigate("/dashboard")} />;
}
