import React, { useEffect, useRef } from 'react';
import flatpickr from 'flatpickr';
import 'flatpickr/dist/flatpickr.min.css';
import './Input.css';

const Input = ({ label, type = 'text', placeholder, value, onChange, required, disabled, className = '', ...props }) => {
    const inputRef = useRef(null);

    useEffect(() => {
        if (type === 'datetime-local' && inputRef.current) {
            flatpickr(inputRef.current, {
                enableTime: true,
                dateFormat: "Y-m-d H:i",
                altInput: true,
                altFormat: "F j, Y at h:i K",
                defaultDate: value,
                onChange: (selectedDates, dateStr) => {
                    // Normalize to the format expected by state
                    if (onChange) {
                        onChange({ target: { value: dateStr } });
                    }
                }
            });
        }
    }, [type, value, onChange]);

    return (
        <div className={`form-group ${className}`}>
            {label && <label className="form-label">{label}</label>}
            <input
                ref={inputRef}
                type={type}
                className="form-input"
                placeholder={placeholder}
                value={value}
                onChange={onChange}
                required={required}
                disabled={disabled}
                {...props}
            />
        </div>
    );
};

export default Input;
