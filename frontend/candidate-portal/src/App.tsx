import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { CandidateLayout } from './components/layout/CandidateLayout';
import { Home } from './pages/Home';
import { ApplicationStatus } from './pages/ApplicationStatus';
import { InterviewRoom } from './pages/InterviewRoom';
import { Profile } from './pages/Profile';
import { Login } from './pages/Login';
import { Register } from './pages/Register';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading } = useAuth();
  if (loading) return null;
  if (!isAuthenticated) return <Navigate to="/login" />;
  return <>{children}</>;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      
      <Route path="/" element={<CandidateLayout />}>
        <Route index element={<Home />} />
        
        <Route path="/status" element={
          <ProtectedRoute>
            <ApplicationStatus />
          </ProtectedRoute>
        } />
        
        <Route path="/interview/:id" element={
          <ProtectedRoute>
            <InterviewRoom />
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
