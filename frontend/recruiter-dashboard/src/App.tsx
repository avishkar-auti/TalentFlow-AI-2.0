import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './components/layout/MainLayout';
import Dashboard from './pages/Dashboard';
import Pipeline from './pages/Pipeline';
import Jobs from './pages/Jobs';
import Candidates from './pages/Candidates';
import Interviews from './pages/Interviews';
import Settings from './pages/Settings';
import CandidateProfile from './pages/CandidateProfile';
import JobDetail from './pages/JobDetail';
import Login from './pages/Login';
import Register from './pages/Register';
import { AuthProvider } from './context/AuthContext';

import { useParams, useLocation } from 'react-router-dom';

function InterviewRedirect() {
  const { id } = useParams();
  const location = useLocation();
  React.useEffect(() => {
    window.location.href = `http://localhost:3001/interview/${id}${location.search}`;
  }, [id, location]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-slate-900 text-white">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mr-4"></div>
      <p className="font-medium text-lg">Redirecting to Live Meeting Room...</p>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/interview/:id" element={<InterviewRedirect />} />
          
          <Route path="/" element={<MainLayout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="pipeline" element={<Pipeline />} />
            <Route path="jobs" element={<Jobs />} />
            <Route path="jobs/:id" element={<JobDetail />} />
            <Route path="candidates" element={<Candidates />} />
            <Route path="candidates/:id" element={<CandidateProfile />} />
            <Route path="interviews" element={<Interviews />} />
            <Route path="settings" element={<Settings />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
