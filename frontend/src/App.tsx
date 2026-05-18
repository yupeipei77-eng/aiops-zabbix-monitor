import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LayoutShell from './components/LayoutShell';
import Dashboard from './pages/Dashboard';
import Alerts from './pages/Alerts';
import AlertDetail from './pages/AlertDetail';
import AIAnalysisPage from './pages/AIAnalysis';
import KnowledgeBase from './pages/KnowledgeBase';
import Reports from './pages/Reports';
import Settings from './pages/Settings';

const App: React.FC = () => (
  <BrowserRouter>
    <LayoutShell>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/alerts" element={<Alerts />} />
        <Route path="/alerts/:id" element={<AlertDetail />} />
        <Route path="/ai-analysis" element={<AIAnalysisPage />} />
        <Route path="/knowledge" element={<KnowledgeBase />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </LayoutShell>
  </BrowserRouter>
);

export default App;
