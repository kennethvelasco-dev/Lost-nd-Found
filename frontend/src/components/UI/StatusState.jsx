import React from 'react';
import Button from './Button';
import './StatusState.css';

const StatusState = ({ 
    loading, 
    error, 
    isEmpty, 
    emptyMessage = "No items found.", 
    onRetry, 
    children 
}) => {
    if (loading) {
        return (
            <div className="status-container loading-state">
                <div className="premium-spinner"></div>
                <p className="status-text">Fetching data...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="status-container error-state">
                <div className="status-icon">⚠️</div>
                <h3>Something went wrong</h3>
                <p className="status-text">{error}</p>
                {onRetry && (
                    <Button onClick={onRetry} variant="primary">
                        Try Again
                    </Button>
                )}
            </div>
        );
    }

    if (isEmpty) {
        return (
            <div className="status-container empty-state">
                <div className="status-icon">🔍</div>
                <h3>Nothing Here</h3>
                <p className="status-text">{emptyMessage}</p>
            </div>
        );
    }

    return <>{children}</>;
};

export default StatusState;
