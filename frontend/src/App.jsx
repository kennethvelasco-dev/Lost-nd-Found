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
import ReportItem from './pages/Discovery/ReportItem';
import AdminDashboard from './pages/Admin/AdminDashboard';
import AdminReports from './pages/Admin/AdminReports';
import AdminClaimList from './pages/Admin/AdminClaimList';
import AdminReturnItem from './pages/Admin/AdminReturnItem';
import MyActivities from './pages/Discovery/MyActivities';
import GlobalErrorBoundary from './components/Layout/GlobalErrorBoundary';
import './index.css';

// A generic ProtectedRoute that requires the user to be logged in
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) return <div className="page-container"><p>Loading session...</p></div>;
  if (!user) return <Navigate to="/login" replace />;
  return children;
};

// Admin route protection
const AdminRoute = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) return <div className="page-container"><p>Loading session...</p></div>;
  if (!user || (user.role !== 'admin' && user.role !== 'Admin')) return <Navigate to="/lost-items" replace />;
  return children;
};

function App() {
  return (
    <Router>
      <GlobalErrorBoundary>
        <AuthProvider>
          <Layout>
            <Routes>
              {/* Public Routes */}
              <Route path="/login" element={<LoginPage />} />
              <Route path="/signup" element={<SignupPage />} />
              <Route path="/" element={<Navigate to="/lost-items" replace />} />
              
              {/* Lost & Found Routes */}
              <Route path="/lost-items" element={<LostItems />} />
              <Route path="/returned-items" element={<ProtectedRoute><ReturnedItems /></ProtectedRoute>} />
              <Route path="/items/:id" element={<ProtectedRoute><ItemDetail /></ProtectedRoute>} />
              <Route path="/items/:id/claim" element={<ProtectedRoute><ClaimForm /></ProtectedRoute>} />
              <Route path="/claim-confirmation" element={<ProtectedRoute><ConfirmationPage /></ProtectedRoute>} />
              <Route path="/report-item" element={<ProtectedRoute><ReportItem /></ProtectedRoute>} />
              <Route path="/my-activities" element={<ProtectedRoute><MyActivities /></ProtectedRoute>} />

              {/* Admin Routes - Protected */}
              <Route path="/admin/dashboard" element={<AdminRoute><AdminDashboard /></AdminRoute>} />
              <Route path="/admin/claims" element={<AdminRoute><AdminClaimList /></AdminRoute>} />
              <Route path="/admin/reports" element={<AdminRoute><AdminReports /></AdminRoute>} />
              <Route path="/admin/return-item" element={<AdminRoute><AdminReturnItem /></AdminRoute>} />

              {/* Fallback */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Layout>
        </AuthProvider>
      </GlobalErrorBoundary>
    </Router>
  );
}

export default App;
