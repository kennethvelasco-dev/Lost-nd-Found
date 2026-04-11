import React, { useEffect } from 'react';
import Card from '../../components/UI/Card';
import { useHttp } from '../../hooks/useHttp';
import StatusState from '../../components/UI/StatusState';
import { DashboardSkeleton } from '../../components/common/Skeleton';

const AdminDashboard = () => {
    const { loading, error, data: stats, request } = useHttp();

    useEffect(() => {
        request({ url: '/admin/stats' });
    }, [request]);

    const statsData = stats || { total_lost: 0, total_found: 0, pending_claims: 0, resolved_items: 0 };

    return (
        <div className="page-container">
            <div className="container">
                <div className="pretty-header">
                    <h1 className="pretty-title">Admin Console</h1>
                    <p className="auth-subtitle">Real-time system oversight and analytics.</p>
                    <div className="title-underline"></div>
                </div>

                <StatusState
                    loading={loading}
                    error={error}
                    onRetry={() => request({ url: '/admin/stats' })}
                    skeleton={<DashboardSkeleton />}
                >
                    <div className="stats-grid" style={{ 
                        display: 'grid', 
                        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', 
                        gap: 'var(--space-4)',
                        marginTop: 'var(--space-4)'
                    }}>
                        <Card>
                            <h3 style={{ color: 'var(--text-secondary)', fontSize: '11px', textTransform: 'uppercase', marginBottom: '8px', letterSpacing: '0.5px' }}>Active Lost Reports</h3>
                            <p style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--primary)', margin: 0 }}>{statsData.total_lost}</p>
                        </Card>
                        <Card>
                            <h3 style={{ color: 'var(--text-secondary)', fontSize: '11px', textTransform: 'uppercase', marginBottom: '8px', letterSpacing: '0.5px' }}>Active Found Items</h3>
                            <p style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--primary)', margin: 0 }}>{statsData.total_found}</p>
                        </Card>
                        <Card>
                            <h3 style={{ color: 'var(--text-secondary)', fontSize: '11px', textTransform: 'uppercase', marginBottom: '8px', letterSpacing: '0.5px' }}>Pending Claims</h3>
                            <p style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--secondary-dark)', margin: 0 }}>{statsData.pending_claims}</p>
                        </Card>
                        <Card>
                            <h3 style={{ color: 'var(--text-secondary)', fontSize: '11px', textTransform: 'uppercase', marginBottom: '8px', letterSpacing: '0.5px' }}>Resolved & Returned</h3>
                            <p style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--success)', margin: 0 }}>{statsData.resolved_items}</p>
                        </Card>
                    </div>
                </StatusState>
            </div>
        </div>
    );
};

export default AdminDashboard;
