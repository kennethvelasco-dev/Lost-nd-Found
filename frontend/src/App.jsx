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
import ReturnLogDetail from './pages/Discovery/ReturnLogDetail';
import AdminDashboard from './pages/Admin/AdminDashboard';
import AdminReports from './pages/Admin/AdminReports';
import AdminClaimList from './pages/Admin/AdminClaimList';
import AdminApprovedClaims from './pages/Admin/AdminApprovedClaims';
import AdminClaimDetail from './pages/Admin/AdminClaimDetail';
import AdminReturnItem from './pages/Admin/AdminReturnItem';
import MyActivities from './pages/Discovery/MyActivities';
import GlobalErrorBoundary from './components/Layout/GlobalErrorBoundary';
import FullPageLoader from './components/common/FullPageLoader';
import './index.css';

// Protected route: only checks auth, not loading
const ProtectedRoute = ({ children }) => {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  return children;
};

const AdminRoute = ({ children }) => {
  const { user } = useAuth();
  if (!user || (user.role !== 'admin' && user.role !== 'Admin')) {
    return <Navigate to="/lost-items" replace />;
  }
  return children;
};

const AppRoutes = () => (
  <Routes>
    {/* Public Auth Routes - Full Screen */}
    <Route path="/login" element={<LoginPage />} />
    <Route path="/signup" element={<SignupPage />} />

    {/* Main Application Shell */}
    <Route element={<Layout />}>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/lost-items" element={<ProtectedRoute><LostItems /></ProtectedRoute>} />
      <Route path="/returned-items" element={<ProtectedRoute><ReturnedItems /></ProtectedRoute>} />
      <Route path="/returns/:id" element={<ProtectedRoute><ReturnLogDetail /></ProtectedRoute>} />
      <Route path="/items/:id" element={<ProtectedRoute><ItemDetail /></ProtectedRoute>} />
      <Route path="/items/:id/claim" element={<ProtectedRoute><ClaimForm /></ProtectedRoute>} />
      <Route path="/confirmation" element={<ProtectedRoute><ConfirmationPage /></ProtectedRoute>} />
      <Route path="/report-item" element={<ProtectedRoute><ReportItem /></ProtectedRoute>} />
      <Route path="/my-activities" element={<ProtectedRoute><MyActivities /></ProtectedRoute>} />

      {/* Admin Routes */}
      <Route path="/admin/dashboard" element={<AdminRoute><AdminDashboard /></AdminRoute>} />
      <Route path="/admin/claims" element={<AdminRoute><AdminClaimList /></AdminRoute>} />
      <Route path="/admin/approved-claims" element={<AdminRoute><AdminApprovedClaims /></AdminRoute>} />
      <Route path="/admin/claims/:id" element={<AdminRoute><AdminClaimDetail /></AdminRoute>} />
      <Route path="/admin/reports" element={<AdminRoute><AdminReports /></AdminRoute>} />
      <Route path="/admin/return-item" element={<AdminRoute><AdminReturnItem /></AdminRoute>} />
    </Route>

    {/* Fallback */}
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes>
);

const AppWithLoader = () => {
  const { loading } = useAuth();

  if (loading) {
    // Global full-page loader while auth/session is initializing
    return <FullPageLoader message="Checking your session and preparing your dashboard..." />;
  }

  return <AppRoutes />;
};

function App() {
  return (
    <Router>
      <GlobalErrorBoundary>
        <AuthProvider>
          <AppWithLoader />
        </AuthProvider>
      </GlobalErrorBoundary>
    </Router>
  );
}

export default App;