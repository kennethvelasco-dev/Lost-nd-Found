import React, { useState, useEffect } from 'react';
import Card from '../../components/UI/Card';
import api from '../../services/api';

const AdminDashboard = () => {
    const [stats, setStats] = useState({
        total_lost: 0,
        total_found: 0,
        pending_claims: 0,
        resolved_items: 0
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await api.get('/admin/stats');
                setStats(response.data.data);
            } catch (err) {
                console.error('Failed to fetch stats', err);
            } finally {
                setLoading(false);
            }
        };
        fetchStats();
    }, []);

    return (
        <div className="page-container">
            <div className="container">
                <div className="pretty-header">
                    <h1 className="pretty-title">Admin Console</h1>
                    <p className="auth-subtitle">Real-time statistics and system oversight.</p>
                    <div className="title-underline"></div>
                </div>

                {loading ? (
                    <div style={{ textAlign: 'center', padding: '100px' }}>Analyzing system data...</div>
                ) : (
                    <div className="stats-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-4)' }}>
                        <Card>
                            <h3 style={{ color: 'var(--text-muted)', fontSize: '12px', textTransform: 'uppercase', marginBottom: '8px' }}>Active Lost Reports</h3>
                            <p style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--primary)' }}>{stats.total_lost}</p>
                        </Card>
                        <Card>
                            <h3 style={{ color: 'var(--text-muted)', fontSize: '12px', textTransform: 'uppercase', marginBottom: '8px' }}>Active Found Items</h3>
                            <p style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--primary)' }}>{stats.total_found}</p>
                        </Card>
                        <Card>
                            <h3 style={{ color: 'var(--text-muted)', fontSize: '12px', textTransform: 'uppercase', marginBottom: '8px' }}>Pending Claims</h3>
                            <p style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--secondary-dark)' }}>{stats.pending_claims}</p>
                        </Card>
                        <Card>
                            <h3 style={{ color: 'var(--text-muted)', fontSize: '12px', textTransform: 'uppercase', marginBottom: '8px' }}>Completed Returns</h3>
                            <p style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--success)' }}>{stats.resolved_items}</p>
                        </Card>
                    </div>
                )}
            </div>
        </div>
    );
};

export default AdminDashboard;
