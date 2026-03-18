import React from 'react';
import Navbar from './Navbar';
import './Layout.css';

const Layout = ({ children }) => {
    return (
        <div className="layout">
            <Navbar />
            <main className="main-content">
                {/* Removed redundant .container here to allow pages to manage their own layout */}
                {children}
            </main>
        </div>
    );
};

export default Layout;
