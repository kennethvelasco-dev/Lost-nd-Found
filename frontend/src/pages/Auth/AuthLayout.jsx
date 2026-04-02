import React from 'react';
import './Auth.css';

const AuthLayout = ({ children }) => {
    return (
        <div className="auth-layout">
            {/* Left Section: Image Area (75%) */}
            <div className="auth-image-section">
                <div className="image-overlay"></div>
                <img src="/assets/farm.jpg" alt="Campus Backdrop" className="auth-bg-img" />
                <div className="auth-branding-overlay">
                    <h2>Lost & Found</h2>
                    <p>Reconnecting our campus community, one item at a time.</p>
                </div>
            </div>

            {/* Right Section: Auth Panel (25%) */}
            <div className="auth-form-section">
                <div className="auth-container">
                    <img src="/assets/pub_logo.png" alt="Lost & Found Logo" className="auth-logo" />
                    {children}
                </div>
            </div>
        </div>
    );
};

export default AuthLayout;

