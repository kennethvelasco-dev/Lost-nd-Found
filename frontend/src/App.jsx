import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Layout from './components/Layout/Layout';
import LoginPage from './pages/Auth/LoginPage';
import SignupPage from './pages/Auth/SignupPage';
import LostItems from './pages/Discovery/LostItems';
import ReturnedItems from './pages/Discovery/ReturnedItems';
import ItemDetail from './pages/Discovery/ItemDetail';
import ClaimForm from './pages/Discovery/ClaimForm';
import ConfirmationPage from './pages/Discovery/ConfirmationPage';
import AdminDashboard from './pages/Admin/AdminDashboard';
import AdminReports from './pages/Admin/AdminReports';
import './index.css';

// A generic ProtectedRoute that requires the user to be logged in
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) return <div>Loading...</div>;
  if (!user) return <Navigate to="/login" replace />;
  return children;
};

// Admin route protection
const AdminRoute = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) return <div>Loading...</div>;
  if (!user || user.role !== 'admin') return <Navigate to="/lost-items" replace />;
  return children;
};

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          {/* Auth Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />

          {/* Main Application Routes - Protected */}
          <Route path="/" element={<Navigate to="/lost-items" replace />} />
          <Route path="/lost-items" element={<ProtectedRoute><Layout><LostItems /></Layout></ProtectedRoute>} />
          <Route path="/returned-items" element={<ProtectedRoute><Layout><ReturnedItems /></Layout></ProtectedRoute>} />
          <Route path="/items/:id" element={<ProtectedRoute><Layout><ItemDetail /></Layout></ProtectedRoute>} />
          <Route path="/items/:id/claim" element={<ProtectedRoute><Layout><ClaimForm /></Layout></ProtectedRoute>} />
          <Route path="/claim-confirmation" element={<ProtectedRoute><Layout><ConfirmationPage /></Layout></ProtectedRoute>} />

          {/* Admin Routes - Protected */}
          <Route path="/admin/dashboard" element={<AdminRoute><Layout><AdminDashboard /></Layout></AdminRoute>} />
          <Route path="/admin/reports" element={<AdminRoute><Layout><AdminReports /></Layout></AdminRoute>} />

          {/* Placeholder for Report Item */}
          <Route path="/report-item" element={<ProtectedRoute><Layout><div>Report Item Page Coming Soon</div></Layout></ProtectedRoute>} />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;

