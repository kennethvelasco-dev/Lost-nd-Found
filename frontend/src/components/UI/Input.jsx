import React from 'react';
import './Input.css';

const Input = ({ label, error, className = '', ...props }) => {
  return (
    <div className={`form-group ${className}`}>
      {label && <label className="form-label">{label}</label>}
      <input 
        className={`form-input ${error ? 'input-error' : ''}`} 
        {...props} 
      />
      {error && <span className="error-message">{error}</span>}
    </div>
  );
};

export default Input;
