import { Routes, Route, Navigate } from "react-router-dom";

import DashboardLayout from "./layouts/DashboardLayout";

import Dashboard from "./pages/Dashboard/Dashboard";
import Upload from "./pages/Upload/Upload";
import Analysis from "./pages/Analysis/Analysis";
import MapViewer from "./pages/MapViewer/MapViewer";
import Ranking from "./pages/Ranking/Ranking";
import Recommendations from "./pages/Recommendations/Recommendations";
import Reports from "./pages/Reports/Reports";
import Downloads from "./pages/Downloads/Downloads";
import Settings from "./pages/Settings/Settings";

function App() {
  return (
    <Routes>

      <Route path="/" element={<DashboardLayout />}>

        <Route index element={<Dashboard />} />

        <Route path="upload" element={<Upload />} />

        <Route path="analysis" element={<Analysis />} />

        <Route path="map" element={<MapViewer />} />

        <Route path="ranking" element={<Ranking />} />

        <Route
          path="recommendations"
          element={<Recommendations />}
        />

        <Route path="reports" element={<Reports />} />

        <Route path="downloads" element={<Downloads />} />

        <Route path="settings" element={<Settings />} />

      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />

    </Routes>
  );
}

export default App;