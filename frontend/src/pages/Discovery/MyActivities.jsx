import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import Card from '../../components/UI/Card';
import './Discovery.css';

const MyActivities = () => {
    const [activities, setActivities] = useState({ reports: [], claims: [] });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchActivities = async () => {
            try {
                const response = await api.get('/items/my-activities');
                setActivities(response.data.data);
            } catch (err) {
                console.error('Failed to fetch activities', err);
            } finally {
                setLoading(false);
            }
        };
        fetchActivities();
    }, []);

    const getStatusColor = (status) => {
        switch (status) {
            case 'pending': 
            case 'pending_approval': return 'var(--secondary-dark)';
            case 'approved':
            case 'lost':
            case 'found': return 'var(--success)';
            case 'rejected': return 'var(--danger)';
            case 'completed': return 'var(--primary)';
            default: return 'var(--text-muted)';
        }
    };

    const renderStatusBadge = (status) => (
        <span style={{ 
            fontSize: '10px', 
            fontWeight: 800, 
            padding: '4px 8px', 
            borderRadius: '12px', 
            backgroundColor: `${getStatusColor(status)}20`, 
            color: getStatusColor(status),
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
        }}>
            {status.replace('_', ' ')}
        </span>
    );

    if (loading) return <div className="page-container"><p>Loading your activities...</p></div>;

    return (
        <div className="page-container">
            <div className="container">
                <div className="pretty-header">
                    <h1 className="pretty-title">My Activities</h1>
                    <p className="auth-subtitle">Track the status of your reports and claims.</p>
                    <div className="title-underline"></div>
                </div>

                <div className="activities-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)' }}>
                    {/* MY REPORTS */}
                    <div className="activity-section">
                        <h2 style={{ marginBottom: 'var(--space-3)', color: 'var(--text)' }}>My Reports</h2>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                            {activities.reports.length > 0 ? activities.reports.map(report => (
                                <Card key={report.id}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                        <h3 style={{ margin: 0, fontSize: '1.1rem' }}>{report.item_type}</h3>
                                        {renderStatusBadge(report.status)}
                                    </div>
                                    <p style={{ fontSize: '13px', color: 'var(--text-muted)', margin: '4px 0' }}>{report.category} • Observed at {report.last_seen_location || report.found_location}</p>
                                    {report.rejection_reason && (
                                        <div style={{ marginTop: '12px', padding: '10px', borderRadius: 'var(--radius-sm)', backgroundColor: 'var(--danger)10', borderLeft: '4px solid var(--danger)' }}>
                                            <p style={{ margin: 0, fontSize: '12px', color: 'var(--danger)', fontWeight: 600 }}>Reason for rejection:</p>
                                            <p style={{ margin: '4px 0 0 0', fontSize: '13px', color: 'var(--text)' }}>{report.rejection_reason}</p>
                                        </div>
                                    )}
                                </Card>
                            )) : <p style={{ color: 'var(--text-muted)' }}>No reports filed yet.</p>}
                        </div>
                    </div>

                    {/* MY CLAIMS */}
                    <div className="activity-section">
                        <h2 style={{ marginBottom: 'var(--space-3)', color: 'var(--text)' }}>My Claims</h2>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                            {activities.claims.length > 0 ? activities.claims.map(claim => (
                                <Card key={claim.claim_id}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                        <h3 style={{ margin: 0, fontSize: '1.1rem' }}>Claim #{claim.claim_id}</h3>
                                        {renderStatusBadge(claim.status || claim.decision)}
                                    </div>
                                    <p style={{ fontSize: '13px', color: 'var(--text-muted)', margin: '4px 0' }}>Item: {claim.found_item_type || 'Unlinked Claim'}</p>
                                    {claim.decision_reason && (
                                        <div style={{ marginTop: '12px', padding: '10px', borderRadius: 'var(--radius-sm)', backgroundColor: 'var(--danger)10', borderLeft: '4px solid var(--danger)' }}>
                                            <p style={{ margin: 0, fontSize: '12px', color: 'var(--danger)', fontWeight: 600 }}>Admin Feedback:</p>
                                            <p style={{ margin: '4px 0 0 0', fontSize: '13px', color: 'var(--text)' }}>{claim.decision_reason}</p>
                                        </div>
                                    )}
                                </Card>
                            )) : <p style={{ color: 'var(--text-muted)' }}>No claims submitted yet.</p>}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MyActivities;
