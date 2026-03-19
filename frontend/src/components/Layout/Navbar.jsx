import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import Button from '../UI/Button';
import './Navbar.css';

const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const isAdmin = user?.role === 'admin' || user?.role === 'Admin';

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path) => location.pathname === path ? 'active' : '';

  return (
    <nav className="navbar">
      <div className="container navbar-inner">
        {/* Top Row: Full-width Brand & Controls */}
        <div className="navbar-brand-row">
            <div className="branding-left">
                <Link to="/" className="navbar-logo-link">
                    <img src="/assets/logo.png" alt="University Logo" className="main-logo" />
                    <h1 className="main-brand-title">Campus Lost & Found</h1>
                </Link>
            </div>
            
            {user && (
            <div className="controls-right user-control">
                <div className="user-info-pill">
                    <span className="user-welcome">Hello, <strong>{user.username}</strong></span>
                </div>
                <Button variant="secondary" size="sm" onClick={handleLogout} className="logout-btn raised-pill">
                Sign Out from Portal
                </Button>
            </div>
            )}
        </div>

        {/* Bottom Row: Centered Navigation */}
        {user && (
            <div className="navbar-links-row">
                {!isAdmin ? (
                <div className="nav-tabs glass-tabs">
                    <Link to="/lost-items" className={`nav-tab ${isActive('/lost-items')}`}>Search Directory</Link>
                    <Link to="/report-item" className={`nav-tab ${isActive('/report-item')}`}>Report Lost Item</Link>
                    <Link to="/my-activities" className={`nav-tab ${isActive('/my-activities')}`}>My Activities</Link>
                    <Link to="/returned-items" className={`nav-tab ${isActive('/returned-items')}`}>Released Items</Link>
                </div>
                ) : (
                <div className="nav-tabs glass-tabs">
                    <Link to="/admin/dashboard" className={`nav-tab ${isActive('/admin/dashboard')}`}>Admin Console</Link>
                    <Link to="/admin/claims" className={`nav-tab ${isActive('/admin/claims')}`}>Review Claims</Link>
                    <Link to="/admin/reports" className={`nav-tab ${isActive('/admin/reports')}`}>Approve Reports</Link>
                    <Link to="/admin/return-item" className={`nav-tab ${isActive('/admin/return-item')}`}>Log Return</Link>
                </div>
                )}
            </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
