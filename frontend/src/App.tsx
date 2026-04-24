import { Routes, Route } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import DashboardPage from './pages/DashboardPage';
import PromptsPage from './pages/PromptsPage';
import SchemasPage from './pages/SchemasPage';
import TestSuitesPage from './pages/TestSuitesPage';

function App() {
  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        <Route index element={<DashboardPage />} />
        <Route path="prompts" element={<PromptsPage />} />
        <Route path="schemas" element={<SchemasPage />} />
        <Route path="test-suites" element={<TestSuitesPage />} />
      </Route>
    </Routes>
  );
}

export default App;