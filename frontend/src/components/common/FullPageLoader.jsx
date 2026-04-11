import React from 'react';
import './FullPageLoader.css';

const FullPageLoader = ({ message = 'Preparing your experience...' }) => {
  return (
    <div className="fullpage-loader">
      <div className="fullpage-loader-content">
        <div className="fullpage-spinner" />
        <p className="fullpage-loader-text">{message}</p>
      </div>
    </div>
  );
};

export default FullPageLoader;