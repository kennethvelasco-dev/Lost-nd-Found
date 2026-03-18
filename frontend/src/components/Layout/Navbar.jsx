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
      {/* Branding Row - Now centered and more prominent */}
      <div className="navbar-brand-row">
        <div className="brand-pill">
            <Link to="/" className="navbar-logo">
                <img src="/assets/logo.png" alt="Lost & Found" />
                <span className="brand-name">Campus Lost & Found</span>
            </Link>
        </div>
        
        {user && (
          <div className="user-control">
            <Button variant="secondary" size="sm" onClick={handleLogout} className="logout-btn">
              Sign Out
            </Button>
          </div>
        )}
      </div>

      {/* Navigation Row */}
      {user && (
        <div className="navbar-links-row">
          <div className="nav-links-container">
            {!isAdmin ? (
              <>
                <Link to="/lost-items" className={`nav-link ${isActive('/lost-items')}`}>Lost Items</Link>
                <Link to="/found-items" className={`nav-link ${isActive('/found-items')}`}>Found Items</Link>
                <Link to="/report-item" className={`nav-link ${isActive('/report-item')}`}>Report Item</Link>
                <Link to="/returned-items" className={`nav-link ${isActive('/returned-items')}`}>Verified Handovers</Link>
              </>
            ) : (
              <>
                <Link to="/admin/dashboard" className={`nav-link ${isActive('/admin/dashboard')}`}>Admin Console</Link>
                <Link to="/admin/claims" className={`nav-link ${isActive('/admin/claims')}`}>Review Claims</Link>
                <Link to="/admin/return-item" className={`nav-link ${isActive('/admin/return-item')}`}>Log Return</Link>
                <Link to="/admin/reports" className={`nav-link ${isActive('/admin/reports')}`}>Reports</Link>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
