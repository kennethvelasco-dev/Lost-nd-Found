import React from 'react';
import './Auth.css';

const AuthLayout = ({ children }) => {
    return (
        <div className="auth-layout">
            {/* Left Section: Image Area (75%) */}
            <div className="auth-image-section">
                <div className="image-overlay"></div>
                <img src="/auth-bg.png" alt="Campus Backdrop" className="auth-bg-img" />
                <div className="auth-branding-overlay">
                    <h2>Campus Lost & Found</h2>
                    <p>Reconnecting the community with what matters.</p>
                </div>
            </div>

            {/* Right Section: Auth Panel (25%) */}
            <div className="auth-form-section">
                <div className="glass-panel auth-glass-form">
                    {children}
                </div>
            </div>
        </div>
    );
};

export default AuthLayout;

