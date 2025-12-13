import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import AuthPage from "./pages/AuthPage";
import ReportConfig from "./pages/ReportConfig";
import GamifiedLoader from "./components/GamifiedLoader";

function App() {
  return (
    <Router>
      <Routes>
        {/* Root is Landing Page (Public) */}
        <Route path="/" element={<LandingPage />} />

        {/* Auth Page */}
        <Route path="/auth" element={<AuthPage />} />

        {/* Main Application Routes */}
        <Route path="/generate" element={<ReportConfig />} />

        {/* Demo */}
        <Route path="/loading-demo" element={<GamifiedLoader />} />
      </Routes>
    </Router>
  );
}

export default App;
