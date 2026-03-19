import React, { useState, useRef } from 'react';
import './FileUpload.css';

const FileUpload = ({ label, onFilesChange, maxFiles = 3, initialFiles = [] }) => {
    const [previews, setPreviews] = useState(initialFiles);
    const fileInputRef = useRef(null);

    const handleFileChange = (e) => {
        const files = Array.from(e.target.files);
        const availableSlots = maxFiles - previews.length;
        const filesToProcess = files.slice(0, availableSlots);

        filesToProcess.forEach(file => {
            const reader = new FileReader();
            reader.onloadend = () => {
                const base64String = reader.result;
                setPreviews(prev => {
                    const next = [...prev, base64String];
                    onFilesChange(next);
                    return next;
                });
            };
            reader.readAsDataURL(file);
        });
        
        // Reset input for same file re-selection if needed
        e.target.value = '';
    };

    const removeFile = (index, e) => {
        e.stopPropagation();
        const next = previews.filter((_, i) => i !== index);
        setPreviews(next);
        onFilesChange(next);
    };

    return (
        <div className="file-upload-container">
            <label className="form-label">{label} ({previews.length}/{maxFiles})</label>
            
            <div className="upload-grid">
                {previews.map((src, index) => (
                    <div key={index} className="preview-item">
                        <img src={src} alt={`Upload ${index + 1}`} className="upload-preview" />
                        <button 
                            type="button" 
                            className="remove-file-btn"
                            onClick={(e) => removeFile(index, e)}
                        >
                            ×
                        </button>
                    </div>
                ))}

                {previews.length < maxFiles && (
                    <div className="upload-zone" onClick={() => fileInputRef.current.click()}>
                        <div className="upload-placeholder">
                            <span className="upload-icon">+</span>
                            <p style={{ fontSize: '12px' }}>Add Photo</p>
                        </div>
                    </div>
                )}
            </div>

            <input 
                type="file" 
                ref={fileInputRef} 
                onChange={handleFileChange} 
                accept="image/*" 
                multiple
                style={{ display: 'none' }}
            />
        </div>
    );
};

export default FileUpload;
