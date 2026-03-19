import React, { useState, useRef } from 'react';
import './FileUpload.css';

const FileUpload = ({ label, onFileSelect, value }) => {
    const [preview, setPreview] = useState(value || null);
    const fileInputRef = useRef(null);

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
                const base64String = reader.result;
                setPreview(base64String);
                onFileSelect(base64String);
            };
            reader.readAsDataURL(file);
        }
    };

    const triggerInput = () => {
        fileInputRef.current.click();
    };

    return (
        <div className="file-upload-container">
            <label className="form-label">{label}</label>
            <div 
                className={`upload-zone ${preview ? 'has-preview' : ''}`} 
                onClick={triggerInput}
            >
                {preview ? (
                    <img src={preview} alt="Upload preview" className="upload-preview" />
                ) : (
                    <div className="upload-placeholder">
                        <span className="upload-icon">📷</span>
                        <p>Click to capture or select photo</p>
                    </div>
                )}
                <input 
                    type="file" 
                    ref={fileInputRef} 
                    onChange={handleFileChange} 
                    accept="image/*" 
                    style={{ display: 'none' }}
                    required={!value}
                />
            </div>
        </div>
    );
};

export default FileUpload;
