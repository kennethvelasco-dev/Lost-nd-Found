import React from 'react';
import Card from '../UI/Card';
import Button from '../UI/Button';

class GlobalErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        console.error("Uncaught error:", error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center', 
                    minHeight: '100vh',
                    background: 'var(--bg)',
                    padding: 'var(--space-4)'
                }}>
                    <Card style={{ maxWidth: '500px', textAlign: 'center' }}>
                        <h1 style={{ color: 'var(--error)', marginBottom: 'var(--space-2)' }}>Oops! Something broke.</h1>
                        <p style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-4)' }}>
                            The application encountered an unexpected error. Don't worry, your data might still be saved in drafts!
                        </p>
                        <Button 
                            variant="primary" 
                            onClick={() => window.location.href = '/'}
                            style={{ width: '100%' }}
                        >
                            Return to Home
                        </Button>
                    </Card>
                </div>
            );
        }

        return this.props.children;
    }
}

export default GlobalErrorBoundary;
