import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Dashboard } from "./pages/Dashboard";
import { AlertDetailPage } from "./pages/AlertDetail";
import { ApiSpec } from "./pages/ApiSpec";
import { ChatBot } from "./components/ChatBot";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/alerts/:alertId" element={<AlertDetailPage />} />
        <Route path="/api-spec" element={<ApiSpec />} />
      </Routes>
      <ChatBot />
    </BrowserRouter>
  );
}

export default App;
