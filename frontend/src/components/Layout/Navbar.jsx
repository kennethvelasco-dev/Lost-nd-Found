import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import './Navbar.css';

const Navbar = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <nav className="navbar">
            {/* Row 1: Site Title */}
            <div className="nav-row-branding">
                <h1 className="nav-site-title">LostnDFound</h1>
            </div>

            {/* Row 2: Navigation Tabs */}
            <div className="nav-row-tabs">
                <div className="nav-tabs-container">
                    <NavLink
                        to="/lost-items"
                        className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                    >
                        Lost Items
                    </NavLink>
                    <NavLink
                        to="/report-item"
                        className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                    >
                        Report Item
                    </NavLink>
                    <NavLink
                        to="/returned-items"
                        className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                    >
                        Returned Items
                    </NavLink>
                    {user?.role === 'admin' && (
                        <NavLink
                            to="/admin/dashboard"
                            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                        >
                            Admin Dashboard
                        </NavLink>
                    )}
                </div>
                <div className="nav-auth-container">
                    {user ? (
                        <>
                            <span className="nav-link" style={{ marginRight: '1rem' }}>Hi, {user.username}</span>
                            <button onClick={handleLogout} className="nav-link auth-btn" style={{ border: 'none', cursor: 'pointer' }}>Logout</button>
                        </>
                    ) : (
                        <>
                            <NavLink to="/login" className="nav-link">Login</NavLink>
                            <NavLink to="/signup" className="nav-link auth-btn">Sign Up</NavLink>
                        </>
                    )}
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
