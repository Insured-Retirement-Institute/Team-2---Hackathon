import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Dashboard } from "./pages/Dashboard";
import { AlertDetailPage } from "./pages/AlertDetail";
import { ApiSpec } from "./pages/ApiSpec";
import { ResponsibleAIDashboard } from "./pages/ResponsibleAIDashboard";
import { AdminDashboard } from "./pages/AdminDashboard";
import { ChatBot } from "./components/ChatBot";

function App() {
  return (
    <BrowserRouter>
      <ChatBot>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/alerts/:alertId" element={<AlertDetailPage />} />
          <Route path="/api-spec" element={<ApiSpec />} />
          <Route path="/admin" element={<AdminDashboard />} />
          <Route
            path="/admin/responsible-ai"
            element={<ResponsibleAIDashboard />}
          />
        </Routes>
      </ChatBot>
    </BrowserRouter>
  );
}

export default App;
