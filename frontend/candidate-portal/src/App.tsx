import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { CandidateLayout } from './components/layout/CandidateLayout';
import { Home } from './pages/Home';
import { JobsList } from './pages/JobsList';
import { ApplicationStatus } from './pages/ApplicationStatus';
import { InterviewRoom } from './pages/InterviewRoom';
import { TechnicalSandbox } from './pages/TechnicalSandbox';
import { Profile } from './pages/Profile';
import { Login } from './pages/Login';
import { Register } from './pages/Register';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading } = useAuth();
  if (loading) return null;
  if (!isAuthenticated) return <Navigate to="/login" />;
  return <>{children}</>;
}

// Recruiters join a live interview meeting straight from the recruiter dashboard's
// meet_link (?role=recruiter) — they don't have a candidate-portal session, so we
// let that specific view through without requiring candidate login.
function InterviewRouteGuard({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const isRecruiterView = new URLSearchParams(location.search).get('role') === 'recruiter';
  if (isRecruiterView) return <>{children}</>;
  return <ProtectedRoute>{children}</ProtectedRoute>;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      
      <Route path="/" element={<CandidateLayout />}>
        <Route index element={<Home />} />
        <Route path="/jobs" element={<JobsList />} />
        
        <Route path="/status" element={
          <ProtectedRoute>
            <ApplicationStatus />
          </ProtectedRoute>
        } />
        
        <Route path="/interview/:id" element={
          <InterviewRouteGuard>
            <InterviewRoom />
          </InterviewRouteGuard>
        } />
        
        <Route path="/technical/:id" element={
          <ProtectedRoute>
            <TechnicalSandbox />
          </ProtectedRoute>
        } />
        
        <Route path="/profile" element={
          <ProtectedRoute>
            <Profile />
          </ProtectedRoute>
        } />
      </Route>
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
