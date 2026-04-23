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
                        <p style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-3)' }}>
                            The application encountered an unexpected error. Don't worry, your data might still be saved in drafts!
                        </p>
                        
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                            <Button 
                                variant="primary" 
                                onClick={() => window.location.href = '/'}
                                style={{ width: '100%' }}
                            >
                                Reload Application
                            </Button>
                            
                            <Button 
                                variant="secondary" 
                                onClick={() => {
                                    localStorage.clear();
                                    sessionStorage.clear();
                                    window.location.href = '/login';
                                }}
                                style={{ width: '100%', fontSize: '13px' }}
                            >
                                Factory Reset (Clears Login & Cache)
                            </Button>
                        </div>

                        {import.meta.env.MODE === 'development' && (
                            <details style={{ marginTop: '20px', textAlign: 'left', fontSize: '12px', opacity: 0.7 }}>
                                <summary>Technical Details</summary>
                                <pre style={{ whiteSpace: 'pre-wrap' }}>{this.state.error?.toString()}</pre>
                            </details>
                        )}
                    </Card>
                </div>
            );
        }

        return this.props.children;
    }
}

export default GlobalErrorBoundary;
