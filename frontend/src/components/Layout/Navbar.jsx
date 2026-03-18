import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import Button from '../UI/Button';
import './Navbar.css';

const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const user = JSON.parse(localStorage.getItem('user') || 'null');
  const isAdmin = user?.role === 'admin';

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  const isActive = (path) => location.pathname === path ? 'active' : '';

  return (
    <nav className="navbar">
      <div className="container navbar-inner">
        {/* Top Row: Branding */}
        <div className="navbar-brand-row">
            <Link to="/" className="navbar-logo">
                <div className="brand-pill">
                    <img src="/assets/logo.png" alt="Logo" />
                    <span className="brand-name">Campus Lost & Found</span>
                </div>
            </Link>
            
            {user && (
            <div className="user-control">
                <span className="user-welcome">Welcome, <strong>{user.username}</strong></span>
                <Button variant="secondary" size="sm" onClick={handleLogout} className="logout-btn">
                Sign Out
                </Button>
            </div>
            )}
        </div>

        {/* Bottom Row: Navigation Tabs */}
        {user && (
            <div className="navbar-links-row">
                {!isAdmin ? (
                <div className="nav-tabs">
                    <Link to="/lost-items" className={`nav-tab ${isActive('/lost-items')}`}>Discovery</Link>
                    <Link to="/report-item" className={`nav-tab ${isActive('/report-item')}`}>Report Lost</Link>
                    <Link to="/returned-items" className={`nav-tab ${isActive('/returned-items')}`}>Verified Handovers</Link>
                </div>
                ) : (
                <div className="nav-tabs">
                    <Link to="/admin/dashboard" className={`nav-tab ${isActive('/admin/dashboard')}`}>Console</Link>
                    <Link to="/admin/claims" className={`nav-tab ${isActive('/admin/claims')}`}>Review Claims</Link>
                    <Link to="/admin/return-item" className={`nav-tab ${isActive('/admin/return-item')}`}>Log Return</Link>
                    <Link to="/admin/reports" className={`nav-tab ${isActive('/admin/reports')}`}>Analytics</Link>
                </div>
                )}
            </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
