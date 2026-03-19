import React, { useEffect } from 'react';
import Card from '../../components/UI/Card';
import { useHttp } from '../../hooks/useHttp';
import StatusState from '../../components/UI/StatusState';
import './Discovery.css';

const MyActivities = () => {
    const { loading, error, data, request } = useHttp();

    useEffect(() => {
        request({ url: '/items/my-activities' });
    }, [request]);

    const activities = data || { reports: [], claims: [] };

    const getStatusColor = (status) => {
        switch (status?.toLowerCase()) {
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

    const StatusBadge = ({ status }) => (
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
            {(status || 'unknown').replace('_', ' ')}
        </span>
    );

    const ActivityCard = ({ item, type }) => (
        <Card>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', alignItems: 'center' }}>
                <h3 style={{ margin: 0, fontSize: '1.1rem' }}>
                    {type === 'report' ? item.item_type : `Claim #${item.claim_id}`}
                </h3>
                <StatusBadge status={item.status || item.decision || 'pending'} />
            </div>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', margin: '4px 0' }}>
                {type === 'report' 
                    ? `${item.category} • ${item.last_seen_location || item.found_location}`
                    : `Linked to: ${item.found_item_type || 'Unknown Item'}`
                }
            </p>
            {(item.rejection_reason || item.decision_reason) && (
                <div style={{ 
                    marginTop: '12px', 
                    padding: '12px', 
                    borderRadius: 'var(--radius-sm)', 
                    backgroundColor: 'rgba(231, 76, 60, 0.08)', 
                    borderLeft: '4px solid var(--danger)' 
                }}>
                    <p style={{ margin: 0, fontSize: '12px', color: 'var(--danger)', fontWeight: 700 }}>Admin Feedback:</p>
                    <p style={{ margin: '4px 0 0 0', fontSize: '13px', color: 'var(--text)' }}>
                        {item.rejection_reason || item.decision_reason}
                    </p>
                </div>
            )}
        </Card>
    );

    const hasAnyActivity = activities.reports.length > 0 || activities.claims.length > 0;

    return (
        <div className="page-container">
            <div className="container">
                <div className="pretty-header">
                    <h1 className="pretty-title">My Activities</h1>
                    <p className="auth-subtitle">Track the status of your reports and claims in real-time.</p>
                    <div className="title-underline"></div>
                </div>

                <StatusState 
                    loading={loading} 
                    error={error} 
                    isEmpty={!hasAnyActivity} 
                    emptyMessage="You haven't reported or claimed any items yet."
                    onRetry={() => request({ url: '/items/my-activities' })}
                >
                    <div className="activities-layout" style={{ 
                        display: 'grid', 
                        gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', 
                        gap: 'var(--space-5)',
                        marginTop: 'var(--space-4)'
                    }}>
                        {/* Reports Section */}
                        <div className="activity-section">
                            <h2 style={{ marginBottom: 'var(--space-3)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                📋 My Reports
                            </h2>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                                {activities.reports.map(report => (
                                    <ActivityCard key={report.id} item={report} type="report" />
                                ))}
                                {activities.reports.length === 0 && <p style={{ color: 'var(--text-muted)' }}>No reports filed.</p>}
                            </div>
                        </div>

                        {/* Claims Section */}
                        <div className="activity-section">
                            <h2 style={{ marginBottom: 'var(--space-3)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                📑 My Claims
                            </h2>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                                {activities.claims.map(claim => (
                                    <ActivityCard key={claim.claim_id} item={claim} type="claim" />
                                ))}
                                {activities.claims.length === 0 && <p style={{ color: 'var(--text-muted)' }}>No claims submitted.</p>}
                            </div>
                        </div>
                    </div>
                </StatusState>
            </div>
        </div>
    );
};

export default MyActivities;
