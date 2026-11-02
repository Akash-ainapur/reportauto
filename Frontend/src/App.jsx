import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import AuthPage from "./pages/AuthPage";
import ReportConfig from "./pages/ReportConfig";
import GamifiedLoader from "./components/GamifiedLoader";
import RoastButton from "./components/RoastButton";

function App() {
  return (
    <Router>
      <RoastButton />
      <Routes>
        {/* Root is Landing Page (Public) */}
        <Route path="/" element={<LandingPage />} />

        {/* Auth Page */}
        <Route path="/auth" element={<AuthPage />} />

        {/* Report form: open to everyone; sign-in is asked for only when generating */}
        <Route path="/generate" element={<ReportConfig />} />

        {/* Demo */}
        <Route path="/loading-demo" element={<GamifiedLoader />} />
      </Routes>
    </Router>
  );
}


export default App;
